from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class AddToStateList(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(AddToStateList, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Add to state list",
                "description": "Adds a value to a list in state, creating a new one if it doesn't exist.",
                "category": "Other",
                "fields": {
                    "element": {
                        "name": "State element",
                        "type": "Text"
                    },
                    "value": {
                        "name": "Value",
                        "type": "Text",
                        "control": "Textarea"
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "If the function doesn't raise an Exception.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "If the function raises an Exception.",
                        "style": "error",
                    },
                },
            }
        ))

    def run(self):
        try:
            element_expr = self._get_field("element")
            value = self._get_field("value")

            element = self.evaluator.evaluate_expression(element_expr, self.instance_path, self.execution_env)

            if not element:
                element = []
            elif not isinstance(element, list):
                element = [element]

            element.append(value)
            self.evaluator.set_state(element_expr, self.instance_path, element, base_context=self.execution_env)
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e