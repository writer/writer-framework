import contextlib
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Union
import uuid

from pydantic import BaseModel, Field


current_parent_container: ContextVar[Union["Component", None]] = ContextVar("current_parent_container")
_current_component_tree: ContextVar[Union["ComponentTree", None]] = ContextVar("current_component_tree", default=None)
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
        self.counter: int = 0
        self.page_counter = 0
        self.components: Dict[str, Component] = {}

        # A separate pool for pre-initialized CMC components,
        # to prevent them from being mixed up with BMCs
        self.cmc_components: Dict[str, Component] = {}
        # A list of keys removed by backend UI actions
        self.cmc_removed_keys: list[str] = []

        if attach_root:
            root_component = Component(
                id="root", type="root", content={}
            )
            self.attach(root_component)

    def get_component(self, component_id: str) -> Optional[Component]:
        return self.components.get(component_id)

    def delete_component(self, component_id: str) -> None:
        if component_id in self.components \
           or component_id in self.cmc_components:
            self.cmc_removed_keys.append(component_id)
        raise KeyError(
            f"Failed to delete component with ID {component_id}: " +
            "no such component"
            )

    def clear_children(self, component_id: str) -> None:
        children = self.get_descendents(component_id)
        for child in children:
            self.delete_component(child.id)

    def get_direct_descendents(self, parent_id: str, include_cmc_pool=True) -> List[Component]:
        target_pool = self.components
        if include_cmc_pool is True:
            target_pool = target_pool | self.cmc_components

        children = list(filter(lambda c: c.parentId == parent_id,
                               target_pool.values()))
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
            position = max([0, max([child.position for child in cmc_children]) + 1])
            return position
        else:
            return 0

    def _commence_attachment(
            self,
            component: Component,
            target: dict[str, Component],
            override=False):
        """
        Attempts to add a given component to a target dictionary.

        This internal method attempts to add the specified component to the
        provided target dictionary. If a component with the same ID already
        exists in the target and override is False, a RuntimeWarning is raised.

        :param component: The component to be added.
        :type component: Component
        :param target: The dictionary to which the component will be added.
        :type target: dict[str, Component]
        :param override: Determines whether to override the existing component
                         with the same ID, defaults to False.
        :type override: bool, optional
        :raises RuntimeWarning: If a component with the same ID already exists
                                in the target and override is False.
        """
        if (component.id in target) and (override is False):
            raise RuntimeWarning(
                f"Component with ID {component.id} already exists"
                )
        target[component.id] = component

    def attach(self, component: Component, override=False) -> None:
        """
        Attaches a component to the main components dictionary of the instance.

        Increments the counter and calls `_commence_attachment` to add the
        component to the instance's components dictionary. If a component with
        the same ID already exists and override is False, a RuntimeWarning is
        raised via `_commence_attachment`.

        :param component: The component to be attached.
        :type component: Component
        :param override: If True, an existing component with the same ID will
                         be overridden. Defaults to False.
        :type override: bool, optional
        """
        self.counter += 1
        self._commence_attachment(component, self.components, override)

    def attach_to_cmc_pool(self, component: Component) -> None:
        """
        Attaches a component to the CMC (Code-Managed Components) pool.

        If the component type is "page" and it's not already in the CMC
        components dictionary, the page counter is incremented. Regardless of
        type, the component is then added to the CMC components dictionary
        using `_commence_attachment`, which doesn't allow overriding by default.

        :param component: The component to be attached to the CMC pool.
        :type component: Component
        """
        if component.type == "page" and component.id not in self.cmc_components:
            self.page_counter += 1
        self._commence_attachment(component, self.cmc_components)

    def ingest(self, serialised_components: Dict[str, Any]) -> None:
        # Identify components removed since the last update, excluding those
        # that are managed or removed via backend UI actions.
        removed_ids = [
            key for key, value in self.components.items()
            if (key not in serialised_components.keys()
                and key not in self.cmc_removed_keys)
            and value.isCodeManaged is False
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


class SessionComponentTree(ComponentTree):

    def __init__(self, base_component_tree: ComponentTree):
        super().__init__(attach_root=False)
        self.base_component_tree = base_component_tree

        # Initialize SessionComponentTree with components from the base tree's
        # CMC pool, added during app initialization, excluding any that were
        # subsequently removed.
        preinitialized_components = {
                key: value for key, value
                in base_component_tree.cmc_components.items()
                if key not in base_component_tree.cmc_removed_keys
            }
        # `update` is used instead of `ingest` due to components in the pool
        # being stored in "raw", non-serialized form.
        self.components.update(**preinitialized_components)
        self.counter = len(self.components)

        preinitialized_pages = \
            filter(lambda c: c.type == "page", self.components.values())
        self.page_counter = len(list(preinitialized_pages))

        self.updated = False

    def determine_position(self, parent_id: str, is_positionless: bool = False):
        session_component_present = parent_id in self.components
        if session_component_present:
            # If present, use ComponentTree method
            # for determining position directly from this class
            return super().determine_position(parent_id, is_positionless)
        else:
            # Otherwise, invoke it on base component tree
            return self.base_component_tree.determine_position(parent_id, is_positionless)

    def get_component(self, component_id: str) -> Optional[Component]:
        # Check if session component tree contains requested key
        session_component_present = component_id in self.components

        if session_component_present:
            # If present, return session component (even if it's None)
            session_component = self.components.get(component_id)
            return session_component

        # Otherwise, try to obtain the base tree component
        return self.base_component_tree.get_component(component_id)

    def delete_component(self, component_id: str) -> None:
        if component_id in self.components:
            self.components.pop(component_id, None)
        super().delete_component(component_id)

    def attach(self, component: Component, override=False) -> None:
        self.updated = True
        if component.type == "page" and component.id not in self.components:
            self.page_counter += 1
        return super().attach(component, override)

    def ingest(self, serialised_components: Dict[str, Any]) -> None:
        self.updated = True
        return super().ingest(serialised_components)

    def to_dict(self) -> Dict:
        active_components = {
            # Collecting serialized base tree components, excluding removed ones
            component_id: base_component.to_dict()
            for component_id, base_component
            in self.base_component_tree.components.items()
            if component_id not in self.base_component_tree.cmc_removed_keys
        }
        for component_id, session_component in self.components.items():
            # Overriding base tree components with session-specific ones
            active_components[component_id] = session_component.to_dict()
        return active_components

    def fetch_updates(self):
        if self.updated:
            self.updated = False
            return self.to_dict()
        return


class UIError(Exception):
    ...


@contextlib.contextmanager
def use_component_tree(component_tree: ComponentTree):
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


def current_component_tree() -> ComponentTree:
    """
    Retrieves the component tree of the current context or the base
    one if no context has been declared.

    :return:
    """
    tree = _current_component_tree.get()
    if tree is None:
        import streamsync.core
        return streamsync.core.base_component_tree

    return tree
