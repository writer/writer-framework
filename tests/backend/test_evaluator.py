import json
from pathlib import Path

from writer import audit_and_fix, evaluator, wf_project
import writer as wf
from writer.core import WriterState
from tests.backend import parse_instance_path

_, sc = wf_project.read_files(Path(__file__).resolve().parent / "basic_test_app")
sc = audit_and_fix.fix_components(sc)

session = wf.session_manager.get_new_session()
session.session_component_tree.ingest(sc)

class TestEvaluator:

    state = WriterState()
    state.x = 12
    state.d = { "a": 12 }
    ev = evaluator.Evaluator(state, session.session_component_tree, session.mail)

    def test_evaluate_instance_field(self) -> None:
        evaluated = self.ev.evaluate_instance_field(
            parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,tesxx6t4lbdk23wb:0,crzronwa55h5t5vk:1,dtl8vxb5ebzthzvr:0"),
            "text",
            None,
            False
        )
        assert evaluated == "Color: White"

    def test_set_state(self) -> None:
        self.ev.set_state("d['b']", 13, {})
        assert self.state.d["b"] == 13