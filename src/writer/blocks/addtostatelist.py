from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate, WriterConfigurationError


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

            element = self.evaluator.evaluate_expression(element_expr, self.instance_path, self.execution_environment)

            if not element:
                element = []
            elif not isinstance(element, list):
                raise WriterConfigurationError(f'The state element must be a list. A value of type "{type(element)}" was found.')

            element.append(value)
            self._set_state(element_expr, element)
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e