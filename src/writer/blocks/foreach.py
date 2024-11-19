from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class ForEach(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(ForEach, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "For-each loop",
                "description": "Executes a workflow repeatedly, based on the items provided.",
                "category": "Logic",
                "fields": {
                    "workflowKey": {
                        "name": "Workflow key",
                        "desc": "The workflow which will be executed for each item.",
                        "type": "Text",
                    },
                    "items": {
                        "name": "Items",
                        "desc": "The item value will be passed in the execution environment and will be available at @{item}, its id at @{itemId}.",
                        "default": "{}",
                        "init": '{ "fr": "France", "pl": "Poland" }',
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
                        "description": "The workflow executed successfully.",
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

    def _run_workflow_for_item(self, workflow_key, base_execution_environment, item_id, item):
        expanded_execution_environment = base_execution_environment | { "itemId": item_id, "item": item }
        return self.runner.run_workflow_by_key(workflow_key, expanded_execution_environment)

    def run(self):
        try:
            workflow_key = self._get_field("workflowKey")
            items = self._get_field("items", as_json=True)
            base_execution_environment = self._get_field("executionEnv", as_json=True)
            std_items = items
            result = None
            if isinstance(items, list):
                std_items = enumerate(std_items, 0)
                result = [self._run_workflow_for_item(workflow_key, base_execution_environment, item_id, item) for item_id, item in std_items]
            elif isinstance(items, dict):
                std_items = items.items()
                result = {item_id:self._run_workflow_for_item(workflow_key, base_execution_environment, item_id, item) for item_id, item in std_items}

            self.result = result
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e