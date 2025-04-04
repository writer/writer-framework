from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate


class RunBlueprint(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        super(RunBlueprint, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Run blueprint",
                    "description": "Starts another blueprint by key. Useful for breaking logic into smaller, reusable parts.",
                    "category": "Logic",
                    "fields": {
                        "blueprintKey": {
                            "name": "Blueprint Key",
                            "type": "Blueprint Key",
                            "validator": {
                                "type": "string",
                                "format": "writer#blueprintKey",
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
                            "description": "The blueprint was executed successfully.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        try:
            blueprint_key = self._get_field("blueprintKey")
            payload = self._get_field("payload")
            expanded_execution_environment = self.execution_environment | {"payload": payload}
            return_value = self.runner.run_blueprint_by_key(
                blueprint_key, expanded_execution_environment
            )
            self.result = return_value
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
