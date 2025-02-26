import sys
import types

import pytest
from writer.blocks.code import CodeBlock


def test_run_code(session, runner, monkeypatch):
    fake_module = types.ModuleType("fake_writeruserapp")
    fake_module.my_fn = lambda: "Monkeypatched!"
    monkeypatch.setitem(sys.modules, "writeruserapp", fake_module)
    session.add_fake_component(
        {
            "code": """
print('hi testing stdout ' + str(test_thing_ee) + my_fn())
"""
        }
    )
    block = CodeBlock("fake_id", runner, {"test_thing_ee": 26})
    block.run()
    assert block.outcome == "success"
    assert block.result == "hi testing stdout 26Monkeypatched!\n"


def test_run_invalid_code(session, runner, monkeypatch):
    fake_module = types.ModuleType("fake_writeruserapp")
    fake_module.my_fn = lambda: "Monkeypatched!"
    monkeypatch.setitem(sys.modules, "writeruserapp", fake_module)

    session.add_fake_component(
        {
            "code": """
print(1/0)
"""
        }
    )
    block = CodeBlock("fake_id", runner, {})
    with pytest.raises(ZeroDivisionError):
        block.run()
    assert block.outcome == "error"
