from writer.abstract import register_abstract_template
from writer.blocks.base_trigger import BlueprintTrigger
from writer.ss_types import AbstractTemplate


class APITrigger(BlueprintTrigger):
    @classmethod
    def register(cls, type: str):
        super(APITrigger, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "API Trigger",
                    "description": "Triggers an event via API call.",
                    "category": "Triggers",
                    "fields": {
                        "defaultResult": {
                            "name": "Default payload",
                            "type": "Code",
                            "desc": 'The payload that is used when the blueprint is triggered from the "Run blueprint" button',
                        },
                    },
                    "outs": {
                        "trigger": {
                            "name": "Trigger",
                            "style": "success",
                        },
                    },
                },
            ),
        )

    def run(self):
        super().run()
        self.outcome = "trigger"
