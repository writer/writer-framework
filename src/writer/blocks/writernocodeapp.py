from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class WriterNoCodeApp(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterNoCodeApp, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "No-code app",
                "description": "Run a no-code app.",
                "category": "Writer",
                "fields": {
                    "appId": {
                        "name": "App Id",
                        "type": "Text",
                        "desc": "The app id can be found in the app's URL. It has a UUID format."
                    },
                    "appInputs": {
                        "name": "App inputs",
                        "type": "Key-Value",
                        "default": "{}"
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "If the execution was successful.",
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

            application_id = self._get_field("appId", required=True)
            app_inputs = self._get_field("appInputs", as_json=True)

            # config = {}
            # if model_id:
            #     config["model"] = model_id

            result = writer.ai.apps.generate_content(application_id, app_inputs).strip()
            self.result = result
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e