from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class WriterCompletion(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterCompletion, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Writer Completion",
                "description": "Set the value for a state element",
                "category": "Content",
                "fields": {
                    "prompt": {
                        "name": "Prompt",
                        "type": "Text",
                    },
                    "tools": {
                        "name": "Tools",
                        "type": "Object"
                    }
                },
                "outs": {
                    # "$tools": {
                    #     "field": "tools"
                    # },
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
        import writer.ai

        prompt = self._get_field("prompt")
        # model_id = self._get_field("modelId")

        config = {}
        # if model_id:
        #     config["model"] = model_id

        try:
            result = writer.ai.complete(prompt, config).strip()
            self.result = result
            self.outcome = "success"
        except BaseException:
            self.result = "Text completion failed"
            self.outcome = "error"