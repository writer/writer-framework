from writer.blocks.base_block import WorkflowBlock


def test_get_field(session, runner):
    session.globals = {
        "animal": "rat",
        "my_list": [1, 2, 3],
        "my_dict": { "a": "b" }
    }
    session.add_fake_component({
        "my_element": "{{animal}}",
        "my_list": "{{my_list}}",
        "my_dict": "{{my_dict}}"
    })
    block = WorkflowBlock("fake_id", runner, {})
    assert "rat" == block._get_field("my_element", as_object=False, default_value="elephant")
    assert [1, 2, 3] == block._get_field("my_list", as_object=True, default_value=None)
    assert "b" == block._get_field("my_dict", as_object=True, default_value=None).get("a")
    assert "ok" == block._get_field("ghost_field", as_object=False, default_value="ok")
    assert {} == block._get_field("ghost_field", as_object=True)
    assert "ok" == block._get_field("ghost_field_json", as_object=True, default_value={ "ok": "ok" }).get("ok")
    block.run()
    assert block.outcome is None


def test_set_state(session, runner):
    session.globals = {
        "animal": "rat",
        "my_list": [1,2,4],
        "my_dict": { "animal": "dog"},
        "unchanged": "unchanged"
    }
    block = WorkflowBlock("fake_id", runner, {})
    block._set_variable("animal", "cat")
    block._set_variable("animal", "bat")
    block._set_variable("my_list", [1, 2])
    block._set_variable("my_dict", { "animal": "cat"})
    block.run()
    assert session.globals["animal"] == "bat"
    assert session.globals["my_list"] == [1, 2]
    assert session.globals["my_dict"]["animal"] == "cat"
    assert session.globals["unchanged"] == "unchanged"
    assert block.outcome is None