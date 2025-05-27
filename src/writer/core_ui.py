import contextlib
import copy
import logging
import uuid
from contextvars import ContextVar
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union, cast

from pydantic import BaseModel, Field, field_validator, validator
from typing_extensions import TypedDict

from writer.ss_types import ComponentDefinition, ServeMode

current_parent_container: ContextVar[Union["Component", None]] = \
    ContextVar("current_parent_container")

# This variable is thread safe and context safe
_current_component_tree: ContextVar[Union["ComponentTree", None]] = \
    ContextVar("current_component_tree", default=None)


def generate_component_id():
    return str(uuid.uuid4())


class Branch(Enum):
    """
    Enum for the component tree branches that can be created in Writer Framework

    * bmc: builder managed component
    * initial_cmc: code managed component
    * session: session managed component

    This enum should be used only in the module core_ui.py.
    """
    bmc = "bmc"
    initial_cmc = "initial_cmc"
    session_cmc = "session_cmc"


class VisibileFields(TypedDict):
    expression: Union[bool, Literal['custom']]
    binding: str
    reversed: bool

class Component(BaseModel):
    id: str = Field(default_factory=generate_component_id)
    type: str
    content: Dict[str, Any] = Field(default_factory=dict)
    isCodeManaged: Optional[bool] = False
    position: int = 0
    parentId: Optional[str] = None
    handlers: Optional[Dict[str, str]] = None
    visible: Optional[VisibileFields] = None
    binding: Optional[Dict] = None
    outs: Optional[Any] = None
    x: Optional[int] = None
    y: Optional[int] = None

    @field_validator("x", "y", mode="before")
    def cast_float_to_int(cls, v):
        if isinstance(v, float):
            return int(v)
        return v

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


class ComponentTreeBranch:
    """
    >>> bmc_tree = ComponentTreeBranch(Branch.bmc, False)
    """

    def __init__(self, id: Branch, freeze: bool = False) -> None:
        """

        :param id: the id of the component tree branch (bmc, cmc, session)
        :param freeze: the component list can not be modified
        """
        self.components: Dict[str, Component] = {}
        # Page counter is required to set
        # predefined IDs & keys for code-managed pages
        self.page_counter = 0
        self.component_tree_id = id
        self.freeze = freeze

    def clone(self) -> 'ComponentTreeBranch':
        """
        Clone a component branch into a new one.

        Writer Framework uses this action when it instantiates the component tree attached to the session.
        This ensures complete insulation of the original shaft.

        >>> cloned = bmc_tree.clone()
        :return:
        """
        cloned = ComponentTreeBranch(self.component_tree_id, self.freeze)
        cloned.components = copy.copy(self.components)
        cloned.page_counter = self.page_counter
        return cloned


    def get_component(self, component_id: str) -> Optional[Component]:
        return self.components.get(component_id)

    def attach(self, component: Component) -> None:
        """
        Attaches a component to the main components dictionary of the instance.

        :param component: The component to be attached.
        """
        if self.freeze:
            raise UIError(f"Component tree {self.component_tree_id} is frozen and cannot be modified")

        if (component.id in self.components):
            raise RuntimeWarning(f"Component with ID {component.id} already exists")

        if component.type == "page" and component.id not in self.components:
            self.page_counter += 1

        self.components[component.id] = component

    def ingest(self, serialised_components: Dict[str, Any]) -> None:
        if self.freeze:
            raise UIError(f"Component tree {self.component_tree_id} is frozen and cannot be modified")

        removed_ids = [key for key in self.components if key not in serialised_components]

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



