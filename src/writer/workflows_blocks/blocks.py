from typing import Dict

import writer.core
import writer.core_ui
import writer.workflows_blocks
from writer.ss_types import InstancePath

block_map = {}

class WorkflowBlock:
    
    @classmethod
    def register(cls, type: str):
        block_map[type] = cls

    def __init__(self, component: "writer.core_ui.Component", execution: Dict, session: "writer.core.WriterSession", execution_env: Dict):
        self.outcome = None
        self.component = component
        self.execution = execution
        self.session = session
        self.execution_env = execution_env
        self.result = None
        self.evaluator = writer.core.Evaluator(session.session_state, session.session_component_tree)
        self.instance_path: InstancePath = [{"componentId": self.component.id, "instanceNumber": 0}]

    def _get_field(self, field_key: str, as_json=False, default_field_value=None):
        if default_field_value is None:
            if as_json:
                default_field_value = "{}"
            else:
                default_field_value = ""
        v = self.evaluator.evaluate_field(self.instance_path, field_key, base_context=self.execution_env, as_json=as_json, default_field_value=default_field_value)

        return v

    def run(self):
        pass