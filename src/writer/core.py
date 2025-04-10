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
    Awaitable,
    Callable,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    cast,
)

import pyarrow  # type: ignore

import writer.blocks
import writer.evaluator
from writer import core_ui
from writer.core_ui import Component
from writer.ss_types import (
    BlueprintExecutionLog,
    InstancePath,
    Readable,
    ServeMode,
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
    request: "AppProcessServerRequest"


_current_request: ContextVar[Optional[CurrentRequest]] = ContextVar("current_request", default=None)


@contextlib.contextmanager
def use_request_context(session_id: str, request: "AppProcessServerRequest"):
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


def get_app_process() -> "AppProcess":
    """
    Retrieves the Writer Framework process context.

    >>> _current_process = get_app_process()
    >>> _current_process.bmc_components # get the component tree
    """
    from writer.app_runner import AppProcess  # Needed during runtime

    raw_process: BaseProcess = multiprocessing.current_process()
    if isinstance(raw_process, AppProcess):
        return raw_process

    raise RuntimeError("Failed to retrieve the AppProcess: running in wrong context")


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


class WriterSession:
    """
    Represents a session.
    """

    def __init__(
        self, session_id: str, cookies: Optional[Dict[str, str]], headers: Optional[Dict[str, str]]
    ) -> None:
        self.session_id = session_id
        self.cookies = cookies
        self.headers = headers
        self.last_active_timestamp: int = int(time.time())
        new_state = WriterState.get_new()
        new_state.user_state.mutated = set()
        self.session_state = new_state
        self.session_component_tree = core_ui.build_session_component_tree(base_component_tree)
        self.event_handler = EventHandler(self)
        self.userinfo: Optional[dict] = None

    def update_last_active_timestamp(self) -> None:
        self.last_active_timestamp = int(time.time())


@dataclasses.dataclass
class MutationSubscription:
    """
    Describes a subscription to a mutation.

    The path on which this subscription is subscribed and the handler
    to execute when a mutation takes place on this path.

    >>> def myhandler(state):
    >>>     state["b"] = state["a"]

    >>> m = MutationSubscription(path="a.c", handler=myhandler)
    """

    type: Literal["subscription", "property"]
    path: str
    handler: Callable  # Handler to execute when mutation happens
    state: "State"
    property_name: Optional[str] = None

    def __post_init__(self):
        if len(self.path) == 0:
            raise ValueError("path cannot be empty.")

        path_parts = parse_state_variable_expression(self.path)
        for part in path_parts:
            if len(part) == 0:
                raise ValueError(f"path {self.path} cannot have empty parts.")

    @property
    def local_path(self) -> str:
        """
        Returns the last part of the key to monitor on the state

        >>> m = MutationSubscription(path="a.c", handler=myhandler)
        >>> m.local_path
        >>> "c"
        """
        path_parts = parse_state_variable_expression(self.path)
        return path_parts[-1]


class StateRecursionWatcher:
    limit = 128

    def __init__(self):
        self.counter_recursion = 0


_state_recursion_watcher = ContextVar("state_recursion_watcher", default=StateRecursionWatcher())


@contextlib.contextmanager
def state_recursion_new(key: str):
    """
    Context manager to watch the state recursion on mutation subscriptions.

    The context throws a RecursionError exception if more than 128 cascading mutations
    are performed on the same state
    """
    recursion_watcher = _state_recursion_watcher.get()
    try:
        recursion_watcher.counter_recursion += 1
        if recursion_watcher.counter_recursion > recursion_watcher.limit:
            raise RecursionError(f"State Recursion limit reached {recursion_watcher.limit}.")
        yield
    finally:
        recursion_watcher.counter_recursion -= 1


class FileWrapper:
    """
    A wrapper for either a string pointing to a file or a file-like object with a read() method.
    Provides a method for retrieving the data as data URL.
    Allows for convenient serialisation of files.
    """

    def __init__(self, file: Union[Readable, str], mime_type: Optional[str] = None):
        if not file:
            raise ValueError("Must specify a file.")
        if not (callable(getattr(file, "read", None)) or isinstance(file, str)):
            raise ValueError(
                "File must provide a read() method or contain a string with a path to a local file."
            )
        self.file = file
        self.mime_type = mime_type

    def _get_file_stream_as_dataurl(self, f_stream: Readable) -> str:
        base64_str = base64.b64encode(f_stream.read()).decode("latin-1")
        dataurl = (
            f"data:{self.mime_type if self.mime_type is not None else ''};base64,{ base64_str }"
        )
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
        from writer.ai import Conversation
        from writer.core_df import EditableDataFrame

        if isinstance(v, State):
            return self._serialise_dict_recursively(v.to_dict())
        if isinstance(v, Conversation):
            return v.serialized_messages
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
        if isinstance(v, EditableDataFrame):
            table = v.pyarrow_table()
            return self._serialise_pyarrow_table(table)
        if v is None:
            return v

        # Checking the MRO allows to determine object type without creating dependencies
        # to these packages

        v_mro = [f"{x.__module__}.{x.__name__}" for x in inspect.getmro(type(v))]

        if isinstance(v, (int, float)):
            if "numpy.float64" in v_mro:
                return float(v)
            if math.isnan(v):
                return None
            return v

        if "pandas.core.frame.DataFrame" in v_mro:
            return self._serialise_pandas_dataframe(v)
        if hasattr(v, "__dataframe__"):
            return self._serialize_dataframe(v)

        if "matplotlib.figure.Figure" in v_mro:
            return self._serialise_matplotlib_fig(v)
        if "plotly.graph_objs._figure.Figure" in v_mro:
            return v.to_json()
        if "numpy.float64" in v_mro:
            return float(v)
        if "numpy.ndarray" in v_mro:
            return self._serialise_list_recursively(v.tolist())
        if "pyarrow.lib.Table" in v_mro:
            return self._serialise_pyarrow_table(v)

        if hasattr(v, "to_dict") and callable(v.to_dict):
            # Covers Altair charts, Plotly graphs
            return self._serialise_dict_recursively(v.to_dict())

        raise StateSerialiserException(
            f"Object of type { type(v) } (MRO: {v_mro}) cannot be serialised."
        )

    def _serialise_dict_recursively(self, d: Dict) -> Dict:
        return {str(k): self.serialise(v) for k, v in d.items()}

    def _serialise_list_recursively(self, l: List) -> List:  # noqa: E741
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

    def _serialize_dataframe(self, df) -> str:
        """
        Serialize a dataframe with pyarrow a dataframe that implements
        the Dataframe Interchange Protocol i.e. the __dataframe__() method

        :param df: dataframe that implements Dataframe Interchange Protocol (__dataframe__ method)
        :return: a arrow file as a dataurl (application/vnd.apache.arrow.file)
        """
        import pyarrow.interchange  # type: ignore

        table = pyarrow.interchange.from_dataframe(df)
        return self._serialise_pyarrow_table(table)

    def _serialise_pandas_dataframe(self, df):
        import pyarrow as pa  # type: ignore

        pa_table = pa.Table.from_pandas(df, preserve_index=True)
        return self._serialise_pyarrow_table(pa_table)

    def _serialise_pyarrow_table(self, table):
        import pyarrow as pa  # type: ignore

        sink = pa.BufferOutputStream()
        batches = table.to_batches()
        with pa.ipc.new_file(sink, table.schema) as writer:
            for batch in batches:
                writer.write_batch(batch)
        buf = sink.getvalue()
        bw = BytesWrapper(buf, "application/vnd.apache.arrow.file")
        return self.serialise(bw)


class MutableValue:
    """
    MutableValue allows you to implement a value whose modification
    will be followed by the state of Writer Framework and will trigger the refresh
    of the user interface.

    >>> class MyValue(MutableValue):
    >>>     def __init__(self, value):
    >>>         self.value = value
    >>>
    >>>     def modify(self, new_value):
    >>>         self.value = new_value
    >>>         self.mutate()
    """

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


class StateProxy:
    """
    The root user state and its children (nested states) are instances of this class.
    Provides proxy functionality to detect state mutations via assignment.
    """

    def __init__(self, raw_state: Dict = {}):
        self.state: Dict[str, Any] = {}
        self.local_mutation_subscriptions: List[MutationSubscription] = []
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

    def items(self) -> Sequence[Tuple[str, Any]]:
        return cast(Sequence[Tuple[str, Any]], self.state.items())

    def get(self, key: str) -> Any:
        return self.state.get(key)

    def __getitem__(self, key: str) -> Any:
        return self.state.get(key)

    def __setitem__(self, key: str, raw_value: Any) -> None:
        with state_recursion_new(key):
            if not isinstance(key, str):
                raise ValueError(f"State keys must be strings. Received {str(key)} ({type(key)}).")
            old_value = self.state.get(key)
            self.state[key] = raw_value

            for local_mutation in self.local_mutation_subscriptions:
                if local_mutation.local_path == key:
                    if local_mutation.type == "subscription":
                        context_data = {"event": "mutation", "mutation": local_mutation.path}
                        payload = {"previous_value": old_value, "new_value": raw_value}

                        EventHandlerExecutor.invoke(
                            local_mutation.handler,
                            {
                                "state": local_mutation.state,
                                "context": context_data,
                                "payload": payload,
                                "session": _event_handler_session_info(),
                                "ui": _event_handler_ui_manager(),
                            },
                        )
                    elif local_mutation.type == "property":
                        assert local_mutation.property_name is not None
                        self[local_mutation.property_name] = local_mutation.handler(
                            local_mutation.state
                        )

            self._apply_raw(f"+{key}")

    def __delitem__(self, key: str) -> None:
        if key in self.state:
            del self.state[key]
            self._apply_raw(f"-{key}")  # Using "-" prefix to indicate deletion

    def remove(self, key: str) -> None:
        return self.__delitem__(key)

    def _apply_raw(self, key: str) -> None:
        self.mutated.add(key)

    def apply_mutation_marker(self, key: Optional[str] = None, recursive: bool = False) -> None:
        """
        Adds the mutation marker to a state. The mutation marker is used to track changes in the state.

        >>> self.apply_mutation_marker()

        Add the mutation marker on a specific field

        >>> self.apply_mutation_marker("field")

        Add the mutation marker to a state and all of its children

        >>> self.apply_mutation_marker(recursive=True)
        """
        keys = [key] if key is not None else self.state.keys()

        for k in keys:
            self._apply_raw(f"+{k}")
            if recursive is True:
                value = self.state[k]
                if isinstance(value, StateProxy):
                    value.apply_mutation_marker(recursive=True)

    @staticmethod
    def escape_key(key):
        return key.replace(".", r"\.")

    def get_mutations_as_dict(self) -> Dict[str, Any]:
        serialised_mutations: Dict[str, Union[Dict, List, str, bool, int, float, None]] = {}

        def carry_mutation_flag(base_key, child_key):
            child_mutation_flag, child_key = child_key[0], child_key[1:]
            return f"{child_mutation_flag}{base_key}.{child_key}"

        for key, value in list(self.state.items()):
            if key.startswith("_"):
                continue

            escaped_key = self.escape_key(key)
            serialised_value = None

            if isinstance(value, StateProxy):
                if f"+{key}" in self.mutated:
                    serialised_mutations[f"+{escaped_key}"] = serialised_value
                value.initial_assignment = False
                child_mutations = value.get_mutations_as_dict()
                if child_mutations is None:
                    continue
                for child_key, child_mutation in child_mutations.items():
                    nested_key = carry_mutation_flag(escaped_key, child_key)
                    serialised_mutations[nested_key] = child_mutation
            elif f"+{key}" in self.mutated:
                try:
                    serialised_value = state_serialiser.serialise(value)
                except BaseException:
                    raise ValueError(
                        f"""Couldn't serialise value of type "{ type(value) }" for key "{ key }"."""
                    )
                serialised_mutations[f"+{escaped_key}"] = serialised_value
            elif isinstance(value, MutableValue) is True and value.mutated():
                try:
                    serialised_value = state_serialiser.serialise(value)
                    value.reset_mutation()
                except BaseException:
                    raise ValueError(
                        f"""Couldn't serialise value of type "{ type(value) }" for key "{ key }"."""
                    )
                serialised_mutations[f"+{escaped_key}"] = serialised_value

        deleted_keys = {self.escape_key(key) for key in self.mutated if key.startswith("-")}
        for key in deleted_keys:
            serialised_mutations[f"{key}"] = None

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
                    f"""Couldn't serialise value of type "{ type(value) }" for key "{ key }"."""
                )
            serialised[key] = serialised_value
        return serialised

    def to_raw_state(self):
        """
        Converts a StateProxy and its children into a python dictionary.

        >>> state = State({'a': 1, 'c': {'a': 1, 'b': 3}})
        >>> _raw_state = state._state_proxy.to_raw_state()
        >>> {'a': 1, 'c': {'a': 1, 'b': 3}}

        :return: a python dictionary that represents the raw state
        """
        raw_state = {}
        for key, value in self.state.items():
            if isinstance(value, StateProxy):
                value = value.to_raw_state()
            raw_state[key] = value

        return raw_state


