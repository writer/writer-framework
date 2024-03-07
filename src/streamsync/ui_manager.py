from typing import Union

from streamsync.core import base_component_tree
from streamsync.core_ui import (Component, SessionComponentTree,
                                UIError, current_parent_container)


class StreamsyncUI:
    """Provides mechanisms to manage and manipulate UI components within a
    Streamsync session.

    This class offers context managers and methods to dynamically create, find,
    and organize UI components based on a structured component tree.
    """

    def __init__(self, component_tree: Union[SessionComponentTree, None] = None):
        self.component_tree = component_tree or base_component_tree
        self.root_component = self.component_tree.get_component('root')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ...

    @staticmethod
    def assert_in_container():
        container = current_parent_container.get(None)
        if container is None:
            raise UIError("A component can only be created inside a container")

    @property
    def root(self) -> Component:
        if not self.root_component:
            raise RuntimeError("Failed to acquire root component")
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

        position = kwargs.pop("position")
        is_positionless = kwargs.pop("positionless", False)

        component = Component(
            type=component_type,
            parentId=parent_id,
            flag="cmc",
            **kwargs
            )

        # We're determining the position separately
        # due to that we need to know whether ID of the component
        # is present within base component tree
        # or a session-specific one
        component.position = \
            position if position is not None else \
            self.component_tree.determine_position(
                component.id,
                parent_id,
                is_positionless=is_positionless
                )

        self.component_tree.attach(component)
        return component

    def create_container_component(self, component_type: str, **kwargs) \
            -> Component:
        container = self._create_component(component_type, **kwargs)
        return container

    def create_component(self, component_type: str, **kwargs) \
            -> Component:
        self.assert_in_container()
        component = self._create_component(component_type, **kwargs)
        return component
