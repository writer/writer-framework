from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate, WriterConfigurationError


class WriterAddChatMessage(BlueprintBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterAddChatMessage, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="blueprints_node",
            writer={
                "name": "Add chat message",
                "description": "Adds a message to the conversation history. Use for displaying user or AI messages.",
                "category": "Writer",
                "fields": {
                    "conversationStateElement": {
                        "name": "Conversation state element",
                        "desc": "Where the conversation is stored",
                        "type": "Text",
                    },
                    "message": {
                        "name": "Message",
                        "type": "Object",
                        "init": '{ "role": "assistant", "content": "Hello" }',
                        "validator": {
                            "type": "object",
                            "properties": {
                                "role": { "type": "string" },
                                "content": { "type": "string" },
                            },
                            "additionalProperties": False,
                        }
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

            conversation_state_element = self._get_field("conversationStateElement", required=True)
            message = self._get_field("message", as_json=True, required=True)

            conversation = self.evaluator.evaluate_expression(conversation_state_element, self.instance_path, self.execution_environment)

            if conversation is None or not isinstance(conversation, writer.ai.Conversation):
                raise WriterConfigurationError("The state element specified doesn't contain a conversation. Initialize one using the block 'Initialize chat'.")
            
            writer.ai.Conversation.validate_message(message)
            conversation += message

            self._set_state(conversation_state_element, conversation)            
            self.result = None
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

    
