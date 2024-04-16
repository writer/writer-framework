import contextlib
import logging
import uuid
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

current_parent_container: ContextVar[Union["Component", None]] = \
    ContextVar("current_parent_container")
_current_component_tree: ContextVar[Union["DependentComponentTree", None]] = \
    ContextVar("current_component_tree", default=None)
# This variable is thread safe and context safe


def generate_component_id():
    return str(uuid.uuid4())


class Component(BaseModel):
    id: str = Field(default_factory=generate_component_id)
    type: str
    content: Dict[str, Any] = Field(default_factory=dict)
    isCodeManaged: Optional[bool] = False
    position: int = 0
    parentId: Optional[str] = None
    handlers: Optional[Dict[str, str]] = None
    visible: Optional[Union[bool, str]] = None
    binding: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """
        Wrapper for model_dump to ensure backward compatibility.
        """
        return self.model_dump(exclude_none=True)

    def __enter__(self) -> "Component":
        self._token = current_parent_container.set(self)
        return self

    def __exit__(self, *_):
        current_parent_container.reset(self._token)


class ComponentTree:

    def __init__(self, attach_root=True) -> None:
        self.components: Dict[str, Component] = {}

        if attach_root:
            root_component = Component(
                id="root", type="root", content={}
            )
            self.attach(root_component)

    def get_component(self, component_id: str) -> Optional[Component]:
        return self.components.get(component_id)

    def get_direct_descendents(self, parent_id: str) -> List[Component]:
        children = list(filter(lambda c: c.parentId == parent_id,
                               self.components.values()))
        return children

    def get_descendents(self, parent_id: str) -> List[Component]:
        children = self.get_direct_descendents(parent_id)
        desc = children.copy()
        for child in children:
            desc += self.get_descendents(child.id)

        return desc

    def determine_position(self, parent_id: str, is_positionless: bool = False):
        if is_positionless:
            return -2

        children = self.get_direct_descendents(parent_id)
        cmc_children = list(filter(lambda c: c.isCodeManaged is True, children))
        if len(cmc_children) > 0:
            position = \
                max([0, max([child.position for child in cmc_children]) + 1])
            return position
        else:
            return 0

    def attach(self, component: Component, override=False) -> None:
        """
        Attaches a component to the main components dictionary of the instance.

        :param component: The component to be attached.
        :type component: Component
        :param override: If True, an existing component with the same ID will
                         be overridden. Defaults to False.
        :type override: bool, optional
        """
        if (component.id in self.components) and (override is False):
            raise RuntimeWarning(
                f"Component with ID {component.id} already exists"
                )
        self.components[component.id] = component

    def ingest(self, serialised_components: Dict[str, Any]) -> None:
        removed_ids = [
            key for key in self.components
            if key not in serialised_components
        ]

        for component_id in removed_ids:
            if component_id == "root":
                continue
            self.components.pop(component_id)
        for component_id, sc in serialised_components.items():
            component = Component(**sc)
            self.components[component_id] = component

    def to_dict(self) -> Dict:
        active_components = {}
        for id, component in self.components.items():
            active_components[id] = component.to_dict()
        return active_components

    def get_parent(self, component_id: str) -> List[str]:
        """
        Returns the list of parents, from the first to the highest level (root normally)

        :param component_id:
        :return:
        """
        components = self.components.values()
        parents = []
        current_node: Optional[str] = component_id
        while current_node is not None:
            for component in components:
                if component.id == current_node:
                    if component.parentId is not None:
                        parents.append(component.parentId)

                    current_node = component.parentId

        return parents


class DependentComponentTree(ComponentTree):

    def __init__(self, base_component_tree: ComponentTree, attach_root=False):
        super().__init__(attach_root)
        self.base_component_tree = base_component_tree

        # Page counter is required to set
        # predefined IDs & keys for code-managed pages
        self.page_counter = 0

    def attach(self, component: Component, override=False) -> None:
        if component.type == "page" and component.id not in self.components:
            self.page_counter += 1
        return super().attach(component, override)

    def get_component(self, component_id: str) -> Optional[Component]:
        own_component_present = component_id in self.components
        if own_component_present:
            # If present, return own component
            own_component = self.components.get(component_id)
            return own_component

        # Otherwise, try to obtain the base tree component
        return self.base_component_tree.get_component(component_id)

    def delete_component(self, component_id: str) -> None:
        if component_id in self.components:
            self.components.pop(component_id, None)
            return
        if component_id in self.base_component_tree.components:
            raise UIError(
                f"Component with ID '{component_id}' " +
                "is builder-managed and cannot be removed by app"
                )
        raise KeyError(
            f"Failed to delete component with ID {component_id}: " +
            "no such component"
            )

    def clear_children(self, component_id: str) -> None:
        children = self.get_descendents(component_id)
        for child in children:
            try:
                self.delete_component(child.id)
            except UIError:
                logger = logging.getLogger("streamsync")
                logger.warning(
                    f"Failed to remove child with ID '{child.id}' " +
                    f"from component with ID '{component_id}': " +
                    "child is a builder-managed component.")
                # This might result in multiple consecutive warnings
                # for the same parent component, but we have to avoid "break"ing
                # due to that the component might still have CMC children

    def get_direct_descendents(self, parent_id: str) -> List[Component]:
        base_children = self.base_component_tree.get_direct_descendents(parent_id)
        own_children = list(filter(lambda c: c.parentId == parent_id, self.components.values()))
        return base_children + own_children

    def to_dict(self) -> Dict:
        active_components = {
            # Collecting serialized base tree components
            component_id: base_component.to_dict()
            for component_id, base_component
            in self.base_component_tree.components.items()
        }
        for component_id, own_component in self.components.items():
            # Overriding base tree components with ones that belong to dependent tree
            active_components[component_id] = own_component.to_dict()
        return active_components



class SessionComponentTree(DependentComponentTree):

    def __init__(self, base_component_tree: ComponentTree, base_cmc_tree: ComponentTree):
        super().__init__(base_component_tree, attach_root=False)

        # Initialize SessionComponentTree with components from the base
        # CMC pool, added during app initialization
        preinitialized_components = base_cmc_tree.to_dict()
        self.ingest(preinitialized_components)

        preinitialized_pages = \
            filter(lambda c: c.type == "page", self.components.values())
        self.page_counter = len(list(preinitialized_pages))

        self.updated = False

    def attach(self, component: Component, override=False) -> None:
        self.updated = True
        return super().attach(component, override)

    def ingest(self, serialised_components: Dict[str, Any]) -> None:
        self.updated = True
        return super().ingest(serialised_components)

    def delete_component(self, component_id: str) -> None:
        self.updated = True
        return super().delete_component(component_id)

    def fetch_updates(self):
        if self.updated:
            self.updated = False
            return self.to_dict()
        return


class UIError(Exception):
    ...


@contextlib.contextmanager
def use_component_tree(component_tree: DependentComponentTree):
    """
    Declares the component tree that will be manipulated during a context.

    The declared tree can be retrieved with the `current_component_tree` method.

    >>> with use_component_tree(component_tree):
    >>>     ui_manager = StreamsyncUIManager()
    >>>     ui_manager.create_component("text", text="Hello, world!")

    :param component_tree:
    """
    token = _current_component_tree.set(component_tree)
    yield
    _current_component_tree.reset(token)


def current_component_tree() -> DependentComponentTree:
    """
    Retrieves the component tree of the current context or the base
    one if no context has been declared.

    :return:
    """
    tree = _current_component_tree.get()
    if tree is None:
        import streamsync.core
        return streamsync.core.base_cmc_tree

    return tree
