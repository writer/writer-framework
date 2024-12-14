import json
import os
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import writer.core
import writer.core_ui
from writer.ss_types import (
    InstancePath,
    WriterConfigurationError,
)

if TYPE_CHECKING:
    from writer.core import WriterState
    from writer.core_ui import ComponentTree


class Evaluator:

    """
    Evaluates templates and expressions in the backend.
    It allows for the sanitisation of frontend inputs.
    """

    EXPRESSIONS_TEMPLATE_REGEX = re.compile(r"\{\{(.*?)\}\}")

    def __init__(self, globals: Dict, component_tree: "ComponentTree"):
        self.globals = globals
        self.component_tree = component_tree
        self.serializer = writer.core.StateSerialiser()

    def evaluate_field(self, instance_path: InstancePath, field_key: str, as_json=False, default_field_value="", base_context={}) -> Any:
        def decode_json(text):
            try:
                return json.loads(text)
            except json.JSONDecodeError as exception:
                raise WriterConfigurationError("Error decoding JSON. " + str(exception)) from exception

        def replacer(matched):
            if matched.string[0] == "\\":  # Escaped @, don't evaluate
                return matched.string
            expr = matched.group(1).strip()
            expr_value = eval(expr, self.globals)

            return expr_value

        component_id = instance_path[-1]["componentId"]
        component = self.component_tree.get_component(component_id)
        if not component:
            raise ValueError(f'Component with id "{component_id}" not found.')

        field_value = component.content.get(field_key) or default_field_value
        replaced = None
        full_match = self.EXPRESSIONS_TEMPLATE_REGEX.fullmatch(field_value)

        if full_match is None:
            replaced = self.EXPRESSIONS_TEMPLATE_REGEX.sub(lambda m: str(replacer(m)), field_value)
            if as_json:
                replaced = decode_json(replaced)
        else:
            replaced = replacer(full_match)
            if as_json and isinstance(replaced, str):
                replaced = decode_json(replaced)

        return replaced


    def get_context_data(self, instance_path: InstancePath, base_context={}) -> Dict[str, Any]:
        context: Dict[str, Any] = base_context
        for i in range(len(instance_path)):
            path_item = instance_path[i]
            component_id = path_item["componentId"]
            component = self.component_tree.get_component(component_id)
            if not component:
                continue
            if component.type != "repeater":
                continue
            if i + 1 >= len(instance_path):
                continue
            repeater_instance_path = instance_path[0:i+1]
            next_instance_path = instance_path[0:i+2]
            instance_number = next_instance_path[-1]["instanceNumber"]
            repeater_object = self.evaluate_field(
                repeater_instance_path, "repeaterObject", True, """{ "a": { "desc": "Option A" }, "b": { "desc": "Option B" } }""")
            key_variable = self.evaluate_field(
                repeater_instance_path, "keyVariable", False, "itemId")
            value_variable = self.evaluate_field(
                repeater_instance_path, "valueVariable", False, "item")

            repeater_items: List[Tuple[Any, Any]] = []
            if isinstance(repeater_object, dict):
                repeater_items = list(repeater_object.items())
            elif isinstance(repeater_object, list):
                repeater_items = list(enumerate(repeater_object))
            else:
                raise ValueError(
                    "Cannot produce context. Repeater object must evaluate to a dictionary.")

            context[key_variable] = repeater_items[instance_number][0]
            context[value_variable] = repeater_items[instance_number][1]

        if len(instance_path) > 0:
            context['target'] = instance_path[-1]['componentId']

        return context

    def set_state(self, expr: str, instance_path: InstancePath, value: Any, base_context = {}) -> None:
        accessors = self.parse_expression(expr, instance_path, base_context)
        state_ref = self.state

        for accessor in accessors[:-1]:
            if isinstance(state_ref, list):
                state_ref = state_ref[int(accessor)]
            else:
                state_ref = state_ref[accessor]

        if not isinstance(state_ref, (writer.core.State, writer.core.WriterState, writer.core.StateProxy, dict)):
            raise ValueError(
                f'Reference "{expr}" cannot be translated to state. Found value of type "{type(state_ref)}".')

        state_ref[accessors[-1]] = value        