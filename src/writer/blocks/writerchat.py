from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate


class WriterChat(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterChat, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Generate chat reply",
                    "description": "Generates an AI chat response using the full conversation history. Requires prior messages.",
                    "category": "Writer",
                    "deprecated": True,
                    "fields": {
                        "conversationStateElement": {
                            "name": "Conversation state element",
                            "desc": "The variable that has your conversation object.",
                            "type": "Binding",
                        },
                        "useStreaming": {
                            "name": "Use streaming",
                            "type": "Boolean",
                            "default": "yes",
                            "validator": {
                                "type": "boolean",
                            },
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
                "conversationStateElement", required=True)
            use_streaming = self._get_field(
                "useStreaming", False, "yes") == "yes"
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

            if conversation is None or not isinstance(conversation, writer.ai.Conversation):
                raise ValueError(
                    "The state element specified doesn't contain a conversation. Initialize one using the block 'Start chat conversation'."
                )

            msg = ""
            if not use_streaming:
                msg = conversation.complete(tools=tools)
                conversation += msg
                self._set_state(conversation_state_element, conversation)
            else:
                for chunk in conversation.stream_complete(tools=tools):
                    if chunk.get("content") is None:
                        chunk["content"] = ""
                    msg += chunk.get("content")
                    conversation += chunk
                    self._set_state(conversation_state_element, conversation)

            self.result = msg
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
