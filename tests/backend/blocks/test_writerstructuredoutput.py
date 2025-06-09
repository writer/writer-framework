import json
from unittest.mock import MagicMock

import pytest
import writer.ai
from writer.blocks.writerstructuredoutput import WriterStructuredOutput


def fake_conversation_complete(self, response_format, config):
    if response_format["json_schema"]["schema"]:
        return {"role": "assistant", "content": "{\"key\": \"value\"}"}
    return {"role": "assistant", "content": None}


def test_successful_run(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr(writer.ai.Conversation, "complete", fake_conversation_complete)
    component = session.add_fake_component(
        {
            "prompt": "Describe an animal.",
            "jsonSchema": "{\"type\": \"object\", \"properties\": {\"key\": {\"type\": \"string\"}}}",
            "modelId": "palmyra-x4",
        }
    )
    block = WriterStructuredOutput(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == {"key": "value"}


def test_error_on_no_content(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr(writer.ai.Conversation, "complete", fake_conversation_complete)
    component = session.add_fake_component(
        {
            "prompt": "Describe an animal.",
            "jsonSchema": "{}",  # bad schema definition
            "modelId": "palmyra-x4",
        }
    )
    block = WriterStructuredOutput(component, runner, {})
    with pytest.raises(RuntimeError, match="No content returned.*"):
        block.run()
    assert block.outcome == "error"


def test_json_decode_error(monkeypatch, session, runner, fake_client):
    def invalid_json_complete(self, response_format, config):
        return {"role": "assistant", "content": "{key: value}"}  # Invalid JSON
    monkeypatch.setattr(writer.ai.Conversation, "complete", invalid_json_complete)
    component = session.add_fake_component(
        {
            "prompt": "Describe an animal.",
            "jsonSchema": "{}",
            "modelId": "palmyra-x4",
        }
    )
    block = WriterStructuredOutput(component, runner, {})
    with pytest.raises(RuntimeError, match="Failed to decode JSON content.*"):
        block.run()
    assert block.outcome == "error"
