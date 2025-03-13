import pytest
from writer.blocks.addtostatelist import AddToStateList


def test_empty_list(session, runner):
    component = session.add_fake_component({"element": "my_list", "value": "my_value"})
    block = AddToStateList(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.session_state["my_list"] == ["my_value"]


def test_non_empty_list(session, runner):
    session.session_state["my_list"] = ["a"]
    component = session.add_fake_component({"element": "my_list", "value": "b"})
    block = AddToStateList(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.session_state["my_list"] == ["a", "b"]


def test_non_list_element(session, runner):
    session.session_state["my_element"] = "dog"
    component = session.add_fake_component({"element": "my_element", "value": "cat"})
    block = AddToStateList(component, runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"
