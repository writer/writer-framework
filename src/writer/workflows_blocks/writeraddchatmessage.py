from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class WriterAddChatMessage(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterAddChatMessage, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Writer Add Chat Message",
                "description": "Add a message to a conversation.",
                "category": "Content",
                "fields": {
                    "conversationStateElement": {
                        "name": "Conversation state element",
                        "desc": "Where the conversation is stored",
                        "type": "Text",
                    },
                    "message": {
                        "name": "Message",
                        "type": "Object",
                        "init": '{ "role": "assistant", "content": "Hello" }'
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
            message = self._get_field("message", as_json=True)
            # model_id = self._get_field("modelId")
            conversation = self.evaluator.evaluate_expression(conversation_state_element, self.instance_path, self.execution_env)

            if not conversation:
                conversation = writer.ai.Conversation()
                self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)

            conversation += message

            self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)            
            self.result = "Success"
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

    