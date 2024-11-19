from typing import TYPE_CHECKING, Any, Dict, Type

if TYPE_CHECKING:
    from writer.core_ui import Component
    from writer.ss_types import InstancePath
    from writer.workflows import WorkflowRunner

WorkflowBlock_T = Type["WorkflowBlock"]
block_map:Dict[str, WorkflowBlock_T] = {}

class WorkflowBlock:
    
    @classmethod
    def register(cls, type: str):
        block_map[type] = cls

    def __init__(self, component: "Component", runner: "WorkflowRunner", execution_environment: Dict):
        self.outcome = None
        self.component = component
        self.runner = runner
        self.execution_time_in_seconds = -1.0
        self.execution_environment = execution_environment
        self.result:Any = None
        self.return_value = None
        self.instance_path: InstancePath = [{"componentId": self.component.id, "instanceNumber": 0}]

    def _get_field(self, field_key: str, as_json=False, default_field_value=None):
        if default_field_value is None:
            if as_json:
                default_field_value = "{}"
            else:
                default_field_value = ""
        value = self.runner.evaluator.evaluate_field(self.instance_path, field_key, as_json, default_field_value, self.execution_environment)
        return value

    def _set_state(self, expr: str, value: Any):
        self.runner.evaluator.set_state(expr, self.instance_path, value, base_context=self.execution_environment)

    def run(self):
        pass