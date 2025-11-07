from writer.abstract import register_abstract_template
from writer.blocks.base_trigger import BlueprintTrigger
from writer.ss_types import AbstractTemplate


class CronTrigger(BlueprintTrigger):
    @classmethod
    def register(cls, type: str):
        super(CronTrigger, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Cron Trigger",
                    "description": "Triggers an event on a schedule based on a cron expression.",
                    "category": "Triggers",
                    "featureFlags": ["cron_trigger"],
                    "fields": {
                        "cronExpression": {
                            "name": "Cron Expression",
                            "type": "Text",
                            "desc": "The cron expression that defines the schedule (e.g., '0 * * * *' for every hour).",
                        },
                        "timezone": {
                            "name": "Timezone",
                            "type": "Text",
                            "desc": "The timezone for the cron schedule (e.g., 'UTC', 'America/New_York'). Defaults to UTC.",
                            "default": "UTC",
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
