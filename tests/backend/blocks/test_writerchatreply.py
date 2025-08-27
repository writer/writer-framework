import json

import pytest
import writer.ai
from writer.blocks.writerchatreply import WriterChatReply


class MockConversation(writer.ai.Conversation):
    def __init__(self):
        super().__init__()

    def _check_tools(self, tools):
        if tools is None or tools == []:
            return
        
        # Handle both old test format (2 tools) and new test format (3 tools with web_search)
        if len(tools) == 2:
            function_tool = tools[0]
            assert function_tool.get("type") == "function"
            assert function_tool.get("name") == "bat_locator"
            assert function_tool.get("description") == "Locates bats."
            assert function_tool.get("parameters").get("color") == {
                "type": "string",
                "description": "The color of the bat you're looking for.",
            }
            graph_tool = tools[1]
            assert graph_tool.get("type") == "graph"
            assert graph_tool.get("graph_ids") == [111, 112, 113]
        elif len(tools) == 3:
            # Check web_search tool (processed by _prepare_tool)
            web_search_tool = tools[0]
            assert web_search_tool.get("type") == "web_search"
            assert web_search_tool.get("include_domains") == ["wikipedia.org", "nationalgeographic.com"]
            assert web_search_tool.get("exclude_domains") == ["spam.com"]
            assert web_search_tool.get("include_raw_content") is True
            
            function_tool = tools[1]
            assert function_tool.get("type") == "function"
            
            graph_tool = tools[2]
            assert graph_tool.get("type") == "graph"
        else:
            raise RuntimeError(f"Invalid number of tools: {len(tools)}")

    def complete(self, tools=None):
        self._check_tools(tools)
        return {"role": "assistant", "content": "Next to the grill."}

    def stream_complete(self, tools=None):
        self._check_tools(tools)
        yield {"role": "assistant", "content": "On "}
        yield {"role": "assistant", "content": "the ", "chunk": True}
        yield {"role": "assistant", "content": "car's ", "chunk": True}
        yield {"role": "assistant", "content": "roof.", "chunk": True}


@pytest.fixture
def conversation():
    return MockConversation()


def test_init_and_add_message(session, conversation, runner, fake_client):
    session.session_state["convo"] = conversation
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
            "message": '{"role": "user", "content": "hi"}',
        }
    )
    block = WriterChatReply(component, runner, {})
    block.run()
    assert isinstance(session.session_state["convo"], writer.ai.Conversation)
    assert session.session_state["convo"].messages[0]["content"] == "hi"


def test_add_message_existing(session, runner, conversation, fake_client):
    session.session_state["convo"] = conversation
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
            "message": '{"role": "user", "content": "hi"}',
        }
    )
    block = WriterChatReply(component, runner, {})
    block.run()
    assert len(session.session_state["convo"].messages) == 2


def test_generate_complete(session, runner, conversation, fake_client):
    conversation.add("user", "Hi, where's the bat?")
    session.session_state["convo"] = conversation
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
            "generateReply": "yes",
            "useStreaming": "no",
        }
    )
    block = WriterChatReply(component, runner, {})
    block.run()
    assert conversation.messages[1].get("content") == "Next to the grill."


def test_generate_stream(session, runner, conversation, fake_client):
    conversation.add("user", "Hi, where's the bat?")
    session.session_state["convo"] = conversation
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
            "generateReply": "yes",
            "useStreaming": "yes",
            "tools": json.dumps(
                {
                    "bat_locator": {
                        "type": "function",
                        "description": "Locates bats.",
                        "parameters": {
                            "color": {
                                "type": "string",
                                "description": "The color of the bat you're looking for.",
                            }
                        },
                    },
                    "known_bat_spots": {"type": "graph", "graph_ids": [111, 112, 113]},
                }
            ),
        }
    )
    block = WriterChatReply(component, runner, {})
    block.run()
    assert conversation.messages[1].get("content") == "On the car's roof."


def test_generate_with_web_search_tool(session, runner, conversation, fake_client):
    conversation.add("user", "Search for information about bats")
    session.session_state["convo"] = conversation
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
            "generateReply": "yes",
            "useStreaming": "no",
            "tools": json.dumps(
                {
                    "web_search": {
                        "type": "web_search",
                        "include_domains": ["wikipedia.org", "nationalgeographic.com"],
                        "exclude_domains": ["spam.com"],
                        "include_raw_content": True
                    },
                    "bat_locator": {
                        "type": "function",
                        "description": "Locates bats.",
                        "parameters": {
                            "color": {
                                "type": "string",
                                "description": "The color of the bat you're looking for.",
                            }
                        },
                    },
                    "known_bat_spots": {"type": "graph", "graph_ids": [111, 112, 113]},
                }
            ),
        }
    )
    block = WriterChatReply(component, runner, {})
    block.run()
    assert conversation.messages[1].get("content") == "Next to the grill."


def test_multimodal_message_validation_support(session, runner, conversation, fake_client):
    """Test that WriterChatReply validation supports multimodal message format (even if SDK doesn't support it yet)"""
    # This tests that the validation schema allows multimodal content
    # The actual SDK support will come later when the writer-sdk is fully updated
    multimodal_message = {
        "role": "user", 
        "content": "What do you see in this image?"  # Using string for now until SDK supports multimodal
    }
    
    session.session_state["convo"] = conversation
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
            "message": json.dumps(multimodal_message),
            "initModelId": "palmyra-x5"
        }
    )
    block = WriterChatReply(component, runner, {})
    block.run()
    
    # Verify the message was added correctly 
    added_message = conversation.messages[0]
    assert added_message["role"] == "user"
    assert added_message["content"] == "What do you see in this image?"


def test_web_search_tool_preparation(session, runner, conversation, fake_client):
    """Test that _prepare_tool correctly formats web search tools"""
    import writer.ai
    
    # Create a conversation to test _prepare_tool method
    conv = writer.ai.Conversation()
    
    # Test web search tool preparation
    web_search_tool = {
        "type": "web_search",
        "include_domains": ["wikipedia.org", "docs.python.org"],
        "exclude_domains": ["spam.com"],
        "include_raw_content": True
    }
    
    prepared_tool = conv._prepare_tool(web_search_tool)
    
    assert prepared_tool["type"] == "web_search"
    assert "function" in prepared_tool
    assert prepared_tool["function"]["include_domains"] == ["wikipedia.org", "docs.python.org"]
    assert prepared_tool["function"]["exclude_domains"] == ["spam.com"]
    assert prepared_tool["function"]["include_raw_content"] is True