class ComponentTree():

    def __init__(self, tree_branches: List[ComponentTreeBranch]):
        assert len(tree_branches) > 0, "Component tree must have at least one tree branch"
        self.tree_branches = tree_branches
        self.updated = False

    @property
    def components(self) -> Dict[str, Component]:
        trees = reversed(self.tree_branches)
        all_components = {}
        for tree in trees:
            all_components.update(tree.components)
        return all_components

    @property
    def page_counter(self) -> int:
        return sum([tree.page_counter for tree in self.tree_branches])

    def get_component(self, component_id: str) -> Optional[Component]:
        for tree in self.tree_branches:
            component = tree.get_component(component_id)
            if component:
                return component

        return None

    def attach(self, component: Component, tree: Optional[Branch] = None) -> None:
        """
        Attach a component to the first tree branch in the component tree.

        >>> component = Component(id="root", type="root", content={})
        >>> component_tree.attach(component)

        When the tree parameter is given, the component is attached to the corresponding branch.

        >>> component = Component(id="root", type="root", content={})
        >>> component_tree.attach(component, tree=Branch.initial_cmc)

        If the component is associated with a frozen branch, an exception is thrown
        """
        self.updated = True

        _branch = self._tree_branch(tree)
        if _branch is None:
            raise ValueError(f"Invalid tree branch : {tree}")

        cast(ComponentTreeBranch, _branch).attach(component)

    def ingest(self, serialised_components: Dict[str, Any], tree: Optional[Branch] = None) -> None:
        self.updated = True
        _branch = self._tree_branch(tree)
        if _branch is None:
            raise ValueError(f"Invalid tree branch : {tree}")

        cast(ComponentTreeBranch, _branch).ingest(serialised_components)

    def delete_component(self, component_id: str) -> None:
        for tree_branch in self.tree_branches:
            if component_id in tree_branch.components and not tree_branch.freeze:
                self.updated = True
                tree_branch.components.pop(component_id, None)
                return
            elif component_id in tree_branch.components and tree_branch.freeze:
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
                self.updated = True
                for tree in self.tree_branches:
                    if not tree.freeze:
                        tree.components.pop(child.id, None)

            except UIError:
                logger = logging.getLogger("writer")
                logger.warning(
                    f"Failed to remove child with ID '{child.id}' " +
                    f"from component with ID '{component_id}': " +
                    "child is a builder-managed component.")
                # This might result in multiple consecutive warnings
                # for the same parent component, but we have to avoid "break"ing
                # due to that the component might still have CMC children


    def to_dict(self) -> Dict:
        trees = reversed(self.tree_branches)
        components = {}
        for tree in trees:
            components.update(tree.to_dict())

        return components

    def next_page_id(self) -> str:
        return f"page-{self.page_counter}"

    def fetch_updates(self):
        if self.updated:
            self.updated = False
            return self.to_dict()

        return

    def determine_position(self, parent_id: str, is_positionless: bool) -> int:
        if is_positionless:
            return -2

        children = self._get_direct_descendents(parent_id)
        cmc_children = list(filter(lambda c: c.isCodeManaged is True, children))
        if len(cmc_children) > 0:
            position = \
                max([0, max([child.position for child in cmc_children]) + 1])
            return position
        else:
            return 0

    def get_descendents(self, parent_id: str) -> List[Component]:
        children = self._get_direct_descendents(parent_id)
        desc = children.copy()
        for child in children:
            desc += self.get_descendents(child.id)

        return desc

    def branch(self, branch_id: Branch) -> ComponentTreeBranch:
        _branch = self._tree_branch(branch_id)
        if _branch is None:
            raise ValueError(f"Component tree with ID {branch_id} does not exist")

        return _branch

    def exists(self, branch_id: Branch) -> bool:
        """
        Checks if a component with the given ID exists in the component tree.
        """
        branch = self._tree_branch(branch_id)
        return branch is not None

    def is_frozen(self, branch_id: Branch) -> bool:
        """
        Checks if a component tree branch is frozen.
        """
        branch = self._tree_branch(branch_id)
        if branch is None:
            raise ValueError(f"Component tree with ID {branch_id} does not exist")

        return branch.freeze

    def _get_direct_descendents(self, parent_id: str) -> List[Component]:
        _all_components = self.components.values()
        children = list(filter(lambda c: c.parentId == parent_id, _all_components))
        return children

    def _tree_branch(self, branch: Optional[Branch]) -> Optional[ComponentTreeBranch]:
        if branch is None:
            return self.tree_branches[0]

        for tree in self.tree_branches:
            if branch == tree.component_tree_id:
                return tree

        return None


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


def build_base_component_tree() -> ComponentTree:
    """
    Create the base component tree. This tree is used when loading Writer Framework.

    It contains the components in common between all users.
    """
    bmc_tree_branch = ComponentTreeBranch(Branch.bmc)
    bmc_tree_branch.attach(Component(id="root", type="root", content={}))
    cmc_tree_branch = ComponentTreeBranch(Branch.initial_cmc)
    return ComponentTree([cmc_tree_branch, bmc_tree_branch])


