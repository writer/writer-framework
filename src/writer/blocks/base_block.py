from typing import TYPE_CHECKING, Any, Dict, Type

import writer.evaluator
from writer.ss_types import WriterConfigurationError

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

    def __init__(self, component_id: str, runner: "WorkflowRunner", execution_environment: Dict):
        self.outcome = None
        self.message = None
        self.component_id = component_id
        self.runner = runner
        self.execution_time_in_seconds = -1.0
        self.execution_environment = execution_environment
        self.result = None
        self.return_value = None
        self.instance_path: InstancePath = [{"componentId": component_id, "instanceNumber": 0}]
        self.evaluator = writer.evaluator.Evaluator(runner.session.session_state, runner.session.session_component_tree)

    def _handle_missing_field(self, field_key):
        component_tree = self.runner.session.session_component_tree
        component = component_tree.get_component(self.component_id)
        field_content = component.content.get(field_key)
        if field_content:
            raise WriterConfigurationError(f'The field `{field_key}` is required. The expression specified, `{field_content}`, resulted in an empty value.')
        else:
            raise WriterConfigurationError(f'The field `{field_key}` is required. It was left empty.')

    def _get_field(self, field_key: str, as_json=False, default_field_value=None, required=False):
        if default_field_value is None:
            if as_json:
                default_field_value = "{}"
            else:
                default_field_value = ""
        value = self.evaluator.evaluate_field(self.instance_path, field_key, as_json, default_field_value, self.execution_environment)

        if required and (value is None or value == "" or value == {}):
            self._handle_missing_field(field_key)
            
        return value

    def _set_state(self, expr: str, value: Any):
        self.evaluator.set_state(expr, self.instance_path, value, base_context=self.execution_environment)

    def run(self):
        pass