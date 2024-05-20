from json import dumps as json_dumps
from typing import Optional

from writer.core_ui import (
    Component,
    ComponentTree,
    UIError,
    current_component_tree,
    current_parent_container,
)


class WriterUI:
    """Provides mechanisms to manage and manipulate UI components within a
    Writer Framework session.

    This class offers context managers and methods to dynamically create, find,
    and organize UI components based on a structured component tree.
    """
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
    def component_tree(self) -> ComponentTree:
        """
        Returns the component tree representation

        :return:
        """
        return current_component_tree()

    @property
    def root(self) -> Component:
        tree = current_component_tree()
        root_component = tree.get_component('root')
        if not root_component:
            raise RuntimeError("Failed to acquire root component")
        return root_component

    @staticmethod
    def find(component_id: str) -> Component:
        """
        Retrieves a component by its ID from the current session's component tree.

        This method searches for a component with the given ID within the
        application's UI structure. If the component is found, it is returned
        for further manipulation or inspection.

        :param component_id: The unique identifier of the component to find.
        :type component_id: str
        :return: The found component with the specified ID.
        :rtype: Component
        :raises RuntimeError: If no component with the specified ID is found
        in the current session's component tree.

        **Example**::

        >>> my_component = ui.find("my-component-id")
        >>> print(my_component.properties)
        """
        # Example context manager for finding components
        component = current_component_tree().get_component(component_id)
        if component is None:
            raise RuntimeError(f"Component {component_id} not found")
        return component

    @staticmethod
    def refresh_with(component_id: str):
        """
        Clears the existing children of a container component and sets it up to
        accept new components. This method is designed to refresh the specified
        container with new content specified in the subsequent block.

        :param component_id: The unique identifier of the container component
                             to be refreshed.
        :raises RuntimeError: If no component with the specified ID is found
        in the current session's component tree.

        .. note:: Upon invocation, this method clears all children of the
        specified container component to prepare for new content. If no new
        components are added within the context block, the container will
        simply be emptied.

        **Example**:
        >>> with ui.refresh_with(id="my-container"):
        >>>     ui.Text({"text": "New content"}, id="new-content-1")
        >>>     ui.Button({"text": "Click me"}, id="new-button-1")

        This method can also be used to clear existing children without adding
        new components:
        >>> with ui.refresh_with(id="my-container"):
        >>>     pass
        """
        component = WriterUI.find(component_id)

        # Clear the children of the specified component.
        current_component_tree().clear_children(component_id)

        return component

    @staticmethod
    def parent(component_id: str, level: int = 1) -> Optional[str]:
        """
        Retrieves the ID of the top-level parent.

        :param component_id:
        :param level:
        :return:
        """
        component_tree = current_component_tree()
        parents_container = component_tree.get_parent(component_id)
        if len(parents_container) < level - 1:
            return None

        return parents_container[level - 1]

    @staticmethod
    def create_container_component(component_type: str, **kwargs) -> Component:
        component_tree = current_component_tree()
        container = _create_component(component_tree, component_type, **kwargs)
        component_tree.attach(container)
        return container

    @staticmethod
    def create_component(component_type: str, **kwargs) -> Component:
        WriterUI.assert_in_container()
        component_tree = current_component_tree()
        component = _create_component(component_tree, component_type, **kwargs)
        component_tree.attach(component)
        return component


def _prepare_handlers(raw_handlers: Optional[dict]):
    handlers = {}
    if raw_handlers is not None:
        for event, handler in raw_handlers.items():
            if callable(handler):
                module_name = \
                    handler.__module__ + "." \
                    if handler.__module__ != "writeruserapp" \
                    else ""
                handlers[event] = \
                    f"{module_name}{handler.__name__}"
            else:
                handlers[event] = handler
    return handlers


def _prepare_binding(raw_binding):
    if raw_binding is not None:
        if len(raw_binding) == 1:
            binding = {
                "eventType": list(raw_binding.keys())[0],
                "stateRef": list(raw_binding.values())[0]
            }
            return binding
        elif len(raw_binding) != 0:
            raise RuntimeError('Improper binding configuration')


def _prepare_value(value):
    if isinstance(value, dict):
        return json_dumps(value)
    return str(value)


def _create_component(component_tree: ComponentTree, component_type: str, **kwargs) -> Component:

    parent_container = current_parent_container.get(None)
    if kwargs.get("id", False) is None:
        kwargs.pop("id")

    if kwargs.get("position", False) is None:
        kwargs.pop("position")

    if kwargs.get("parentId", False) is None:
        kwargs.pop("parentId")

    if "parentId" in kwargs:
        parent_id: str = kwargs.pop("parentId")
    else:
        parent_id = "root" if not parent_container else parent_container.id

    # Converting all passed content values to strings
    raw_content: dict = kwargs.pop("content", {})
    content = {key: _prepare_value(value) for key, value in raw_content.items()}

    # A pre-defined ID is required for page components
    # to prevent page focus loss on app reload
    if component_type == "page" and "id" not in kwargs:
        identifier = f"cmc-page-{component_tree.page_counter + 1}"
        if "key" not in content:
            content["key"] = identifier
        if "id" not in kwargs:
            kwargs["id"] = identifier

    position: Optional[int] = kwargs.pop("position", None)
    is_positionless: bool = kwargs.pop("positionless", False)
    raw_handlers: dict = kwargs.pop("handlers", {})
    raw_binding: dict = kwargs.pop("binding", {})

    handlers = _prepare_handlers(raw_handlers) or None
    binding = _prepare_binding(raw_binding) or None

    component = Component(
        type=component_type,
        parentId=parent_id,
        isCodeManaged=True,
        content=content,
        handlers=handlers,
        binding=binding,
        **kwargs
        )

    # We're determining the position separately
    # due to that we need to know whether parent of the component
    # is present within base component tree
    # or a session-specific one
    component.position = \
        position if position is not None else \
        component_tree.determine_position(
            parent_id,
            is_positionless=is_positionless
            )

    return component
