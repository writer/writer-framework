import pytest
from writer.blocks.runworkflow import RunWorkflow


def test_workflow_that_does_not_exist(session, runner):
    session.add_fake_component({
        "workflowKey": "workflowThatDoesNotExist",
    })
    block = RunWorkflow("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"

def test_duplicator(session, runner):
    session.add_fake_component({
        "workflowKey": "duplicator",
        "payload": '{"item": 23}'
    })
    block = RunWorkflow("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == 46

def test_bad_workflow(session, runner):
    session.add_fake_component({
        "workflowKey": "boom"
    })
    block = RunWorkflow("fake_id", runner, {})
    with pytest.raises(BaseException):
        block.run()
    assert block.outcome == "error"