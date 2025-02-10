import pytest
from writer.blocks.addtostatelist import AddToStateList
from writer.workflows import WorkflowRunner


def test_empty_list(session, runner):
    session.add_fake_component({
        "element": "my_list",
        "value": "my_value"
    })
    block = AddToStateList("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.state.my_list == ["my_value"]

def test_non_empty_list(session, runner):
    session.state.my_list = ["a"]
    session.add_fake_component({
        "element": "my_list",
        "value": "b"
    })
    block = AddToStateList("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert session.state.my_list == ["a", "b"]


def test_non_list_element(session, runner):
    session.state.my_element = "dog"
    session.add_fake_component({
        "element": "my_element",
        "value": "cat"
    })
    block = AddToStateList("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"