def get_annotations(instance) -> Dict[str, Any]:
    """
    Returns the annotations of the class in a way that works on python 3.9 and python 3.10
    """
    if isinstance(instance, type):
        ann = instance.__dict__.get("__annotations__", None)
    else:
        ann = getattr(instance, "__annotations__", None)

    if ann is None:
        ann = {}
    return ann


class StateMeta(type):
    """
    Constructs a class at runtime that extends WriterState or State
    with dynamic properties for each annotation of the class.
    """

    def __new__(cls, name, bases, attrs):
        klass = super().__new__(cls, name, bases, attrs)
        cls.bind_annotations_to_state_proxy(klass)
        return klass

    @classmethod
    def bind_annotations_to_state_proxy(cls, klass):
        """
        Loops through the class annotations and creates properties dynamically for each one.

        >>> class MyState(State):
        >>>     counter: int

        will be transformed into

        >>> class MyState(State):
        >>>
        >>>     @property
        >>>     def counter(self):
        >>>         return self._state_proxy["counter"]
        >>>
        >>>    @counter.setter
        >>>    def counter(self, value):
        >>>        self._state_proxy["counter"] = value

        Annotations that reference a State are ignored. The link will be established through a State instance
        when ingesting state data.

        >>> class MyAppState(State):
        >>>     title: str

        >>> class MyState(State):
        >>>     myapp: MyAppState # Nothing happens
        """

        annotations = get_annotations(klass)
        for key, expected_type in annotations.items():
            if key == "_state_proxy":
                raise AttributeError(
                    "_state_proxy is an reserved keyword for Writer Framework, don't use it in annotation."
                )

            if not (inspect.isclass(expected_type) and issubclass(expected_type, State)):
                proxy = DictPropertyProxy("_state_proxy", key)
                setattr(klass, key, proxy)


