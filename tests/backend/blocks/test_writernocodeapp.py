import json

import pytest
import writer.ai
from writer.blocks.writernocodeapp import WriterNoCodeApp


def fake_generate_content(application_id, app_inputs):
    assert application_id == "123"

    name = app_inputs.get("name")
    animal = app_inputs.get("animal")

    return f"{name} the {animal}  "


def test_call_nocode_app(monkeypatch, session, runner):
    monkeypatch.setattr("writer.ai.apps.generate_content", fake_generate_content)
    component = session.add_fake_component(
        {"appId": "123", "appInputs": json.dumps({"name": "Koko", "animal": "Hamster"})}
    )
    block = WriterNoCodeApp(component, runner, {})
    block.run()
    assert block.result == "Koko the Hamster"
    assert block.outcome == "success"


def test_call_nocode_app_missing_appid(monkeypatch, session, runner):
    monkeypatch.setattr("writer.ai.apps.generate_content", fake_generate_content)
    component = session.add_fake_component(
        {"appId": "", "appInputs": json.dumps({"name": "Momo", "animal": "Squirrel"})}
    )
    block = WriterNoCodeApp(component, runner, {})

    with pytest.raises(ValueError):
        block.run()
