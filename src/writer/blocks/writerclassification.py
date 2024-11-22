import json

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class WriterClassification(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterClassification, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Classification",
                "description": "Classify a text.",
                "category": "Writer",
                "fields": {
                    "text": {
                        "name": "Text",
                        "type": "Text",
                    },
                    "categories": {
                        "name": "Categories",
                        "type": "Key-Value",
                        "default": "{}"
                    },
                    "additionalContext": {
                        "name": "Additional context",
                        "type": "Text",
                        "control": "Textarea"
                    },
                },
                "outs": {
                    "category": {
                        "field": "categories",
                        "style": "dynamic"
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
            import writer.ai

            text = self._get_field("text", required=True)
            additional_context = self._get_field("additionalContext")
            categories = self._get_field("categories", as_json=True, required=True)

            config = {}

            prompt = f"""
Classify the text under “CONTENT” into one of the following categories:

{ json.dumps(categories) }

Your output should be only the key and not contain anything else. For example: { " , ".join(list(categories.keys())) }.

Additional context:

{ additional_context }

CONTENT:
------
{ text }
"""
            result = writer.ai.complete(prompt, config).strip()
            self.result = result
            self.outcome = f"category_{result}"
        except BaseException as e:
            self.outcome = "error"
            raise e