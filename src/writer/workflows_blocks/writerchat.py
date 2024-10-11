from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class WriterChat(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterChat, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Writer Chat",
                "description": "Handles chat completions.",
                "category": "Content",
                "fields": {
                    "conversationStateElement": {
                        "name": "Conversation state element",
                        "desc": "Where the conversation will be stored",
                        "type": "Text",
                    },
                    "incomingMessage": {
                        "name": "Incoming message",
                        "type": "Object",
                        "default": "{}"
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "If the function doesn't raise an Exception.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "If the function raises an Exception.",
                        "style": "error",
                    },
                },
            }
        ))

    def run(self):
        try:
            import writer.ai

            conversation_state_element = self._get_field("conversationStateElement")
            incoming_message = self._get_field("incomingMessage", as_json=True)
            # model_id = self._get_field("modelId")
            conversation = self.evaluator.evaluate_expression(conversation_state_element, self.instance_path, self.execution_env)

            if not conversation:
                conversation = writer.ai.Conversation()
                self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)

            incoming_message = self._get_field("incomingMessage")

            if incoming_message:
                conversation += incoming_message
                self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)
                msg = conversation.complete()
                conversation += msg
                self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)

            # config = {}
            # if model_id:
            #     config["model"] = model_id
            
            self.result = "Success"
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

    