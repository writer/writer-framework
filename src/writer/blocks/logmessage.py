from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class LogMessage(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(LogMessage, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="workflows_node",
                writer={
                    "name": "Log message",
                    "description": "Appends a message to the log.",
                    "category": "Other",
                    "fields": {
                        "type": {
                            "name": "Type",
                            "type": "Text",
                            "options": {"info": "Info", "error": "Error"},
                            "default": "info",
                        },
                        "message": {"name": "Message", "type": "Text", "control": "Textarea"},
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
                },
            ),
        )

    def run(self):
        try:
            type = self._get_field("type", False, "info")
            message = str(self._get_field("message", required=True))

            self.runner.session.session_state.add_log_entry(type, "Workflows message", message)
            self.result = message
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
