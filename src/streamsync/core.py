import contextlib
import copy
import datetime
import inspect
import logging
import secrets
import sys
import time
import traceback
from typing import Any, Callable, Dict, List, Literal, Optional, Set, Tuple, Union
import urllib.request
import base64
import io
import re
import json
import math
from streamsync.ss_types import Readable, InstancePath, StreamsyncEvent, StreamsyncEventResult, StreamsyncFileItem


class Config:

    is_mail_enabled_for_log: bool = False
    mode: str = "run"
    logger: Optional[logging.Logger] = None


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


class StateSerialiserException(ValueError):
    pass


class StateSerialiser:

    """
    Serialises user state values before sending them to the front end.
    Provides JSON-compatible values, including data URLs for binary data.
    """

    def serialise(self, v: Any) -> Union[Dict, List, str, bool, int, float, None]:
        if isinstance(v, StateProxy):
            return self._serialise_dict_recursively(v.to_dict())
        if isinstance(v, (FileWrapper, BytesWrapper)):
            return self._serialise_ss_wrapper(v)
        if isinstance(v, (datetime.datetime, datetime.date)):
            return str(v)
        if isinstance(v, bytes):
            return self.serialise(BytesWrapper(v))
        if isinstance(v, dict):
            return self._serialise_dict_recursively(v)
        if isinstance(v, list):
            return self._serialise_list_recursively(v)
        if isinstance(v, (str, bool)):
            return v
        if v is None:
            return v

        # Checking the MRO allows to determine object type without creating dependencies
        # to these packages

        v_mro = [
            f"{x.__module__}.{x.__name__}" for x in inspect.getmro(type(v))]

        if isinstance(v, (int, float)):
            if "numpy.float64" in v_mro:
                return float(v)
            if math.isnan(v):
                return None
            return v

        if "matplotlib.figure.Figure" in v_mro:
            return self._serialise_matplotlib_fig(v)
        if "plotly.graph_objs._figure.Figure" in v_mro:
            return v.to_json()
        if "numpy.float64" in v_mro:
            return float(v)
        if "numpy.ndarray" in v_mro:
            return self._serialise_list_recursively(v.tolist())
        if "pandas.core.frame.DataFrame" in v_mro:
            return self._serialise_pandas_dataframe(v)
        if "pyarrow.lib.Table" in v_mro:
            return self._serialise_pyarrow_table(v)

        if hasattr(v, "to_dict") and callable(v.to_dict):
            # Covers Altair charts, Plotly graphs
            return self._serialise_dict_recursively(v.to_dict())

        raise StateSerialiserException(
            f"Object of type { type(v) } (MRO: {v_mro}) cannot be serialised.")

    def _serialise_dict_recursively(self, d: Dict) -> Dict:
        return {str(k): self.serialise(v) for k, v in d.items()}

    def _serialise_list_recursively(self, l: List) -> List:
        return [self.serialise(v) for v in l]

    def _serialise_ss_wrapper(self, v: Union[FileWrapper, BytesWrapper]) -> str:
        return v.get_as_dataurl()

    def _serialise_matplotlib_fig(self, fig) -> str:
        # It's safe to import matplotlib here without listing it as a dependency.
        # If this method is called, it's because a matplotlib figure existed.
        # Note: matplotlib type needs to be ignored since it doesn't provide types
        import matplotlib.pyplot as plt  # type: ignore

        iobytes = io.BytesIO()
        fig.savefig(iobytes, format="png")
        iobytes.seek(0)
        plt.close(fig)
        return FileWrapper(iobytes, "image/png").get_as_dataurl()

    def _serialise_pandas_dataframe(self, df):
        import pyarrow as pa # type: ignore

        pa_table = pa.Table.from_pandas(df, preserve_index=True)
        return self._serialise_pyarrow_table(pa_table)

    def _serialise_pyarrow_table(self, table):
        import pyarrow as pa # type: ignore

        sink = pa.BufferOutputStream()
        batches = table.to_batches()
        with pa.ipc.new_file(sink, table.schema) as writer:
            for batch in batches:
                writer.write_batch(batch)
        buf = sink.getvalue()
        bw = BytesWrapper(buf, "application/vnd.apache.arrow.file")
        return self.serialise(bw)


