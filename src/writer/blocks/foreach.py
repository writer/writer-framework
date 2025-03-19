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
                    "description": "Executes a branch repeatedly, based on the items provided.",
                    "category": "Logic",
                    "fields": {
                        "items": {
                            "name": "Items",
                            "desc": "The item value will be passed in the execution environment and will be available at @{item}, its id at @{itemId}. You can use either a list or a dictionary.",
                            "default": "[]",
                            "init": '["France", "Poland"]',
                            "type": "Object",
                            "control": "Textarea",
                        },
                        "prefix": {
                            "name": "Prefix",
                            "type": "Text",
                            "desc": "If set, the item will be available at @{prefix_item} and the item id at @{prefix_itemId}.",
                        },
                    },
                    "outs": {
                        "loop": {
                            "name": "Loop",
                            "description": "Connect the branch that you'd like to loop on. The branch plugged in here will be executed once per item.",
                            "style": "dynamic",
                        },
                        "success": {
                            "name": "Success",
                            "description": "The branch referenced executed successfully for each item.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "The branch referenced has failed for at least one of the items.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        try:
            items = self._get_field("items", as_json=True)
            prefix = str(self._get_field("prefix", as_json=False, default_field_value="")).strip()
            if prefix:
                prefix += "_"
            base_execution_environment = self.execution_environment

            if not isinstance(items, (list, dict)):
                raise ValueError("Items must be a list or dictionary.")

            if isinstance(items, list):
                workflow_environments = [
                    base_execution_environment | {f"{prefix}itemId": i, f"{prefix}item": item}
                    for i, item in enumerate(items)
                ]

                results = self.runner.run_branch_pool(
                    self.component.id, "loop", workflow_environments
                )
                self.result = results  # Return as a list

            elif isinstance(items, dict):
                workflow_environments = {
                    str(item_id): base_execution_environment
                    | {f"{prefix}itemId": str(item_id), f"{prefix}item": item}
                    for item_id, item in items.items()
                }
                results = self.runner.run_branch_pool(
                    self.component.id, "loop", list(workflow_environments.values())
                )
                self.result = {
                    item_id: results[i] for i, item_id in enumerate(workflow_environments.keys())
                }

            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
