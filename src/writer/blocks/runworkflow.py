from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class RunWorkflow(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(RunWorkflow, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="workflows_node",
                writer={
                    "name": "Run blueprint",
                    "description": "Executes a workflow with a given key.",
                    "category": "Logic",
                    "fields": {
                        "workflowKey": {
                            "name": "Workflow Key",
                            "type": "Workflow Key",
                            "validator": {
                                "type": "string",
                                "format": "writer#workflowKey",
                            },
                        },
                        "payload": {
                            "name": "Payload",
                            "desc": "The value specified will be available using the template syntax i.e. @{payload}",
                            "default": "{}",
                            "type": "Text",
                            "control": "Textarea",
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
                            "description": "The workflow was executed successfully.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        try:
            workflow_key = self._get_field("workflowKey")
            payload = self._get_field("payload")
            expanded_execution_environment = self.execution_environment | {"payload": payload}
            return_value = self.runner.run_workflow_by_key(
                workflow_key, expanded_execution_environment
            )
            self.result = return_value
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
