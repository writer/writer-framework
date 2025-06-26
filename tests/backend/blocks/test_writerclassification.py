import json

import pytest
import writer.ai
from writer.blocks.writerclassification import WriterClassification


def fake_conversation_complete(self, response_format, config):
    return {"role": "assistant", "content": "\"dog\""}


def test_classify(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr(writer.ai.Conversation, "complete", fake_conversation_complete)
    component = session.add_fake_component(
        {
            "text": "canine",
            "categories": json.dumps({"cat": "Pertaining to cats.", "dog": "Pertaining to dogs."}),
            "additionalContext": "It's about animal classification.",
        }
    )
    block = WriterClassification(component, runner, {})
    block.run()
    assert block.result == "dog"
    assert block.outcome == "category_dog"


def test_classify_invalid_category(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr(writer.ai.Conversation, "complete", fake_conversation_complete)
    categories = json.dumps(
        {
            "apple": "is an apple",
            "banana": "is a banana",
            "other!": "is another fruit"
        }
    )
    component = session.add_fake_component({"text": "fruits", "categories": categories})
    block = WriterClassification(component, runner, {})

    with pytest.raises(ValueError):
        block.run()


def test_classify_missing_categories(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr(writer.ai.Conversation, "complete", fake_conversation_complete)
    component = session.add_fake_component({"text": "canine", "categories": json.dumps({})})
    block = WriterClassification(component, runner, {})

    with pytest.raises(ValueError):
        block.run()
