import json

import requests

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class ParseJSON(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(ParseJSON, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Parse JSON",
                "description": "Parses a JSON string.",
                "category": "Content",
                "fields": {
                    "plainText": {
                        "name": "Plain text",
                        "type": "Text",
                        "control": "Textarea"
                    },
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
            }
        ))

    def run(self):
        try:
            plain_text = self._get_field("plainText")
            self.result = json.loads(plain_text)
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e