import json

import pytest
from writer.blocks.parsejson import ParseJSON
from writer.workflows import WorkflowRunner


def test_valid_json(session, runner):
    session.add_fake_component({
        "plainText": '{ "hi": "yes" }'
    })
    block = ParseJSON("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result.get("hi") == "yes"

def test_invalid_json(session, runner):
    session.add_fake_component({
        "plainText": '{ "hi": yes }'
    })
    block = ParseJSON("fake_id", runner, {})
    with pytest.raises(json.JSONDecodeError):
        block.run()

    assert block.outcome == "error"