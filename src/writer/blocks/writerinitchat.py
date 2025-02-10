from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate, WriterConfigurationError

DEFAULT_MODEL = "palmyra-x-004"


class WriterInitChat(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterInitChat, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Initialize chat",
                "description": "If it doesn't already exist, initializes a conversation for Chat completion",
                "category": "Writer",
                "fields": {
                    "conversationStateElement": {
                        "name": "Conversation state element",
                        "desc": "If not empty, the conversation will be stored in this state element. Specify the state element directly, without the template syntax.",
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
                        "default": "0.7",
                        "validator": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
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

            conversation_state_element = self._get_field("conversationStateElement")
            temperature = float(self._get_field("temperature", False, "0.7"))
            model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)
            config = { "temperature": temperature, "model": model_id}

            conversation = self.evaluator.evaluate_expression(conversation_state_element, self.instance_path, self.execution_environment)

            if conversation is not None and not isinstance(conversation, writer.ai.Conversation):
                raise WriterConfigurationError(f'The state element specified does not contain a Conversation. A value of type "{type(conversation)}" was found.')
            elif conversation is not None:
                self.result = "The conversation already exists. It will not be overwritten."
                self.outcome = "success"
                return

            conversation = writer.ai.Conversation(config=config)
            self._set_state(conversation_state_element, conversation)
            self.result = None
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

    