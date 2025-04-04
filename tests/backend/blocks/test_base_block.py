from writer.blocks.base_block import BlueprintBlock
from writer.core import WriterState


def test_get_field(session, runner):
    session.session_state = WriterState(
        {"animal": "rat", "my_list": "[1,2,3]", "my_dict": '{ "a": "b" }'}
    )
    component = session.add_fake_component(
        {"my_element": "@{animal}", "my_list": "@{my_list}", "my_dict": "@{my_dict}"}
    )
    block = BlueprintBlock(component, runner, {})
    assert "rat" == block._get_field("my_element", as_json=False, default_field_value="elephant")
    assert [1, 2, 3] == block._get_field("my_list", as_json=True, default_field_value=None)
    assert "b" == block._get_field("my_dict", as_json=True, default_field_value=None).get("a")
    assert "ok" == block._get_field("ghost_field", as_json=False, default_field_value="ok")
    assert {} == block._get_field("ghost_field", as_json=True)
    assert "ok" == block._get_field(
        "ghost_field_json", as_json=True, default_field_value='{ "ok": "ok" }'
    ).get("ok")
    block.run()
    assert block.outcome is None


def test_set_state(session, runner):
    session.session_state = WriterState(
        {
            "animal": "rat",
            "my_list": [1, 2, 4],
            "my_dict": {"animal": "dog"},
            "unchanged": "unchanged",
        }
    )
    component = session.add_fake_component(
        {"my_element": "@{animal}", "my_list": "@{my_list}", "my_dict": "@{my_dict}"}
    )
    block = BlueprintBlock(component, runner, {})
    block._set_state("animal", "cat")
    block._set_state("animal", "bat")
    block._set_state("my_list", [1, 2])
    block._set_state("my_dict", {"animal": "cat"})
    block.run()
    assert session.session_state["animal"] == "bat"
    assert session.session_state["my_list"] == [1, 2]
    assert session.session_state["my_dict"]["animal"] == "cat"
    assert session.session_state["unchanged"] == "unchanged"
    assert block.outcome is None
