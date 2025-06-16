import hashlib
import json
import logging
import os
import threading
import time
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from contextlib import contextmanager
from contextvars import copy_context
from typing import Any, Dict, Generator, List, Literal, Optional, OrderedDict, Union

import writer.blocks
import writer.blocks.base_block
import writer.core
import writer.core_ui
from writer.ss_types import BlueprintExecutionError, BlueprintExecutionLog, WriterConfigurationError


class GraphNode:
    tool_class: writer.blocks.base_block.BlueprintBlock_T
    component: writer.core_ui.Component
    future: Optional[Future] = None
    tool: Optional[writer.blocks.base_block.BlueprintBlock] = None
    # filrered lists of inputs and outputs with only edges from graph
    inputs: List[Any]
    outputs: List[Any]

    def __init__(self, component: writer.core_ui.Component, graph: "Graph"):
        self.component = component
        self.graph = graph
        tool_class = graph.tools.get(component.type)
        self.inputs = []
        self.outputs = []
        if not tool_class:
            raise WriterConfigurationError(
                f"Component type '{component.type}' is not registered as a block."
            )
        self.tool_class = tool_class


    @property
    def id(self) -> str:
        return self.component.id

    @property
    def result(self) -> Optional[Union[str, Dict]]:
        if self.tool:
            return self.tool.result
        return None

    @property
    def outcome(self) -> Optional[str]:
        if self.tool:
            return self.tool.outcome
        return None

    @property
    def message(self) -> Optional[str]:
        if self.tool:
            return self.tool.message
        return None

    @property
    def return_value(self) -> Optional[Any]:
        if self.tool:
            return self.tool.return_value
        return None

    def run_tool(self, tool: writer.blocks.base_block.BlueprintBlock):
        start_time = time.time()
        tool.execution_environment["call_stack"] = []
        tool.execution_environment["trace"] = []

        try:
            tool.outcome = "in_progress"
            tool.run()
            tool.outcome = tool.outcome or "success"
        except BaseException as e:
            if not tool.outcome or tool.outcome == "in_progress":
                tool.outcome = "error"
            if isinstance(e, WriterConfigurationError):
                tool.message = str(e)
            else:
                tool.message = repr(e)
            if self._is_error_handled(tool.component, tool.outcome):
                print("Error handled in component:", tool.component.id, tool.message)
                return self 
            else:
                print("Error not handled in component:", tool.component.id, tool.message)
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

        return self 

    def _is_error_handled(self, component: writer.core_ui.Component, outcome: str) -> bool:
        if not component.outs:
            return False
        for output in component.outs:
            if output.get("outId") == outcome:
                return True
        return False

    def _get_env(self, execution_environment: Dict) -> Dict:
        env = execution_environment.copy()
        for inputs in self.inputs:
            from_node = self.graph.get_node(inputs["fromNodeId"])
            if from_node and from_node.tool:
                out_id = inputs.get("outId")
                if out_id and from_node.outcome == out_id:
                    result = from_node.result
                    env['result'] = result
                    env['message'] = from_node.tool.message
        env['results'] = self.graph.get_results()
        return env

    def can_run(self) -> bool:
        if not self.inputs:
            return True
        # all inputs must be evaluated
        for input in self.inputs:
            from_node = self.graph.get_node(input["fromNodeId"])
            if not from_node or from_node.outcome is None or from_node.outcome == "in_progress":
                return False
        # at least one input must fulfilled
        for input in self.inputs:
            from_node = self.graph.get_node(input["fromNodeId"])
            if from_node and from_node.outcome == input.get("outId"):
                return True
        return False

    def run(self, execution_environment: Dict, runner, executor):
        self.tool = self.tool_class(self.component, runner, self._get_env(execution_environment))
        self.tool.outcome = "in_progress"
        ctx = copy_context()
        self.future = executor.submit(ctx.run, self.run_tool, self.tool)
        return self.future

    def debug_info(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.component.type,
            "outputs": self.outputs,
            "inputs": self.inputs,
            "result": self.result,
            "message": self.message if self.tool else None,
            "return_value": self.tool.return_value if self.tool else None,
            "outcome": self.outcome if self.tool else None,
        }

