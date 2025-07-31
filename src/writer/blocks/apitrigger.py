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
                        "blueprintId": {
                            "name": "Blueprint ID",
                            "type": "Blueprint Id",
                        },
                        "defaultResult": {
                            "name": "Default result",
                            "type": "Code",
                            "desc": 'The result that is used when the blueprint is triggered from the "Run blueprint" button',
                            "isArtifactField": True,
                        },
                    },
                    "outs": {
                        "trigger": {
                            "name": "Trigger",
                            "style": "success",
                        },
                    },
                    "settingsArtifacts": [
                        {"key": "apiTriggerDetails", "position": "bottom"}
                    ]
                },
            ),
        )

    def run(self):
        super().run()
        self.outcome = "trigger"
