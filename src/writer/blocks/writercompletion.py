from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate

DEFAULT_MODEL = "palmyra-x5"

class WriterCompletion(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterCompletion, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Text generation",
                    "description": "Generates text using a Writer model. Use for completions, summaries, or creative writing.",
                    "category": "Writer",
                    "fields": {
                        "prompt": {"name": "Prompt", "type": "Text", "control": "Textarea"},
                        "modelId": {"name": "Model", "type": "Model Id", "default": DEFAULT_MODEL},
                        "temperature": {
                            "name": "Temperature",
                            "type": "Number",
                            "default": "0.7",
                            "validator": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
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
        try:
            import writer.ai

            prompt = self._get_field("prompt")
            temperature = float(self._get_field("temperature", False, "0.7"))
            model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)
            max_tokens = int(self._get_field("max_tokens", False, "1024"))
            config = {"temperature": temperature, "model": model_id, "max_tokens": max_tokens}
            result = writer.ai.complete(prompt, config).strip()
            self.result = result
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
