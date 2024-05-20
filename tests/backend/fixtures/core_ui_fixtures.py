from typing import List

from writer.core_ui import Branch, Component, ComponentTree, ComponentTreeBranch


def build_fake_component_tree(components: List[Component] = None, init_root=True):
    """
    Builds a fake component tree for testing purposes.

    :param components: list of components to attach
    :param init_root: create a root component
    """
    component_tree = ComponentTree([ComponentTreeBranch(Branch.bmc, freeze=False)])
    if init_root:
        component_tree.attach(Component(id='root', parentId=None, type='root'))

    for component in components or []:
        component_tree.attach(component)

    return component_tree
