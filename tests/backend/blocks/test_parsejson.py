import json

import pytest
from writer.blocks.parsejson import ParseJSON
from writer.blueprints import BlueprintRunner


def test_valid_json(session, runner):
    component = session.add_fake_component({"plainText": '{ "hi": "yes" }'})
    block = ParseJSON(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result.get("hi") == "yes"


def test_invalid_json(session, runner):
    component = session.add_fake_component({"plainText": '{ "hi": yes }'})
    block = ParseJSON(component, runner, {})
    with pytest.raises(json.JSONDecodeError):
        block.run()

    assert block.outcome == "error"
