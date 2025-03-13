from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class WriterToolCalling(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterToolCalling, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="workflows_node",
                writer={
                    "name": "Tool calling",
                    "description": "Handles tool calling without the need for a chat.",
                    "category": "Writer",
                    "fields": {
                        "prompt": {"name": "Prompt", "type": "Text", "control": "Textarea"},
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
        import time

        def callable(**args):
            expanded_execution_environment = self.execution_environment | args
            return_value = repr(
                self.runner.run_branch(
                    self.component.id,
                    f"tools_{tool_name}",
                    expanded_execution_environment,
                    f"Workflow branch execution (tool {tool_name})",
                )
            )
            if return_value is None:
                self.outcome = "error"
                raise ValueError(
                    f'No value has been returned for the outcome branch "{tool_name}". Use the block "Return value" to specify one.'
                )
            self.execution_environment.get("trace").append(
                {
                    "type": "functionCall",
                    "time": time.time(),
                    "name": tool_name,
                    "parameters": args,
                }
            )
            return return_value

        return callable

    def _get_tools(self):
        import writer.ai

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

        def reasoning_callable(**kwargs):
            import time

            thought = kwargs.get("thought")
            action = kwargs.get("action")

            message = f"💡 Thought: {thought}. ⚡️ Action: {action}."
            self.execution_environment.get("trace").append(
                {"type": "reasoning", "time": time.time(), "thought": thought, "action": action}
            )
            self.runner.session.session_state.add_log_entry(
                "info", "Reasoning...", message, id="reasoning"
            )

        reasoning_tool = {
            "type": "function",
            "name": "disclose_reasoning",
            "description": "Use this function to disclose your reasoning.",
            "callable": reasoning_callable,
            "parameters": {
                "thought": {
                    "type": "string",
                    "description": "A look into your internal reasoning.",
                },
                "action": {
                    "type": "string",
                    "description": "A summary of the actions you took and why.",
                },
            },
        }

        tools.append(reasoning_tool)

        return tools

    def run(self):
        import writer.ai

        try:
            prompt = self._get_field("prompt")
            conversation = writer.ai.Conversation()
            tools = self._get_tools()

            for i in range(10):
                conversation += {"role": "user", "content": prompt}
                config = {"model": "palmyra-x5"}
                msg = conversation.complete(tools=tools, config=config)
                conversation += msg
                if "<DONE>" in msg.get("content"):
                    break

            self.result = msg.get("content")
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
