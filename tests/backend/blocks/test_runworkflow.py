import json

import pytest
from writer.blocks.runworkflow import RunWorkflow


def test_workflow_that_does_not_exist(session, runner):
    component = session.add_fake_component(
        {
            "workflowKey": "workflowThatDoesNotExist",
        }
    )
    block = RunWorkflow(component, runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"


def test_duplicator(session, runner):
    session.session_state["item_dict"] = json.loads('{"item": 23}')
    component = session.add_fake_component({"workflowKey": "duplicator", "payload": "@{item_dict}"})
    block = RunWorkflow(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == 46


def test_bad_workflow(session, runner):
    component = session.add_fake_component({"workflowKey": "boom"})
    block = RunWorkflow(component, runner, {})
    with pytest.raises(BaseException):
        block.run()
    assert block.outcome == "error"
