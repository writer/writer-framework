import json

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate

DEFAULT_MODEL = "palmyra-x5"


class WriterStructuredOutput(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterStructuredOutput, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Structured output",
                    "description": "Allows to define a JSON response format, which the agent will use to structure its output.",
                    "category": "Writer",
                    "fields": {
                        "prompt": {"name": "Prompt", "type": "Text", "control": "Textarea", "desc": "Description of a JSON object to be created."},
                        "modelId": {
                            "name": "Model",
                            "type": "Model Id",
                            "default": DEFAULT_MODEL
                        },
                        "jsonSchema": {
                            "name": "JSON Schema",
                            "desc": "JSON schema that defines the structure of the response. For example, `{\"type\": \"object\", \"properties\": {...}, \"required\": [...]}`.",
                            "type": "JSON",
                            "default": "{}"
                        },
                        "max_tokens": {
                            "name": "Max output tokens",
                            "type": "Number",
                            "default": "1024",
                            "validator": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 16384,
                            }
                        }
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
            schema = self._get_field("jsonSchema", True, default_field_value="{}")
            max_tokens = int(self._get_field("max_tokens", False, "1024"))

            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "schema": schema
                    }
                }

            conversation += {
                "role": "user",
                "content": prompt,
            }
            config = { "model": model_id, "max_tokens": max_tokens }
            msg = conversation.complete(response_format=response_format, config=config)
            conversation += msg

            raw_content = msg.get("content")
            if not raw_content:
                self.outcome = "error"
                raise RuntimeError("No content returned from the model. Please validate the prompt and model configuration.")

            try:
                # Attempt to parse the raw content as JSON
                content = json.loads(raw_content)
            except json.JSONDecodeError:
                self.outcome = "error"
                raise RuntimeError(
                    f"Failed to decode JSON content. The raw content was: {raw_content}. Please validate the prompt and model configuration."
                )

            self.result = content
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
