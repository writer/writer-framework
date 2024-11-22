import pytest
from writer.blocks.setstate import SetState
from writer.workflows import WorkflowRunner


def test_basic_assignment(session):
    session.add_fake_component({
        "element": "my_element",
        "value": "my_value"
    })
    runner = WorkflowRunner(session)
    block = SetState("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.session_state["my_element"] == "my_value"

def test_nested_assignment_without_parent(session):
    session.add_fake_component({
        "element": "parent_element.my_element",
        "value": "my_value"
    })
    runner = WorkflowRunner(session)
    block = SetState("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"

def test_nested_assignment_with_parent(session, runner):
    session.session_state["parent_element"] = {
        "sibling_element": "yes"
    }
    session.add_fake_component({
        "element": "parent_element.my_element",
        "value": "my_value"
    })
    block = SetState("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.session_state["parent_element"]["sibling_element"] == "yes"
    assert session.session_state["parent_element"]["my_element"] == "my_value"

def test_assignment_with_empty_element(session):
    session.add_fake_component({
        "element": "",
        "value": "my_value"
    })
    runner = WorkflowRunner(session)
    block = SetState("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"

def test_assignment_with_empty_value(session):
    session.add_fake_component({
        "element": "my_element",
        "value": ""
    })
    runner = WorkflowRunner(session)
    block = SetState("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"