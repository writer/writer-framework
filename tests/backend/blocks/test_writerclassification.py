import json

import pytest
import writer.ai
from writer.blocks.writerclassification import WriterClassification


def fake_complete(prompt, config):
    additional_context = "It's about animal classification."
    if "canine" in prompt and additional_context in prompt:
        return "dog"
    if "feline" in prompt and additional_context in prompt:
        return "cat"
    return "other"


def test_classify(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.complete", fake_complete)
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


def test_classify_missing_categories(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.complete", fake_complete)
    component = session.add_fake_component({"text": "canine", "categories": json.dumps({})})
    block = WriterClassification(component, runner, {})

    with pytest.raises(ValueError):
        block.run()
