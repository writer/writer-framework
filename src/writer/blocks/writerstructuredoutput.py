import json

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate

DEFAULT_MODEL = "palmyra-x-004"

class WriterStructuredOutput(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterStructuredOutput, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Structured Output",
                    "description": "Allows to define a JSON response format, which the agent will use to structure its output.",
                    "category": "Writer",
                    "fields": {
                        "prompt": {"name": "Prompt", "type": "Text", "control": "Textarea", "desc": "Description of a JSON object that needs to be created."},
                        "modelId": {
                            "name": "Model",
                            "type": "Model Id",
                            "default": DEFAULT_MODEL
                        },
                        "response_format": {
                            "name": "Response Format",
                            "desc": "JSON schema that defines the structure of the response. For example, `{\"type\": \"object\", \"properties\": {...}, \"required\": [...]}`.",
                            "type": "Object",
                            "default": "{}",
                            "validator": {
                                "type": "object"
                            }
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
                },
            ),
        )

    def run(self):
        import writer.ai

        try:
            prompt = self._get_field("prompt")
            model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)
            conversation = writer.ai.Conversation()
            raw_response_format = self._get_field("response_format", True, default_field_value="{}")

            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "schema": raw_response_format
                    }
                }

            conversation += {
                "role": "user",
                "content": prompt,
            }
            config = {"model": model_id}
            msg = conversation.complete(response_format=response_format, config=config)
            conversation += msg

            self.result = msg.get("content")
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
