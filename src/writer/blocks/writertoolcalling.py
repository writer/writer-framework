from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate

DEFAULT_MODEL = "palmyra-x-004"

class WriterToolCalling(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterToolCalling, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Tool calling",
                    "description": "Connects the Agent to external tools to complete tasks it cannot handle directly.",
                    "category": "Writer",
                    "fields": {
                        "prompt": {"name": "Prompt", "type": "Text", "control": "Textarea", "desc": "The task that needs to be carried out."},
                        "modelId": {
                            "name": "Model id",
                            "type": "Text",
                            "default": DEFAULT_MODEL
                        },
                        "maxIterations": {
                            "name": "Max iterations",
                            "type": "Number",
                            "default": 10
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
        import time

        def callable(**args):
            expanded_execution_environment = self.execution_environment | args
            return_value = repr(
                self.runner.run_branch(
                    self.component.id,
                    f"tools_{tool_name}",
                    expanded_execution_environment,
                    f"Blueprint branch execution (tool {tool_name})",
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
            status = kwargs.get("status")

            self.execution_environment.get("trace").append({
                "type": "reasoning",
                "time": time.time(),
                "thought": thought,
                "action": action
            })
            if status == "DONE":
                self.is_complete = True
                

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
                "status": {
                    "type": "string",
                    "description": "Set to DONE if you consider the task complete. Set to INCOMPLETE if you wish to keep iterating."
                }
            },
        }

        tools.append(reasoning_tool)

        return tools

    def _get_react_prompt(self, base_prompt: str):
        return f"""
        You're a ReAct agent.
        Disclose your reasoning using the provided function.
        
        Task: {base_prompt}
        """


    def run(self):
        import writer.ai
        self.is_complete = False

        try:
            prompt = self._get_field("prompt")
            model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)
            max_iterations = int(self._get_field("maxIterations", False, "10"))
            conversation = writer.ai.Conversation()
            tools = self._get_tools()

            for i in range(max_iterations):
                conversation += {
                    "role": "user",
                    "content": self._get_react_prompt(prompt)
                }
                config = {"model": model_id}
                msg = conversation.complete(tools=tools, config=config)
                conversation += msg
                if self.is_complete:
                    break

            self.result = msg.get("content")
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
