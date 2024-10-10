import writer.workflows
from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class RunWorkflow(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(RunWorkflow, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Run workflow",
                "description": "Executes a workflow",
                "category": "Content",
                "fields": {
                    "workflowKey": {
                        "name": "Workflow key",
                        "type": "Text",
                    },
                    "context": {
                        "name": "Context",
                        "desc": "Values passed in the context will be available using the template syntax i.e. @{my_context_var}",
                        "default": "{}",
                        "type": "Object",
                        "control": "Textarea"
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
            }
        ))

    def run(self):
        workflow_key = self._get_field("workflowKey")
        context = self._get_field("context", as_json=True)

        try:
            writer.workflows.run_workflow_by_key(self.session, workflow_key, context)
            self.outcome = "success"
        except Exception as e:
            print("running the other workflow " + repr(e))
            self.result = "Running workflow failed."
            self.outcome = "error"