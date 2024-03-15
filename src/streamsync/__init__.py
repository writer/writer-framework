import importlib.metadata
from typing import Union, Optional, Dict, Any, Generator, ContextManager
from streamsync.core import Readable, FileWrapper, BytesWrapper, Config
from streamsync.ui import StreamsyncUIManager
from streamsync.core import initial_state, base_component_tree, session_manager, session_verifier

VERSION = importlib.metadata.version("streamsync")

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


def init_state(state_dict: Dict[str, Any]):
    """
    Sets the initial state, which will be used as the starting point for
    every session.
    """

    initial_state.user_state.state = {}
    initial_state.user_state.ingest(state_dict)
    return initial_state


def init_ui() -> StreamsyncUIManager:
    """
    Initializes and returns an instance of StreamsyncUIManager. This manager provides 
    methods to dynamically create and manage UI components in a Streamsync application.

    The returned StreamsyncUIManager allows for the creation of application-wide, 
    code-managed components during startup, ensuring that the set of components 
    is initially accessible by all sessions.

    Returns:
        StreamsyncUIManager: An instance that serves as a bridge for programmatically 
        interacting with the frontend, facilitating dynamic UI component management.

    Example:
    >>> with ss.init_ui() as ui:
    >>>     with ui.Page({"key": "hello"}):
    >>>         ui.Text({"text": "Hello pigeons"})
    """
    return StreamsyncUIManager()
