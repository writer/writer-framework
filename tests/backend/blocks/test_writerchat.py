import json

import pytest
from writer.ai import Conversation
from writer.blocks.writerchat import WriterChat


class MockConversation(Conversation):

    def __init__(self):
        super().__init__()

    def _check_tools(self, tools):
        if tools is None or tools == []:
            return
        if len(tools) != 2:
            raise RuntimeError("Invalid number of tools.")
        function_tool = tools[0]
        
        assert function_tool.get("type") == "function"
        assert function_tool.get("name") == "bat_locator"
        assert function_tool.get("description") == "Locates bats."
        assert function_tool.get("parameters").get("color") == {
            "type": "string",
            "description": "The color of the bat you're looking for."
        }
        graph_tool = tools[1]
        assert graph_tool.get("type") == "graph"
        assert graph_tool.get("graph_ids") == [111, 112, 113]

    def complete(self, tools=None):
        self._check_tools(tools)
        return {
            "role": "assistant",
            "content": "Next to the grill."
        }
    
    def stream_complete(self, tools=None):
        self._check_tools(tools)
        yield {
            "role": "assistant",
            "content": "On "
        }
        yield {
            "role": "assistant",
            "content": "the ",
            "chunk": True
        }
        yield {
            "role": "assistant",
            "content": "car's ",
            "chunk": True
        }
        yield {
            "role": "assistant",
            "content": "roof.",
            "chunk": True
        }

@pytest.fixture
def conversation():
    return MockConversation()

def test_chat_complete(session, runner, conversation):
    conversation.add("user", "Hi, where's the bat?")
    session.state.convo = conversation
    session.add_fake_component({
        "conversationStateElement": "convo",
        "useStreaming": "no"
    })
    block = WriterChat("fake_id", runner, {})
    block.run()
    assert conversation.messages[1].get("content") == "Next to the grill."


def test_chat_stream_complete(session, runner, conversation):
    conversation.add("user", "Hi, where's the bat?")
    session.state.convo = conversation
    session.add_fake_component({
        "conversationStateElement": "convo"
        # streaming should be default
    })
    block = WriterChat("fake_id", runner, {})
    block.run()
    assert conversation.messages[1].get("content") == "On the car's roof."


def test_chat_stream_complete_with_tools(session, runner, conversation):
    conversation.add("user", "Hi, where's the bat?")
    session.state.convo = conversation
    session.add_fake_component({
        "conversationStateElement": "convo",
        "tools": json.dumps({
            "bat_locator": {
                "type": "function",
                "description": "Locates bats.",
                "parameters": {
                    "color": {
                        "type": "string",
                        "description": "The color of the bat you're looking for."
                    }
                }
            },
            "known_bat_spots": {
                "type": "graph",
                "graph_ids": [111, 112, 113]
            }
        }),
        "useStreaming": "yes"
    })
    block = WriterChat("fake_id", runner, {})
    block.run()
    assert conversation.messages[1].get("content") == "On the car's roof."


def test_chat_stream_complete_no_conversation(session, runner, conversation):
    conversation.add("user", "Hi, where's the bat?")
    session.state.convo = "not_a_conversation"
    session.add_fake_component({
        "conversationStateElement": "convo"
        # streaming should be default
    })
    block = WriterChat("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()