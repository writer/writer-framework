import pytest
from writer.ai import Conversation
from writer.blocks.writerinitchat import WriterInitChat


def test_init_chat_already_initialized(session, runner, fake_client):
    session.session_state["convo"] = Conversation()
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
        }
    )
    block = WriterInitChat(component, runner, {})
    block.run()
    assert block.outcome == "success"


def test_init_chat_already_initialized_with_rubbish(session, runner, fake_client):
    session.session_state["convo"] = (
        "-hello -hello there. This is a conversation but not the right kind."
    )
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
        }
    )
    block = WriterInitChat(component, runner, {})

    with pytest.raises(ValueError):
        block.run()


def test_init_chat_from_scratch(session, runner, fake_client):
    component = session.add_fake_component(
        {
            "conversationStateElement": "convo",
        }
    )
    block = WriterInitChat(component, runner, {})
    block.run()
    assert isinstance(session.session_state["convo"], Conversation)
    assert block.outcome == "success"
