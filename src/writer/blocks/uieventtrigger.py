from writer.abstract import register_abstract_template
from writer.blocks.base_trigger import WorkflowTrigger
from writer.ss_types import AbstractTemplate


class UIEventTrigger(WorkflowTrigger):
    @classmethod
    def register(cls, type: str):
        super(UIEventTrigger, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="workflows_node",
                writer={
                    "name": "UI Trigger",
                    "description": "Trigger the workflow when an UI event takes place.",
                    "category": "Triggers",
                    "fields": {
                        "refComponentId": {
                            "name": "Component Id",
                            "type": "Text",
                            "options": "uiComponentsWithEvents",
                            "desc": "The id of the component that will trigger this branch.",
                        },
                        "refEventType": {
                            "name": "Event type",
                            "type": "Text",
                            "desc": "The type of the event that will trigger this branch. For example, wf-click.",
                            "options": "eventTypes",
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
        self.outcome = "trigger"
