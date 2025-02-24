from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate

DEFAULT_MODEL = "palmyra-x-004"

class WriterCompletion(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterCompletion, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Completion",
                "description": "Handles text completions.",
                "category": "Writer",
                "fields": {
                    "prompt": {
                        "name": "Prompt",
                        "type": "Text",
                        "control": "Textarea"
                    },
                    "modelId": {
                        "name": "Model id",
                        "type": "Text",
                        "default": DEFAULT_MODEL
                    },
                    "temperature": {
                        "name": "Temperature",
                        "type": "Number",
                        "default": "0.7",
                        "validator": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
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
            }
        ))

    def run(self):
        try:
            import writer.ai

            prompt = self._get_field("prompt")
            temperature = float(self._get_field("temperature", False, "0.7"))
            model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)
            config = { "temperature": temperature, "model": model_id}
            result = writer.ai.complete(prompt, config).strip()
            self.result = result
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e