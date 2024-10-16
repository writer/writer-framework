from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock
import logging

logging.basicConfig(level=logging.DEBUG)

DEFAULT_MODEL = "palmyra-x-004"

function_tools_init = """{
  "estimate_customer_risk": {
    "parameters": {
      "time": {"type": "float", "description": "How many months they've been a customer for"},
      "transactions": {"type": "float", "description": "How many transactions they've performed"}
    }
  },
  "get_employee_info": {
    "parameters": {
      "id": {"type": "float", "description": "Id of the employee"},
    }
  }

}"""

def get_latitude_and_longitude(city):
    return "lat: 52.40692, lon: 16.92993"

def get_weather(latitude, longitude):
    return "37c"

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
                    "functionTools": {
                        "name": "Function tools",
                        "type": "Object",
                        "default": "{}",
                        "init": function_tools_init
                    }
                },
                "outs": {
                    "$dynamic": {
                        "field": "functionTools"
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
        print(f"Executing {outcome} with args {repr(args)}")
        if outcome == "$dynamic_get_employee_info":
            if args.get("employee_id") == 4:
                return "The name of the employee is Jackson Koko and they're 35 years old they're manager of internal affairs"
            else:
                return "The name of the employee is Williams Bernard and they're 40 years old they're manager of public relations"

    def run(self):
        try:
            import writer.ai

            conversation_state_element = self._get_field("conversationStateElement")
            temperature = float(self._get_field("temperature", False, "0.7"))
            model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)
            config = { "temperature": temperature, "model": model_id}
            function_tools_raw = self._get_field("functionTools", True)
            tools = []

            for tool_name, tool_raw in function_tools_raw.items():
                # callable = None
                # if tool_name == "get_weather":
                #     callable = get_weather
                # elif tool_name == "get_latitude_and_longitude":
                #     callable = get_latitude_and_longitude
                # else:
                #     raise ValueError("unrecognised")
                tool = writer.ai.FunctionTool(
                    type="function",
                    name=tool_name,
                    # callable=callable,
                    callable=lambda **args: self.run_branch(f"$dynamic_{tool_name}", **args),
                    parameters=tool_raw.get("parameters")
                )
                tr = repr(tool_raw.get("parameters"))
                print(f"appended {tool_name} {tr}")
                tools.append(tool)

            # print(repr(tools))

            conversation = self.evaluator.evaluate_expression(conversation_state_element, self.instance_path, self.execution_env)

            if not conversation:
                conversation = writer.ai.Conversation(config=config)
                self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)

            for chunk in conversation.stream_complete(tools=tools):
                if chunk.get("content") is None:
                    chunk["content"] = ""
                conversation += chunk
                self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)

            # msg = conversation.complete(tools=tools)
            # conversation += msg
            self.evaluator.set_state(conversation_state_element, self.instance_path, conversation, base_context=self.execution_env)            
            # self.result = msg
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

    