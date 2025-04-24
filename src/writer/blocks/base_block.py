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
                try:
                    log_entry["response"]["content"] = (
                        response.text if response.is_closed or response.is_stream_consumed else "<stream>"
                    )
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
                self.env = env

                if env_storage_key:
                    self.env_storage_key = env_storage_key

                self.env.setdefault(
                    self.env_storage_key, []
                    )
                self.instance_path = instance_path

            def request_hook(self, request: httpx.Request):
                import datetime as dt
                request_id = str(uuid.uuid4())
                if not request.stream:
                    content = \
                        request.content.decode('utf-8', errors='replace') \
                        if request.content else None
                else:
                    content = "<stream>"

                log_entry = {
                    'id': request_id,
                    'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                    'created_by': self.instance_path,
                    'request': {
                        'method': request.method,
                        'url': str(request.url),
                        'headers': dict(request.headers),
                        'content': content
                    },
                    'response': None  # Will populate later
                }

                self.env[self.env_storage_key].append(log_entry)
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
