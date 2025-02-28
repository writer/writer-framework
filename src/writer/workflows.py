import hashlib
import json
import logging
import os
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, wait
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
        self.executor_lock = threading.Lock()

    @contextmanager
    def _get_executor(self):
        new_executor = None
        try:
            current_app_process = writer.core.get_app_process()
            with self.executor_lock:
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

    def _generate_run_id(self):
        timestamp = str(int(time.time() * 1000))
        salt = os.urandom(8).hex()
        raw_id = f"{self.session.session_id}_{timestamp}_{salt}"
        hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()[:24]
        return hashed_id

    def run_nodes(
        self,
        nodes: List[writer.core_ui.Component],
        execution_environment: Dict,
        title: str = "Workflow execution",
    ):
        execution: Dict[str, Optional[writer.blocks.base_block.WorkflowBlock]] = {}
        tool_futures: Dict[str, Future] = {}
        return_value = None
        execution_environment["run_id"] = self._generate_run_id()
        trace = execution_environment.get("trace", []).copy()
        try:
            futures = []
            with self._get_executor() as executor:
                for node in self.get_terminal_nodes(nodes):
                    futures.append(
                        executor.submit(
                            self.run_node,
                            node,
                            nodes,
                            execution_environment,
                            execution,
                            tool_futures,
                            trace,
                        )
                    )

            wait(futures)

            for tool in execution.values():
                if tool and tool.return_value is not None:
                    return_value = tool.return_value
        except WriterConfigurationError:
            self._generate_run_log(
                execution,
                title,
                "error",
                msg="Execution finished.",
                run_id=execution_environment.get("run_id"),
            )
            # No need to re-raise, it's a configuration error under control and shown as message in the relevant tool
        except BaseException as e:
            self._generate_run_log(
                execution,
                title,
                "error",
                msg="Execution finished.",
                run_id=execution_environment.get("run_id"),
            )
            raise e
        else:
            self._generate_run_log(
                execution,
                "Workflow execution finished",
                "info",
                return_value,
                msg="Execution finished.",
                run_id=execution_environment.get("run_id"),
            )
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
        execution: Dict[str, Optional[writer.blocks.base_block.WorkflowBlock]],
        title: str,
        entry_type: Literal["info", "error"],
        return_value: Optional[Any] = None,
        msg: str = "",
        run_id: Optional[str] = None,
    ):
        if not writer.core.Config.is_mail_enabled_for_log:
            return
        if run_id is None:
            run_id = self._generate_run_id()
        exec_log: WorkflowExecutionLog = WorkflowExecutionLog(summary=[])
        for component_id, tool in execution.items():
            if tool is None:
                exec_log.summary.append({"componentId": component_id})
                continue
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

        self.session.session_state.add_log_entry(
            entry_type, title, msg, workflow_execution=exec_log, id=run_id
        )

    def get_terminal_nodes(self, nodes):
        return [node for node in nodes if not node.outs]

    def _get_node_dependencies(
        self, target_node: writer.core_ui.Component, nodes: List[writer.core_ui.Component]
    ) -> List[Tuple]:
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
        execution: Dict[str, Optional[writer.blocks.base_block.WorkflowBlock]],
        tool_futures: Dict[str, Future],
        trace: List[str],
    ):
        tool_class = writer.blocks.base_block.block_map.get(target_node.type)
        if not tool_class:
            raise RuntimeError(f'Could not find tool for "{target_node.type}".')
        dependencies = self._get_node_dependencies(target_node, nodes)

        execution[target_node.id] = None
        result = None
        matched_dependencies = 0
        dependencies_futures = []

        with self._get_executor() as executor:
            for node, out_id in dependencies:
                tool_future = tool_futures.get(node.id)

                if tool_future is None:
                    tool_future = executor.submit(
                        self.run_node,
                        node,
                        nodes,
                        execution_environment,
                        execution,
                        tool_futures,
                        trace,
                    )
                    tool_futures[node.id] = tool_future
                dependencies_futures.append(tool_future)

        wait(dependencies_futures)  # Important to preserve order, don't switch to as_completed

        for future, dependency in zip(dependencies_futures, dependencies):
            (node, out_id) = dependency
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

        trace += [target_node.id]
        expanded_execution_environment = execution_environment | {
            "trace": trace.copy(),
            "result": result,
            "results": {k: v.result if v is not None else None for k, v in execution.items()},
        }
        tool = tool_class(target_node.id, self, expanded_execution_environment)

        try:
            tool.outcome = "in_progress"
            del execution[target_node.id]
            execution[target_node.id] = tool
            self._generate_run_log(
                execution,
                "Running workflow...",
                "info",
                msg="Execution in progress.",
                run_id=execution_environment.get("run_id"),
            )
            start_time = time.time()
            tool.run()
            tool.execution_time_in_seconds = time.time() - start_time
        except BaseException as e:
            if not tool:
                raise e
            if self._is_outcome_managed(target_node, tool.outcome):
                return tool
            if not tool.outcome or tool.outcome == "in_progress":
                tool.outcome = "error"
            if isinstance(e, WriterConfigurationError):
                tool.message = str(e)
            else:
                tool.message = repr(e)
            raise e
        finally:
            self._generate_run_log(
                execution,
                "Running workflow...",
                "info",
                msg="Execution in progress.",
                run_id=execution_environment.get("run_id"),
            )

        return tool
