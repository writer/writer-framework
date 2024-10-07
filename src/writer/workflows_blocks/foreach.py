import writer.workflows
from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class ForEach(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(ForEach, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "For-each loop",
                "description": "Executes a workflow repeatedly, based on the items provided.",
                "category": "Content",
                "fields": {
                    "workflowKey": {
                        "name": "Workflow key",
                        "desc": "The workflow which will be executed for each item.",
                        "type": "Text",
                    },
                    "items": {
                        "name": "Items",
                        "desc": "The item value will be passed in the execution environment and will be available via @{item}.",
                        "default": "{}",
                        "type": "Object",
                        "control": "Textarea"
                    },
                    "executionEnv": {
                        "name": "Execution environment",
                        "desc": "You can add other values to the execution environment.",
                        "default": "{}",
                        "type": "Object",
                        "control": "Textarea"
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The workflow wasn't executed successfully.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "The workflow wasn't executed successfully.",
                        "style": "error",
                    },
                },
            }
        ))

    def run(self):
        workflow_key = self._get_field("workflowKey")
        items = self._get_field("items", as_json=True)
        base_execution_env = self._get_field("executionEnv", as_json=True)

        try:
            for item in items:
                writer.workflows.run_workflow_by_key(self.session, workflow_key, base_execution_env | { "item": item })
            self.outcome = "success"
        except BaseException as e:
            self.session.session_state.add_log_entry("error", "Workflows exception", repr(e))
            self.result = "HTTP call failed."
            self.outcome = "error"