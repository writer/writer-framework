from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

DEFAULT_MODEL = "palmyra-x-004"

class WriterChat(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterChat, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Chat completion",
                "description": "Handles chat completions.",
                "category": "Writer",
                "fields": {
                    "conversationStateElement": {
                        "name": "Conversation state element",
                        "desc": "Where the conversation will be stored",
                        "type": "Text",
                    },
                    "modelId": {
                        "name": "Model id",
                        "type": "Text",
                        "default": DEFAULT_MODEL
                    },
                    "temperature": {
                        "name": "Temperature",
                        "type": "Number",
                        "default": "0.7"
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
            temperature = float(self._get_field("temperature", False, "0.7"))
            model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)
            config = { "temperature": temperature, "model": model_id}

            conversation = self.evaluator.evaluate_expression(conversation_state_element, self.instance_path, self.execution_env)

            if not conversation:
                conversation = writer.ai.Conversation(config=config)
                self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)

            # for chunk in conversation.stream_complete():
            #     if chunk.get("content") is None:
            #         chunk["content"] = ""
            #     conversation += chunk

            msg = conversation.complete()
            conversation += msg
            self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)            
            self.result = msg
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

    