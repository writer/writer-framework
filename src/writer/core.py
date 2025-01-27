import asyncio
import base64
import contextlib
import copy
import dataclasses
import datetime
import functools
import inspect
import io
import logging
import math
import multiprocessing
import numbers
import re
import secrets
import time
import traceback
import typing
import urllib.request
from contextvars import ContextVar
from multiprocessing.process import BaseProcess
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypedDict,
    Union,
    cast,
)

import pyarrow  # type: ignore

import writer.blocks
import writer.evaluator
from writer import core_ui
from writer.core_ui import Component
from writer.serializer import serialize
from writer.ss_types import (
    InstancePath,
    Readable,
    ServeMode,
    WorkflowExecutionLog,
    WriterEvent,
    WriterEventResult,
    WriterFileItem,
)

if TYPE_CHECKING:
    import pandas

    from writer.app_runner import AppProcess
    from writer.ss_types import AppProcessServerRequest

@dataclasses.dataclass
class CurrentRequest:
    session_id: str
    request: 'AppProcessServerRequest'

_current_request: ContextVar[Optional[CurrentRequest]] = ContextVar("current_request", default=None)

@contextlib.contextmanager
def use_request_context(session_id: str, request: 'AppProcessServerRequest'):
    """
    Context manager to set the current request context.

    >>> session_id = "xxxxxxxxxxxxxxxxxxxxxxxxx"
    >>> request = AppProcessServerRequest(type='event', payload=EventPayload(event='my_event'))
    >>> with use_request_context(session_id, request):
    >>>     pass
    """
    try:
        _current_request.set(CurrentRequest(session_id, request))
        yield
    finally:
        _current_request.set(None)

def get_app_process() -> 'AppProcess':
    """
    Retrieves the Writer Framework process context.

    >>> _current_process = get_app_process()
    >>> _current_process.bmc_components # get the component tree
    """
    from writer.app_runner import AppProcess  # Needed during runtime
    raw_process: BaseProcess = multiprocessing.current_process()
    if isinstance(raw_process, AppProcess):
        return raw_process

    raise RuntimeError( "Failed to retrieve the AppProcess: running in wrong context")


