import json

import pytest
import writer.ai
from writer.blocks.writernocodeapp import WriterNoCodeApp
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_app_content_generation():
    with patch('writer.ai.apps.generate_content') as mock_generate_content:
        def fake_generate_content(application_id, app_inputs):
            assert application_id == "123"

            name = app_inputs.get("name")
            animal = app_inputs.get("animal")

            return f"{name} the {animal}  "
        mock_generate_content.side_effect = fake_generate_content

        yield mock_generate_content

def test_call_nocode_app(mock_app_content_generation, session, runner):
    session.add_fake_component({
        "appId": "123",
        "appInputs": json.dumps({
            "name": "Koko",
            "animal": "Hamster"    
        })
    })
    block = WriterNoCodeApp("fake_id", runner, {})
    block.run()
    assert block.result == "Koko the Hamster"
    assert block.outcome == "success"


def test_call_nocode_app_missing_appid(mock_app_content_generation, session, runner):
    session.add_fake_component({
        "appId": "",
        "appInputs": json.dumps({
            "name": "Momo",
            "animal": "Squirrel"    
        })
    })
    block = WriterNoCodeApp("fake_id", runner, {})
    
    with pytest.raises(ValueError):
        block.run()