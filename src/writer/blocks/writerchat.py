import writer.workflows
from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows import WorkflowBlock


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
                    "useStreaming": {
                        "name": "Use streaming",
                        "type": "Text",
                        "default": "yes",
                        "options": {
                            "yes": "Yes",
                            "no": "No"
                        }
                    },
                    "tools": {
                        "name": "Tools",
                        "type": "Tools",
                        "default": "{}",
                        "category": "Tools"
                    }
                },
                "outs": {
                    "tools": {
                        "name": "Tools",
                        "field": "tools",
                        "description": "Run associated tools.",
                        "style": "dynamic"
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
            }
        ))

    def _make_callable(self, tool_name: str):
        def callable(**args):
            expanded_execution_environment = self.execution_environment | args
            return_value = self.run_branch(self.component.id, f"tools_{tool_name}", expanded_execution_environment)

            if return_value is None:
                self.result = f'No value has been returned for the outcome branch "{tool_name}". Use the block "Return value" to specify one.'
                self.outcome = "error"
                raise ValueError(f'No value has been returned for the outcome branch "{tool_name}".')

            return return_value
        return callable

    def run(self):
        try:
            import writer.ai

            conversation_state_element = self._get_field("conversationStateElement")
            use_streaming = self._get_field("useStreaming", False, "yes") == "yes"
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
                        parameters=tool_raw.get("parameters")
                    )
                elif tool_type == "graph":
                    tool = {
                        "type": "graph",
                        "graph_ids": tool_raw.get("graph_ids")
                    }
                else:
                    continue
                tools.append(tool)

            conversation = self.runner.evaluator.evaluate_expression(conversation_state_element, self.instance_path, self.execution_environment)

            if conversation is None or not isinstance(conversation, writer.ai.Conversation):
                self.result = "The state element specified doesn't contain a conversation. Initialize one using the block 'Initialize chat'."
                self.outcome = "error"
                return

            try:
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
            except BaseException:
                msg = {
                    "role": "assistant",
                    "content": "Couldn't process the request."
                }
                conversation += msg
                self._set_state(conversation_state_element, conversation)
            
            if not self.outcome:
                self.result = msg
                self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e