class State(metaclass=StateMeta):
    def __init__(self, raw_state: Optional[Dict[str, Any]] = None):
        final_raw_state = raw_state if raw_state is not None else {}

        self._state_proxy: StateProxy = StateProxy(final_raw_state)
        self.ingest(final_raw_state)

        # This step saves the properties associated with the instance
        for attribute in calculated_properties_per_state_type.get(self.__class__, []):
            getattr(self, attribute)

    def ingest(self, raw_state: Dict[str, Any]) -> None:
        """
        hydrates a state from raw data by applying a schema when it is provided.
        The existing content in the state is erased.


        >>> state = WriterState({'message': "hello world"})
        >>> state.ingest({'a': 1, 'b': 2})
        >>> {'a': 1, 'b': 2}
        """
        self._state_proxy.state = {}
        for key, value in raw_state.items():
            assert not isinstance(
                value, StateProxy
            ), f"state proxy datatype is not expected in ingest operation, {locals()}"
            self._set_state_item(key, value)

    def to_dict(self) -> dict:
        """
        Serializes state data as a dictionary

        Private attributes, prefixed with _, are ignored.

        >>> state = WriterState({'message': "hello world"})
        >>> return state.to_dict()
        """
        return self._state_proxy.to_dict()

    def to_raw_state(self) -> dict:
        """
        Converts a StateProxy and its children into a python dictionary that can be used to recreate the
        state from scratch.

        >>> state = WriterState({'a': 1, 'c': {'a': 1, 'b': 3}})
        >>> raw_state = state.to_raw_state()
        >>> "{'a': 1, 'c': {'a': 1, 'b': 3}}"

        :return: a python dictionary that represents the raw state
        """
        return self._state_proxy.to_raw_state()

    def __repr__(self) -> str:
        return self._state_proxy.__repr__()

    def __getitem__(self, key: str) -> Any:
        # Essential to support operation like
        # state['item']['a'] = state['item']['b']
        if hasattr(self, key):
            value = getattr(self, key)
            if isinstance(value, State):
                return value

        return self._state_proxy.__getitem__(key)

    def __setitem__(self, key: str, raw_value: Any) -> None:
        assert not isinstance(
            raw_value, StateProxy
        ), f"state proxy datatype is not expected, {locals()}"

        self._set_state_item(key, raw_value)

    def __delitem__(self, key: str) -> Any:
        return self._state_proxy.__delitem__(key)

    def remove(self, key: str) -> Any:
        return self.__delitem__(key)

    def items(self) -> Generator[Tuple[str, Any], None, None]:
        for k, v in self._state_proxy.items():
            if isinstance(v, StateProxy):
                # We don't want to expose StateProxy to the user, so
                # we replace it with relative State
                yield k, getattr(self, k)
            else:
                yield k, v

    def __contains__(self, key: str) -> bool:
        return self._state_proxy.__contains__(key)

    def _set_state_item(self, key: str, value: Any):
        """ """

        """
        At this level, the values that arrive are either States which encapsulate a StateProxy, or another datatype. 
        If there is a StateProxy, it is a fault in the code.
        """
        annotations = get_annotations(self)
        expected_type = annotations.get(key, None)
        expect_dict = _type_match_dict(expected_type)
        if isinstance(value, dict) and not expect_dict:
            """
            When the value is a dictionary and the attribute does not explicitly 
            expect a dictionary, we instantiate a new state to manage mutations.
            """
            state = annotations[key](value) if key in annotations else State()
            if not isinstance(state, State):
                raise ValueError(
                    f"Attribute {key} must inherit of State or requires a dict to accept dictionary"
                )

            setattr(self, key, state)
            state.ingest(value)
            self._state_proxy[key] = state._state_proxy
        else:
            if isinstance(value, State):
                value._state_proxy.apply_mutation_marker(recursive=True)
                self._state_proxy[key] = value._state_proxy
            else:
                self._state_proxy[key] = value

    def subscribe_mutation(
        self,
        path: Union[str, List[str]],
        handler: Callable[..., Union[None, Awaitable[None]]],
        initial_triggered: bool = False,
    ) -> None:
        r"""
        Automatically triggers a handler when a mutation occurs in the state.

        >>> def _increment_counter(state):
        >>>     state['my_counter'] += 1
        >>>
        >>> state = WriterState({'a': 1, 'c': {'a': 1, 'b': 3}, 'my_counter': 0})
        >>> state.subscribe_mutation('a', _increment_counter)
        >>> state.subscribe_mutation('c.a', _increment_counter)
        >>> state['a'] = 2 # will trigger _increment_counter
        >>> state['a'] = 3 # will trigger _increment_counter
        >>> state['c']['a'] = 2 # will trigger _increment_counter

        subscribe mutation accepts the signature of an event handler.

        >>> def _increment_counter(state, payload, context, session, ui):
        >>>     state['my_counter'] += 1
        >>>
        >>> state = WriterState({'a': 1, 'my_counter': 0})
        >>> state.subscribe_mutation('a', _increment_counter)
        >>> state['a'] = 2 # will trigger _increment_counter

        subscribe mutation accepts escaped dot expressions to encode key that contains `dot` separator

        >>> def _increment_counter(state, payload, context, session, ui):
        >>>     state['my_counter'] += 1
        >>>
        >>> state = WriterState({'a.b': 1, 'my_counter': 0})
        >>> state.subscribe_mutation('a\.b', _increment_counter)
        >>> state['a.b'] = 2 # will trigger _increment_counter

        :param path: path of mutation to monitor
        :param func: handler to call when the path is mutated
        """
        if isinstance(path, str):
            path_list = [path]
        else:
            path_list = path

        for p in path_list:
            state_proxy = self._state_proxy
            path_parts = parse_state_variable_expression(p)
            for i, path_part in enumerate(path_parts):
                if i == len(path_parts) - 1:
                    local_mutation = MutationSubscription("subscription", p, handler, self)
                    state_proxy.local_mutation_subscriptions.append(local_mutation)

                    # At startup, the application must be informed of the
                    # existing states. To cause this, we trigger manually
                    # the handler.
                    if initial_triggered is True:
                        EventHandlerExecutor.invoke(
                            handler,
                            {
                                "state": self,
                                "context": {"event": "init"},
                                "payload": {},
                                "session": {},
                                "ui": _event_handler_ui_manager(),
                            },
                        )

                elif path_part in state_proxy:
                    state_proxy = state_proxy[path_part]
                else:
                    raise ValueError(f"Mutation subscription failed - {p} not found in state")

    def calculated_property(
        self,
        property_name: str,
        path: Union[str, List[str]],
        handler: Callable[..., Union[None, Awaitable[None]]],
    ) -> None:
        """
        Update a calculated property when a mutation triggers

        This method is dedicated to be used through a calculated property. It is not
        recommended to invoke it directly.

        >>> class MyState(State):
        >>>     title: str
        >>>
        >>>     wf.property('title')
        >>>     def title_upper(self):
        >>>         return self.title.upper()

        Usage
        =====

        >>> state = wf.init_state({'title': 'hello world'})
        >>> state.calculated_property('title_upper', 'title', lambda state: state.title.upper())
        """
        if isinstance(path, str):
            path_list = [path]
        else:
            path_list = path

        for p in path_list:
            state_proxy = self._state_proxy
            path_parts = parse_state_variable_expression(p)
            for i, path_part in enumerate(path_parts):
                if i == len(path_parts) - 1:
                    local_mutation = MutationSubscription(
                        "property", p, handler, self, property_name
                    )
                    state_proxy.local_mutation_subscriptions.append(local_mutation)
                    state_proxy[property_name] = handler(self)
                elif path_part in state_proxy:
                    state_proxy = state_proxy[path_part]
                else:
                    raise ValueError(f"Property subscription failed - {p} not found in state")


