import pytest
import writer.ai
from writer.blocks.writeraddchatmessage import WriterAddChatMessage


def test_add_chat_message(session, runner):
    session.session_state["convo"] = writer.ai.Conversation()
    session.add_fake_component({
        "conversationStateElement": "convo",
        "message": '{ "role": "user", "content": "hi" }'
    })
    block = WriterAddChatMessage("fake_id", runner, {})
    assert len(session.session_state["convo"].messages) == 0
    block.run()
    assert len(session.session_state["convo"].messages) == 1


def test_add_chat_message_bad_template(session, runner):
    session.session_state["convo"] = writer.ai.Conversation()
    session.add_fake_component({
        "conversationStateElement": "@{convo}", # Should be convo not @{convo}
        "message": '{ "role": "user", "content": "hi" }'
    })
    block = WriterAddChatMessage("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()


def test_add_chat_message_bad_message(session, runner):
    session.session_state["convo"] = writer.ai.Conversation()
    session.add_fake_component({
        "conversationStateElement": "convo", # Should be convo not @{convo}
        "message": '{ "x": "user", "content": "hi" }'
    })
    block = WriterAddChatMessage("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()


def test_add_chat_message_missing_convo(session, runner):
    session.session_state["convo"] = None
    session.add_fake_component({
        "conversationStateElement": "@{convo}",
        "message": '{ "role": "user", "content": "hi" }'
    })
    block = WriterAddChatMessage("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()


