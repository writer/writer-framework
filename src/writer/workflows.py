import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from contextlib import contextmanager
from typing import Any, Dict, List, Literal, Optional, Tuple

import writer.blocks
import writer.blocks.base_block
import writer.core
import writer.core_ui
from writer.ss_types import WorkflowExecutionLog, WriterConfigurationError


class WorkflowRunner:
    def __init__(self, session: writer.core.WriterSession):
        self.session = session

    @contextmanager
    def _get_executor(self):
        new_executor = None
        try:
            current_app_process = writer.core.get_app_process()
            yield current_app_process.executor
        except RuntimeError:
            logging.info(
                "The main pool executor isn't being reused. This is only expected in test or debugging situations."
            )
            new_executor = ThreadPoolExecutor(20)
            yield new_executor  # Pool executor for debugging (running outside of AppProcess)
        finally:
            if new_executor:
                new_executor.shutdown()

    def execute_ui_trigger(
        self, ref_component_id: str, ref_event_type: str, execution_environment: Dict = {}
    ):
        components = self.session.session_component_tree.get_descendents("workflows_root")
        ui_triggers = list(filter(lambda c: c.type == "workflows_uieventtrigger", components))
        for trigger in ui_triggers:
            if trigger.content.get("refComponentId") != ref_component_id:
                continue
            if trigger.content.get("refEventType") != ref_event_type:
                continue
            self.run_branch(trigger.id, "trigger", execution_environment, "UI trigger execution")

    def run_workflow_by_key(self, workflow_key: str, execution_environment: Dict = {}):
        all_components = self.session.session_component_tree.components.values()
        workflows = list(
            filter(
                lambda c: c.type == "workflows_workflow" and c.content.get("key") == workflow_key,
                all_components,
            )
        )
        if len(workflows) == 0:
            raise ValueError(f'Workflow with key "{workflow_key}" not found.')
        workflow = workflows[0]
        return self.run_workflow(
            workflow.id, execution_environment, f"Workflow execution ({workflow_key})"
        )

    def run_workflow_pool(self, workflow_key: str, execution_environments: List[Dict]):
        """
        Executes the same workflow multiple times in parallel with different execution environments.

        :param workflow_key: The workflow identifier (same workflow for all executions).
        :param execution_environments: A list of execution environments, one per execution.
        :return: A list of results in the same order as execution_environments.
        """

        with self._get_executor() as executor:
            futures = [
                executor.submit(self.run_workflow_by_key, workflow_key, env)
                for env in execution_environments
            ]

        wait(futures)  # Important to preserve order, don't switch to as_completed

        results = []
        for future in futures:
            results.append(future.result())

        return results

    def _get_workflow_nodes(self, component_id):
        return self.session.session_component_tree.get_descendents(component_id)

    def _get_branch_nodes(self, base_component_id: str, base_outcome: Optional[str] = None):
        root_node = self.session.session_component_tree.get_component(base_component_id)
        if not root_node:
            raise RuntimeError(
                f'Cannot obtain branch. Could not find component "{base_component_id}".'
            )
        if not root_node:
            return []
        branch_nodes: List[writer.core_ui.Component] = []
        if not root_node.outs:
            return branch_nodes
        for out in root_node.outs:
            if base_outcome is not None and base_outcome != out.get("outId"):
                continue
            branch_root_node = self.session.session_component_tree.get_component(
                out.get("toNodeId")
            )
            if not branch_root_node:
                continue
            branch_nodes.append(branch_root_node)
            branch_nodes += self._get_branch_nodes(out.get("toNodeId"), base_outcome=None)
        return branch_nodes

    def run_branch(
        self,
        base_component_id: str,
        base_outcome: str,
        execution_environment: Dict,
        title: str = "Branch execution",
    ):
        nodes = self._get_branch_nodes(base_component_id, base_outcome)
        return self.run_nodes(nodes, execution_environment, title)

    def run_workflow(
        self, component_id: str, execution_environment: Dict, title="Workflow execution"
    ):
        nodes = self._get_workflow_nodes(component_id)
        return self.run_nodes(nodes, execution_environment, title)

    def run_nodes(
        self,
        nodes: List[writer.core_ui.Component],
        execution_environment: Dict,
        title: str = "Workflow execution",
    ):
        execution: Dict[str, writer.blocks.base_block.WorkflowBlock] = {}
        return_value = None
        try:
            for node in self.get_terminal_nodes(nodes):
                self.run_node(node, nodes, execution_environment, execution)
            for tool in execution.values():
                if tool and tool.return_value is not None:
                    return_value = tool.return_value
        except WriterConfigurationError:
            self._generate_run_log(execution, title, "error")
            # No need to re-raise, it's a configuration error under control and shown as message in the relevant tool
        except BaseException as e:
            self._generate_run_log(execution, title, "error")
            raise e
        else:
            self._generate_run_log(execution, title, "info", return_value)
        return return_value

    def _summarize_data_for_log(self, data):
        if isinstance(data, list):
            return [self._summarize_data_for_log(item) for item in data]
        if isinstance(data, dict):
            return {k: self._summarize_data_for_log(v) for k, v in data.items()}
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        try:
            return json.loads(json.dumps(data))
        except (TypeError, OverflowError):
            return f"Can't be displayed in the log. Value of type: {str(type(data))}."

    def _generate_run_log(
        self,
        execution: Dict[str, writer.blocks.base_block.WorkflowBlock],
        title: str,
        entry_type: Literal["info", "error"],
        return_value: Optional[Any] = None,
    ):
        if not writer.core.Config.is_mail_enabled_for_log:
            return
        exec_log: WorkflowExecutionLog = WorkflowExecutionLog(summary=[])
        for component_id, tool in execution.items():
            exec_log.summary.append(
                {
                    "componentId": component_id,
                    "outcome": tool.outcome,
                    "message": tool.message,
                    "result": self._summarize_data_for_log(tool.result),
                    "returnValue": self._summarize_data_for_log(tool.return_value),
                    "executionEnvironment": self._summarize_data_for_log(
                        tool.execution_environment
                    ),
                    "executionTimeInSeconds": tool.execution_time_in_seconds,
                }
            )
        msg = "Execution finished."

        self.session.session_state.add_log_entry(
            entry_type, title, msg, workflow_execution=exec_log
        )

    def get_terminal_nodes(self, nodes):
        return [node for node in nodes if not node.outs]

    def _get_node_dependencies(
        self, target_node: writer.core_ui.Component, nodes: List[writer.core_ui.Component]
    ):
        dependencies: List[Tuple] = []
        parent_id = target_node.parentId
        if not parent_id:
            return []
        for node in nodes:
            if not node.outs:
                continue
            for out in node.outs:
                to_node_id = out.get("toNodeId")
                out_id = out.get("outId")
                if to_node_id == target_node.id:
                    dependencies.append((node, out_id))
        return dependencies

    def _is_outcome_managed(self, target_node: writer.core_ui.Component, target_out_id: str):
        if not target_node.outs:
            return False
        for out in target_node.outs:
            if out.get("outId") == target_out_id:
                return True
        return False

    def run_node(
        self,
        target_node: writer.core_ui.Component,
        nodes: List[writer.core_ui.Component],
        execution_environment: Dict,
        execution: Dict[str, writer.blocks.base_block.WorkflowBlock],
    ):
        tool_class = writer.blocks.base_block.block_map.get(target_node.type)
        if not tool_class:
            raise RuntimeError(f'Could not find tool for "{target_node.type}".')
        dependencies = self._get_node_dependencies(target_node, nodes)

        tool = execution.get(target_node.id)
        if tool:
            return tool

        result = None
        matched_dependencies = 0

        with self._get_executor() as executor:
            future_to_node = {
                executor.submit(self.run_node, node, nodes, execution_environment, execution): (
                    node,
                    out_id,
                )
                for node, out_id in dependencies
            }

        for future in as_completed(future_to_node):
            node, out_id = future_to_node[future]
            tool = future.result()

            if not tool:
                continue

            if tool.outcome == out_id:
                matched_dependencies += 1

            result = tool.result

            if tool.return_value is not None:
                return tool.return_value

        if len(dependencies) > 0 and matched_dependencies == 0:
            return

        expanded_execution_environment = execution_environment | {
            "result": result,
            "results": {k: v.result for k, v in execution.items()},
        }
        tool = tool_class(target_node.id, self, expanded_execution_environment)

        try:
            start_time = time.time()
            tool.run()
            tool.execution_time_in_seconds = time.time() - start_time
        except BaseException as e:
            if not tool:
                raise e
            if not tool.outcome:
                tool.outcome = "error"
            if self._is_outcome_managed(target_node, tool.outcome):
                pass
            if isinstance(e, WriterConfigurationError):
                tool.message = str(e)
            else:
                tool.message = repr(e)
            raise e

        return tool
