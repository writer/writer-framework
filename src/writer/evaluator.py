import json
import os
import re
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import writer.core
import writer.core_ui
from writer.serializer import serialize
from writer.ss_types import (
    InstancePath,
)

if TYPE_CHECKING:
    from writer.core_ui import ComponentTree


class Evaluator:

    """
    Evaluates templates and expressions in the backend.
    It allows for the sanitisation of frontend inputs.
    """

    EXPRESSIONS_TEMPLATE_REGEX = re.compile(r"\{\{([^{}]*)\}\}")

    def __init__(self, state: "writer.core.WriterState", component_tree: "ComponentTree", mail: "writer.core.SessionMail"):
        self.state = state
        self.component_tree = component_tree
        self.mail = mail
        self.evaluated_tree = None

    @classmethod
    def _transform_expression_to_state_reference(cls, expr: str) -> str:
        pattern = r"^(\w+)([\.\[]?.*)"
        transformed_expr = re.sub(pattern, r'state.\1\2', expr)
        return transformed_expr

    def set_state(self, expr: str, value: Any, locals: Dict) -> None:        
        # expr is safe and always defined by an app editor.

        try:
            transformed_expr = Evaluator._transform_expression_to_state_reference(expr)
            exec(f"{transformed_expr} = __wf_temp_assignment_value", None, locals | {"state": self.state, "__wf_temp_assignment_value": value})
        except BaseException as e:
            import traceback
            msg = f"Couldn't assign value to expression `{expr}`. Please make sure that it's a valid left-hand side expression."
            self.mail.add_log_entry("error", "Assignment error", msg, traceback.format_exc())
            raise ValueError(msg)

    @classmethod
    def has_template(cls, text: str) -> bool:
        return re.search(Evaluator.EXPRESSIONS_TEMPLATE_REGEX, text) is not None

    def _get_scaffolding(self):
        """
        Returns a structure that, for every componentId, contains the fields which require evaluation.
        If inside content, values are expected to use the template syntax i.e. {{ my_var }}.

        {"root", {
            "binding": {
                "reference": "a['ok']"
            },
            "content": {
                "text": "Max value is {{a + 2}}"
            }
        }}
        """

        def crawl_component(component: "writer.core_ui.Component"):
            found = {}
            component_dict = component.model_dump(exclude_unset=True)

            for field_key, field_value in component_dict.get("content", {}).items():
                if not Evaluator.has_template(field_value) and component_dict["type"] != "repeater":
                    continue
                if not "content" in found:
                    found["content"] = {}
                found["content"][field_key] = field_value

            return found

        result = {}
        for tree in reversed(self.component_tree.tree_branches):
            for component in tree.components.values():
                fields_requiring_evaluation = crawl_component(component)
                if fields_requiring_evaluation:
                    result[component.id] = fields_requiring_evaluation

        return result

    @classmethod
    def flatten_instance_path(cls, instance_path: InstancePath):
        flat_ip = ",".join(map(lambda item: f"{item['componentId']}:{item['instanceNumber']}", instance_path))
        return flat_ip

    def parse_json_if_needed(self, original_value: Any, as_object: bool):
        if not as_object or not isinstance(original_value, str):
            return original_value
        parsed_value = None
        try:
            parsed_value = json.loads(original_value)
        except json.JSONDecodeError as e:
            import traceback
            self.mail.add_log_entry("error",
                                    "Evaluation error",
                                    f"Couldn't interpret `{original_value}` as JSON.", traceback.format_exc())
        return parsed_value

    def refresh_evaluated_tree(self):
        self.evaluated_tree = self.generate_evaluated_tree()

    def get_evaluated_tree(self):
        self.refresh_evaluated_tree()
        return self.evaluated_tree

    def generate_evaluated_tree(self):
        """
        Returns a structure that contains flattened instance paths and evaluated templates.
        It starts from the UI root, ignoring workflows_root.

        {"root:0", {
            "content": {
                "text": "Max value is 4"
            }
        }}
        """

        def evaluate_scaffolding(template, context):
            evaled = {}
            for field_key, field_value in template.get("content", {}).items():
                if not "content" in evaled:
                    evaled["content"] = {}
                evaled["content"][field_key] = self.evaluate_template(field_value, context)
            binding_reference = template.get("binding", {}).get("reference")
            if binding_reference:
                evaled["binding"] = {
                    "reference": self.evaluate_expression(binding_reference, context)
                }
            return evaled 

        def crawl_branch(instance_path: InstancePath, evaluated_tree: Dict, context: Dict):
            component_id = instance_path[-1]["componentId"]
            component_scaffolding = self.scaffolding.get(component_id)
            if component_scaffolding is not None:
                evaluated_tree[Evaluator.flatten_instance_path(instance_path)] = evaluate_scaffolding(component_scaffolding, context)
                evaluated_tree[Evaluator.flatten_instance_path(instance_path)]["_context"] = context
            children = self.component_tree.get_direct_descendents(component_id)
            for child in children:
                child_instance_path = instance_path + [{"componentId": child.id, "instanceNumber": 0}]
                if child.type == "repeater":
                    crawl_repeater_branch(child_instance_path, evaluated_tree, context)
                    continue
                crawl_branch(child_instance_path, evaluated_tree, context)

        def crawl_repeater_branch(instance_path: InstancePath, evaluated_tree: Dict, context: Dict):
            component_id = instance_path[-1]["componentId"]
            component_scaffolding = self.scaffolding.get(component_id)
            if component_scaffolding is not None:
                flat_instance_path = Evaluator.flatten_instance_path(instance_path)
                evaluated_tree[flat_instance_path] = evaluate_scaffolding(component_scaffolding, context)
                evaluated_tree[flat_instance_path]["_context"] = context
            repeater_object = self.evaluate_field(component_id,
                                                  "repeaterObject",
                                                  { "a": { "desc": "Option A" }, "b": { "desc": "Option B" }},
                                                  context,
                                                  True)
            repeater_items: List[Tuple[Any, Any]] = []
            if isinstance(repeater_object, dict):
                repeater_items = list(repeater_object.items())
            elif isinstance(repeater_object, list):
                repeater_items = list(enumerate(repeater_object))
            else:
                raise ValueError(
                    f'Cannot produce context. Repeater object must evaluate to a dictionary or list. Got {type(repr(repeater_object))}.')

            key_variable = self.evaluate_field(component_id, "keyVariable", "itemId", context, False)
            value_variable = self.evaluate_field(component_id, "valueVariable", "item", context, False)
            children = self.component_tree.get_direct_descendents(component_id)

            for child in children:
                for instance_number, repeater_item in enumerate(repeater_items):
                    child_instance_path = instance_path + [{"componentId": child.id, "instanceNumber": instance_number}]
                    new_context = context | {
                        key_variable: repeater_item[0],
                        value_variable: repeater_item[1]
                    }
                    if child.type == "repeater":
                        crawl_repeater_branch(child_instance_path, evaluated_tree, new_context)
                        continue
                    crawl_branch(child_instance_path, evaluated_tree, new_context)

        self.scaffolding = self._get_scaffolding()
        evaluated_tree = {}
        crawl_branch(
            [{"componentId": "root", "instanceNumber": 0}],
            evaluated_tree=evaluated_tree,
            context={})
        return serialize(evaluated_tree)

    def evaluate_field(self, component_id: str, field_key: str, default_value: Any, locals:Dict, as_object: bool):
        component = self.component_tree.get_component(component_id)
        static_value = component.content.get(field_key)
        if not static_value:
            return default_value
        if not Evaluator.has_template(static_value):
            return self.parse_json_if_needed(static_value, as_object)
        evaluated_field = self.evaluate_template(static_value, locals)
        if evaluated_field is not None:
            return self.parse_json_if_needed(evaluated_field, as_object)
        return default_value

    def evaluate_instance_field(self, instance_path: InstancePath, field_key: str, default_value: Any, as_object: bool):
        locals = self.get_context(instance_path)
        component_id = instance_path[-1]["componentId"]
        return self.evaluate_field(component_id, field_key, default_value, locals, as_object)

    def evaluate_template(self, template: str, locals:Dict={}):
        if template is None:
            return None
        if not isinstance(template, str):
            raise ValueError(f"{repr(template)} isn't a valid template.")
        full_match = self.EXPRESSIONS_TEMPLATE_REGEX.fullmatch(template)
        if full_match is None:
            return self.EXPRESSIONS_TEMPLATE_REGEX.sub(lambda m: str(self.evaluate_expression(m.group(1).strip(), locals)), template)
        return self.evaluate_expression(full_match.group(1).strip(), locals)

    def evaluate_expression(self, expr: str, locals: Dict):
        if not expr or not isinstance(expr, str):
            return None
        if expr.startswith("$") and len(expr) > 1:
            return os.getenv(expr[1:])
        try:
            return eval(expr, None, self.state._state_data | locals)
        except BaseException as e:
            import traceback
            self.mail.add_log_entry("error", "Evaluation error",
                                             f"Couldn't evaluate expression `{expr}`.", traceback.format_exc())
            return None

    def get_context(self, instance_path: InstancePath):
        context = {}
        partial_instance_path = []
        evaluated_tree = self.get_evaluated_tree()

        for instance_item in instance_path:
            partial_instance_path.append(instance_item)

            flat_partial_instance_path = Evaluator.flatten_instance_path(partial_instance_path)
            tree_entry = evaluated_tree.get(flat_partial_instance_path)
            if not tree_entry:
                continue
            context = tree_entry.get("_context", context)

        return context