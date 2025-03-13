import pytest
from writer.blocks.foreach import ForEach


def test_basic_list(session, runner):
    component = session.add_fake_component({"items": "[2226, 2223]"})
    block = ForEach(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert 4 == block.result[0]
    assert 4 == block.result[1]


def test_basic_dict(session, runner):
    component = session.add_fake_component({"items": '{"a": "zzz", "b": "fff"}'})
    block = ForEach(component, runner, {})
    block.run()
    assert block.outcome == "success"
    assert 4 == block.result.get("a")
    assert 4 == block.result.get("b")
