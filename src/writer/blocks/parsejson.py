import json

from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate


class ParseJSON(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        super(ParseJSON, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Parse JSON",
                    "description": "Converts a JSON string into an object, so you can work with it in your logic.",
                    "category": "Other",
                    "fields": {
                        "plainText": {"name": "Plain text", "type": "Text", "control": "Textarea"},
                    },
                    "outs": {
                        "success": {
                            "name": "Success",
                            "description": "The request was successful.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "The text provided couldn't be parsed.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        try:
            plain_text = self._get_field("plainText")
            if isinstance(plain_text, dict):
                self.result = plain_text
            else:
                self.result = json.loads(plain_text)
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
