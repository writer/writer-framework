import json

import pytest
import writer.ai
from writer.blocks.writerchatmanager import WriterChatManager


class MockConversation(writer.ai.Conversation):
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
            "description": "The color of the bat you're looking for.",
        }
        graph_tool = tools[1]
        assert graph_tool.get("type") == "graph"
        assert graph_tool.get("graph_ids") == [111, 112, 113]

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


def test_init_and_add_message(session, runner, fake_client):
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
            "message": '{"role": "user", "content": "hi"}',
            "generateReply": "no",
        }
    )
    block = WriterChatManager(component, runner, {})
    block.run()
    assert isinstance(session.session_state["convo"], writer.ai.Conversation)
    assert session.session_state["convo"].messages[0]["content"] == "hi"


def test_add_message_existing(session, runner, fake_client):
    session.session_state["convo"] = writer.ai.Conversation()
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
            "message": '{"role": "user", "content": "hi"}',
            "generateReply": "no",
        }
    )
    block = WriterChatManager(component, runner, {})
    block.run()
    assert len(session.session_state["convo"].messages) == 1


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
    block = WriterChatManager(component, runner, {})
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
    block = WriterChatManager(component, runner, {})
    block.run()
    assert conversation.messages[1].get("content") == "On the car's roof."
