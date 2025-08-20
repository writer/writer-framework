from typing import TYPE_CHECKING, Any, Dict, Optional, Type

import httpx
from writerai import DefaultHttpxClient, Writer

import writer.core_ui
import writer.evaluator
from writer.ss_types import WriterConfigurationError

if TYPE_CHECKING:
    from writer.blueprints import BlueprintRunner
    from writer.core_ui import Component
    from writer.ss_types import InstancePath

BlueprintBlock_T = Type["BlueprintBlock"]
block_map: Dict[str, BlueprintBlock_T] = {}


class BlueprintBlock:
    _parent_client_class = httpx.Client
    _custom_httpx_client: Optional[httpx.Client] = None
    _log_requests: bool = True

    @classmethod
    def register(cls, type: str):
        block_map[type] = cls

    def __init_subclass__(
        cls,
        custom_httpx_client: Optional['httpx.Client'] = None,
        log_requests: bool = True,
        **kwargs
    ):
        super().__init_subclass__(**kwargs)
        cls._custom_httpx_client = custom_httpx_client
        cls._log_requests = log_requests

    def __init__(
        self,
        component: writer.core_ui.Component,
        runner: "BlueprintRunner",
        execution_environment: Dict,
    ):
        self.outcome: Optional[str] = None
        self.message: Optional[str] = None
        self.component = component
        self.runner = runner
        self.execution_time_in_seconds = -1.0
        self.execution_environment = execution_environment
        # A stable snapshot of the execution environment taken after the block
        # has finished running. Used when generating logs to avoid concurrent
        # mutations while serialising.
        self.execution_environment_snapshot: Optional[Dict] = None
        self.result = None
        self.return_value = None
        self.instance_path: InstancePath = [{"componentId": component.id, "instanceNumber": 0}]
        self.evaluator = writer.evaluator.Evaluator(
            runner.session.session_state, runner.session.session_component_tree
        )

    def _handle_missing_field(self, field_key):
        field_content = self.component.content.get(field_key)
        if field_content:
            raise WriterConfigurationError(
                f"The field `{field_key}` is required. The expression specified, `{field_content}`, resulted in an empty value."
            )
        else:
            raise WriterConfigurationError(
                f"The field `{field_key}` is required. It was left empty."
            )

    def _get_field(self, field_key: str, as_json=False, default_field_value=None, required=False):
        if default_field_value is None:
            if as_json:
                default_field_value = "{}"
            else:
                default_field_value = ""
        value = self.evaluator.evaluate_field(
            self.instance_path, field_key, as_json, default_field_value, self.execution_environment
        )

        if required and (value is None or value == "" or value == {}):
            self._handle_missing_field(field_key)

        return value

    def _set_state(self, expr: str, value: Any):
        self.evaluator.set_state(
            expr, self.instance_path, value, base_context=self.execution_environment
        )

    def run(self):
        pass

    def create_httpx_client(self, *args, **kwargs) -> httpx.Client:
        """
        Create a custom HTTPX client with request and response logging.
        """
        logger = self.create_logger() if self._log_requests else None

        event_hooks = {
            "request": [logger.request_hook] if logger else [],
            "response": [logger.response_hook] if logger else [],
        }

        def send(self_inner, request, **kw):
            response = self._parent_client_class.send(self_inner, request, **kw)
            log_entry = response.extensions.get("log_entry")
            if log_entry:
                # Store reference to log entry for later update
                response._log_entry_ref = log_entry
                
                try:
                    # For non-streaming responses, capture content immediately
                    if response.is_closed or response.is_stream_consumed:
                        log_entry["response"]["content"] = response.text
                    else:
                        # For streaming responses, we'll update after consumption
                        log_entry["response"]["content"] = "<pending stream consumption>"
                        
                        # Wrap the response read/iter methods to capture content after streaming
                        original_read = response.read
                        original_iter_raw = response.iter_raw
                        original_iter_bytes = response.iter_bytes
                        original_iter_text = response.iter_text
                        original_iter_lines = response.iter_lines
                        
                        def wrapped_read():
                            try:
                                content = original_read()
                            except Exception as e:
                                if hasattr(response, '_log_entry_ref'):
                                    response._log_entry_ref["response"]["content"] = f"<error reading response stream: {e}>"
                                raise
                            else:
                                if hasattr(response, '_log_entry_ref'):
                                    try:
                                        response._log_entry_ref["response"]["content"] = content.decode('utf-8', errors='replace')
                                    except Exception:
                                        response._log_entry_ref["response"]["content"] = "<binary content>"
                                return content
                        
                        def wrapped_iter_raw(*args, **kwargs):
                            chunks = []
                            try:
                                for chunk in original_iter_raw(*args, **kwargs):
                                    chunks.append(chunk)
                                    yield chunk
                            finally:
                                if hasattr(response, '_log_entry_ref'):
                                    try:
                                        response._log_entry_ref["response"]["content"] = b"".join(chunks).decode("utf-8", errors="replace")
                                    except Exception:
                                        response._log_entry_ref["response"]["content"] = "<binary content>"
                        
                        def wrapped_iter_bytes(*args, **kwargs):
                            accumulated_content = []
                            try:
                                for chunk in original_iter_bytes(*args, **kwargs):
                                    accumulated_content.append(chunk)
                                    yield chunk
                            finally:
                                if hasattr(response, '_log_entry_ref'):
                                    try:
                                        full_content = b''.join(accumulated_content)
                                        response._log_entry_ref["response"]["content"] = full_content.decode('utf-8', errors='replace')
                                    except Exception:
                                        response._log_entry_ref["response"]["content"] = "<binary content>"
                        
                        def wrapped_iter_text(*args, **kwargs):
                            text_chunks = []
                            try:
                                for chunk in original_iter_text(*args, **kwargs):
                                    text_chunks.append(chunk)
                                    yield chunk
                            finally:
                                if hasattr(response, '_log_entry_ref'):
                                    response._log_entry_ref["response"]["content"] = ''.join(text_chunks)
                        
                        def wrapped_iter_lines(*args, **kwargs):
                            lines = []
                            try:
                                for line in original_iter_lines(*args, **kwargs):
                                    lines.append(line)
                                    yield line
                            finally:
                                if hasattr(response, '_log_entry_ref'):
                                    response._log_entry_ref["response"]["content"] = '\n'.join(lines)
                        
                        response.read = wrapped_read
                        response.iter_raw = wrapped_iter_raw
                        response.iter_bytes = wrapped_iter_bytes
                        response.iter_text = wrapped_iter_text
                        response.iter_lines = wrapped_iter_lines
                except Exception as e:
                    log_entry["response"]["content"] = f"<error reading response: {e}>"
            return response

        # Create a new class that inherits from the parent client class
        # and overrides the send method to include logging.
        LoggingHttpxClient = type(
            "LoggingHttpxClient",
            (self._parent_client_class,),
            {"send": send}
        )

        return LoggingHttpxClient(
            *args,
            event_hooks=kwargs.pop("event_hooks", {}) | event_hooks,
            **kwargs
        )

    def acquire_httpx_client(self) -> httpx.Client:
        """
        Acquire an HTTPX client for making requests.
        """
        if self._custom_httpx_client:
            return self._custom_httpx_client

        # Create a new HTTPX client with request and response logging
        return self.create_httpx_client()

    def create_logger(
            self,
            env_storage_key: Optional[str] = None
    ):
        import uuid
        instance_path = self.instance_path[0].get('componentId', None)

        class ExecutionEnvironmentLogger:
            """
            This class provides hooks to log requests and responses
            to the execution environment.
            """
            env_storage_key = 'httpx_requests'

            def __init__(
                    self,
                    env: Dict,
                    env_storage_key: Optional[str] = None
            ):
                self.env = env  # Fallback environment

                if env_storage_key:
                    self.env_storage_key = env_storage_key

                # Create a copy of inherited API calls to avoid shared reference issues
                inherited_calls = self.env.get(self.env_storage_key, [])
                self.env[self.env_storage_key] = inherited_calls.copy()
                self.instance_path = instance_path
            
            def _get_current_execution_environment(self) -> Dict:
                """Resolve the currently executing block's environment for logging."""
                try:
                    from writer.blueprints import get_current_block
                    current_block = get_current_block()
                    if current_block and hasattr(current_block, 'execution_environment'):
                        return current_block.execution_environment
                except Exception:
                    pass
                return self.env

            def request_hook(self, request: httpx.Request):
                import datetime as dt
                request_id = str(uuid.uuid4())
                
                # Get the current block's ID for accurate logging
                current_block_id = self.instance_path  # fallback (should be componentId)
                try:
                    from writer.blueprints import get_current_block
                    current_block = get_current_block()
                    if current_block and hasattr(current_block, 'instance_path'):
                        # Extract componentId from the current block's instance path
                        current_block_id = current_block.instance_path[0].get('componentId', None)
                except Exception:
                    pass
                
                # Capture request content
                content = None
                if request.content:
                    try:
                        content = request.content.decode('utf-8', errors='replace')
                    except Exception:
                        content = "<binary content>"
                elif request.stream:
                    # For streaming requests, we can't easily capture the content
                    # without consuming the stream
                    content = "<streaming request body>"
                else:
                    content = None

                log_entry = {
                    'id': request_id,
                    'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                    'created_by': current_block_id,
                    'request': {
                        'method': request.method,
                        'url': str(request.url),
                        'headers': dict(request.headers),
                        'content': content
                    },
                    'response': None  # Will populate later
                }

                # Resolve current block's environment for accurate logging
                target_env = self._get_current_execution_environment()
                target_env.setdefault(self.env_storage_key, []).append(log_entry)
                request.extensions['log_entry'] = log_entry

            def response_hook(self, response: httpx.Response):
                log_entry = response.request.extensions.get('log_entry')
                if not log_entry:
                    # Unlikely scenario
                    return

                log_entry['response'] = {
                    'status_code': response.status_code,
                    'url': str(response.url),
                    'headers': dict(response.headers),
                    'content': None  # Initially empty
                }
                response.extensions['log_entry'] = log_entry

        return ExecutionEnvironmentLogger(
            self.execution_environment,
            env_storage_key=env_storage_key
            )


class WriterBlock(BlueprintBlock):
    """
    Base class for all Writer blocks.
    """
    _parent_client_class = DefaultHttpxClient

    def __init__(
        self,
        component: writer.core_ui.Component,
        runner: "BlueprintRunner",
        execution_environment: Dict,
    ):
        super().__init__(component, runner, execution_environment)

        # Initialize the SDK client via block property
        # to set the context and enable logging for AI module downstream.
        # This way, the AI module can use the same HTTPX client
        # without explicitly passing it.
        _ = self.writer_sdk_client

    def _acquire_writer_client(
            self,
            force_new_client: Optional[bool] = False
    ) -> Writer:
        from writer.ai import WriterAIManager

        return WriterAIManager.acquire_client(
            custom_httpx_client=self.acquire_httpx_client(),
            force_new_client=force_new_client
            )

    def create_logger(self, env_storage_key: Optional[str] = "api_calls"):
        return super().create_logger(env_storage_key=env_storage_key)

    @property
    def writer_sdk_client(self) -> Writer:
        return self._acquire_writer_client()
