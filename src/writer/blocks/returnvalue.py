from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate, WriterConfigurationError


class ReturnValue(BlueprintBlock):

    @classmethod
    def register(cls, type: str):
        super(ReturnValue, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="blueprints_node",
            writer={
                "name": "Return value",
                "description": "Returns a value from this block to the caller. Use to pass results to another blueprint.",
                "category": "Logic",
                "fields": {
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
            value = self._get_field("value")
            if value is None:
                raise WriterConfigurationError("Return value cannot be empty or None.")
            self.result = value
            self.return_value = value
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
