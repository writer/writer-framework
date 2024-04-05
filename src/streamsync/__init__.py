import importlib.metadata
import sys
import types
from typing import List, Union, Optional, Dict, Any, Type, TypeVar, cast

from streamsync.core import (BytesWrapper, Config, FileWrapper, Readable,
                             base_component_tree, base_cmc_tree, initial_state,
                             session_manager, session_verifier, handler_registry)
from streamsync.core import Readable, FileWrapper, BytesWrapper, Config, StreamsyncState
from streamsync.core import new_initial_state, base_component_tree, session_manager, session_verifier
from streamsync.ui import StreamsyncUIManager

VERSION = importlib.metadata.version("streamsync")

base_component_tree
base_cmc_tree
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

S = TypeVar('S', bound=StreamsyncState)

def init_ui() -> StreamsyncUIManager:
    """Initializes and returns an instance of StreamsyncUIManager.
    This manager provides methods to dynamically create and manage UI
    components in a Streamsync application.

    The StreamsyncUIManager allows for the creation of application-wide,
    code-managed components during startup, ensuring that the set of components
    is initially accessible by all sessions.

    :return: An instance that serves as a bridge for programmatically
    interacting with the frontend, facilitating dynamic UI component management.
    :rtype: StreamsyncUIManager

    **Example**::

    >>> import streamsync as ss
    >>>
    >>> with ss.init_ui() as ui:
    >>>     with ui.Page({"key": "hello"}):
    >>>         ui.Text({"text": "Hello pigeons"})
    """
    return StreamsyncUIManager()


def init_state(raw_state: Dict[str, Any], schema: Optional[Type[S]] = None) -> Union[S, StreamsyncState]:
    """
    Sets the initial state, which will be used as the starting point for
    every session.

    initial_state.user_state.state = {}
    initial_state.user_state.ingest(state_dict)
    return initial_state



    >>> import streamsync as ss

    >>> initial_state = ss.init_state({
    >>>   "counter": 0,
    >>> }, schema=AppSchema)
    """
    concrete_schema = cast(Type[S], StreamsyncState if schema is None else schema)
    if not issubclass(concrete_schema, StreamsyncState):
        raise ValueError("Root schema must inherit from StreamsyncState")

    _initial_state: S = new_initial_state(concrete_schema, raw_state)
    return _initial_state


def init_handlers(handler_modules: Union[List[types.ModuleType], types.ModuleType]):
    """
    Registers one or more handler modules to enable its containing functions
    to be used as event handlers by the application's frontend.

    :param handler_modules: A module or list of modules for registration.
    :type handler_modules: module or list of modules

    **Examples**

    Register a single handler module:

    >>> import streamsync as ss
    >>> import my_handler_module
    >>> ss.init_handlers(my_handler_module)

    Register multiple handler modules:

    >>> import streamsync as ss
    >>> import module_one, module_two
    >>> ss.init_handlers([module_one, module_two])

    :raises ValueError: If an object that is not a module is attempted to be registered.
    """
    # Ensure handler_modules is a list
    if not isinstance(handler_modules, list):
        handler_modules = [handler_modules]

    for module in handler_modules:
        handler_registry.register_module(module)