class Graph:
    def __init__(self, 
        nodes: List[writer.core_ui.Component],
        tools: Dict[str, writer.blocks.base_block.BlueprintBlock_T]
    ):
        self.tools = tools
        self.nodes = [GraphNode(node, self) for node in nodes]
        self.node_map = {node.id: node for node in self.nodes}
        self._calculate_io()
        self.start_nodes = self._find_start_nodes()

    def get_start_nodes(self) -> List[GraphNode]:
        return self.start_nodes

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.node_map.get(node_id)

    def get_results(self) -> Dict[str, Any]:
        results = {}
        for node in self.nodes:
            if node.tool and node.tool.outcome == "success":
                results[node.id] = node.result
        return results

    def _calculate_io(self):
        for node in self.nodes:
            if not node.component.outs:
                continue
            for output in node.component.outs:
                if output.get("toNodeId") in self.node_map:
                    node.outputs.append(output)
                    target_node = self.node_map[output.get("toNodeId")]
                    target_node.inputs.append({
                        "fromNodeId": node.id,
                        "outId": output.get("outId"),
                    })

    def _find_start_nodes(self) -> List[GraphNode]:
        start_nodes = []
        output_nodes = set()
        for node in self.nodes:
            if node.outputs:
                for output in node.outputs:
                    output_nodes.add(output.get("toNodeId"))

        for node in self.nodes:
            if node.id not in output_nodes:
                start_nodes.append(node)

        return start_nodes
    def debug_info(self) -> Dict[str, Any]:
        return {
            "nodes": [node.debug_info() for node in self.nodes],
            "start_nodes": [node.id for node in self.start_nodes],
            "tools": list(self.tools.keys()),
        }

class GraphBuilder:
    def __init__(self, components: List[writer.core_ui.Component] = [], tools: Dict[str, writer.blocks.base_block.BlueprintBlock_T] = {}):
        self.components = components 
        self.tools = tools
        self.start_ids: List[str] = []

    def set_start_node(self, start_component_id: str):
        self.start_ids.append(start_component_id)

    def set_start_edge(self, component_id: str, out_id: str):
        for component in self.components:
            if component.id == component_id:
                if not component.outs:
                    break
                for out in component.outs:
                    if out.get("outId") == out_id:
                        self.start_ids.append(out.get("toNodeId"))

    def build(self) -> Graph:
        return Graph(self._filter_components(), self.tools)

    def _filter_components(self) -> List[writer.core_ui.Component]:
        if not self.start_ids:
            return self.components
        component_map = {component.id: component for component in self.components}
        # todo: remove duplicates
        filtered_components = []
        queue = [component_map[component_id] for component_id in self.start_ids if component_id in component_map] 
        while queue:
            component = queue.pop(0)
            filtered_components.append(component)
            if component.outs is None:
                continue
            for out in component.outs:
                next_component_id = out["toNodeId"]
                if next_component_id in component_map:
                    queue.append(component_map[next_component_id])

        return filtered_components


class StatusLogger:
    def __init__(self,
        graph: Graph,
        runner,
        title: str = "Blueprint execution"
    ):
        self.runner = runner
        self.graph = graph
        self.title = title
        self.run_id = self._generate_run_id()

    def log(
        self,
        msg: str = "",
        entry_type: Literal["info", "error"] = "info",
    ):
        if not writer.core.Config.is_mail_enabled_for_log:
            return
        run_id = self.run_id
        exec_log: BlueprintExecutionLog = BlueprintExecutionLog(summary=[])
        for node in self.graph.nodes:
            #print(node.debug_info())
            if node.tool is None:
                exec_log.summary.append({"componentId": node.id})
                continue
            if node.tool.outcome == "in_progress":
                exec_log.summary.append(
                    {
                        "componentId": node.id,
                        "outcome": node.tool.outcome,
                        "message": node.tool.message,
                        "executionTimeInSeconds": node.tool.execution_time_in_seconds,
                    }
                )
                continue

            exec_log.summary.append(
                {
                    "componentId": node.id,
                    "outcome": node.tool.outcome,
                    "message": node.tool.message,
                    "result": self._summarize_data_for_log(node.tool.result),
                    "returnValue": self._summarize_data_for_log(node.tool.return_value),
                    "executionEnvironment": self._summarize_data_for_log(getattr(node.tool, "execution_environment_snapshot", None)),
                    "executionTimeInSeconds": node.tool.execution_time_in_seconds,
                }
            )
        self.runner.session.session_state.add_log_entry(
            entry_type, self.title, msg, blueprint_execution=exec_log, id=run_id
        )

    def _generate_run_id(self):
        timestamp = str(int(time.time() * 1000))
        salt = os.urandom(8).hex()
        raw_id = f"{self.runner.session.session_id}_{timestamp}_{salt}"
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


