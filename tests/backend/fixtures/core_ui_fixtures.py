from typing import List

from streamsync.core_ui import Component, ComponentTree


def build_fake_component_tree(components: List[Component] = None, init_root=True):
    """
    Builds a fake component tree for testing purposes.

    :param components: list of components to attach
    :param init_root: create a root component
    """
    component_tree = ComponentTree(attach_root=init_root)
    for component in components or []:
        component_tree.attach(component)

    return component_tree
