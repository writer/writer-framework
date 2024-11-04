import writer.workflows
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

    def run_branch(self, outcome: str, **args):
        branch_root_nodes = self._get_nodes_at_outcome(outcome)
        return_value = None
        for branch_root_node in branch_root_nodes:
            branch_nodes = writer.workflows.get_branch_nodes(branch_root_node.id)

            terminal_nodes = writer.workflows.get_terminal_nodes(branch_nodes)

            for terminal_node in terminal_nodes:
                tool = writer.workflows.run_node(terminal_node, branch_nodes, self.execution, self.session, self.execution_env | args)
                if tool and tool.return_value:
                    return_value = tool.return_value

        return repr(return_value)

    def _make_callable(self, tool_name: str):
        def callable(**args):
            return self.run_branch(f"tools_{tool_name}", **args)
        return callable

    def run(self):
        try:
            import writer.ai

            conversation_state_element = self._get_field("conversationStateElement")
            temperature = float(self._get_field("temperature", False, "0.7"))
            model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)
            config = { "temperature": temperature, "model": model_id}
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

            conversation = self.evaluator.evaluate_expression(conversation_state_element, self.instance_path, self.execution_env)

            if not conversation:
                conversation = writer.ai.Conversation(config=config)
                self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)

            # msg = ""
            # for chunk in conversation.stream_complete(tools=tools):
            #     if chunk.get("content") is None:
            #         chunk["content"] = ""
            #     msg += chunk.get("content")
            #     conversation += chunk
            #     self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)

            msg = None
            try:
                msg = conversation.complete(tools=tools)
            except BaseException as e:
                msg = {
                    "role": "assistant",
                    "content": "Couldn't process the request."
                }
                raise e
            finally:
                conversation += msg

            self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)            
            self.result = msg
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

    