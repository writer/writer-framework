from typing import Union

from streamsync.core import StreamsyncSession, session_manager
from streamsync.core_ui import (Component, SessionComponentTree, UIError,
                                current_parent_container)


class StreamsyncUI:
    """Provides mechanisms to manage and manipulate UI components within a
    Streamsync session.

    This class offers context managers and methods to dynamically create, find,
    and organize UI components based on a structured component tree.
    """

    def __init__(self, session_id: str):
        self.session: Union[StreamsyncSession, None] = session_manager.get_session(session_id)
        if self.session is None:
            raise RuntimeError("Invalid session passed to the UI manager")
        # Initialize the component tree with the session
        self.component_tree: SessionComponentTree = \
            self.session.session_component_tree
        self.root_component = self.component_tree.get_component("root")
        if not self.root_component:
            raise RuntimeError(f"Failed to acquire root component in session {session_id}")

    @staticmethod
    def assert_in_container():
        container = current_parent_container.get(None)
        if container is None:
            raise UIError("A component can only be created inside a container")

    @property
    def root(self) -> Component:
        if not self.session:
            raise RuntimeError("No session object on UI manager")
        if not self.root_component:
            raise RuntimeError(f"Failed to acquire root component in session {self.session.session_id}")
        return self.root_component

    def find(self, component_id: str) \
            -> Component:
        # Example context manager for finding components
        component = self.component_tree.get_component(component_id)
        if component is None:
            raise RuntimeError(f"Component {component_id} not found")
        return component

    def _create_component(self, component_type: str, **kwargs) -> Component:
        parent_container = current_parent_container.get(None)
        if "parentId" in kwargs:
            parent_id = kwargs.pop("parentId")
        else:
            parent_id = "root" if not parent_container else parent_container.id
        component = Component(
            type=component_type, parentId=parent_id, flag="cmc", **kwargs
            )
        self.component_tree.attach(component, attach_to_bottom=True)
        return component

    def create_container(self, component_type: str, **kwargs) \
            -> Component:
        container = self._create_component(component_type, **kwargs)
        return container

    def create_component(self, component_type: str, **kwargs) \
            -> Component:
        self.assert_in_container()
        component = self._create_component(component_type, **kwargs)
        return component
