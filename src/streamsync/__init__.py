import importlib.metadata
from typing import Any, Dict, Optional, Union

from streamsync.core import (BytesWrapper, Config, FileWrapper, Readable,
                             base_component_tree, initial_state,
                             session_manager, session_verifier)
from streamsync.ui import StreamsyncUIManager

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

    >>> with ss.init_ui() as ui:
    >>>     with ui.Page({"key": "hello"}):
    >>>         ui.Text({"text": "Hello pigeons"})
    """
    return StreamsyncUIManager()
