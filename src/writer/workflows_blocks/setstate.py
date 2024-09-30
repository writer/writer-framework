from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class SetState(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(SetState, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Set state",
                "description": "Set the value for a state element",
                "category": "Content",
                "fields": {
                    "element": {
                        "name": "State element",
                        "type": "Text",
                    },
                    "value": {
                        "name": "Value",
                        "type": "Text",
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
        element = self._get_field("element")
        value = self._get_field("value")

        try:
            self.evaluator.set_state(element, self.instance_path, value)
            self.outcome = "success"
        except Exception as e:
            self.outcome = "error"