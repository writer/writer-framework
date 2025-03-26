import pytest
from writer.blocks.setstate import SetState
from writer.workflows import WorkflowRunner


def test_basic_assignment(session):
    component = session.add_fake_component({"element": "my_element", "value": "my_value"})
    runner = WorkflowRunner(session)
    block = SetState(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.session_state["my_element"] == "my_value"


def test_json_assignment(session):
    component = session.add_fake_component(
        {"element": "my_element", "value": '{ "dog": true, "cat": 0 }', "valueType": "JSON"}
    )
    runner = WorkflowRunner(session)
    block = SetState(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.session_state["my_element"]["dog"] is True
    assert session.session_state["my_element"]["cat"] == 0


def test_nested_assignment_without_parent(session):
    component = session.add_fake_component(
        {"element": "parent_element.my_element", "value": "my_value"}
    )
    runner = WorkflowRunner(session)
    block = SetState(component, runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"


def test_nested_assignment_with_parent(session, runner):
    session.session_state["parent_element"] = {"sibling_element": "yes"}
    component = session.add_fake_component(
        {"element": "parent_element.my_element", "value": "my_value"}
    )
    block = SetState(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.session_state["parent_element"]["sibling_element"] == "yes"
    assert session.session_state["parent_element"]["my_element"] == "my_value"


def test_assignment_with_empty_element(session):
    component = session.add_fake_component({"element": "", "value": "my_value"})
    runner = WorkflowRunner(session)
    block = SetState(component, runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"


def test_assignment_with_empty_value(session):
    component = session.add_fake_component({"element": "my_element", "value": ""})
    runner = WorkflowRunner(session)
    block = SetState(component, runner, {})
    block.run()
    assert block.outcome == "success"
