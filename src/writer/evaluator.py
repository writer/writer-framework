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

    TEMPLATE_REGEX = re.compile(r"[\\]?@{([^{]*?)}")
    CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")

    def __init__(self, state: "WriterState", component_tree: "ComponentTree"):
        self.state = state
        self.component_tree = component_tree
        self.serializer = writer.core.StateSerialiser()

    def evaluate_field(
        self,
        instance_path: InstancePath,
        field_key: str,
        as_json=False,
        default_field_value="",
        base_context={},
    ) -> Any:
        def decode_json(text):
            if not isinstance(text, str):
                return text
            try:
                # Remove control chars
                clean_text = Evaluator.CONTROL_CHARS.sub("", text)
                return json.loads(clean_text, strict=False)
            except json.JSONDecodeError as exception:
                raise WriterConfigurationError(
                    "Error decoding JSON. " + str(exception)
                ) from exception

        component_id = instance_path[-1]["componentId"]
        component = self.component_tree.get_component(component_id)
        if not component:
            raise ValueError(f'Component with id "{component_id}" not found.')

        field_value = component.content.get(field_key) or default_field_value
        replaced = None
        full_match = self.TEMPLATE_REGEX.fullmatch(field_value)

        def replacer(matched):
            if matched.string[0] == "\\":  # Escaped @, don't evaluate
                return matched.string
            expr = matched.group(1).strip()
            expr_value = self.evaluate_expression(expr, instance_path, base_context)
            if full_match is not None:
                return expr_value
            if as_json:
                return json.dumps(expr_value)
            if not isinstance(expr_value, str):
                return json.dumps(expr_value)
            return expr_value

        if full_match is None:
            replaced = field_value
            if as_json:
                # First pass to remove quotes around @{my_var}
                replaced = re.sub(r'"(@{\s*[^"]+?\s*})"', r"\1", field_value)
            replaced = self.TEMPLATE_REGEX.sub(replacer, replaced)
            if as_json:
                replaced = decode_json(replaced)
        else:
            replaced = replacer(full_match)
            if as_json:
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
            repeater_instance_path = instance_path[0 : i + 1]
            next_instance_path = instance_path[0 : i + 2]
            instance_number = next_instance_path[-1]["instanceNumber"]
            repeater_object = self.evaluate_field(
                repeater_instance_path,
                "repeaterObject",
                True,
                """{ "a": { "desc": "Option A" }, "b": { "desc": "Option B" } }""",
            )
            key_variable = self.evaluate_field(
                repeater_instance_path, "keyVariable", False, "itemId"
            )
            value_variable = self.evaluate_field(
                repeater_instance_path, "valueVariable", False, "item"
            )

            repeater_items: List[Tuple[Any, Any]] = []
            if isinstance(repeater_object, dict):
                repeater_items = list(repeater_object.items())
            elif isinstance(repeater_object, list):
                repeater_items = list(enumerate(repeater_object))
            else:
                raise ValueError(
                    "Cannot produce context. Repeater object must evaluate to a dictionary."
                )

            context[key_variable] = repeater_items[instance_number][0]
            context[value_variable] = repeater_items[instance_number][1]

        if len(instance_path) > 0:
            context["target"] = instance_path[-1]["componentId"]

        return context

    def set_state(
        self, expr: str, instance_path: InstancePath, value: Any, base_context={}
    ) -> None:
        accessors = self.parse_expression(expr, instance_path, base_context)
        state_ref = self.state

        for accessor in accessors[:-1]:
            if isinstance(state_ref, list):
                state_ref = state_ref[int(accessor)]
            else:
                state_ref = state_ref[accessor]

        if not isinstance(
            state_ref, (writer.core.State, writer.core.WriterState, writer.core.StateProxy, dict)
        ):
            raise ValueError(
                f'Reference "{expr}" cannot be translated to state. Found value of type "{type(state_ref)}".'
            )

        state_ref[accessors[-1]] = value

    def parse_expression(
        self, expr: str, instance_path: Optional[InstancePath] = None, base_context={}
    ) -> List[str]:
        """Returns a list of accessors from an expression."""

        if not isinstance(expr, str):
            raise ValueError(
                f'Expression must be of type string. Value of type "{ type(expr) }" found.'
            )

        accessors: List[str] = []
        s = ""
        level = 0

        i = 0
        while i < len(expr):
            character = expr[i]
            if character == "\\":
                if i + 1 < len(expr):
                    s += expr[i + 1]
                    i += 1
            elif character == ".":
                if level == 0:
                    accessors.append(s)
                    s = ""
                else:
                    s += character
            elif character == "[":
                if level == 0:
                    accessors.append(s)
                    s = ""
                else:
                    s += character
                level += 1
            elif character == "]":
                level -= 1
                if level == 0:
                    s = str(self.evaluate_expression(s, instance_path, base_context))
                else:
                    s += character
            else:
                s += character

            i += 1

        if s:
            accessors.append(s)

        return accessors

    def get_env_variable_value(self, expr: str):
        return os.getenv(expr[1:])

    def evaluate_expression(
        self, expr: str, instance_path: Optional[InstancePath] = None, base_context={}
    ) -> Any:
        context_data = base_context
        result = None
        if instance_path:
            context_data = self.get_context_data(instance_path, base_context)
        context_ref: Any = context_data
        state_ref: Any = self.state.user_state
        accessors: List[str] = self.parse_expression(expr, instance_path, base_context)

        for accessor in accessors:
            if isinstance(state_ref, (writer.core.StateProxy, dict)) and accessor in state_ref:
                state_ref = state_ref.get(accessor)
                result = state_ref
            elif isinstance(state_ref, (list)) and state_ref[int(accessor)] is not None:
                state_ref = state_ref[int(accessor)]
                result = state_ref
            elif isinstance(context_ref, dict) and accessor in context_ref:
                context_ref = context_ref.get(accessor)
                result = context_ref

        if isinstance(result, writer.core.StateProxy):
            return result.to_dict()

        if result is None and expr.startswith("$"):
            return self.get_env_variable_value(expr)

        return result