def import_failure(rvalue: Any = None):
    """
    This decorator captures the failure to load a volume and returns a value instead.

    If the import of a module fails, the decorator returns the value given as a parameter.

    >>> @import_failure(rvalue=False)
    >>> def my_handler():
    >>>     import pandas
    >>>     return pandas.DataFrame()

    :param rvalue: the value to return
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ImportError:
                return rvalue
        return wrapper
    return decorator


class Config:

    is_mail_enabled_for_log: bool = False
    mode: ServeMode = "run"
    logger: Optional[logging.Logger] = None
    feature_flags: list[str] = []


class SessionMail:

    LOG_ENTRY_MAX_LEN = 8192

    def __init__(self):
        self.mail = []
    
    def add_mail(self, type: str, payload: Any) -> None:
        mail_item = {
            "type": type,
            "payload": payload
        }
        self.mail.insert(0, mail_item)

    def add_notification(self, type: Literal["info", "success", "warning", "error"], title: str, message: str) -> None:
        self.add_mail("notification", {
            "type": type,
            "title": title,
            "message": message,
        })

    def _log_entry_in_logger(self, type: Literal["debug", "info", "warning", "error", "critical"], title: str, message: str, code: Optional[str] = None) -> None:
        if not Config.logger:
            return
        log_args: Tuple[str, ...] = ()

        if code:
            log_args = (title, message, code)
        else:
            log_args = (title, message)

        log_colors = {
            "debug": "\x1b[36;20m",    # Cyan for debug
            "info": "\x1b[34;20m",     # Blue for info
            "warning": "\x1b[33;20m",  # Yellow for warning
            "error": "\x1b[31;20m",    # Red for error
            "critical": "\x1b[35;20m"  # Magenta for critical
        }

        log_methods = {
            "debug": Config.logger.debug,
            "info": Config.logger.info,
            "warning": Config.logger.warning,
            "error": Config.logger.error,
            "critical": Config.logger.critical
        }

        log_message = "From app log: " + ("\n%s" * len(log_args))

        color = log_colors.get(type, "\x1b[0m")  # Default to no color if type not found
        log_method = log_methods.get(type, Config.logger.info)  # Default to info level if type not found

        log_method(f"{color}{log_message}\x1b[0m", *log_args)

    def add_log_entry(self, type: Literal["info", "error"], title: str, message: str, code: Optional[str] = None, workflow_execution: Optional[WorkflowExecutionLog] = None) -> None:
        self._log_entry_in_logger(type, title, message, code)
        if not Config.is_mail_enabled_for_log:
            return
        shortened_message = None
        if len(message) > SessionMail.LOG_ENTRY_MAX_LEN:
            shortened_message = message[0:SessionMail.LOG_ENTRY_MAX_LEN] + "..."
        else:
            shortened_message = message
        self.add_mail("logEntry", {
            "type": type,
            "title": title,
            "message": shortened_message,
            "code": code,
            "workflowExecution": workflow_execution
        })

    def file_download(self, data: Any, file_name: str):
        if not isinstance(data, (bytes, FileWrapper, BytesWrapper)):
            raise ValueError(
                "Data for a fileDownload mail must be bytes, a FileWrapper or a BytesWrapper.")
        self.add_mail("fileDownload", {
            "data": serialize(data),
            "fileName": file_name
        })

    def open_url(self, url: str):
        self.add_mail("openUrl", url)

    def clear_mail(self) -> None:
        self.mail = []

    def set_page(self, active_page_key: str) -> None:
        self.add_mail("pageChange", active_page_key)

    def set_route_vars(self, route_vars: Dict[str, str]) -> None:
        self.add_mail("routeVarsChange", route_vars)

    def import_stylesheet(self, stylesheet_key: str, path: str) -> None:
        self.add_mail("importStylesheet", {
            "stylesheetKey": stylesheet_key,
            "path": path
        })

    def import_script(self, script_key: str, path: str) -> None:
        """
        imports the content of a script into the page
        """
        self.add_mail("importScript", {
            "scriptKey": script_key,
            "path": path
        })

    def import_frontend_module(self, module_key: str, specifier: str) -> None:
        self.add_mail("importModule", {
            "moduleKey": module_key,
            "specifier": specifier
        })

    def call_frontend_function(self, module_key: str, function_name: str, args: List) -> None:
        self.add_mail("functionCall", {
            "moduleKey": module_key,
            "functionName": function_name,
            "args": args
        })

class WriterSession:

    """
    Represents a session.
    """

    def __init__(self, session_id: str, cookies: Optional[Dict[str, str]], headers: Optional[Dict[str, str]]) -> None:
        self.session_id = session_id
        self.cookies = cookies
        self.headers = headers
        self.last_active_timestamp: int = int(time.time())
        self.session_component_tree = core_ui.build_session_component_tree(base_component_tree)
        self.userinfo: Optional[dict] = None
        self.globals = {}
        self.state = WriterState()
        self.mail = SessionMail()
        self.handler_registry = EventHandlerRegistry()
        self.middleware_registry = MiddlewareRegistry()
        self.evaluator = writer.evaluator.Evaluator(self.state, self.session_component_tree, self.mail)
        self.event_handler = EventHandler(self)

    def update_last_active_timestamp(self) -> None:
        self.last_active_timestamp = int(time.time())

class FileWrapper:
    """
    A wrapper for either a string pointing to a file or a file-like object with a read() method.
    Provides a method for retrieving the data as data URL.
    Allows for convenient serialisation of files.
    """

    def __init__(self, file: Union[Readable, str], mime_type: Optional[str] = None):
        if not file:
            raise ValueError("Must specify a file.")
        if not (
                callable(getattr(file, "read", None)) or
                isinstance(file, str)):
            raise ValueError(
                "File must provide a read() method or contain a string with a path to a local file.")
        self.file = file
        self.mime_type = mime_type

    def _get_file_stream_as_dataurl(self, f_stream: Readable) -> str:
        base64_str = base64.b64encode(f_stream.read()).decode("latin-1")
        dataurl = f"data:{self.mime_type if self.mime_type is not None else ''};base64,{ base64_str }"
        return dataurl

    def get_as_dataurl(self) -> str:
        if isinstance(self.file, str):
            with open(self.file, "rb") as f_stream:
                return self._get_file_stream_as_dataurl(f_stream)
        elif callable(getattr(self.file, "read", None)):
            return self._get_file_stream_as_dataurl(self.file)
        else:
            raise ValueError("Invalid file.")


class BytesWrapper:

    """
    A wrapper for raw byte data.
    Provides a method for retrieving the data as data URL.
    Allows for convenient serialisation of byte data.
    """

    def __init__(self, raw_data: Any, mime_type: Optional[str] = None):
        self.raw_data = raw_data
        self.mime_type = mime_type

    def get_as_dataurl(self) -> str:
        b64_data = base64.b64encode(self.raw_data).decode("utf-8")
        durl = f"data:{self.mime_type if self.mime_type is not None else ''};base64,{ b64_data }"
        return durl


def get_annotations(instance) -> Dict[str, Any]:
    """
    Returns the annotations of the class in a way that works on python 3.9 and python 3.10
    """
    if isinstance(instance, type):
        ann = instance.__dict__.get('__annotations__', None)
    else:
        ann = getattr(instance, '__annotations__', None)

    if ann is None:
        ann = {}
    return ann


class MiddlewareExecutor():
    """
    A MiddlewareExecutor executes middleware in a controlled context. It allows writer framework
    to manage different implementations of middleware.

    Case 1 : A middleware is a generator, then run before and after code

    >>> @wf.middleware()
    >>> def my_middleware():
    >>>     print("before event handler")
    >>>     yield()
    >>>     print("after event handler")

    Case 2 : A middleware is just a function, then run the function before

    >>> @wf.middleware()
    >>> def my_middleware():
    >>>     print("before event handler")
    """

    def __init__(self, middleware: Callable):
        self.middleware = middleware

    @contextlib.contextmanager
    def execute(self, args: dict):
        middleware_args = EventHandlerExecutor.build_arguments(self.middleware, args)
        it = self.middleware(*middleware_args)
        try:
            yield from it
        except StopIteration:
            yield
        except TypeError:
            yield


class MiddlewareRegistry:

    def __init__(self) -> None:
        self.registry: List[MiddlewareExecutor] = []

    def register(self, middleware: Callable):
        me = MiddlewareExecutor(middleware)
        self.registry.append(me)

    def executors(self) -> List[MiddlewareExecutor]:
        """
        Retrieves middlewares prepared for execution
        """
        return self.registry

class EventHandlerRegistry:
    """
    Maps functions registered as event handlers from the user app's core
    and external modules, providing an access mechanism to these maps.
    """

    class HandlerMeta(TypedDict):
        name: str
        args: List[str]

    class HandlerEntry(TypedDict):
        callable: Callable
        meta: 'EventHandlerRegistry.HandlerMeta'

    def __init__(self):
        self.handler_map: Dict[str, 'EventHandlerRegistry.HandlerEntry'] = {}  # type: ignore

    def __iter__(self):
        return iter(self.handler_map.keys())

    def register_handler(self, handler: Callable):
        module_name = handler.__module__

        # Prepare "access name"
        # (i.e. the key that frontend uses to retrieve handler)
        if module_name is None:
            # Use the handler's __qualname__ directly
            # for functions from main.py in user's app
            access_name = handler.__qualname__
        else:
            # For external handlers, separate the module name
            # and handler __qualname__by a dot
            access_name = f"{module_name}.{handler.__qualname__}"

        entry: EventHandlerRegistry.HandlerEntry = \
            {
                "callable": handler,
                "meta": {
                    "name": access_name,
                    "args": inspect.getfullargspec(handler).args
                }
            }

        self.handler_map[access_name] = entry

    def register_dict(self, funcs_dict: Dict):
        if isinstance(funcs_dict, dict):
            all_fn_names = (k for k, v in funcs_dict.items() if inspect.isfunction(v))
            
            exposed_fn_names = list(
                filter(lambda x: not x.startswith("_"), all_fn_names))

            for fn_name in exposed_fn_names:
                fn_callable = funcs_dict.get(fn_name)
                if not fn_callable:
                    continue
                self.register_handler(fn_callable)
        else:
            raise ValueError(f"Attempted to register a non-dict object: {funcs_dict}")

    def register_module(self, module: ModuleType | Dict):
        if isinstance(module, ModuleType):
                all_fn_names = (x[0] for x in inspect.getmembers(
                    module, inspect.isfunction))
            
        exposed_fn_names = list(filter(lambda x: not x.startswith("_"), all_fn_names))

        for fn_name in exposed_fn_names:
            fn_callable = getattr(module, fn_name)
            if not fn_callable:
                continue
            self.register_handler(fn_callable)
        else:
            raise ValueError(f"Attempted to register a non-module object: {module}")

    def find_handler_callable(self, handler_name: str) -> Optional[Callable]:
        if handler_name not in self.handler_map:
            return None
        handler_entry: EventHandlerRegistry.HandlerEntry = \
            self.handler_map[handler_name]
        return handler_entry["callable"]

    def get_handler_meta(
            self,
            handler_name: str
            ) -> "EventHandlerRegistry.HandlerMeta":
        if handler_name not in self.handler_map:
            raise RuntimeError(f"Handler {handler_name} is not registered")
        entry: EventHandlerRegistry.HandlerEntry = \
            self.handler_map[handler_name]
        return entry["meta"]

    def gather_handler_meta(self) -> List["EventHandlerRegistry.HandlerMeta"]:
        return [self.get_handler_meta(handler_name) for handler_name in self]


class EventDeserializer:

    """Applies transformations to the payload of an incoming event, depending on its type.

    The transformation happens in place: the event passed to the transform method is mutated.

    Its main goal is to deserialise incoming content in a controlled and predictable way,
    applying sanitisation of inputs where relevant."""

    def __init__(self, session: "WriterSession"):
        self.evaluator = writer.evaluator.Evaluator(session.state, session.session_component_tree, session.mail)

    def transform(self, ev: WriterEvent) -> None:
        # Events without payloads are safe
        # This includes non-custom events such as click
        # Events not natively provided by Writer Framework aren't sanitised

        if ev.payload is None or not ev.type.startswith("wf-"):
            return

        # Look for a method in this class that matches the event type
        # As a security measure, all event types starting with "wf-" must be linked to a transformer function.

        custom_event_name = ev.type[3:]
        func_name = "_transform_" + custom_event_name.replace("-", "_")
        if not hasattr(self, func_name):
            if ev.isSafe:
                return
            ev.payload = {}
            raise ValueError(
                "No payload transformer available for custom event type.")
        tf_func = getattr(self, func_name)
        try:
            tf_payload = tf_func(ev)
        except BaseException as e:
            ev.payload = {}
            raise RuntimeError("Payload transformation failed.")
        else:
            ev.payload = tf_payload

    def _unescape_bigint_matching_string(self, string: str) -> str:
        """
        Unescapes a string

        >>> _unescape_bigint_matching_string(r"13456\n")
        >>> r"13456n"
        """
        if len(string) == 0:
            return string

        if re.match(r"^\d+\\*n$", string) is None:
            return string

        result = ""
        for i in range(len(string)):
            c = string[-i]
            if c == "\\":
                i += 1
                continue
            result += c

        return result

    def _deserialize_bigint_format(self, payload: Optional[Union[dict, list]]):
        """
        Decodes the payload of a big int serialization

        >>> _deserialize_bigint_format({"bigint": "12345678901234567890n"})
        >>> {"bigint" : 12345678901234567890}

        It support escape character on bigint matching format.

        >>> _deserialize_bigint_format({"bigint": '12345678901234567890\n'})
        >>> {"bigint" : "12345678901234567890n"}

        It support nested structure

        >>> _deserialize_bigint_format({
        >>>     "record": {
        >>>         "bigint": '12345678901234567890n'
        >>>     }
        >>> })
        >>> {
        >>>     "record": {
        >>>         "bigint": '12345678901234567890'
        >>>     }
        >>> }
        :param payload:
        :return:
        """
        if isinstance(payload, dict):
            for elt in payload.keys():
                if isinstance(payload[elt], str) and len(payload[elt]) > 0 and payload[elt][-1] == "n":
                    if payload[elt][:-1].isdigit():
                        payload[elt] = int(payload[elt][:-1])
                    else:
                        unescape_payload = self._unescape_bigint_matching_string(payload[elt])
                        payload[elt] = unescape_payload

                if isinstance(payload[elt], dict) or isinstance(payload[elt], list):
                    self._deserialize_bigint_format(payload[elt])
        elif isinstance(payload, list):
            for elt in range(len(payload)):
                if isinstance(payload[elt], str) and payload[elt][-1] == "n":
                    if payload[elt][:-1].isdigit():
                        payload[elt] = int(payload[elt][:-1])
                    else:
                        unescape_payload = self._unescape_bigint_matching_string(payload[elt])
                        payload[elt] = unescape_payload
                if isinstance(payload[elt], dict) or isinstance(payload[elt], list):
                    self._deserialize_bigint_format(payload[elt])

        return payload

    def _transform_tag_click(self, ev: WriterEvent) -> Optional[str]:
        payload = ev.payload
        instance_path = ev.instancePath
        if not instance_path:
            raise ValueError("This event cannot be run as a global event.")
        options = self.evaluator.evaluate_instance_field(instance_path, "tags", {}, True)
        if not isinstance(options, dict):
            raise ValueError("Invalid value for tags")
        if payload not in options.keys():
            raise ValueError("Unauthorized option")
        return payload

    def _transform_option_change(self, ev: WriterEvent) -> Optional[str]:
        payload = ev.payload
        instance_path = ev.instancePath
        if not instance_path:
            raise ValueError("This event cannot be run as a global event.")
        options = self.evaluator.evaluate_instance_field(
            instance_path, "options", { "a": "Option A", "b": "Option B" }, True)
        if not isinstance(options, dict):
            raise ValueError("Invalid value for options")
        if payload not in options.keys():
            raise ValueError("Unauthorized option")
        return payload

    def _transform_options_change(self, ev: WriterEvent) -> Optional[List[str]]:
        payload = ev.payload
        instance_path = ev.instancePath
        if not instance_path:
            raise ValueError("This event cannot be run as a global event.")
        options = self.evaluator.evaluate_instance_field(
            instance_path, "options", { "a": "Option A", "b": "Option B" }, True)
        if not isinstance(options, dict):
            raise ValueError("Invalid value for options")
        if not isinstance(payload, list):
            raise ValueError(
                "Invalid multiple options payload. Expected a list.")
        if not all(item in options.keys() for item in payload):
            raise ValueError("Unauthorized option")
        return payload

    def _transform_toggle(self, ev: WriterEvent) -> bool:
        payload = bool(ev.payload)
        return payload

    def _transform_keydown(self, ev) -> Dict:
        payload = ev.payload
        key = str(payload.get("key"))
        ctrl_key = bool(payload.get("ctrlKey"))
        shift_key = bool(payload.get("shiftKey"))
        meta_key = bool(payload.get("metaKey"))
        tf_payload = {
            "key": key,
            "ctrl_key": ctrl_key,
            "shift_key": shift_key,
            "meta_key": meta_key
        }
        return tf_payload

    def _transform_click(self, ev) -> Dict:
        payload = ev.payload
        ctrl_key = bool(payload.get("ctrlKey"))
        shift_key = bool(payload.get("shiftKey"))
        meta_key = bool(payload.get("metaKey"))
        tf_payload = {
            "ctrl_key": ctrl_key,
            "shift_key": shift_key,
            "meta_key": meta_key
        }
        return tf_payload

    def _transform_hashchange(self, ev) -> Dict:
        payload = ev.payload
        page_key = payload.get("pageKey")
        route_vars = dict(payload.get("routeVars"))
        tf_payload = {
            "page_key": page_key,
            "route_vars": route_vars
        }
        return tf_payload

    def _transform_page_open(self, ev) -> str:
        payload = str(ev.payload)
        return payload

    def _transform_app_open(self, ev) -> dict:
        payload = ev.payload
        page_key = payload.get("pageKey")
        route_vars = dict(payload.get("routeVars"))
        tf_payload = {
            "page_key": page_key,
            "route_vars": route_vars
        }
        return tf_payload

    def _transform_chatbot_message(self, ev) -> dict:
        payload = dict(ev.payload)
        return payload

    def _transform_chatbot_action_click(self, ev) -> str:
        payload = str(ev.payload)
        return payload

    def _transform_change(self, ev) -> str:
        payload = str(ev.payload)
        return payload

    def _transform_change_finish(self, ev) -> str:
        return self._transform_change(ev)

    def _transform_number_change(self, ev) -> Optional[float]:
        try:
            return float(ev.payload)
        except ValueError:
            return None

    def _transform_number_change_finish(self, ev) -> Optional[float]:
        return self._transform_number_change(ev)

    def _transform_webcam(self, ev) -> Any:
        return urllib.request.urlopen(ev.payload).read()

    def _file_item_transform(self, file_item: WriterFileItem) -> Dict:
        data = file_item.get("data")
        if data is None:
            raise ValueError("No data provided.")
        return {
            "name": file_item.get("name"),
            "type": file_item.get("type"),
            "data": urllib.request.urlopen(data).read()
        }

    def _transform_file_change(self, ev) -> List[Dict]:
        payload = ev.payload
        tf_payload = list(map(self._file_item_transform, payload))

        return tf_payload

    def _transform_date_change(self, ev) -> str:
        payload = ev.payload

        if not isinstance(payload, str):
            raise ValueError("Date must be a string.")
        try:
            datetime.date.fromisoformat(payload)
        except ValueError:
            raise ValueError(
                "Date must be in YYYY-MM-DD format or another valid ISO 8601 format.")

        return payload

    def _transform_time_change(self, ev) -> str:
        payload = ev.payload

        if not isinstance(payload, str):
            raise ValueError("Time must be a string.")
        try:
            time.strptime(payload, '%H:%M')
        except ValueError:
            raise ValueError(
                "Time must be in hh:mm format (in 24-hour format that includes leading zeros).")

        return payload

    def _transform_range_change(self, ev) -> list[int]:
        payload = ev.payload

        if not isinstance(payload, list):
            raise ValueError("Range must be an array.")

        if len(payload) != 2:
            raise ValueError("Range must contains exactly two values.")

        if not isinstance(payload[0], numbers.Real):
            raise ValueError("First item is not a number.")

        if not isinstance(payload[1], numbers.Real):
            raise ValueError("Second item is not a number.")

        if payload[0] > payload[1]:
            raise ValueError("First item is higher than second.")

        return payload

    def _transform_change_page_size(self, ev) -> Optional[int]:
        try:
            return int(ev.payload)
        except ValueError:
            return None

    def _transform_change_page(self, ev) -> Optional[int]:
        try:
            return int(ev.payload)
        except ValueError:
            return None

    def _transform_dataframe_update(self, ev: WriterEvent) -> Optional[Dict]:
        payload = ev.payload
        if not isinstance(payload, dict):
            return None
        
        payload = self._deserialize_bigint_format(payload)
        return payload

    def _transform_dataframe_add(self, ev: WriterEvent) -> Optional[Dict]:
        payload = ev.payload
        if not isinstance(payload, dict):
            return None

        payload = self._deserialize_bigint_format(payload)
        return payload

    def _transform_dataframe_action(self, ev: WriterEvent) -> Optional[Dict]:
        payload = ev.payload
        if not isinstance(payload, dict):
            return None

        payload = self._deserialize_bigint_format(payload)
        return payload


class SessionManager:

    """
    Stores and manages sessions.
    """

    IDLE_SESSION_MAX_SECONDS = 3600
    TOKEN_SIZE_BYTES = 32
    hex_pattern = re.compile(
        r"^[0-9a-fA-F]{" + str(TOKEN_SIZE_BYTES*2) + r"}$")

    def __init__(self) -> None:
        self.sessions: Dict[str, WriterSession] = {}
        self.verifiers: List[Callable] = []

    def add_verifier(self, verifier: Callable) -> None:
        self.verifiers.append(verifier)

    def _verify_before_new_session(self, cookies: Optional[Dict] = None, headers: Optional[Dict] = None) -> bool:
        for verifier in self.verifiers:
            args = inspect.getfullargspec(verifier).args
            arg_values = []
            for arg in args:
                if arg == "cookies":
                    arg_values.append(cookies)
                elif arg == "headers":
                    arg_values.append(headers)
            verifier_result = verifier(*arg_values)
            if verifier_result is False:
                return False
            elif verifier_result is True:
                pass
            else:
                raise ValueError(
                    "Invalid verifier return value. Must be True or False.")
        return True

    def _check_proposed_session_id(self, proposed_session_id: Optional[str]) -> bool:
        if proposed_session_id is None:
            return True
        if SessionManager.hex_pattern.match(proposed_session_id):
            return True
        return False

    def get_new_session(self, cookies: Optional[Dict] = None, headers: Optional[Dict] = None, proposed_session_id: Optional[str] = None) -> Optional[WriterSession]:
        if not self._check_proposed_session_id(proposed_session_id):
            return None
        if not self._verify_before_new_session(cookies, headers):
            return None
        new_id = None
        if proposed_session_id is None:
            new_id = self._generate_session_id()
        else:
            new_id = proposed_session_id
        new_session = WriterSession(new_id, cookies, headers)
        self.sessions[new_id] = new_session
        return new_session

    def get_session(self, session_id: Optional[str], restore_initial_mail: bool = False) -> Optional[WriterSession]:
        if session_id is None:
            return None

        session = self.sessions.get(session_id)
        if session is not None and restore_initial_mail is True:
            session.session_state.mail = copy.copy(initial_state.mail)

        return session

    def _generate_session_id(self) -> str:
        return secrets.token_hex(SessionManager.TOKEN_SIZE_BYTES)

    def clear_all(self) -> None:
        self.sessions = {}

    def close_session(self, session_id: str) -> None:
        if session_id not in self.sessions:
            return
        del self.sessions[session_id]

    def prune_sessions(self) -> None:
        cutoff_timestamp = int(time.time()) - \
            SessionManager.IDLE_SESSION_MAX_SECONDS
        prune_sessions = []
        for session_id, session in self.sessions.items():
            if session.last_active_timestamp < cutoff_timestamp:
                prune_sessions.append(session_id)
        for session_id in prune_sessions:
            self.close_session(session_id)

    @staticmethod
    def generate_session_id() -> str:
        """
        Generates a random session identifier which can be used to propose a session number before starting
        the app process in the apiinit route.
        """
        return secrets.token_hex(SessionManager.TOKEN_SIZE_BYTES)


class EventHandler:

    """
    Handles events in the context of a Session.
    """

    def __init__(self, session: WriterSession) -> None:
        import writer.workflows

        self.session = session
        self.session_component_tree = session.session_component_tree
        self.deser = EventDeserializer(session)
        self.workflow_runner = writer.workflows.WorkflowRunner(session)


    def _handle_binding(self, event_type, target_component, instance_path, payload) -> None:
        if not target_component.binding:
            return
        binding = target_component.binding
        if binding["eventType"] != event_type:
            return
        locals = self.session.evaluator.get_context(instance_path)
        self.session.evaluator.set_state(binding["reference"], payload, locals)

    def _get_workflow_callable(self, workflow_key: Optional[str] = None, workflow_id: Optional[str] = None):
        def fn(payload, context, session):
            execution_environment = {
                "payload": payload,
                "context": context,
                "session": session
            }
            if workflow_key:
                return self.workflow_runner.run_workflow_by_key(workflow_key, execution_environment)
            elif workflow_id:
                return self.workflow_runner.run_workflow(workflow_id, execution_environment, "Workflow execution triggered on demand")
        return fn

    def _get_handler_callable(self, handler: str) -> Optional[Callable]:
        if handler.startswith("$runWorkflow_"):
            workflow_key = handler[13:] 
            return self._get_workflow_callable(workflow_key=workflow_key)

        if handler.startswith("$runWorkflowById_"):
            workflow_id = handler[17:]
            return self._get_workflow_callable(workflow_id=workflow_id)

        handler_registry = self.session.handler_registry
        callable_handler = handler_registry.find_handler_callable(handler)
        return callable_handler

    def _get_calling_arguments(self, ev: WriterEvent, instance_path: Optional[InstancePath] = None):
        context_data = self.session.evaluator.get_context(instance_path) if instance_path else {}
        return {
            "state": self.session.state,
            "payload": ev.payload,
            "context": context_data,
            "session": _event_handler_session_info(),
            "ui": _event_handler_ui_manager(),
            "event": ev.type
        }

    def _call_handler_callable(
        self,
        handler_callable: Callable,
        calling_arguments: Dict
    ) -> Any:        
        result = None
        captured_stdout = None
        with core_ui.use_component_tree(self.session.session_component_tree), \
            contextlib.redirect_stdout(io.StringIO()) as f:
            middlewares_executors = self.session.middleware_registry.executors()
            result = EventHandlerExecutor.invoke_with_middlewares(middlewares_executors, handler_callable, calling_arguments)
            captured_stdout = f.getvalue()

        if captured_stdout:
            self.session.mail.add_log_entry("info", "Stdout message", captured_stdout)

        return result

    def _deserialize(self, ev: WriterEvent):
        try:
            self.deser.transform(ev)
        except BaseException as e: 
            self.session.mail.add_notification(
                "error", "Error", f"A deserialization error occurred when handling event '{ ev.type }'.")
            self.session.mail.add_log_entry("error", "Deserialization Failed",
                                             f"The data sent might be corrupt. A runtime exception was raised when deserializing event '{ ev.type }'.", traceback.format_exc())
            raise e

    def _handle_global_event(self, ev: WriterEvent):
        if not ev.isSafe:
            error_message = "Attempted executing a global event in an unsafe context."
            self.session.mail.add_log_entry("error", "Forbidden operation", error_message, traceback.format_exc())
            raise PermissionError(error_message)
        if not ev.handler:
            raise ValueError("Handler not specified when attempting to execute global event.")
        handler_callable = self._get_handler_callable(ev.handler)
        if not handler_callable:
            return
        calling_arguments = self._get_calling_arguments(ev, instance_path=None)
        return self._call_handler_callable(handler_callable, calling_arguments)

    def _handle_component_event(self, ev: WriterEvent):
        instance_path = ev.instancePath
        try:
            if not instance_path:
                raise ValueError("Component event must specify an instance path.")
            target_id = instance_path[-1]["componentId"]
            target_component = cast(Component, self.session_component_tree.get_component(target_id))
            self._handle_binding(ev.type, target_component, instance_path, ev.payload)
            if not target_component.handlers:
                return None
            handler = target_component.handlers.get(ev.type)
            if not handler:
                return None
            handler_callable = self._get_handler_callable(handler)
            if not handler_callable:
                return
            calling_arguments = self._get_calling_arguments(ev, instance_path)
            return self._call_handler_callable(handler_callable, calling_arguments)
        except BaseException as e:
            self.session.mail.add_notification("error", "Runtime Error", f"An error occurred when processing event '{ ev.type }'.",
                                                )
            self.session.mail.add_log_entry("error", "Runtime Exception",
                                             f"A runtime exception was raised when processing event '{ ev.type }'.", traceback.format_exc())
            raise e

    def handle(self, ev: WriterEvent) -> WriterEventResult:
        try:
            if not ev.isSafe and ev.handler is not None:
                raise PermissionError("Unexpected handler set on event.")
            self._deserialize(ev)
            if not ev.instancePath:
                return {"ok": True, "result": self._handle_global_event(ev)}
            else:
                return {"ok": True, "result": self._handle_component_event(ev)}
        except BaseException as e:
            return {"ok": False, "result": str(e)}


class EventHandlerExecutor:

    @staticmethod
    def build_arguments(func: Callable, writer_args: dict) -> List[Any]:
        """
        Constructs the list of arguments based on the signature of the function
        which can be a handler or middleware.

        >>> def my_event_handler(context):
        >>>     yield

        >>> args = EventHandlerExecutor.build_arguments(my_event_handler, {'payload': {}, 'context': {"target": '11'}, 'session': None, 'ui': None})
        >>> [{}, {"target": '11'}]

        :param func: the function that will be called
        :param writer_args: the possible arguments in writer (payload, ...)
        """
        handler_args = inspect.getfullargspec(func).args
        func_args = []
        for arg in handler_args:
            if arg in writer_args:
                func_args.append(writer_args[arg])

        return func_args

    @staticmethod
    def invoke(callable_handler: Callable, writer_args: dict) -> Any:
        """
        Runs a handler based on its signature.

        If the handler is asynchronous, it is executed asynchronously.
        If the handler only has certain parameters, only these are passed as arguments

        >>> def my_handler():
        >>      global a
        >>>     a = 2
        >>>
        >>> EventHandlerExecutor.invoke(my_handler, {'payload': None, 'context': None, 'session': None, 'ui': None})
        """
        is_async_handler = inspect.iscoroutinefunction(callable_handler)
        if (not callable(callable_handler) and not is_async_handler):
            raise ValueError("Invalid handler. The handler isn't a callable object.")

        handler_args = EventHandlerExecutor.build_arguments(callable_handler, writer_args)

        if is_async_handler:
            async_wrapper = _async_wrapper_internal(callable_handler, handler_args)
            result = asyncio.run(async_wrapper)
        else:
            result = callable_handler(*handler_args)

        return result

    @staticmethod
    def invoke_with_middlewares(middlewares_executors: List[MiddlewareExecutor], callable_handler: Callable, writer_args: dict) -> Any:
        """
        Runs the middlewares then the handler. This function allows you to manage exceptions that are triggered in middleware

        :param middlewares_executors: The list of middleware to run
        :param callable_handler: The target handler

        >>> @wf.middleware()
        >>> def my_middleware(payload, context, session, ui):
        >>>     yield

        >>> executor = MiddlewareExecutor(my_middleware, {'payload': None, 'context': None, 'session': None, 'ui': None})
        >>> EventHandlerExecutor.invoke_with_middlewares([executor], my_handler, {'payload': None, 'context': None, 'session': None, 'ui': None}
        """
        if len(middlewares_executors) == 0:
            return EventHandlerExecutor.invoke(callable_handler, writer_args)
        else:
            executor = middlewares_executors[0]
            with executor.execute(writer_args):
                return EventHandlerExecutor.invoke_with_middlewares(middlewares_executors[1:], callable_handler, writer_args)

def session_verifier(func: Callable) -> Callable:
    """
    Decorator for marking session verifiers.
    """

    def wrapped(*args, **kwargs):
        pass

    session_manager.add_verifier(func)
    return wrapped


def get_session() -> Optional[WriterSession]:
    """
    Retrieves the current session.

    This function works exclusively in the context of a request.
    """
    req = _current_request.get()
    if req is None:
        return None

    session_id = req.session_id
    session = session_manager.get_session(session_id)
    if not session:
        return None

    return session


def reset_base_component_tree() -> None:
    """
    Reset the base component tree to zero

    (use mainly in tests)
    """
    global base_component_tree
    base_component_tree = core_ui.build_base_component_tree()

async def _async_wrapper_internal(callable_handler: Callable, arg_values: List[Any]) -> Any:
    result = await callable_handler(*arg_values)
    return result

def _event_handler_session_info() -> Dict[str, Any]:
    """
    Returns the session information for the current event handler.

    This information is exposed in the session parameter of a handler
    
    """
    current_session = get_session()
    session_info: Dict[str, Any] = {}
    if current_session is not None:
        session_info['id'] = current_session.session_id
        session_info['cookies'] = current_session.cookies
        session_info['headers'] = current_session.headers
        session_info['userinfo'] = current_session.userinfo or {}

    return session_info

def _event_handler_ui_manager():
    from writer import PROPER_UI_INIT, _get_ui_runtime_error_message
    if PROPER_UI_INIT:
        from writer.ui import WriterUIManager
        return WriterUIManager()
    else:
        raise RuntimeError(_get_ui_runtime_error_message())




class MutableValue:
    def __init__(self):
        self._mutated = False

    def mutated(self) -> bool:
        """
        Returns whether the value has been mutated.
        :return:
        """
        return self._mutated

    def mutate(self) -> None:
        """
        Marks the value as mutated.
        This will trigger the refresh of the user interface on the next round trip
        :return:
        """
        self._mutated = True

    def reset_mutation(self) -> None:
        """
        Resets the mutation flag to False.
        :return:
        """
        self._mutated = False

class WriterState:

    def __init__(self):
        self._state_data = {}

    def __setattr__(self, name, value):
        if name == "_state_data":
            super().__setattr__(name, value)
            return
        self._state_data[name] = value
    
    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            _state_data = super().__getattribute__("_state_data")
            if name in _state_data:
                return _state_data[name]
            raise AttributeError(f""""{name}" isn't present in state.""")

    def __dict__(self):
        return self._state_data

    def __repr__(self):
        return repr(self._state_data)

base_component_tree = core_ui.build_base_component_tree()
session_manager: SessionManager = SessionManager()