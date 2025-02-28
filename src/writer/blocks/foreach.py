from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class ForEach(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(ForEach, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="workflows_node",
                writer={
                    "name": "For-each loop",
                    "description": "Executes a workflow repeatedly, based on the items provided.",
                    "category": "Logic",
                    "fields": {
                        "workflowKey": {
                            "name": "Workflow Key",
                            "desc": "The workflow which will be executed for each item.",
                            "type": "Workflow Key",
                        },
                        "items": {
                            "name": "Items",
                            "desc": "The item value will be passed in the execution environment and will be available at @{payload.item}, its id at @{payload.itemId}.",
                            "default": "{}",
                            "init": '{ "fr": "France", "pl": "Poland" }',
                            "type": "Object",
                            "control": "Textarea",
                        },
                    },
                    "outs": {
                        "success": {
                            "name": "Success",
                            "description": "The workflow executed successfully.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "The workflow wasn't executed successfully.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        try:
            workflow_key = self._get_field("workflowKey")
            items = self._get_field("items", as_json=True)
            base_execution_environment = self.execution_environment

            if not isinstance(items, (list, dict)):
                raise ValueError("Items must be a list or dictionary.")

            if isinstance(items, list):
                workflow_environments = [
                    base_execution_environment | {"payload": {"itemId": i, "item": item}}
                    for i, item in enumerate(items)
                ]
                results = self.runner.run_workflow_pool(workflow_key, workflow_environments)
                self.result = results  # Return as a list

            elif isinstance(items, dict):
                workflow_environments = {
                    str(item_id): base_execution_environment
                    | {"payload": {"itemId": str(item_id), "item": item}}
                    for item_id, item in items.items()
                }
                results = self.runner.run_workflow_pool(
                    workflow_key, list(workflow_environments.values())
                )
                self.result = {
                    item_id: results[i] for i, item_id in enumerate(workflow_environments.keys())
                }

            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