class WriterState(State):
    """
    Root state. Comprises user configurable state and
    mail (notifications, log entries, etc).
    """

    LOG_ENTRY_MAX_LEN = 8192

    def __init__(self, raw_state: Dict[str, Any] = {}, mail: List[Any] = []):
        super().__init__(raw_state)
        self.mail = copy.deepcopy(mail)

    @property
    def user_state(self) -> StateProxy:
        return self._state_proxy

    @classmethod
    def get_new(cls):
        """Returns a new WriterState instance set to the initial state."""

        return initial_state.get_clone()

    def get_clone(self) -> "WriterState":
        """
        get_clone clones the destination application state for the session.

        The class is rebuilt identically in the case where the user
        has constructed a schema inherited from WriterState

        >>> class AppSchema(WriterState):
        >>>     counter: int
        >>>
        >>> root_state = AppSchema({'counter': 1})
        >>> clone_state = root_state.get_clone() # instance of AppSchema
        """
        try:
            cloned_user_state = copy.deepcopy(self.user_state.to_raw_state())
            cloned_mail = copy.deepcopy(self.mail)
        except BaseException:
            substitute_state = WriterState()
            substitute_state.add_log_entry(
                "error",
                "Cannot clone state",
                "The state may contain unpickable objects, such as modules.",
                traceback.format_exc(),
            )
            return substitute_state

        cloned_state = self.__class__(cloned_user_state, cloned_mail)
        _clone_mutation_subscriptions(cloned_state, self)
        return cloned_state

    def add_mail(self, type: str, payload: Any) -> None:
        mail_item = {"type": type, "payload": payload}
        self.mail.append(mail_item)

    def add_notification(
        self, type: Literal["info", "success", "warning", "error"], title: str, message: str
    ) -> None:
        self.add_mail(
            "notification",
            {
                "type": type,
                "title": title,
                "message": message,
            },
        )

    def _log_entry_in_logger(
        self,
        type: Literal["debug", "info", "warning", "error", "critical"],
        title: str,
        message: str,
        code: Optional[str] = None,
        blueprint_execution: Optional[BlueprintExecutionLog] = None,
    ) -> None:
        if not Config.logger:
            return
        log_args: Tuple[str, ...] = ()

        if code:
            log_args = (title, message, code)
        else:
            log_args = (title, message)

        log_colors = {
            "debug": "\x1b[36;20m",  # Cyan for debug
            "info": "\x1b[34;20m",  # Blue for info
            "warning": "\x1b[33;20m",  # Yellow for warning
            "error": "\x1b[31;20m",  # Red for error
            "critical": "\x1b[35;20m",  # Magenta for critical
        }

        log_methods = {
            "debug": Config.logger.debug,
            "info": Config.logger.info,
            "warning": Config.logger.warning,
            "error": Config.logger.error,
            "critical": Config.logger.critical,
        }

        log_message = "From app log: " + ("\n%s" * len(log_args))

        if blueprint_execution:
            log_message += "\n"
            for entry in blueprint_execution.summary:
                outcome = entry.get("outcome")
                if outcome is None:
                    continue
                component_id = entry.get("componentId")
                entry_message = entry.get("message")
                log_message += f"- Id: {component_id} | Outcome: {outcome} | {entry_message}\n"

        color = log_colors.get(type, "\x1b[0m")  # Default to no color if type not found
        log_method = log_methods.get(
            type, Config.logger.info
        )  # Default to info level if type not found

        log_method(f"{color}{log_message}\x1b[0m", *log_args)

    def add_log_entry(
        self,
        type: Literal["info", "error"],
        title: str,
        message: str,
        code: Optional[str] = None,
        blueprint_execution: Optional[BlueprintExecutionLog] = None,
        id: Optional[str] = None,
    ) -> None:
        self._log_entry_in_logger(type, title, message, code, blueprint_execution)
        if not Config.is_mail_enabled_for_log:
            return
        shortened_message = None
        if len(message) > WriterState.LOG_ENTRY_MAX_LEN:
            shortened_message = message[0 : WriterState.LOG_ENTRY_MAX_LEN] + "..."
        else:
            shortened_message = message
        self.add_mail(
            "logEntry",
            {
                "type": type,
                "title": title,
                "message": shortened_message,
                "code": code,
                "blueprintExecution": blueprint_execution,
                "id": id,
            },
        )

    def file_download(self, data: Any, file_name: str):
        if not isinstance(data, (bytes, FileWrapper, BytesWrapper)):
            raise ValueError(
                "Data for a fileDownload mail must be bytes, a FileWrapper or a BytesWrapper."
            )
        self.add_mail(
            "fileDownload", {"data": state_serialiser.serialise(data), "fileName": file_name}
        )

    def open_url(self, url: str):
        self.add_mail("openUrl", url)

    def clear_mail(self) -> None:
        self.mail = []

    def set_page(self, active_page_key: str) -> None:
        self.add_mail("pageChange", active_page_key)

    def set_route_vars(self, route_vars: Dict[str, str]) -> None:
        self.add_mail("routeVarsChange", route_vars)

    def import_stylesheet(self, stylesheet_key: str, path: str) -> None:
        self.add_mail("importStylesheet", {"stylesheetKey": stylesheet_key, "path": path})

    def import_script(self, script_key: str, path: str) -> None:
        """
        imports the content of a script into the page

        >>> initial_state = wf.init_state({
        >>>     "counter": 1
        >>> })
        >>>
        >>> initial_state.import_script("my_script", "/static/script.js")
        """
        self.add_mail("importScript", {"scriptKey": script_key, "path": path})

    def import_frontend_module(self, module_key: str, specifier: str) -> None:
        self.add_mail("importModule", {"moduleKey": module_key, "specifier": specifier})

    def call_frontend_function(self, module_key: str, function_name: str, args: List) -> None:
        self.add_mail(
            "functionCall", {"moduleKey": module_key, "functionName": function_name, "args": args}
        )


