import copy
import hashlib
import json
import logging
import os
import threading
import time
from collections import OrderedDict, deque
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from contextlib import contextmanager
from contextvars import copy_context
from typing import Any, Dict, List, Literal, Optional

import writer.blocks
import writer.blocks.base_block
import writer.core
import writer.core_ui
from writer.ss_types import BlueprintExecutionError, BlueprintExecutionLog, WriterConfigurationError


class BlueprintRunner:
    MAX_DAG_DEPTH = 32

    def __init__(self, session: writer.core.WriterSession):
        self.session = session
        self.executor_lock = threading.Lock()

    @property
    def api_blueprints(self):
        return self._gather_api_blueprints()

    @contextmanager
    def _get_executor(self):
        """Return the application's thread pool executor.

        In normal operation we reuse the main executor provided by the running
        application process. In situations where that process is unavailable
        (for example during tests) a temporary executor is created.
        """

        new_executor = None
        try:
            try:
                current_app_process = writer.core.get_app_process()
                executor = current_app_process.executor
            except RuntimeError:
                logging.info(
                    "The main pool executor isn't being reused. This is only expected in test or debugging situations."
                )
                new_executor = ThreadPoolExecutor(20)  # New executor for debugging/testing
                executor = new_executor

            yield executor
        finally:
            if new_executor:
                new_executor.shutdown()

    def execute_ui_trigger(
        self, ref_component_id: str, ref_event_type: str, execution_environment: Dict = {}
    ):
        components = self.session.session_component_tree.get_descendents("blueprints_root")
        ui_triggers = list(filter(lambda c: c.type == "blueprints_uieventtrigger", components))
        for trigger in ui_triggers:
            if trigger.content.get("refComponentId") != ref_component_id:
                continue
            if trigger.content.get("refEventType") != ref_event_type:
                continue
            self.run_branch(trigger.id, None, execution_environment, "UI trigger execution")

    def run_blueprint_by_key(self, blueprint_key: str, execution_environment: Dict = {}):
        all_components = self.session.session_component_tree.components.values()
        blueprints = list(
            filter(
                lambda c: c.type == "blueprints_blueprint" and c.content.get("key") == blueprint_key,
                all_components,
            )
        )
        if len(blueprints) == 0:
            raise ValueError(f'Blueprint with key "{blueprint_key}" not found.')
        blueprint = blueprints[0]
        return self.run_blueprint(
            blueprint.id, execution_environment, f"Blueprint execution ({blueprint_key})"
        )

    def is_blueprint_api_available(
        self, blueprint_key: str
    ):
        """
        Checks if a blueprint with the given key is available for API execution.

        :param blueprint_key: The blueprint identifier.
        :return: True if the blueprint is available for API execution, False otherwise.
        """
        return blueprint_key in self.api_blueprints

    def get_blueprint_api_trigger(
        self, blueprint_key: str
    ):
        """
        Retrieves the API trigger for a given blueprint key.

        :param blueprint_key: The blueprint identifier.
        :return: The API trigger component.
        """
        if not self.is_blueprint_api_available(blueprint_key):
            raise ValueError(
                f'API trigger not found for blueprint "{blueprint_key}".'
            )
        return self.api_blueprints[blueprint_key]

    def _gather_api_blueprints(self):
        """
        Gathers all blueprints that have an API trigger.

        :return: A set of blueprint keys that have an API trigger.
        """
        triggers = [
            c for c in self.session.session_component_tree.components.values()
            if c.type == "blueprints_apitrigger"
            ]
        api_blueprints = {}

        for trigger in triggers:
            parent_blueprint_id = \
                self.session.session_component_tree.get_parent(trigger.id)[0]
            parent_blueprint = \
                self.session.session_component_tree.get_component(
                    parent_blueprint_id
                    )

            if (
                parent_blueprint
                and
                parent_blueprint.type == "blueprints_blueprint"
            ):
                # Store the blueprint key against its trigger ID
                api_blueprints[parent_blueprint.content.get("key")] = \
                    trigger.id

        return api_blueprints

    def run_blueprint_via_api(
        self,
        blueprint_key: str,
        execution_environment: Optional[Dict[str, Any]] = None
    ):
        """
        Executes a blueprint by its key via the API.

        :param blueprint_key: The blueprint identifier.
        :param execution_environment: The execution environment for
        the blueprint.
        :return: The result of the blueprint execution.
        """
        if execution_environment is None:
            execution_environment = {}

        trigger_id = self.get_blueprint_api_trigger(blueprint_key)

        return self.run_branch(
            trigger_id,
            None,
            execution_environment,
            f"API trigger execution ({blueprint_key})"
        )

    def run_blueprint_pool(self, blueprint_key: str, execution_environments: List[Dict]):
        """
        Executes the same blueprint multiple times in parallel with different execution environments.

        :param blueprint_key: The blueprint identifier (same blueprint for all executions).
        :param execution_environments: A list of execution environments, one per execution.
        :return: A list of results in the same order as execution_environments.
        """

        with self._get_executor() as executor:
            futures = [
                executor.submit(self.run_blueprint_by_key, blueprint_key, env)
                for env in execution_environments
            ]

        wait(futures)  # Important to preserve order, don't switch to as_completed

        results = []
        for future in futures:
            results.append(future.result())

        return results

    def _get_blueprint_nodes(self, component_id):
        current_node_id = component_id
        while current_node_id is not None:
            node = self.session.session_component_tree.get_component(current_node_id)
            if not node:
                break
            if node.type == "blueprints_blueprint":
                return self.session.session_component_tree.get_descendents(current_node_id)
            current_node_id = node.parentId

    def run_branch(
        self,
        start_node_id: str,
        branch_out_id: Optional[str],
        execution_environment: Dict,
        title: str = "Branch execution",
    ):
        blueprint_nodes = self._get_blueprint_nodes(start_node_id)
        nodes = self.filter_branch(blueprint_nodes, start_node_id, branch_out_id)
        return self.execute_dag(nodes, execution_environment, title)

    def run_branch_pool(
        self, base_component_id: str, base_outcome: str, execution_environments: List[Dict]
    ):
        """
        Executes the same branch multiple times in parallel with different execution environments.
        """

        with self._get_executor() as executor:
            futures = [
                executor.submit(self.run_branch, base_component_id, base_outcome, env)
                for env in execution_environments
            ]

        wait(futures)  # Important to preserve order, don't switch to as_completed

        results = []
        for future in futures:
            results.append(future.result())

        return results

    def run_blueprint(
        self, component_id: str, execution_environment: Dict, title="Blueprint execution"
    ):
        nodes = self._get_blueprint_nodes(component_id)
        return self.execute_dag(nodes, execution_environment, title)

    def _generate_run_id(self):
        timestamp = str(int(time.time() * 1000))
        salt = os.urandom(8).hex()
        raw_id = f"{self.session.session_id}_{timestamp}_{salt}"
        hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()[:24]
        return hashed_id

    def _summarize_data_for_log(self, data):
        """Convert arbitrary data into a log friendly representation."""

        if data is None:
            return None

        MAX_ROWS = 100
        if isinstance(data, list):
            return [self._summarize_data_for_log(item) for item in data[:MAX_ROWS]]
        if isinstance(data, dict):
            return {
                k: self._summarize_data_for_log(v)
                for i, (k, v) in enumerate(data.items())
                if i < MAX_ROWS
            }
        if isinstance(data, (str, int, float, bool, type(None))):
            return data

        try:
            return json.loads(json.dumps(data))
        except (TypeError, OverflowError):
            return f"Can't be displayed in the log. Value of type: {str(type(data))}."

    def _generate_run_log(
        self,
        tools: OrderedDict[str, Optional[writer.blocks.base_block.BlueprintBlock]],
        title: str,
        entry_type: Literal["info", "error"],
        msg: str = "",
        run_id: Optional[str] = None,
    ):
        if not writer.core.Config.is_mail_enabled_for_log:
            return
        if run_id is None:
            run_id = self._generate_run_id()
        exec_log: BlueprintExecutionLog = BlueprintExecutionLog(summary=[])
        for component_id, tool in tools.items():
            if tool is None:
                exec_log.summary.append({"componentId": component_id})
                continue
            if tool.outcome == "in_progress":
                exec_log.summary.append(
                    {
                        "componentId": component_id,
                        "outcome": tool.outcome,
                        "message": tool.message,
                        "executionTimeInSeconds": tool.execution_time_in_seconds,
                    }
                )
                continue

            exec_log.summary.append(
                {
                    "componentId": component_id,
                    "outcome": tool.outcome,
                    "message": tool.message,
                    "result": self._summarize_data_for_log(tool.result),
                    "returnValue": self._summarize_data_for_log(tool.return_value),
                    "executionEnvironment": self._summarize_data_for_log(getattr(tool, "execution_environment_snapshot", None)),
                    "executionTimeInSeconds": tool.execution_time_in_seconds,
                }
            )
        self.session.session_state.add_log_entry(
            entry_type, title, msg, blueprint_execution=exec_log, id=run_id
        )

    def filter_branch(
        self,
        nodes: List[writer.core_ui.Component],
        start_node_id: str,
        branch_out_id: Optional[str] = None,
    ):
        node_map = {node.id: node for node in nodes}
        filtered_node_ids = set()
        stack = []
        if branch_out_id is not None:
            start_node = node_map.get(start_node_id)
            if not start_node:
                raise ValueError(f"Start node {start_node_id} not found in nodes.")
            for out in start_node.outs or []:
                if out.get("outId") == branch_out_id:
                    stack.append(out.get("toNodeId"))
        else:
            stack.append(start_node_id)
        while stack:
            current_id = stack.pop()
            if current_id in filtered_node_ids:
                continue
            filtered_node_ids.add(current_id)
            current_node = node_map.get(current_id)
            if not current_node:
                continue
            for out in current_node.outs or []:
                if current_id == start_node_id and branch_out_id:
                    if out.get("outId") != branch_out_id:
                        continue
                to_node_id = out.get("toNodeId")
                if to_node_id not in filtered_node_ids:
                    stack.append(to_node_id)
        return [node_map[node_id] for node_id in filtered_node_ids]

    def execute_dag(
        self,
        nodes: List[writer.core_ui.Component],
        execution_environment: Dict,
        title: str = "Blueprint execution",
    ):
        run_id = self._generate_run_id()
        tools: OrderedDict[str, Optional[writer.blocks.base_block.BlueprintBlock]] = OrderedDict()
        graph = {}
        in_degree = {node.id: 0 for node in nodes}
        is_cancelled = False

        inputs: Dict[str, List] = {}
        for node in nodes:
            outs = node.outs or []
            for out in outs:
                to_node_id = out.get("toNodeId")
                if to_node_id not in inputs:
                    inputs[to_node_id] = []
                inputs[to_node_id].append({"nodeId": node.id, "outId": out.get("outId")})

        def check_requirements(tool):
            if is_cancelled:
                return False
            node_id = tool.component.id
            if node_id not in inputs:
                return True
            at_least_one = False
            for input in inputs[node_id]:
                in_tool = tools.get(input.get("nodeId"))
                if not in_tool:
                    continue
                if in_tool.outcome != input.get("outId"):
                    continue
                at_least_one = True

            return at_least_one

        def update_log(message: str, entry_type="info"):
            self._generate_run_log(tools, title, entry_type, msg=message, run_id=run_id)

        for node in nodes:
            graph[node.id] = node
            tools[node.id] = None
            out_node_ids = {out.get("toNodeId") for out in (node.outs or [])}
            for node_id in out_node_ids:
                in_degree[node_id] += 1

        ready: deque = deque()
        for node in nodes:
            if in_degree[node.id] > 0:
                continue
            tool = self._get_tool(node, execution_environment)
            ready.append(tool)
            tools.move_to_end(node.id)
            tools[node.id] = tool

        with self._get_executor() as executor:
            futures: set[Future] = set()
            first_exception: Optional[BaseException] = None
            while ready or futures:
                while ready:
                    tool = ready.popleft()
                    if not check_requirements(tool):
                        break
                    tool.outcome = "in_progress"
                    ctx = copy_context()
                    future = executor.submit(ctx.run, self.run_tool, tool)
                    futures.add(future)

                update_log("Executing...")
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    futures.remove(future)
                    try:
                        tool = future.result()
                    except BaseException as e:
                        is_cancelled = True
                        if first_exception is None:
                            first_exception = e
                        continue
                    else:
                        update_log("Executing...")
                    if tool.return_value is not None:
                        return tool.return_value
                    node = tool.component
                    for out in node.outs or []:
                        to_node_id = out.get("toNodeId")
                        out_id = out.get("outId")
                        in_degree[to_node_id] -= 1
                        if tool.outcome != out_id:
                            continue
                        if in_degree[to_node_id] == 0:
                            new_call_stack = tool.execution_environment.get("call_stack", []) + [
                                node.id
                            ]
                            expanded_environment = execution_environment | {
                                "call_stack": new_call_stack,
                                "result": tool.result,
                                "results": {
                                    k: v.result if v is not None else None for k, v in tools.items()
                                },
                            }
                            to_node = graph.get(to_node_id)
                            if not to_node:
                                continue
                            to_tool = self._get_tool(to_node, expanded_environment)
                            tools.move_to_end(to_node_id)
                            tools[to_node_id] = to_tool
                            ready.append(to_tool)
            if is_cancelled:
                update_log("Execution failed.", entry_type="error")
                if first_exception is not None:
                    raise BlueprintExecutionError(
                        f"Blueprint execution was cancelled due to an error - {first_exception.__class__.__name__}: {first_exception}"
                        ) from first_exception
                else:
                    raise BlueprintExecutionError("Blueprint execution was cancelled.")
            else:
                update_log("Execution completed.")

    def _get_tool(self, node: writer.core_ui.Component, execution_environment: Dict):
        tool_class = writer.blocks.base_block.block_map.get(node.type)
        if not tool_class:
            raise RuntimeError(f'Could not find tool for "{node.type}".')
        tool = tool_class(node, self, execution_environment)
        return tool

    def _is_outcome_managed(self, target_node: writer.core_ui.Component, target_out_id: str):
        if not target_node.outs:
            return False
        for out in target_node.outs:
            if out.get("outId") == target_out_id:
                return True
        return False

    def run_tool(self, tool: writer.blocks.base_block.BlueprintBlock):
        start_time = time.time()

        call_stack = tool.execution_environment.get("call_stack", []) + [tool.component.id]
        call_depth = call_stack.count(tool.component.id)
        if call_depth > BlueprintRunner.MAX_DAG_DEPTH:
            error_message = f"Maximum call depth ({BlueprintRunner.MAX_DAG_DEPTH}) exceeded. Check that you don't have any unintended circular references."
            tool.outcome = "error"
            tool.message = error_message
            raise RuntimeError(error_message)
        tool.execution_environment["call_stack"] = call_stack
        tool.execution_environment["trace"] = []

        try:
            tool.run()
        except BaseException as e:
            if not tool.outcome or tool.outcome == "in_progress":
                tool.outcome = "error"
            if self._is_outcome_managed(tool.component, tool.outcome):
                return tool
            if isinstance(e, WriterConfigurationError):
                tool.message = str(e)
            else:
                tool.message = tool.message or repr(e)
            raise e
        finally:
            tool.execution_time_in_seconds = time.time() - start_time
            try:
                tool.execution_environment_snapshot = {
                    k: v for k, v in tool.execution_environment.items() if k != "vault"
                }
            except Exception:
                # pragma: no cover - best effort defensive code
                logging.debug(
                    "Couldn't snapshot execution environment", exc_info=True
                )

        return tool
