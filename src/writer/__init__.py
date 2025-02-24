import importlib.metadata
import logging
import textwrap
from types import ModuleType
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from writer.core import (
    BytesWrapper,
    Config,
    FileWrapper,
    Readable,
    State,
    WriterState,
    base_component_tree,
    get_app_process,
    initial_state,
    new_initial_state,
    session_manager,
    session_verifier,
)
from writer.core import (
    writerproperty as property,
)
from writer.core_df import EditableDataFrame

try:
    from writer.ui import WriterUIManager
    PROPER_UI_INIT = True
except ModuleNotFoundError:
    logging.error(
            textwrap.dedent(
                """\
                \x1b[31;20mError: Failed to import `writer.ui` module.
                This indicates that the Writer Framework was not built properly.
                Please refer to CONTRIBUTING.md for instructions to resolve this issue.\x1b[0m"""
            )
        )
    PROPER_UI_INIT = False

def _get_ui_runtime_error_message() -> str:
    return "UI module is unavailable – Writer Framework is not properly built. " + \
            "Please refer to CONTRIBUTING.md for instructions to resolve this issue."

VERSION = importlib.metadata.version("writer")

base_component_tree
session_manager
Config
session_verifier


def pack_file(file: Union[Readable, str], mime_type: Optional[str] = None):
    """
    Returns a FileWrapper for the file provided, which is automatically
    serialised to a data URL.
    """

    return FileWrapper(file, mime_type)


def pack_bytes(raw_data, mime_type: Optional[str] = None):
    """
    Returns a BytesWrapper for the bytes raw data provided, which is automatically
    serialised to a data URL.
    """

    return BytesWrapper(raw_data, mime_type)


S = TypeVar('S', bound=WriterState)


def init_ui() -> 'WriterUIManager':
    """Initializes and returns an instance of WriterUIManager.
    This manager provides methods to dynamically create and manage UI
    components in a Writer Framework application.

    The WriterUIManager allows for the creation of application-wide,
    code-managed components during startup, ensuring that the set of components
    is initially accessible by all sessions.

    :return: An instance that serves as a bridge for programmatically
    interacting with the frontend, facilitating dynamic UI component management.
    :rtype: WriterUIManager

    **Example**::

    >>> import writer as wf
    >>>
    >>> with wf.init_ui() as ui:
    >>>     with ui.Page({"key": "hello"}):
    >>>         ui.Text({"text": "Hello pigeons"})
    """
    if PROPER_UI_INIT:
        return WriterUIManager()
    else:
        raise RuntimeError(_get_ui_runtime_error_message())


def init_state(raw_state: Dict[str, Any], schema: Optional[Type[S]] = None) -> Union[S, WriterState]:
    """
    Sets the initial state, which will be used as the starting point for
    every session.

    initial_state.user_state.state = {}
    initial_state.user_state.ingest(state_dict)
    return initial_state



    >>> import writer as wf

    >>> initial_state = wf.init_state({
    >>>   "counter": 0,
    >>> }, schema=AppSchema)
    """
    concrete_schema = cast(Type[S], WriterState if schema is None else schema)
    if not issubclass(concrete_schema, WriterState):
        raise ValueError("Root schema must inherit from WriterState")

    _initial_state: S = new_initial_state(concrete_schema, raw_state)

    return _initial_state


def init_handlers(handler_modules: Union[List[ModuleType], ModuleType]):
    """
    Registers one or more handler modules to enable its containing functions
    to be used as event handlers by the application's frontend.

    :param handler_modules: A module or list of modules for registration.
    :type handler_modules: module or list of modules

    **Examples**

    Register a single handler module:

    >>> import writer as wf
    >>> import my_handler_module
    >>> wf.init_handlers(my_handler_module)

    Register multiple handler modules:

    >>> import writer as wf
    >>> import module_one, module_two
    >>> wf.init_handlers([module_one, module_two])

    :raises ValueError: If an object that is not a module is attempted to be registered.
    """
    from writer.core import get_app_process
    current_app_process = get_app_process()
    handler_registry = current_app_process.handler_registry
    # Ensure handler_modules is a list
    if not isinstance(handler_modules, list):
        handler_modules = [handler_modules]

    for module in handler_modules:
        handler_registry.register_module(module)


def middleware():
    """
    A "middleware" is a function that works with every event handler before it is processed and also before returning it.

    >>> import writer as wf
    >>>
    >>> @wf.middleware()
    >>> def my_middleware(state):
    >>>     state['processing'] += 1
    >>>     yield
    >>>     state['processing'] -= 1

    Middleware accepts the same arguments as an event handler.

    >>> import writer as wf
    >>>
    >>> @wf.middleware()
    >>> def my_middleware(state, payload, session):
    >>>     state['processing'] += 1
    >>>     yield
    >>>     state['processing'] -= 1
    """
    def inner(func):
        _app_process = get_app_process()
        _app_process.middleware_registry.register(func)


    return inner
