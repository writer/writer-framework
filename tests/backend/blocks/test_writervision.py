import json

import pytest
from writer.blocks.writervision import WriterVision
from writer.ss_types import WriterConfigurationError


class FakeVisionClient:
    class FakeVisionResource:
        def analyze(self, *, variables, **_):
            if variables:
                return FakeResponse({"analysis": "mock result"})
            else:
                return None
    vision = FakeVisionResource()


class FakeResponse:
    def __init__(self, data):
        self.data = data


@pytest.fixture
def valid_images():
    return [
        {"name": "cat", "file_id": "file123"},
        {"name": "dog", "file_id": "file456"}
    ]


@pytest.fixture
def session_with_component(session, valid_images):
    def _create_component(prompt):
        return session.add_fake_component({
            "prompt": prompt,
            "images": json.dumps(valid_images)
        })
    return _create_component


def test_successful_run(monkeypatch, session_with_component, runner, fake_client):
    monkeypatch.setattr("writer.blocks.writervision.WriterVision.writer_sdk_client", FakeVisionClient())
    component = session_with_component("Analyze {{cat}} and {{dog}}")
    block = WriterVision(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == {"analysis": "mock result"}


def test_empty_prompt_error(session_with_component, runner, fake_client):
    component = session_with_component("")
    block = WriterVision(component, runner, {})
    with pytest.raises(ValueError, match="Prompt cannot be empty.*"):
        block.run()
    assert block.outcome == "error"


def test_missing_placeholder_error(session_with_component, runner, fake_client):
    component = session_with_component("Just analyze the animals")
    block = WriterVision(component, runner, {})
    with pytest.raises(ValueError, match="Prompt must include image names.*"):
        block.run()
    assert block.outcome == "error"


def test_missing_image_placeholder_in_prompt(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.blocks.writervision.WriterVision.writer_sdk_client", FakeVisionClient())
    images = [{"name": "cat", "file_id": "file123"}]
    component = session.add_fake_component({
        "prompt": "Analyze {{dog}}",  # but only "cat" provided
        "images": json.dumps(images)
    })
    block = WriterVision(component, runner, {})
    with pytest.raises(ValueError, match="Image name 'cat' not found.*"):
        block.run()
    assert block.outcome == "error"


def test_empty_images_list(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.blocks.writervision.WriterVision.writer_sdk_client", FakeVisionClient())
    component = session.add_fake_component({
        "prompt": "Analyze {{cat}}",
        "images": json.dumps([])
    })
    block = WriterVision(component, runner, {})
    with pytest.raises(ValueError, match="Images list cannot be empty.*"):
        block.run()
    assert block.outcome == "error"


def test_invalid_images_type(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.blocks.writervision.WriterVision.writer_sdk_client", FakeVisionClient())
    component = session.add_fake_component({
        "prompt": "Analyze {{cat}}",
        "images": 'not_a_list'
    })
    block = WriterVision(component, runner, {})
    with pytest.raises(WriterConfigurationError, match="Error decoding JSON.*"):
        block.run()
    assert block.outcome == "error"


def test_invalid_image_dict(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.blocks.writervision.WriterVision.writer_sdk_client", FakeVisionClient())
    component = session.add_fake_component({
        "prompt": "Analyze {{cat}}",
        "images": json.dumps([{"file_id": "file123"}])  # missing name field
    })
    block = WriterVision(component, runner, {})
    with pytest.raises(ValueError, match="Invalid image definition.*"):
        block.run()
    assert block.outcome == "error"
