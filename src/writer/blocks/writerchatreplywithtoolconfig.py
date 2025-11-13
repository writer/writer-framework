from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate, WriterConfigurationError

DEFAULT_MODEL = "palmyra-x5"

class WriterChatReplyWithToolConfig(WriterBlock):
    def __init__(self, component, runner, execution_environment):
        super().__init__(component, runner, execution_environment)

    @classmethod
    def register(cls, type: str):
        super(WriterChatReplyWithToolConfig, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Chat reply with tool config",
                    "description": "Initializes conversations, adds messages, and generates replies with tool configuration. NOTE: This is a temporary block with MCP tools mocked - tool calls use hardcoded mock responses instead of making actual HTTP requests.",
                    "category": "Writer",
                    "featureFlags": ["mcp"],
                    "fields": {
                        "conversationStateElement": {
                            "name": "Conversation Object",
                            "desc": "The variable that has your conversation object.",
                            "init": "chat",
                            "type": "Binding",
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
                            "init": '{ "role": "user", "content": "Hello" }',
                            "desc": "A message object. Content can be text string or array of objects for multimodal (text + images) with X5 model.",
                            "validator": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {
                                        "oneOf": [
                                            {"type": "string"},
                                            {
                                                "type": "array",
                                                "items": {
                                                    "oneOf": [
                                                        {
                                                            "type": "object",
                                                            "properties": {
                                                                "type": {
                                                                    "type": "string",
                                                                    "enum": ["text"],
                                                                },
                                                                "text": {"type": "string"},
                                                            },
                                                            "required": ["type", "text"],
                                                            "additionalProperties": False,
                                                        },
                                                        {
                                                            "type": "object",
                                                            "properties": {
                                                                "type": {
                                                                    "type": "string",
                                                                    "enum": ["image_url"],
                                                                },
                                                                "image_url": {
                                                                    "type": "object",
                                                                    "properties": {
                                                                        "url": {"type": "string"}
                                                                    },
                                                                    "required": ["url"],
                                                                    "additionalProperties": False,
                                                                },
                                                            },
                                                            "required": ["type", "image_url"],
                                                            "additionalProperties": False,
                                                        },
                                                    ]
                                                },
                                            },
                                        ]
                                    },
                                },
                                "additionalProperties": False,
                            },
                        },
                        "generateReply": {
                            "name": "Generate reply",
                            "type": "Boolean",
                            "default": "yes",
                            "desc": "If set to 'yes', the block will generate a reply from the model after adding the message. If set to 'no', it will only add the message to the conversation.",
                            "validator": {
                                "type": "boolean",
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
                                "maximum": 2,
                            },
                        },
                        "initMaxTokens": {
                            "name": "Initial max tokens",
                            "type": "Number",
                            "default": "1024",
                            "validator": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 16384,
                            },
                        },
                        "useStreaming": {
                            "name": "Use streaming",
                            "type": "Boolean",
                            "default": "yes",
                            "desc": "If set to 'yes', the block will stream the reply as it is generated. If set to 'no', it will wait for the entire reply to be generated before returning.",
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
                        "toolConfig": {
                            "name": "Tool config",
                            "type": "Object",
                            "default": "{}",
                            "desc": "Additional configuration for tools.",
                            "validator": {
                                "type": "object",
                                "additionalProperties": True,
                            },
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

    def _make_callable(self, tool_name: str, app_id: str, function_name: str):
        def callable(**args):
            import json
            import os
            import uuid

            import httpx

            from writer.core import get_session
            current_session = get_session()
            
            org_id = None
            user_id = None
            
            if current_session and current_session.headers:
                org_id = current_session.headers.get("x-organization-id")
                user_id = current_session.headers.get("x-user-id")
            
            if not org_id:
                org_id = os.getenv("WRITER_ORG_ID")
            
            if not org_id:
                raise ValueError("Organization ID not found. Set x-organization-id header or WRITER_ORG_ID environment variable.")
            
            if not user_id:
                user_id = os.getenv("WRITER_USER_ID", "1")
            
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                user_id = 1
            
            # url = f"http://localhost:8001/api/v1/namespaces/default/services/mcp-gateway:80/proxy/api/private/mcp-gateway/organization/1/mcp"
            # auth_token_header = "X-Auth-Token-Data-User-Individual"
            # auth_token_data = json.dumps({
            #     "userId": user_id,
            #     "authType": "Password",
            #     "confirmed": True
            # }).encode()
            #
            # headers = {
            #     "Content-Type": "application/json",
            #     auth_token_header: auth_token_data,
            # }
            #
            # jsonrpc_request = {
            #     "jsonrpc": "2.0",
            #     "id": str(uuid.uuid4()),
            #     "method": "tools/call",
            #     "params": {
            #         "name": function_name,
            #         "arguments": args
            #     }
            # }
            
            result = {
                'id': '2c22bbee-65eb-4471-bd05-4e1be617db74',
                'jsonrpc': '2.0',
                'result': {
                    'content': [{
                        'text': '[\n  45873434,\n  45873113,\n  45785840\n]',
                        'type': 'text'
                    }]
                }
            }
            
            # if "error" in result:
            #     error = result["error"]
            #     error_message = error.get("message", "Unknown MCP error") if isinstance(error, dict) else str(error)
            #     raise RuntimeError(f"MCP gateway API returned error: {error_message}")
            
            result_data = result.get("result", {})
            
            content_items = result_data.get("content", [])
            if content_items:
                return_value = []
                for item in content_items:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            return_value.append(item.get("text", ""))
                        elif item.get("type") == "image":
                            return_value.append(f"[Image: {item.get('mimeType', 'image/png')}]")
                        else:
                            return_value.append(str(item))
                    else:
                        return_value.append(str(item))
                return_value = "\n".join(return_value) if return_value else ""
            else:
                return_value = result_data.get("result") or result_data.get("content") or result_data
            
            return return_value

        return callable

    def run(self):
        try:
            import writer.ai

            conversation_state_element = self._get_field("conversationStateElement", required=True)
            message = self._get_field("message", as_json=True)
            generate_reply = self._get_field("generateReply", False, "yes") == "yes"

            system_prompt = self._get_field("systemPrompt", False, default_field_value=None)
            init_model_id = self._get_field("initModelId", False, default_field_value=DEFAULT_MODEL)
            try:
                init_temperature = float(self._get_field("initTemperature", False, "0.7"))
                init_max_tokens = int(self._get_field("initMaxTokens", False, "1024"))
            except ValueError as e:
                raise WriterConfigurationError(f"Invalid numeric value in configuration: {e}")
            use_streaming = self._get_field("useStreaming", False, "yes") == "yes"
            tools_raw = self._get_field("tools", True)

            tools = []

            conversation = self.evaluator.evaluate_expression(
                conversation_state_element, self.instance_path, self.execution_environment
            )

            if conversation is None:
                config = {
                    "temperature": init_temperature,
                    "model": init_model_id,
                    "max_tokens": init_max_tokens,
                }
                conversation = writer.ai.Conversation(
                    prompt_or_history=system_prompt, config=config
                )
                self._set_state(conversation_state_element, conversation)
            elif not isinstance(conversation, writer.ai.Conversation):
                raise WriterConfigurationError(
                    "The state element specified doesn't contain a Conversation."
                )

            if message not in (None, {}, ""):
                writer.ai.Conversation.validate_message(message)
                conversation += message
                self._set_state(conversation_state_element, conversation)

            if not generate_reply:
                self.result = ""
                self.outcome = "success"
                return

            for tool_name, tool_raw in tools_raw.items():
                if not isinstance(tool_raw, dict):
                    continue
                
                if not isinstance(tool_name, str) or not tool_name:
                    continue
                
                tool_type = tool_raw.get("type")
                if tool_type != "mcp":
                    continue
                
                try:
                    app_id = tool_raw.get("appId")
                    function_name = tool_raw.get("functionName")
                    
                    if not app_id:
                        continue
                    
                    if not function_name:
                        continue
                    
                    mcp_function = tool_raw.get("function", {})
                    description = mcp_function.get("description", "")
                    parameters = mcp_function.get("parameters", {})
                    
                    if parameters:
                        if not isinstance(parameters, dict):
                            continue
                        
                        if "properties" in parameters:
                            parameters = parameters.get("properties", {})
                        elif "type" not in parameters:
                            parameters = {
                                "type": "object",
                                "properties": parameters
                            }

                    tool = writer.ai.FunctionTool(
                        type="function",
                        name=tool_name,
                        description=description,
                        callable=self._make_callable(tool_name, app_id, function_name),
                        parameters=parameters or {},
                    )
                    tools.append(tool)

                except Exception:
                    continue
            
            if tools_raw and len(tools) == 0:
                raise WriterConfigurationError(
                    "No valid tools could be created from the provided tools configuration. "
                    "Please check that tools have the required fields and valid structure."
                )

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
            self.result = msg
            self._set_state(conversation_state_element, conversation)
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

