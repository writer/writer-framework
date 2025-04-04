import json

import pytest
from writer.blocks.runblueprint import RunBlueprint


def test_blueprint_that_does_not_exist(session, runner):
    component = session.add_fake_component(
        {
            "blueprintKey": "blueprintThatDoesNotExist",
        }
    )
    block = RunBlueprint(component, runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"


def test_duplicator(session, runner):
    session.session_state["item_dict"] = json.loads('{"item": 23}')
    component = session.add_fake_component({"blueprintKey": "duplicator", "payload": "@{item_dict}"})
    block = RunBlueprint(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == 46


def test_bad_blueprint(session, runner):
    component = session.add_fake_component({"blueprintKey": "boom"})
    block = RunBlueprint(component, runner, {})
    with pytest.raises(BaseException):
        block.run()
    assert block.outcome == "error"
