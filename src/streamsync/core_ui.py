from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Union
import uuid

from pydantic import BaseModel, Field

current_parent_container: ContextVar[Union["Component", None]] = \
    ContextVar("current_parent_container")
# This variable is thread safe and context safe


def generate_component_id():
    return str(uuid.uuid4())


class Component(BaseModel):
    id: str = Field(default_factory=generate_component_id)
    type: str
    content: Dict[str, Any] = Field(default_factory=dict)
    flag: Optional[str] = None
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

    def __init__(self) -> None:
        self.counter: int = 0
        self.components: Dict[str, Component] = {}
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

    def get_direct_descendents_length(self, parent_id):
        return len(self.get_direct_descendents(parent_id))

    def get_descendents(self, parent_id: str) -> List[Component]:
        children = self.get_direct_descendents(parent_id)
        desc = children.copy()
        for child in children:
            desc += self.get_descendents(child.id)

        return desc

    def determine_position(self, _: str, parent_id: str, is_positionless: bool = False):
        if is_positionless:
            return -2

        children = self.get_direct_descendents(parent_id)
        if len(children) > 0:
            position = max([0, max([child.position for child in children]) + 1])
            return position
        else:
            return 0

    def attach(self, component: Component, override=False) -> None:
        self.counter += 1
        if (component.id in self.components) and (override is False):
            raise RuntimeWarning(f"Component with ID {component.id} already exists")
        self.components[component.id] = component

    def ingest(self, serialised_components: Dict[str, Any]) -> None:
        removed_ids = self.components.keys() - serialised_components.keys()

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
        super().__init__()
        self.base_component_tree = base_component_tree
        self.root_modified = False

    def determine_position(self, component_id: str, parent_id: str, is_positionless: bool = False):
        session_component_present = component_id in self.components
        if session_component_present:
            # If present, use ComponentTree method
            # for determining position directly from this class
            return super().determine_position(component_id, parent_id, is_positionless)
        else:
            # Otherwise, invoke it on base component tree
            return self.base_component_tree.determine_position(component_id, parent_id, is_positionless)

    def get_component(self, component_id: str) -> Optional[Component]:
        # Check if session component tree contains requested key
        session_component_present = component_id in self.components

        if session_component_present:
            # If present, return session component (even if it's None)
            session_component = self.components.get(component_id)

            # Prevent overriding root
            if not (component_id == "root" and self.root_modified is False):
                return session_component

        # Otherwise, try to obtain the base tree component
        return self.base_component_tree.get_component(component_id)

    def to_dict(self) -> Dict:
        active_components = {
            # Collecting serialized base tree components
            component_id: base_component.to_dict()
            for component_id, base_component
            in self.base_component_tree.components.items()
        }
        for component_id, session_component in self.components.items():
            if component_id == "root" and self.root_modified is False:
                continue

            # Overriding base tree components with session-specific ones
            active_components[component_id] = session_component.to_dict()
        return active_components


class UIError(Exception):
    ...