class MiddlewareExecutor:
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

        >>> executors = middleware_registry.executors()
        >>> result = writer_event_handler_invoke_with_middlewares(executors, lambda state: pass, {'state': {}, 'payload': {}})
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
        meta: "EventHandlerRegistry.HandlerMeta"

    def __init__(self):
        self.handler_map: Dict[str, "EventHandlerRegistry.HandlerEntry"] = {}  # type: ignore

    def __iter__(self):
        return iter(self.handler_map.keys())

    def register_handler(self, handler: Callable):
        module_name = handler.__module__

        # Prepare "access name"
        # (i.e. the key that frontend uses to retrieve handler)
        if module_name == "writeruserapp":
            # Use the handler's __qualname__ directly
            # for functions from main.py in user's app
            access_name = handler.__qualname__
        else:
            # For external handlers, separate the module name
            # and handler __qualname__by a dot
            access_name = f"{module_name}.{handler.__qualname__}"

        entry: EventHandlerRegistry.HandlerEntry = {
            "callable": handler,
            "meta": {"name": access_name, "args": inspect.getfullargspec(handler).args},
        }

        self.handler_map[access_name] = entry

    def register_module(self, module: ModuleType):
        if isinstance(module, ModuleType):
            all_fn_names = (x[0] for x in inspect.getmembers(module, inspect.isfunction))
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
        handler_entry: EventHandlerRegistry.HandlerEntry = self.handler_map[handler_name]
        return handler_entry["callable"]

    def get_handler_meta(self, handler_name: str) -> "EventHandlerRegistry.HandlerMeta":
        if handler_name not in self.handler_map:
            raise RuntimeError(f"Handler {handler_name} is not registered")
        entry: EventHandlerRegistry.HandlerEntry = self.handler_map[handler_name]
        return entry["meta"]

    def gather_handler_meta(self) -> List["EventHandlerRegistry.HandlerMeta"]:
        return [self.get_handler_meta(handler_name) for handler_name in self]


