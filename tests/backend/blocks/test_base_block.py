from writer.blocks.base_block import WorkflowBlock


def test_get_field(session, runner):
    session.state.animal = "rat"
    session.state.my_list = [1, 2, 3]
    session.state.my_dict = { "a": "b" }
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
    assert None == block._get_field("ghost_field", as_object=True)
    assert "ok" == block._get_field("ghost_field_json", as_object=True, default_value={ "ok": "ok" }).get("ok")
    block.run()
    assert block.outcome is None


def test_set_state(session, runner):
    session.state.animal = "rat"
    session.state.my_list = [1,2,4]
    session.state.my_dict = { "animal": "dog"}
    session.state.unchanged = "unchanged"
    block = WorkflowBlock("fake_id", runner, {})
    block._set_state("animal", "cat")
    block._set_state("animal", "bat")
    block._set_state("my_list", [1, 2])
    block._set_state("my_dict", { "animal": "cat"})
    block.run()
    assert session.state.animal == "bat"
    assert session.state.my_list == [1, 2]
    assert session.state.my_dict["animal"] == "cat"
    assert session.state.unchanged == "unchanged"
    assert block.outcome is None