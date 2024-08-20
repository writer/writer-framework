"""
This module allows you to migrate obsolete data structures to newer data structures.
For example, when loading the ui.
"""


def fix_components(components: dict) -> dict:
    """
    Migrates obsolete components to their newer format and avoids errors in Pydantic.
    """
    components = _fix_visible_fields(components)
    return components


def _fix_visible_fields(components: dict) -> dict:
    """
    Migrates the component visibility attribute to a more descriptive format.

    >>> components['root']['visible'] = True

    >>> components['root']['visible'] = {
    >>>     'expression': True,
    >>>     'binding': "",
    >>>     'reversed': False
    >>> }

    If the visible attribute does not exist, it remains absent.
    """
    for key, value in components.items():
        visible = value.get('visible')

        if visible is not None and isinstance(visible, bool):
            components[key]['visible'] = {
                'expression': visible,
                'binding': "",
                "reversed": False
            }

        if visible is not None and isinstance(visible, str):
            components[key]['visible'] = {
                'expression': "custom",
                'binding': visible,
                'reversed': False
            }

    return components