class EventDeserialiser:
    """Applies transformations to the payload of an incoming event, depending on its type.

    The transformation happens in place: the event passed to the transform method is mutated.

    Its main goal is to deserialise incoming content in a controlled and predictable way,
    applying sanitisation of inputs where relevant."""

    def __init__(self, session: "WriterSession"):
        self.evaluator = writer.evaluator.Evaluator(
            session.session_state, session.session_component_tree
        )

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
            raise ValueError("No payload transformer available for custom event type.")
        tf_func = getattr(self, func_name)
        try:
            tf_payload = tf_func(ev)
        except BaseException:
            ev.payload = {}
            raise RuntimeError("Payload transformation failed.")
        else:
            ev.payload = tf_payload

    def _transform_tag_click(self, ev: WriterEvent) -> Optional[str]:
        payload = ev.payload
        instance_path = ev.instancePath
        if not instance_path:
            raise ValueError("This event cannot be run as a global event.")
        options = self.evaluator.evaluate_field(instance_path, "tags", True, "{ }")
        if not isinstance(options, dict):
            raise ValueError("Invalid value for tags")
        if payload not in options.keys():
            raise ValueError("Unauthorised option")
        return payload

    def _transform_option_change(self, ev: WriterEvent) -> Optional[str]:
        payload = ev.payload
        instance_path = ev.instancePath
        if not instance_path:
            raise ValueError("This event cannot be run as a global event.")
        options = self.evaluator.evaluate_field(
            instance_path, "options", True, """{ "a": "Option A", "b": "Option B" }"""
        )
        if not isinstance(options, dict):
            raise ValueError("Invalid value for options")
        if payload not in options.keys():
            raise ValueError("Unauthorised option")
        return payload

    def _transform_options_change(self, ev: WriterEvent) -> Optional[List[str]]:
        payload = ev.payload
        instance_path = ev.instancePath
        if not instance_path:
            raise ValueError("This event cannot be run as a global event.")
        options = self.evaluator.evaluate_field(
            instance_path, "options", True, """{ "a": "Option A", "b": "Option B" }"""
        )
        if not isinstance(options, dict):
            raise ValueError("Invalid value for options")
        if not isinstance(payload, list):
            raise ValueError("Invalid multiple options payload. Expected a list.")
        if not all(item in options.keys() for item in payload):
            raise ValueError("Unauthorised option")
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
            "meta_key": meta_key,
        }
        return tf_payload

    def _transform_click(self, ev) -> Dict:
        payload = ev.payload
        ctrl_key = bool(payload.get("ctrlKey"))
        shift_key = bool(payload.get("shiftKey"))
        meta_key = bool(payload.get("metaKey"))
        tf_payload = {"ctrl_key": ctrl_key, "shift_key": shift_key, "meta_key": meta_key}
        return tf_payload

    def _transform_hashchange(self, ev) -> Dict:
        payload = ev.payload
        page_key = payload.get("pageKey")
        route_vars = dict(payload.get("routeVars"))
        tf_payload = {"page_key": page_key, "route_vars": route_vars}
        return tf_payload

    def _transform_page_open(self, ev) -> str:
        payload = str(ev.payload)
        return payload

    def _transform_app_open(self, ev) -> dict:
        payload = ev.payload
        page_key = payload.get("pageKey")
        route_vars = dict(payload.get("routeVars"))
        tf_payload = {"page_key": page_key, "route_vars": route_vars}
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
            "data": urllib.request.urlopen(data).read(),
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
            raise ValueError("Date must be in YYYY-MM-DD format or another valid ISO 8601 format.")

        return payload

    def _transform_time_change(self, ev) -> str:
        payload = ev.payload

        if not isinstance(payload, str):
            raise ValueError("Time must be a string.")
        try:
            time.strptime(payload, "%H:%M")
        except ValueError:
            raise ValueError(
                "Time must be in hh:mm format (in 24-hour format that includes leading zeros)."
            )

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

        payload = _deserialize_bigint_format(payload)
        return payload

    def _transform_dataframe_add(self, ev: WriterEvent) -> Optional[Dict]:
        payload = ev.payload
        if not isinstance(payload, dict):
            return None

        payload = _deserialize_bigint_format(payload)
        return payload

    def _transform_dataframe_action(self, ev: WriterEvent) -> Optional[Dict]:
        payload = ev.payload
        if not isinstance(payload, dict):
            return None

        payload = _deserialize_bigint_format(payload)
        return payload