class StateProxy:

    """
    The root user state and its children (nested states) are instances of this class.
    Provides proxy functionality to detect state mutations via assignment.
    """

    def __init__(self, raw_state: Dict = {}):
        self.state: Dict[str, Any] = {}
        self.initial_assignment = True
        self.mutated: Set[str] = set()
        self.ingest(raw_state)

    def __repr__(self) -> str:
        return self.state.__repr__()

    def __contains__(self, key: str) -> bool:
        return self.state.__contains__(key)

    def ingest(self, raw_state: Dict) -> None:
        for key, raw_value in raw_state.items():
            self.__setitem__(key, raw_value)

    def get(self, key) -> Any:
        return self.state.get(key)

    def __getitem__(self, key) -> Any:
        return self.state.get(key)

    def __setitem__(self, key, raw_value) -> None:
        if not isinstance(key, str):
            raise ValueError(
                f"State keys must be strings. Received {str(key)} ({type(key)}).")

        # Items that are dictionaries are converted to StateProxy instances

        if isinstance(raw_value, dict):
            value = StateProxy(raw_value)
        else:
            value = raw_value

        self.state[key] = value
        self.apply(key)

    def apply(self, key) -> None:
        self.mutated.add(key)

    # TODO This method has side effect of clearing mutations
    # It should be renamed so it's not confused with a simple getter
    # extract_mutations
    def get_mutations_as_dict(self) -> Dict[str, Any]:
        serialised_mutations: Dict[str, Union[Dict,
                                              List, str, bool, int, float, None]] = {}
        for key, value in list(self.state.items()):
            if key.startswith("_"):
                continue
            escaped_key = key.replace(".", "\.")

            serialised_value = None
            if isinstance(value, StateProxy):
                if value.initial_assignment:
                    serialised_mutations[escaped_key] = serialised_value
                value.initial_assignment = False
                child_mutations = value.get_mutations_as_dict()
                if child_mutations is None:
                    continue
                for child_key, child_mutation in child_mutations.items():
                    nested_key = f"{escaped_key}.{child_key}"
                    serialised_mutations[nested_key] = child_mutation
            elif key in self.mutated:
                serialised_value = None
                try:
                    serialised_value = state_serialiser.serialise(value)
                except BaseException:
                    raise ValueError(
                        f"""Couldn't serialise value of type "{ type(value) }" for key "{ key }".""")
                serialised_mutations[escaped_key] = serialised_value

        self.mutated = set()
        return serialised_mutations

    def to_dict(self) -> Dict[str, Any]:
        serialised = {}
        for key, value in self.state.items():
            if key.startswith("_"):
                continue
            serialised_value = None
            try:
                serialised_value = state_serialiser.serialise(value)
            except BaseException:
                raise ValueError(
                    f"""Couldn't serialise value of type "{ type(value) }" for key "{ key }".""")
            serialised[key] = serialised_value
        return serialised


