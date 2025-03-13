import pytest
from writer.blocks.foreach import ForEach


def test_basic_list(session, runner):
    component = session.add_fake_component({"workflowKey": "workflow1", "items": "[2, 2, 2, 2]"})
    block = ForEach(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == [1, 1, 1, 1]


def test_list_of_dict(session, runner):
    component = session.add_fake_component({"workflowKey": "workflowDict", "items": "[2, 2]"})
    block = ForEach(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == [{"a": "b"}, {"a": "b"}]


def test_basic_dict(session, runner):
    component = session.add_fake_component(
        {"workflowKey": "workflow1", "items": '{"a": "zzz", "b": "zzz"}'}
    )
    block = ForEach(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == {"a": 1, "b": 1}


def test_workflow_that_does_not_exist(session, runner):
    component = session.add_fake_component(
        {"workflowKey": "workflowThatDoesNotExist", "items": '{"a": "zzz", "b": "zzz"}'}
    )
    block = ForEach(component, runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"


def test_duplicator(session, runner):
    component = session.add_fake_component(
        {"workflowKey": "duplicator", "items": '{"a": 1, "b": 2, "c": 11}'}
    )
    block = ForEach(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result == {"a": 2, "b": 4, "c": 22}
