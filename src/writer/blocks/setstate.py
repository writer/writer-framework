from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate


class SetState(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        super(SetState, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Set state",
                    "description": "Stores a value in the Agent's state. Use to remember data across steps.",
                    "category": "Other",
                    "fields": {
                        "element": {
                            "name": "Link Variable",
                            "type": "Binding",
                            "desc": "Set the variable here and use it across your agent",
                        },
                        "valueType": {
                            "name": "Value type",
                            "type": "Text",
                            "description": "Specify whether to interpret the value as plain text or JSON.",
                            "options": {
                                "text": "Plain text",
                                "JSON": "JSON",
                            },
                            "default": "text",
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
            value_type = self._get_field("valueType")
            value = self._get_field("value", as_json=value_type == "JSON")

            self._set_state(element, value)
            self.result = value
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
