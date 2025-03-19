from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class SetState(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(SetState, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="workflows_node",
                writer={
                    "name": "Set state",
                    "description": "Set the value for a state element.",
                    "category": "Other",
                    "fields": {
                        "element": {
                            "name": "State element",
                            "type": "Text",
                            "desc": "The name of the state element. If set to 'my_var' the value will be available at @{my_var} when using as part of a template.",
                        },
                        "value": {"name": "Value", "type": "Text", "control": "Textarea"},
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
                },
            ),
        )

    def run(self):
        try:
            element = self._get_field("element", required=True)
            value = self._get_field("value")

            self._set_state(element, value)
            self.result = value
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
