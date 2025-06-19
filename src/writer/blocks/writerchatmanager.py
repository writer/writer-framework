from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate, WriterConfigurationError

DEFAULT_MODEL = "palmyra-x-004"


class WriterChatManager(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterChatManager, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Chat manager",
                    "description": "Initializes conversations, adds messages, and can generate replies.",
                    "category": "Writer",
                    "fields": {
                        "conversationStateElement": {
                            "name": "Conversation state element",
                            "desc": "Where the conversation will be stored",
                            "type": "Text",
                        },
                        "systemPrompt": {
                            "name": "System prompt",
                            "type": "Text",
                            "control": "Textarea",
                            "default": "",
                            "desc": "A system prompt to set the context for the conversation. Can be left empty if conversation is already initialized in state.",
                        },
                        "message": {
                            "name": "Message",
                            "type": "Object",
                            "init": '{ "role": "assistant", "content": "Hello" }',
                            "desc": "The message to add to the conversation. Can be left empty if only generating a reply from AI.",
                            "validator": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"},
                                },
                                "additionalProperties": False,
                            },
                        },
                        "initModelId": {
                            "name": "Initial model",
                            "type": "Model Id",
                            "default": DEFAULT_MODEL,
                        },
                        "initTemperature": {
                            "name": "Initial temperature",
                            "type": "Number",
                            "default": "0.7",
                            "validator": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                        },
                        "initMaxTokens": {
                            "name": "Initial max tokens",
                            "type": "Number",
                            "default": "1024",
                            "validator": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 8192,
                            },
                        },
                        "generateReply": {
                            "name": "Generate reply",
                            "type": "Text",
                            "default": "no",
                            "desc": "If set to 'yes', the block will generate a reply based on the conversation. If set to 'no', it will only add the message to the conversation.",
                            "options": {"yes": "Yes", "no": "No"},
                        },
                        "useStreaming": {
                            "name": "Use streaming",
                            "type": "Text",
                            "default": "yes",
                            "desc": "If set to 'yes', the block will stream the reply as it is generated. If set to 'no', it will wait for the entire reply to be generated before returning.",
                            "options": {"yes": "Yes", "no": "No"},
                        },
                        "tools": {
                            "name": "Tools",
                            "type": "Tools",
                            "default": "{}",
                            "init": "",
                            "category": "Tools",
                        },
                    },
                    "outs": {
                        "tools": {
                            "name": "Tools",
                            "field": "tools",
                            "description": "Run associated tools.",
                            "style": "dynamic",
                        },
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
                },
            ),
        )

    def _make_callable(self, tool_name: str):
        def callable(**args):
            expanded_execution_environment = self.execution_environment | args
            return_value = self.runner.run_branch(
                self.component.id,
                f"tools_{tool_name}",
                expanded_execution_environment,
                f"Blueprint branch execution (chat tool {tool_name})",
            )

            if return_value is None:
                self.outcome = "error"
                raise ValueError(
                    f'No value has been returned for the outcome branch "{tool_name}". Use the block "Return value" to specify one.'
                )

            return return_value

        return callable

    def run(self):
        try:
            import writer.ai

            conversation_state_element = self._get_field(
                "conversationStateElement", required=True
            )
            message = self._get_field("message", as_json=True)
            system_prompt = self._get_field(
                "systemPrompt", False, default_field_value=None
            )
            init_model_id = self._get_field(
                "initModelId", False, default_field_value=DEFAULT_MODEL
            )
            init_temperature = float(self._get_field("initTemperature", False, "0.7"))
            init_max_tokens = int(self._get_field("initMaxTokens", False, "1024"))
            use_streaming = self._get_field("useStreaming", False, "yes") == "yes"
            generate_reply = self._get_field("generateReply", False, "no") == "yes"
            tools_raw = self._get_field("tools", True)
            tools = []

            for tool_name, tool_raw in tools_raw.items():
                tool_type = tool_raw.get("type")
                tool = None
                if tool_type == "function":
                    tool = writer.ai.FunctionTool(
                        type="function",
                        name=tool_name,
                        description=tool_raw.get("description"),
                        callable=self._make_callable(tool_name),
                        parameters=tool_raw.get("parameters"),
                    )
                elif tool_type == "graph":
                    tool = writer.ai.GraphTool(
                        type="graph",
                        graph_ids=tool_raw.get("graph_ids"),
                        subqueries=False,
                        description=tool_name,
                    )
                else:
                    continue
                tools.append(tool)

            conversation = self.evaluator.evaluate_expression(
                conversation_state_element, self.instance_path, self.execution_environment
            )

            if conversation is None:
                config = {
                    "temperature": init_temperature,
                    "model": init_model_id,
                    "max_tokens": init_max_tokens,
                }
                conversation = writer.ai.Conversation(prompt_or_history=system_prompt, config=config)
                self._set_state(conversation_state_element, conversation)
            elif not isinstance(conversation, writer.ai.Conversation):
                raise WriterConfigurationError(
                    "The state element specified doesn't contain a Conversation."
                )

            if message not in (None, {}, ""):
                writer.ai.Conversation.validate_message(message)
                conversation += message

            result_text = None
            if generate_reply:
                msg = ""
                if not use_streaming:
                    reply = conversation.complete(tools=tools)
                    msg = reply.get("content") or ""
                    conversation += reply
                    self._set_state(conversation_state_element, conversation)
                else:
                    for chunk in conversation.stream_complete(tools=tools):
                        if chunk.get("content") is None:
                            chunk["content"] = ""
                        msg += chunk.get("content")
                        conversation += chunk
                        self._set_state(conversation_state_element, conversation)
                result_text = msg
            self._set_state(conversation_state_element, conversation)
            self.result = result_text
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