class SessionManager:
    """
    Stores and manages sessions.
    """

    IDLE_SESSION_MAX_SECONDS = 3600
    TOKEN_SIZE_BYTES = 32
    hex_pattern = re.compile(r"^[0-9a-fA-F]{" + str(TOKEN_SIZE_BYTES * 2) + r"}$")

    def __init__(self) -> None:
        self.sessions: Dict[str, WriterSession] = {}
        self.verifiers: List[Callable] = []

    def add_verifier(self, verifier: Callable) -> None:
        self.verifiers.append(verifier)

    def _verify_before_new_session(
        self, cookies: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> bool:
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
                raise ValueError("Invalid verifier return value. Must be True or False.")
        return True

    def _check_proposed_session_id(self, proposed_session_id: Optional[str]) -> bool:
        if proposed_session_id is None:
            return True
        if SessionManager.hex_pattern.match(proposed_session_id):
            return True
        return False

    def get_new_session(
        self,
        cookies: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        proposed_session_id: Optional[str] = None,
    ) -> Optional[WriterSession]:
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

    def get_session(
        self, session_id: Optional[str], restore_initial_mail: bool = False
    ) -> Optional[WriterSession]:
        if session_id is None:
            return None
        if session_id == "anonymous":
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
        cutoff_timestamp = int(time.time()) - SessionManager.IDLE_SESSION_MAX_SECONDS
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
        import writer.blueprints

        self.session = session
        self.session_state = session.session_state
        self.session_component_tree = session.session_component_tree
        self.deser = EventDeserialiser(session)
        self.evaluator = writer.evaluator.Evaluator(
            session.session_state, session.session_component_tree
        )
        self.blueprint_runner = writer.blueprints.BlueprintRunner(session)

    def _handle_binding(self, event_type, target_component, instance_path, payload) -> None:
        if not target_component.binding:
            return
        binding = target_component.binding
        if binding["eventType"] != event_type:
            return
        self.evaluator.set_state(binding["stateRef"], instance_path, payload)

    def _get_blueprint_callable(
        self,
        blueprint_key: Optional[str] = None,
        blueprint_id: Optional[str] = None,
        branch_id: Optional[str] = None,
    ):
        def fn(payload, context, session):
            execution_environment = {"payload": payload, "context": context, "session": session}
            if blueprint_key:
                return self.blueprint_runner.run_blueprint_by_key(blueprint_key, execution_environment)
            elif blueprint_id:
                return self.blueprint_runner.run_blueprint(
                    blueprint_id, execution_environment, "Blueprint execution triggered on demand"
                )
            elif branch_id:
                return self.blueprint_runner.run_branch(
                    branch_id,
                    None,
                    execution_environment,
                    "Blueprint branch execution triggered on demand",
                )

        return fn

    def _get_handler_callable(self, handler: str) -> Optional[Callable]:
        if handler.startswith("$runBlueprint_"):
            blueprint_key = handler[14:]
            return self._get_blueprint_callable(blueprint_key=blueprint_key)

        if handler.startswith("$runBlueprintById_"):
            blueprint_id = handler[18:]
            return self._get_blueprint_callable(blueprint_id=blueprint_id)

        if handler.startswith("$runBlueprintTriggerBranchById_"):
            branch_id = handler[31:]
            return self._get_blueprint_callable(branch_id=branch_id)

        current_app_process = get_app_process()
        handler_registry = current_app_process.handler_registry
        callable_handler = handler_registry.find_handler_callable(handler)
        return callable_handler

    def _get_calling_arguments(self, ev: WriterEvent, instance_path: Optional[InstancePath] = None):
        context_data = self.evaluator.get_context_data(instance_path) if instance_path else {}
        context_data["event"] = ev.type
        return {
            "state": self.session_state,
            "payload": ev.payload,
            "context": context_data,
            "session": _event_handler_session_info(),
            "ui": _event_handler_ui_manager(),
        }

    def _call_handler_callable(self, handler_callable: Callable, calling_arguments: Dict) -> Any:
        current_app_process = get_app_process()
        result = None
        captured_stdout = None
        with (
            core_ui.use_component_tree(self.session.session_component_tree),
            contextlib.redirect_stdout(io.StringIO()) as f,
        ):
            middlewares_executors = current_app_process.middleware_registry.executors()
            result = EventHandlerExecutor.invoke_with_middlewares(
                middlewares_executors, handler_callable, calling_arguments
            )
            captured_stdout = f.getvalue()

        if captured_stdout:
            self.session_state.add_log_entry("info", "Stdout message", captured_stdout)

        return result

    def _deserialize(self, ev: WriterEvent):
        try:
            self.deser.transform(ev)
        except BaseException as e:
            self.session_state.add_notification(
                "error",
                "Error",
                f"A deserialization error occurred when handling event '{ ev.type }'.",
            )
            self.session_state.add_log_entry(
                "error",
                "Deserialization Failed",
                f"The data sent might be corrupt. A runtime exception was raised when deserializing event '{ ev.type }'.",
                traceback.format_exc(),
            )
            raise e

    def _handle_global_event(self, ev: WriterEvent):
        try:
            if not ev.isSafe:
                raise PermissionError("Attempted executing a global event in an unsafe context.")
            if not ev.handler:
                raise ValueError("Handler not specified when attempting to execute global event.")
            handler_callable = self._get_handler_callable(ev.handler)
            if not handler_callable:
                return
            calling_arguments = self._get_calling_arguments(ev, instance_path=None)
            return self._call_handler_callable(handler_callable, calling_arguments)
        except BaseException as e:
            self.session_state.add_notification(
                "error",
                "Runtime Error",
                f"An error occurred when processing event '{ ev.type }'.",
            )
            self.session_state.add_log_entry(
                "error",
                "Runtime Exception",
                f"A runtime exception was raised when processing event '{ ev.type }'.",
                traceback.format_exc(),
            )
            raise e

    def _handle_component_event(self, ev: WriterEvent):
        instance_path = ev.instancePath
        try:
            if not instance_path:
                raise ValueError("Component event must specify an instance path.")
            target_id = instance_path[-1]["componentId"]
            target_component = cast(Component, self.session_component_tree.get_component(target_id))
            self._handle_binding(ev.type, target_component, instance_path, ev.payload)
            calling_arguments = self._get_calling_arguments(ev, instance_path)
            self.blueprint_runner.execute_ui_trigger(target_id, ev.type, calling_arguments)
            if not target_component.handlers:
                return None
            handler = target_component.handlers.get(ev.type)
            if not handler:
                return None
            handler_callable = self._get_handler_callable(handler)
            if not handler_callable:
                return
            return self._call_handler_callable(handler_callable, calling_arguments)
        except BaseException as e:
            self.session_state.add_notification(
                "error",
                "Runtime Error",
                f"An error occurred when processing event '{ ev.type }'.",
            )
            self.session_state.add_log_entry(
                "error",
                "Runtime Exception",
                f"A runtime exception was raised when processing event '{ ev.type }'.",
                traceback.format_exc(),
            )
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

        >>> def my_event_handler(state, context):
        >>>     yield

        >>> args = EventHandlerExecutor.build_arguments(my_event_handler, {'state': {}, 'payload': {}, 'context': {"target": '11'}, 'session': None, 'ui': None})
        >>> [{}, {"target": '11'}]

        :param func: the function that will be called
        :param writer_args: the possible arguments in writer (state, payload, ...)
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

        >>> def my_handler(state):
        >>>     state['a'] = 2
        >>>
        >>> EventHandlerExecutor.invoke(my_handler, {'state': {'a': 1}, 'payload': None, 'context': None, 'session': None, 'ui': None})
        """
        is_async_handler = inspect.iscoroutinefunction(callable_handler)
        if not callable(callable_handler) and not is_async_handler:
            raise ValueError("Invalid handler. The handler isn't a callable object.")

        handler_args = EventHandlerExecutor.build_arguments(callable_handler, writer_args)

        if is_async_handler:
            async_wrapper = _async_wrapper_internal(callable_handler, handler_args)
            result = asyncio.run(async_wrapper)
        else:
            result = callable_handler(*handler_args)

        return result

    @staticmethod
    def invoke_with_middlewares(
        middlewares_executors: List[MiddlewareExecutor],
        callable_handler: Callable,
        writer_args: dict,
    ) -> Any:
        """
        Runs the middlewares then the handler. This function allows you to manage exceptions that are triggered in middleware

        :param middlewares_executors: The list of middleware to run
        :param callable_handler: The target handler

        >>> @wf.middleware()
        >>> def my_middleware(state, payload, context, session, ui):
        >>>     yield

        >>> executor = MiddlewareExecutor(my_middleware, {'state': {}, 'payload': None, 'context': None, 'session': None, 'ui': None})
        >>> EventHandlerExecutor.invoke_with_middlewares([executor], my_handler, {'state': {}, 'payload': None, 'context': None, 'session': None, 'ui': None}
        """
        if len(middlewares_executors) == 0:
            return EventHandlerExecutor.invoke(callable_handler, writer_args)
        else:
            executor = middlewares_executors[0]
            with executor.execute(writer_args):
                return EventHandlerExecutor.invoke_with_middlewares(
                    middlewares_executors[1:], callable_handler, writer_args
                )


class DictPropertyProxy:
    """
    A descriptor based recipe that makes it possible to write shorthands
    that forward attribute access from one object onto another.

    >>> class A:
    >>>     foo: int = DictPropertyProxy("proxy_state", "prop1")
    >>>     bar: int = DictPropertyProxy("proxy_state", "prop2")
    >>>
    >>>     def __init__(self):
    >>>         self._state_proxy = StateProxy({"prop1": 1, "prop2": 2})
    >>>
    >>> a = A()
    >>> print(a.foo)

    This descriptor avoids writing the code below to establish a proxy
     with a child instance

    >>> class A:
    >>>
    >>>     def __init__(self):
    >>>         self._state_proxy = StateProxy({"prop1": 1, "prop2": 2})
    >>>
    >>>     @property
    >>>     def prop1(self):
    >>>         return self._state_proxy['prop1']
    >>>
    >>>     @foo.setter
    >>>     def prop1(self, value):
    >>>         self._state_proxy['prop1'] = value
    >>>
    """

    def __init__(self, objectName, key):
        self.objectName = objectName
        self.key = key

    def __get__(self, instance, owner=None):
        proxy = getattr(instance, self.objectName)
        return proxy[self.key]

    def __set__(self, instance, value):
        proxy = getattr(instance, self.objectName)
        proxy[self.key] = value


S = TypeVar("S", bound=WriterState)


def new_initial_state(klass: Type[S], raw_state: dict) -> S:
    """
    Initializes the initial state of the application and makes it globally accessible.

    The class used for the initial state must be a subclass of WriterState.

    >>> class MyState(WriterState):
    >>>     pass
    >>>
    >>> initial_state = new_initial_state(MyState, {})
    """
    global initial_state
    if raw_state is None:
        raw_state = {}

    initial_state = klass(raw_state)

    return initial_state


"""
This variable contains the list of properties calculated for each class 
that inherits from State.

This mechanic allows Writer Framework to subscribe to mutations that trigger 
these properties when loading an application.
"""
calculated_properties_per_state_type: Dict[Type[State], List[str]] = {}


def writerproperty(path: Union[str, List[str]]):
    """
    Mechanism for declaring a calculated property whenever an attribute changes
    in the state of the Writer Framework application.

    >>> class MyState(wf.WriterState):
    >>>     counter: int
    >>>
    >>>     @wf.property("counter")
    >>>     def double_counter(self):
    >>>         return self.counter * 2

    This mechanism also supports a calculated property that depends on several dependencies.

    >>> class MyState(wf.WriterState):
    >>>     counterA: int
    >>>     counterB: int
    >>>
    >>>     @wf.property(["counterA", "counterB"])
    >>>     def counter_sum(self):
    >>>         return self.counterA + self.counterB
    """

    class Property:
        def __init__(self, func):
            self.func = func
            self.initialized = False
            self.property_name = None

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

        def __set_name__(self, owner: Type[State], name: str):
            """
            Saves the calculated properties when loading a State class.
            """
            if owner not in calculated_properties_per_state_type:
                calculated_properties_per_state_type[owner] = []

            calculated_properties_per_state_type[owner].append(name)
            self.property_name = name

        def __get__(self, instance: State, cls):
            """
            This mechanism retrieves the property instance.
            """
            args = inspect.getfullargspec(self.func)
            if len(args.args) > 1:
                logging.warning(
                    f"Wrong signature for calculated property '{instance.__class__.__name__}:{self.property_name}'. It must declare only self argument."
                )
                return None

            if self.initialized is False:
                instance.calculated_property(
                    property_name=self.property_name, path=path, handler=self.func
                )
                self.initialized = True

            return self.func(instance)

    return Property


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


def _clone_mutation_subscriptions(
    session_state: State, app_state: State, root_state: Optional["State"] = None
) -> None:
    """
    clone subscriptions on mutations between the initial state of the application and the state created for the session

    >>> state = wf.init_state({"counter": 0})
    >>> state.subscribe_mutation("counter", lambda state: print(state["counter"]))

    >>> session_state = state.get_clone()

    :param session_state:
    :param app_state:
    :param root_state:
    """
    state_proxy_app = app_state._state_proxy
    state_proxy_session = session_state._state_proxy

    state_proxy_session.local_mutation_subscriptions = []

    _root_state = root_state if root_state is not None else session_state
    for mutation_subscription in state_proxy_app.local_mutation_subscriptions:
        new_mutation_subscription = copy.copy(mutation_subscription)
        new_mutation_subscription.state = (
            _root_state if new_mutation_subscription.type == "subscription" else session_state
        )
        session_state._state_proxy.local_mutation_subscriptions.append(new_mutation_subscription)


def parse_state_variable_expression(p: str):
    r"""
    Parses a state variable expression into a list of parts.

    >>> parse_state_variable_expression("a.b.c")
    >>> ["a", "b", "c"]

    >>> parse_state_variable_expression("a\.b.c")
    >>> ["a.b", "c"]
    """
    parts = []
    it = 0
    last_split = 0
    while it < len(p):
        if p[it] == "\\":
            it += 2
        elif p[it] == ".":
            new_part = p[last_split:it]
            parts.append(new_part.replace("\\.", "."))

            last_split = it + 1
            it += 1
        else:
            it += 1

    new_part = p[last_split : len(p)]
    parts.append(new_part.replace("\\.", "."))
    return parts


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
        session_info["id"] = current_session.session_id
        session_info["cookies"] = current_session.cookies
        session_info["headers"] = current_session.headers
        session_info["userinfo"] = current_session.userinfo or {}

    return session_info


def _event_handler_ui_manager():
    from writer import PROPER_UI_INIT, _get_ui_runtime_error_message

    if PROPER_UI_INIT:
        from writer.ui import WriterUIManager

        return WriterUIManager()
    else:
        raise RuntimeError(_get_ui_runtime_error_message())


def _deserialize_bigint_format(payload: Optional[Union[dict, list]]):
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
                    unescape_payload = unescape_bigint_matching_string(payload[elt])
                    payload[elt] = unescape_payload

            if isinstance(payload[elt], dict) or isinstance(payload[elt], list):
                _deserialize_bigint_format(payload[elt])
    elif isinstance(payload, list):
        for elt in range(len(payload)):
            if isinstance(payload[elt], str) and payload[elt][-1] == "n":
                if payload[elt][:-1].isdigit():
                    payload[elt] = int(payload[elt][:-1])
                else:
                    unescape_payload = unescape_bigint_matching_string(payload[elt])
                    payload[elt] = unescape_payload
            if isinstance(payload[elt], dict) or isinstance(payload[elt], list):
                _deserialize_bigint_format(payload[elt])

    return payload


def _type_match_dict(expected_type: Type):
    """
    Checks if the expected type expect a dictionary type

    >>> _type_match_dict(dict) # True
    >>> _type_match_dict(int) # False
    >>> _type_match_dict(Dict[str, Any]) # True

    >>> class SpecifcDict(TypedDict):
    >>>     a: str
    >>>     b: str
    >>>
    >>> _type_match_dict(SpecifcDict) # True
    """
    if (
        expected_type is not None
        and inspect.isclass(expected_type)
        and issubclass(expected_type, dict)
    ):
        return True

    if typing.get_origin(expected_type) == dict:
        return True

    return False


def unescape_bigint_matching_string(string: str) -> str:
    """
    Unescapes a string

    >>> unescape_bigint_matching_string(r"13456\n")
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


state_serialiser = StateSerialiser()
initial_state = WriterState()
base_component_tree = core_ui.build_base_component_tree()
session_manager: SessionManager = SessionManager()
