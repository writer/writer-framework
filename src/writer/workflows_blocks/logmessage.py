import writer.workflows
from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class LogMessage(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(LogMessage, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Log message",
                "description": "Adds a message to the log.",
                "category": "Content",
                "fields": {
                    "type": {
                        "name": "Type",
                        "type": "Text"
                    },
                    "message": {
                        "name": "Message",
                        "type": "Text",
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
        type = self._get_field("type")
        message = self._get_field("message")

        try:
            self.session.session_state.add_log_entry(type, "Workflows message", message)
            self.result = None
            self.outcome = "success"
        except Exception as e:
            self.result = "Logging message failed."
            self.outcome = "error"