from typing import TYPE_CHECKING
import writer.workflows_blocks
import writer.core

if TYPE_CHECKING:
    from writer.core_ui import Component

block_map = {}

class WorkflowBlock:
    
    @classmethod
    def register(cls, type: str):
        block_map[type] = cls

    def __init__(self, component: "Component", execution: dict, session: "writer.core.WriterSession", result: dict):
        self.outcome = None
        self.component = component
        self.execution = execution
        self.session = session
        self.result = result
        self.evaluator = writer.core.Evaluator(session.session_state, session.session_component_tree)
        self.instance_path = [{"componentId": self.component.id, "instanceNumber": 0}]

    def _get_field(self, field_key: str, as_json=False):
        base_context = {
            "result": self.result
        }

        v = self.evaluator.evaluate_field(self.instance_path, field_key, base_context=base_context, as_json=as_json)

        print(f"Evaluating {field_key} resulted in {repr(v)}, using context {repr(base_context)}")

        return v

    def run(self):
        pass