class StreamsyncState():

    """
    Root state. Comprises user configurable state and
    mail (notifications, log entries, etc).
    """

    LOG_ENTRY_MAX_LEN = 8192

    def __init__(self, raw_state: Dict[str, Any] = {}, mail: List[Any] = []):
        self.user_state: StateProxy = StateProxy(raw_state)
        self.mail = copy.deepcopy(mail)

    def __repr__(self) -> str:
        return self.user_state.__repr__()

    @classmethod
    def get_new(cls):
        """ Returns a new StreamsyncState instance set to the initial state."""

        return initial_state.get_clone()

    def get_clone(self):
        try:
            cloned_user_state = copy.deepcopy(self.user_state.state)
            cloned_mail = copy.deepcopy(self.mail)
        except BaseException:
            substitute_state = StreamsyncState()
            substitute_state.add_log_entry("error",
                                           "Cannot clone state",
                                           "The state may contain unpickable objects, such as modules.",
                                           traceback.format_exc())
            return substitute_state
        return StreamsyncState(cloned_user_state, cloned_mail)

    def __getitem__(self, key: str) -> Any:
        return self.user_state.__getitem__(key)

    def __setitem__(self, key: str, raw_value: Any) -> None:
        self.user_state.__setitem__(key, raw_value)

    def __contains__(self, key: str) -> bool:
        return self.user_state.__contains__(key)

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

    def add_log_entry(self, type: Literal["info", "error"], title: str, message: str, code: Optional[str] = None) -> None:
        self._log_entry_in_logger(type, title, message, code)
        if not Config.is_mail_enabled_for_log:
            return
        shortened_message = None
        if len(message) > StreamsyncState.LOG_ENTRY_MAX_LEN:
            shortened_message = message[0:StreamsyncState.LOG_ENTRY_MAX_LEN] + "..."
        else:
            shortened_message = message
        self.add_mail("logEntry", {
            "type": type,
            "title": title,
            "message": shortened_message,
            "code": code
        })

    def file_download(self, data: Any, file_name: str):
        if not isinstance(data, (bytes, FileWrapper, BytesWrapper)):
            raise ValueError(
                "Data for a fileDownload mail must be bytes, a FileWrapper or a BytesWrapper.")
        self.add_mail("fileDownload", {
            "data": state_serialiser.serialise(data),
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

        >>> initial_state = ss.init_state({
        >>>     "counter": 1
        >>> })
        >>>
        >>> initial_state.import_script("my_script", "/static/script.js")
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


# TODO Consider switching Component to use Pydantic

class Component:

    def __init__(self, id: str, type: str, content: Dict[str, str] = {}):
        self.id = id
        self.type = type
        self.content = content
        self.position: int = 0
        self.parentId: Optional[str] = None
        self.handlers: Optional[Dict[str, str]] = None
        self.visible: Optional[bool] = None
        self.binding: Optional[Dict] = None

    def to_dict(self) -> Dict:
        c_dict = {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "parentId": self.parentId,
            "position": self.position,
        }
        if self.handlers is not None:
            c_dict["handlers"] = self.handlers
        if self.binding is not None:
            c_dict["binding"] = self.binding
        if self.visible is not None:
            c_dict["visible"] = self.visible
        return c_dict


class ComponentManager:

    def __init__(self) -> None:
        self.counter: int = 0
        self.components: Dict[str, Component] = {}
        root_component = Component("root", "root", {})
        self.attach(root_component)

    def get_descendents(self, parent_id: str) -> List[Component]:
        children = list(filter(lambda c: c.parentId == parent_id,
                               self.components.values()))
        desc = children.copy()
        for child in children:
            desc += self.get_descendents(child.id)

        return desc

    def attach(self, component: Component) -> None:
        self.counter += 1
        self.components[component.id] = component

    def ingest(self, serialised_components: Dict[str, Any]) -> None:
        removed_ids = self.components.keys() - serialised_components.keys()

        for component_id in removed_ids:
            if component_id == "root":
                continue
            self.components.pop(component_id)
        for component_id, sc in serialised_components.items():
            component = Component(
                component_id, sc["type"], sc["content"])
            component.parentId = sc.get("parentId")
            component.handlers = sc.get("handlers")
            component.position = sc.get("position")
            component.visible = sc.get("visible")
            component.binding = sc.get("binding")
            self.components[component_id] = component

    def to_dict(self) -> Dict:
        active_components = {}
        for id, component in self.components.items():
            active_components[id] = component.to_dict()
        return active_components


class EventDeserialiser:

    """Applies transformations to the payload of an incoming event, depending on its type.

    The transformation happens in place: the event passed to the transform method is mutated.

    Its main goal is to deserialise incoming content in a controlled and predictable way,
    applying sanitisation of inputs where relevant."""

    def __init__(self, session_state: StreamsyncState):
        self.evaluator = Evaluator(session_state)

    def transform(self, ev: StreamsyncEvent) -> None:
        # Events without payloads are safe
        # This includes non-custom events such as click
        # Events not natively provided by Streamsync aren't sanitised

        if ev.payload is None or not ev.type.startswith("ss-"):
            return

        # Look for a method in this class that matches the event type
        # As a security measure, all event types starting with "ss-" must be linked to a transformer function.

        custom_event_name = ev.type[3:]
        func_name = "_transform_" + custom_event_name.replace("-", "_")
        if not hasattr(self, func_name):
            ev.payload = {}
            raise ValueError(
                "No payload transformer available for custom event type.")
        tf_func = getattr(self, func_name)
        try:
            tf_payload = tf_func(ev)
        except BaseException:
            ev.payload = {}
            raise RuntimeError("Payload transformation failed.")
        else:
            ev.payload = tf_payload

    def _transform_option_change(self, ev: StreamsyncEvent) -> Optional[str]:
        payload = ev.payload
        instance_path = ev.instancePath
        options = self.evaluator.evaluate_field(
            instance_path, "options", True, """{ "a": "Option A", "b": "Option B" }""")
        if not isinstance(options, dict):
            raise ValueError("Invalid value for options")
        if payload not in options.keys():
            raise ValueError("Unauthorised option")
        return payload

    def _transform_options_change(self, ev: StreamsyncEvent) -> Optional[List[str]]:
        payload = ev.payload
        instance_path = ev.instancePath
        options = self.evaluator.evaluate_field(
            instance_path, "options", True, """{ "a": "Option A", "b": "Option B" }""")
        if not isinstance(options, dict):
            raise ValueError("Invalid value for options")
        if not isinstance(payload, list):
            raise ValueError(
                "Invalid multiple options payload. Expected a list.")
        if not all(item in options.keys() for item in payload):
            raise ValueError("Unauthorised option")
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

    def _file_item_transform(self, file_item: StreamsyncFileItem) -> Dict:
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



class Evaluator:

    """
    Evaluates templates and expressions in the backend.
    It allows for the sanitisation of frontend inputs.
    """

    template_regex = re.compile(r"[\\]?@{([\w\s.]*)}")

    def __init__(self, session_state: StreamsyncState):
        self.ss = session_state

    def evaluate_field(self, instance_path: InstancePath, field_key: str, as_json=False, default_field_value="") -> Any:
        def replacer(matched):
            if matched.string[0] == "\\":  # Escaped @, don't evaluate
                return matched.string
            expr = matched.group(1).strip()
            expr_value = self.evaluate_expression(expr, instance_path)

            serialised_value = None
            try:
                serialised_value = state_serialiser.serialise(expr_value)
            except BaseException:
                raise ValueError(
                    f"""Couldn't serialise value of type "{ type(expr_value) }" when evaluating field "{ field_key }".""")

            if as_json:
                return json.dumps(serialised_value)
            return str(serialised_value)

        component_id = instance_path[-1]["componentId"]
        component = component_manager.components[component_id]
        field_value = component.content.get(field_key) or default_field_value
        replaced = self.template_regex.sub(replacer, field_value)

        if as_json:
            return json.loads(replaced)
        else:
            return replaced

    def get_context_data(self, instance_path: InstancePath) -> Dict[str, Any]:
        context: Dict[str, Any] = {}

        for i in range(len(instance_path)):
            path_item = instance_path[i]
            component_id = path_item["componentId"]
            component = component_manager.components[component_id]
            if component.type != "repeater":
                continue
            if i + 1 >= len(instance_path):
                continue
            repeater_instance_path = instance_path[0:i+1]
            next_instance_path = instance_path[0:i+2]
            instance_number = next_instance_path[-1]["instanceNumber"]
            repeater_object = self.evaluate_field(
                repeater_instance_path, "repeaterObject", True, """{ "a": { "desc": "Option A" }, "b": { "desc": "Option B" } }""")
            key_variable = self.evaluate_field(
                repeater_instance_path, "keyVariable", False, "itemId")
            value_variable = self.evaluate_field(
                repeater_instance_path, "valueVariable", False, "item")

            repeater_items: List[Tuple[Any, Any]] = []
            if isinstance(repeater_object, dict):
                repeater_items = list(repeater_object.items())
            elif isinstance(repeater_object, list):
                repeater_items = [(k, v)
                                  for (k, v) in enumerate(repeater_object)]
            else:
                raise ValueError(
                    "Cannot produce context. Repeater object must evaluate to a dictionary.")

            context[key_variable] = repeater_items[instance_number][0]
            context[value_variable] = repeater_items[instance_number][1]

        return context

    def set_state(self, expr: str, instance_path: InstancePath, value: Any) -> None:
        accessors = self.parse_expression(expr, instance_path)
        state_ref: Any = self.ss.user_state
        for accessor in accessors[:-1]:
            state_ref = state_ref[accessor]

        if not isinstance(state_ref, StateProxy):
            raise ValueError(
                f"Incorrect state reference. Reference \"{expr}\" isn't part of a StateProxy.")

        state_ref[accessors[-1]] = value

    def parse_expression(self, expr: str, instance_path: Optional[InstancePath] = None) -> List[str]:

        """ Returns a list of accessors from an expression. """

        accessors: List[str] = []
        s = ""
        level = 0

        for c in expr:
            if c == ".":
                if level == 0:
                    accessors.append(s)
                    s = ""
                else:
                    s += c
            elif c == "[":
                if level == 0:
                    accessors.append(s)
                    s = ""
                else:
                    s += c
                level += 1
            elif c == "]":
                level -= 1
                if level == 0:
                    s = str(self.evaluate_expression(s, instance_path))
                else:
                    s += c
            else:
                s += c

        if s:
            accessors.append(s);

        return accessors


    def evaluate_expression(self, expr: str, instance_path: Optional[InstancePath]) -> Any:
        context_data = None
        if instance_path:
            context_data = self.get_context_data(instance_path)
        context_ref: Any = context_data
        state_ref: Any = self.ss.user_state.state
        accessors: List[str] = self.parse_expression(expr, instance_path)
        for accessor in accessors:
            if isinstance(state_ref, (StateProxy, dict)):
                state_ref = state_ref.get(accessor)

            if context_ref and isinstance(context_ref, dict):
                context_ref = context_ref.get(accessor)

        result = None
        if context_ref:
            result = context_ref
        elif state_ref:
            result = state_ref

        if isinstance(result, StateProxy):
            return result.to_dict()
        return result


class StreamsyncSession:

    """
    Represents a session.
    """

    def __init__(self, session_id: str, cookies: Optional[Dict[str, str]], headers: Optional[Dict[str, str]]) -> None:
        self.session_id = session_id
        self.cookies = cookies
        self.headers = headers
        self.last_active_timestamp: int = int(time.time())
        new_state = StreamsyncState.get_new()
        new_state.user_state.mutated = set()
        self.session_state = new_state
        self.event_handler = EventHandler(self)

    def update_last_active_timestamp(self) -> None:
        self.last_active_timestamp = int(time.time())


class SessionManager:

    """
    Stores and manages sessions.
    """

    IDLE_SESSION_MAX_SECONDS = 3600
    TOKEN_SIZE_BYTES = 32
    hex_pattern = re.compile(
        r"^[0-9a-fA-F]{" + str(TOKEN_SIZE_BYTES*2) + r"}$")

    def __init__(self) -> None:
        self.sessions: Dict[str, StreamsyncSession] = {}
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

    def get_new_session(self, cookies: Optional[Dict] = None, headers: Optional[Dict] = None, proposed_session_id: Optional[str] = None) -> Optional[StreamsyncSession]:
        if not self._check_proposed_session_id(proposed_session_id):
            return None
        if not self._verify_before_new_session(cookies, headers):
            return None
        new_id = None
        if proposed_session_id is None:
            new_id = self._generate_session_id()
        else:
            new_id = proposed_session_id
        new_session = StreamsyncSession(
            new_id, cookies, headers)
        self.sessions[new_id] = new_session
        return new_session

    def get_session(self, session_id: str) -> Optional[StreamsyncSession]:
        return self.sessions.get(session_id)

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


class EventHandler:

    """
    Handles events in the context of a Session.
    """

    def __init__(self, session: StreamsyncSession) -> None:
        self.session = session
        self.session_state = session.session_state
        self.deser = EventDeserialiser(self.session_state)
        self.evaluator = Evaluator(self.session_state)

    def _handle_binding(self, event_type, target_component, instance_path, payload) -> None:
        if not target_component.binding:
            return
        binding = target_component.binding
        if binding["eventType"] != event_type:
            return
        self.evaluator.set_state(binding["stateRef"], instance_path, payload)

    def _call_handler_callable(self, event_type, target_component, instance_path, payload) -> Any:
        streamsyncuserapp = sys.modules.get("streamsyncuserapp")
        if streamsyncuserapp is None:
            raise ValueError("Couldn't find app module (streamsyncuserapp).")

        if not target_component.handlers:
            return
        handler = target_component.handlers.get(event_type)
        if not handler:
            return

        if not hasattr(streamsyncuserapp, handler):
            raise ValueError(
                f"""Invalid handler. Couldn't find the handler "{ handler }".""")
        callable_handler = getattr(streamsyncuserapp, handler)

        if not callable(callable_handler):
            raise ValueError(
                "Invalid handler. The handler isn't a callable object.")

        args = inspect.getfullargspec(callable_handler).args
        arg_values = []
        for arg in args:
            if arg == "state":
                arg_values.append(self.session_state)
            elif arg == "payload":
                arg_values.append(payload)
            elif arg == "context":
                context = self.evaluator.get_context_data(instance_path)
                arg_values.append(context)
            elif arg == "session":
                session_info = {
                    "id": self.session.session_id,
                    "cookies": self.session.cookies,
                    "headers": self.session.headers
                }
                arg_values.append(session_info)

        result = None
        with contextlib.redirect_stdout(io.StringIO()) as f:
            result = callable_handler(*arg_values)
        captured_stdout = f.getvalue()
        if captured_stdout:
            self.session_state.add_log_entry(
                "info",
                "Stdout message",
                captured_stdout
            )
        return result

    def handle(self, ev: StreamsyncEvent) -> StreamsyncEventResult:
        ok = True

        try:
            self.deser.transform(ev)
        except BaseException:
            ok = False
            self.session_state.add_notification(
                "error", "Error", f"A deserialisation error occurred when handling event '{ ev.type }'.")
            self.session_state.add_log_entry("error", "Deserialisation Failed",
                                             f"The data sent might be corrupt. A runtime exception was raised when deserialising event '{ ev.type }'.", traceback.format_exc())

        result = None
        try:
            instance_path = ev.instancePath
            target_id = instance_path[-1]["componentId"]
            target_component = component_manager.components[target_id]

            self._handle_binding(ev.type, target_component, instance_path, ev.payload)
            result = self._call_handler_callable(
                ev.type, target_component, instance_path, ev.payload)
        except BaseException:
            ok = False
            self.session_state.add_notification("error", "Runtime Error", f"An error occurred when processing event '{ ev.type }'.",
                                                )
            self.session_state.add_log_entry("error", "Runtime Exception",
                                             f"A runtime exception was raised when processing event '{ ev.type }'.", traceback.format_exc())

        return {"ok": ok, "result": result}


state_serialiser = StateSerialiser()
component_manager = ComponentManager()
initial_state = StreamsyncState()
session_manager = SessionManager()


def session_verifier(func: Callable) -> Callable:
    """
    Decorator for marking session verifiers.
    """

    def wrapped(*args, **kwargs):
        pass

    session_manager.add_verifier(func)
    return wrapped
