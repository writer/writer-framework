import pytest
from writer.blocks.returnvalue import ReturnValue
from writer.core import WriterState


def test_basic_return(session, runner):
    session.session_state = WriterState({
        "animal": "marmot",
    })
    session.add_fake_component({
        "value": "@{animal}"
    })
    block = ReturnValue("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"    
    assert block.result == block.return_value
    assert block.return_value == "marmot"

def test_empty_return(session, runner):
    session.session_state = WriterState({
        "animal": None,
    })
    session.add_fake_component({
        "value": "@{animal}"
    })
    block = ReturnValue("fake_id", runner, {})
    
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"