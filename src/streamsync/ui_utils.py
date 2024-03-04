from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Union
import uuid

from pydantic import BaseModel, Field

current_parent_container: ContextVar[Union['Component', None]] = \
    ContextVar('current_parent_container')
# This variable is thread safe and context safe


class Component(BaseModel):
    @staticmethod
    def generate_component_id():
        return str(uuid.uuid4())

    id: str = Field(default_factory=generate_component_id)
    type: str
    content: Dict[str, str] = Field(default_factory=dict)
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

    def __enter__(self) -> 'Component':
        self._token = current_parent_container.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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

    def attach(self, component: Component, override=False) -> None:
        self.counter += 1
        if (component.id in self.components) and (override is False):
            raise RuntimeWarning(f'Component with ID {component.id} already exists')
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

    def get_component(self, component_id: str) -> Optional[Component]:
        # Check if session component tree contains requested key
        session_component_present = component_id in self.components

        if session_component_present:
            # If present, return session component (even if it's None)
            session_component = self.components.get(component_id)
            return session_component

        # Otherwise, try to obtain the base tree component
        return self.base_component_tree.get_component(component_id)

    def attach(
            self,
            component: Component,
            override=False,
            attach_to_bottom=False) -> None:
        if attach_to_bottom is True and component.position == 0:
            if component.parentId is not None:
                tree = self \
                        if component.parentId in self.components \
                        else self.base_component_tree
                parent_length = \
                    tree.get_direct_descendents_length(component.parentId)
                component.position = parent_length + 1
        super().attach(component, override=override)

    def to_dict(self) -> Dict:
        active_components = {
            # Collecting serialized base tree components
            component_id: base_component.to_dict()
            for component_id, base_component
            in self.base_component_tree.components.items()
        }
        for component_id, session_component in self.components.items():
            # Overriding base tree components with session-specific ones
            active_components[component_id] = session_component.to_dict()
        return active_components


class UIError(Exception):
    ...