class GraphRunner:
    def __init__(self, 
        graph: Graph,
        execution_environment: Dict,
        runner,
        title: str = "Blueprint execution"
    ):
        self.runner = runner
        self.graph = graph
        self.execution_environment = execution_environment
        self.tools: OrderedDict[str, Optional[writer.blocks.base_block.BlueprintBlock]] = OrderedDict()
        self.status_logger = StatusLogger(self.graph, self.runner, title)

    def run(self):
        #print(json.dumps(self.graph.debug_info(), indent=2))
        queue = self.graph.get_start_nodes()
        futures = []
        if not queue:
            raise WriterConfigurationError("No start nodes found in the blueprint.")
        with self.runner._get_executor() as executor:
            while queue or futures:
                while queue:
                    node = queue.pop(0)
                    #print(node.debug_info())
                    if node.can_run() and node.outcome is None:
                        futures.append(node.run(self.execution_environment, self.runner, executor))

                self.status_logger.log("Executing...")
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    futures.remove(future)
                    try:
                        node = future.result()
                        if node.return_value is not None:
                            self.status_logger.log(
                                f"Execution completed, node {node.id} returned value: {node.return_value}",
                                entry_type="info"
                            )
                            #executor.shutdown(wait=False)
                            return node.return_value
                    except BaseException as e:
                        #executor.shutdown(wait=False)
                        self.status_logger.log("Execution failed.", entry_type="error")
                        raise BlueprintExecutionError(
                            f"Blueprint execution was cancelled due to an error - {e.__class__.__name__}: {e}"
                        ) from e 
                    for output in node.outputs:
                        to_node_id = output.get("toNodeId")
                        next_node = self.graph.get_node(to_node_id)
                        if next_node:
                            queue.append(next_node)
        self.status_logger.log("Execution completed.")

class BlueprintRunner:
    MAX_DAG_DEPTH = 32

    def __init__(self, session: writer.core.WriterSession):
        self.session = session
        self.executor_lock = threading.Lock()

    @property
    def api_blueprints(self):
        return self._gather_api_blueprints()

    @contextmanager
    def _get_executor(self) -> Generator[ThreadPoolExecutor, None, None]:
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

            if not executor:
                raise RuntimeError(
                    "The main pool executor isn't available. This is only expected in test or debugging situations."
                )

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
        return []


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

    def run_branch(
        self,
        start_node_id: str,
        branch_out_id: Optional[str],
        execution_environment: Dict,
        title: str = "Branch execution",
    ):
        builder = GraphBuilder(
            components=self._get_blueprint_nodes(start_node_id),
            tools=writer.blocks.base_block.block_map
        )
        if branch_out_id is None:
            builder.set_start_node(start_node_id)
        else:
            builder.set_start_edge(start_node_id, branch_out_id)

        return GraphRunner(
            builder.build(),
            execution_environment, self, title=title
        ).run()

    def run_blueprint(
        self, component_id: str, execution_environment: Dict, title="Blueprint execution"
    ):
        graph = Graph(
            nodes=self._get_blueprint_nodes(component_id),
            tools=writer.blocks.base_block.block_map
        )
        return GraphRunner(
            graph,
            execution_environment,
            self,
            title=title
        ).run()