def build_session_component_tree(base_component_tree: ComponentTree) -> ComponentTree:
    """
    Creates a session component tree.

    The session component tree is associated with a user session, i.e. a browser tab.
    If the user refreshes the page, a new component tree for the session is created.

    The builder managed component, copy from base component tree, can not be modified anymore.
    The code managed component can be modified.
    """
    session_tree_branch = ComponentTreeBranch(Branch.session_cmc)

    cmc_tree_branch = base_component_tree.branch(Branch.initial_cmc).clone()
    bmc_tree_branch = base_component_tree.branch(Branch.bmc).clone()
    # bmc_tree_branch.freeze = True

    return ComponentTree([session_tree_branch, cmc_tree_branch, bmc_tree_branch])


def ingest_bmc_component_tree(component_tree: ComponentTree, components: Dict[str, Any], ignore_freeze: bool = False):
    """
    Updates the builder managed component tree branch with the provided components.
    This method is used on the event `componentUpdate`.

    >>> ingest_bmc_component_tree(component_tree, {"root": {"type": "root", "content": {}})
    """
    assert component_tree.exists(Branch.bmc) is True, \
        "bmc component tree branch does not exists in this component tree"
    assert component_tree.is_frozen(Branch.bmc) is False or ignore_freeze is True, \
        "builder managed component tree are frozen and cannot be updated"

    component_tree.ingest(components, tree=Branch.bmc)

def filter_components_by(components: Dict[str, ComponentDefinition], parent: Optional[str] = None) -> Dict[str, ComponentDefinition]:
    """
    Filters tree components whose parent is {parent_id}, parent included

    >>> filtered_components = filter_components_by(components, parent="6a490318-239e-4fe9-a56b-f0f33d628c87")
    """

    if parent is not None:
        parent_list = {parent}
        target_components: Dict[str, ComponentDefinition] = {}
        has_changed = True
        # in some cases, the order requires to loops few times
        while True:
            if has_changed is False:
                break

            has_changed = False
            for c in components.values():
                if c['id'] == parent and c['id'] not in target_components:
                    target_components[c['id']] = c
                elif c.get('parentId', None) in parent_list and c['id'] not in target_components:
                    target_components[c['id']] = c
                    parent_list.add(c['id'])
                    has_changed = True

        components = target_components

    return components


def cmc_components_list(component_tree: ComponentTree) -> list:
    """
    Returns the list of code managed components in the component tree.

    (use mainly for testing purposes)
    """
    return list(component_tree.branch(Branch.initial_cmc).components.values())


def session_components_list(component_tree: ComponentTree) -> list:
    """
   Returns the list of session managed components in the component tree.

   (use mainly for testing purposes)
   """
    return list(component_tree.branch(Branch.session_cmc).components.values())

def export_component_tree(component_tree: ComponentTree, mode: ServeMode, only_update=False) -> Optional[Dict]:
    """
    Exports the component tree to the ui.

    >>> filtered_component_tree = core_ui.export_component_tree(session.session_component_tree, mode=writer.Config.mode)

    This function filters artifacts that should be hidden from the user, for example blueprints in run mode.

    :param component_tree: the full component tree
    :param mode: the mode of the application (edit, run)
    :param updated: return something only if component tree has been updated
    :return: a dictionary representing the component tree
    """
    if only_update is True and component_tree.updated is False:
        return None

    roots = ['root']
    if mode == "edit":
        roots.append('blueprints_root')

    _components: List[Component] = []
    for root in roots:
        _root_component = cast(Component, component_tree.get_component(root))
        _components.append(_root_component)
        _components += component_tree.get_descendents(root)

    # filters notes in run mode
    if mode == "run":
        _components = [c for c in _components if c.type != "note"]

    return {c.id: c.to_dict() for c in _components}

class UIError(Exception):
    ...


@contextlib.contextmanager
def use_component_tree(component_tree: ComponentTree):
    """
    Declares the component tree that will be manipulated during a context.

    The declared tree can be retrieved with the `current_component_tree` method.

    >>> with use_component_tree(component_tree):
    >>>     ui_manager = WriterUIManager()
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
        import writer.core
        return writer.core.base_component_tree

    return tree
