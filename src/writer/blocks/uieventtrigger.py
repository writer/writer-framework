from writer.abstract import register_abstract_template
from writer.blocks.base_trigger import BlueprintTrigger
from writer.ss_types import AbstractTemplate


class UIEventTrigger(BlueprintTrigger):
    @classmethod
    def register(cls, type: str):
        super(UIEventTrigger, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "UI Trigger",
                    "description": "Triggers an event based on UI interactions like button clicks or input changes.",
                    "category": "Triggers",
                    "fields": {
                        "refComponentId": {
                            "name": "Component Id",
                            "type": "Component Id",
                            "options": "uiComponentsWithEvents",
                            "desc": "The id of the component that will trigger this branch.",
                        },
                        "refEventType": {
                            "name": "Event type",
                            "type": "Component Event Type",
                            "desc": "The type of the event that will trigger this branch. For example, wf-click.",
                            "options": "eventTypes",
                        },
                        "defaultResult": {
                            "name": "Default result",
                            "type": "Code",
                            "desc": 'The result that is used when the blueprint is triggered from the "Run blueprint" button',
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
