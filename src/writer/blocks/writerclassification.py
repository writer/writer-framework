import json

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate


class WriterClassification(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterClassification, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Classification",
                    "description": "Classifies text into predefined categories using AI. Useful for tagging and routing inputs.",
                    "category": "Writer",
                    "fields": {
                        "text": {
                            "name": "Text",
                            "type": "Text",
                            "desc": "The text you want to classify.",
                        },
                        "categories": {
                            "name": "Categories",
                            "type": "Key-Value",
                            "default": "{}",
                            "desc": "The keys should be the categories you want to classify the text in, for example 'valid' and 'invalid', and the values the criteria for each category.",
                        },
                        "additionalContext": {
                            "name": "Additional context",
                            "type": "Text",
                            "control": "Textarea",
                            "desc": "Any additional information that might help the AI in making the classification decision.",
                        },
                    },
                    "outs": {
                        "category": {"field": "categories", "style": "dynamic"},
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
