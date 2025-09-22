import hashlib
import itertools
import json
import logging
import os
import threading
import time
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from contextlib import contextmanager
from contextvars import ContextVar, copy_context
from typing import Any, Dict, Generator, List, Literal, Optional, OrderedDict, Union

import writer.blocks
import writer.blocks.base_block
import writer.core
import writer.core_ui
from writer.ss_types import BlueprintExecutionError, BlueprintExecutionLog, WriterConfigurationError

MAX_DAG_DEPTH = 32
MAX_LOG_ITERABLE_SIZE = 100
MAX_LOG_STRING_LENGTH = 5000

_current_block: ContextVar[Optional[writer.blocks.base_block.BlueprintBlock]] = \
    ContextVar("current_block", default=None)


class BlueprintRunManager:
    def __init__(self):
        self._runs: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    @contextmanager
    def register(self, run_id: str):
        event = self.register_run(run_id)
        try:
            yield event
        finally:
            self.deregister_run(run_id)

    def register_run(self, run_id: str):
        with self._lock:
            if run_id not in self._runs:
                self._runs[run_id] = {"counter": 0, "event": threading.Event()}
            self._runs[run_id]["counter"] += 1
            event = self._runs[run_id]["event"]
        return event

    def deregister_run(self, run_id: str):
        with self._lock:
            if run_id in self._runs:
                self._runs[run_id]["counter"] -= 1
                if self._runs[run_id]["counter"] <= 0:
                    del self._runs[run_id]

    def cancel_run(self, run_id: str):
        with self._lock:
            if run_id in self._runs:
                self._runs[run_id]["event"].set()


class BlueprintRunner:
    def __init__(self, session: writer.core.WriterSession):
        self.session = session
        self.executor_lock = threading.Lock()
        self.run_manager = BlueprintRunManager()

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
        self, blueprint_id: str
    ):
        """
        Checks if a blueprint with the given key is available for API execution.

        :param blueprint_id: The blueprint identifier.
        :return: True if the blueprint is available for API execution, False otherwise.
        """
        return blueprint_id in self.api_blueprints

    def get_blueprint_api_trigger(
        self, blueprint_id: str
    ):
        """
        Retrieves the API trigger for a given blueprint key.

        :param blueprint_key: The blueprint identifier.
        :return: The API trigger component.
        """
        if not self.is_blueprint_api_available(blueprint_id):
            raise ValueError(
                f'API trigger not found for blueprint "{blueprint_id}".'
            )
        return self.api_blueprints[blueprint_id]

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
                api_blueprints[parent_blueprint_id] = \
                    trigger.id

        return api_blueprints

    def run_blueprint_via_api(
        self,
        blueprint_id: str,
        execution_environment: Optional[Dict[str, Any]] = None
    ):
        """
        Executes a blueprint by its key via the API.

        :param blueprint_id: The blueprint identifier.
        :param execution_environment: The execution environment for
        the blueprint.
        :return: The result of the blueprint execution.
        """
        if execution_environment is None:
            execution_environment = {}

        trigger_id = self.get_blueprint_api_trigger(blueprint_id)

        return self.run_branch(
            trigger_id,
            None,
            execution_environment,
            f"API trigger execution ({blueprint_id})"
        )

    def run_blueprint_batch(self, blueprint_key: str, execution_environments: List[Dict]):
        """
        Executes the same blueprint multiple times sequentially with different execution environments.

        :param blueprint_key: The blueprint identifier (same blueprint for all executions).
        :param execution_environments: A list of execution environments, one per execution.
        :return: A list of results in the same order as execution_environments.
        """
        results = []
        for env in execution_environments:
            result = self.run_blueprint_by_key(blueprint_key, env)
            results.append(result)

        return results

    def _get_blueprint_nodes(self, component_id):
        current_node_id = component_id
        while current_node_id is not None:
            node = self.session.session_component_tree.get_component(current_node_id)
            if not node:
                break
            if node.type == "blueprints_blueprint":
                nodes = self.session.session_component_tree.get_descendents(current_node_id)
                return [node for node in nodes if node.type != 'note']
            current_node_id = node.parentId
        return []

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

    def run_branch_batch(
        self, base_component_id: str, base_outcome: str, execution_environments: List[Dict]
    ):
        """
        Executes the same branch multiple times sequentially with different execution environments.
        """
        results = []
        for env in execution_environments:
            result = self.run_branch(base_component_id, base_outcome, env)
            results.append(result)

        return results

    def run_blueprint(
        self, component_id: str, execution_environment: Dict, title="Blueprint execution"
    ):
        builder = GraphBuilder(
            components=self._get_blueprint_nodes(component_id),
            tools=writer.blocks.base_block.block_map
        )

        return GraphRunner(
            builder.build(),
            execution_environment, self, title=title
        ).run()

    def cancel_blueprint_execution(self, run_id: str):
        self.run_manager.cancel_run(run_id)


class GraphNode:
    tool_class: writer.blocks.base_block.BlueprintBlock_T
    component: writer.core_ui.Component
    future: Optional[Future] = None
    tool: Optional[writer.blocks.base_block.BlueprintBlock] = None
    # filrered lists of inputs and outputs with only edges from graph
    inputs: List[Any]
    outputs: List[Any]
    status: Optional[str] = None
    _message: Optional[str] = None

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
        if self.status:
            return self.status
        if self.tool:
            return self.tool.outcome
        return None

    @property
    def message(self) -> Optional[str]:
        if self._message:
            return self._message
        if self.tool:
            return self.tool.message
        return None

    @message.setter
    def message(self, value: str):
        self._message = value

    @property
    def return_value(self) -> Optional[Any]:
        if self.tool:
            return self.tool.return_value
        return None

    def run_tool(self, tool: writer.blocks.base_block.BlueprintBlock) -> "GraphNode":
        start_time = time.time()

        call_stack = tool.execution_environment.get("call_stack", []) + [self.id]
        call_depth = call_stack.count(tool.component.id)
        if call_depth > MAX_DAG_DEPTH:
            error_message = f"Maximum call depth ({MAX_DAG_DEPTH}) exceeded. Check that you don't have any unintended circular references."
            tool.outcome = "error"
            tool.message = error_message
            raise RuntimeError(error_message)
        tool.execution_environment["call_stack"] = call_stack
        tool.execution_environment["trace"] = []

        try:
            tool.outcome = "in_progress"
            with use_current_block(tool):
                tool.run()
            if self.outcome == "stopped":
                return self
            tool.outcome = tool.outcome or "success"
        except BlueprintExecutionError as e:
                raise e
        except BaseException as e:
            if not tool.outcome or tool.outcome == "in_progress":
                tool.outcome = "error"
            if isinstance(e, WriterConfigurationError):
                tool.message = str(e)
            else:
                tool.message = repr(e)
            if self._is_error_handled(tool.component, tool.outcome):
                return self 
            else:
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
                    env['call_stack'] = from_node.tool.execution_environment.get('call_stack', [])
                    env['result'] = result
                    env['message'] = from_node.tool.message
                    
                    # Pass through accumulated API calls from previous block (like call_stack)
                    env['api_calls'] = from_node.tool.execution_environment.get('api_calls', [])
                    env['httpx_requests'] = from_node.tool.execution_environment.get('httpx_requests', [])
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
        return True

    def _is_skipped(self) -> bool:
        if not self.inputs:
            return False
        for input in self.inputs:
            from_node = self.graph.get_node(input["fromNodeId"])
            if from_node and from_node.outcome == input.get("outId"):
                return False
        return True

    def run(self, execution_environment: Dict, runner, executor) -> Future:
        if self.outcome is not None or self._is_skipped():
            self.status = "skipped"
            future: Future = Future()
            future.set_result(self)
            return future

        self.tool = self.tool_class(self.component, runner, self._get_env(execution_environment))
        self.tool.outcome = "in_progress"
        ctx = copy_context()
        self.future = executor.submit(ctx.run, self.run_tool, self.tool)
        if not isinstance(self.future, Future):
            raise WriterConfigurationError(
                f"Unable to run tool {self.tool.component.id} - the executor did not return a Future."
            )
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
    status: Optional[str] = None
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
            if node.tool and node.tool.outcome in ["success", "trigger"]:
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
    def __init__(self, components: List[writer.core_ui.Component], tools: Dict[str, writer.blocks.base_block.BlueprintBlock_T]):
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

    def validate_graph(self, graph: Graph):
        """Validates the graph for cycles and unreachable nodes and marks them as errors."""
        visited = set()
        stack = set()
        has_cycle = False

        def visit(node: GraphNode):
            if node.status == "error":
                return
            if node.id in stack:
                node.status = "error"
                node.message = "Circular dependency detected."
                nonlocal has_cycle
                has_cycle = True
            if node.id in visited:
                return
            visited.add(node.id)
            stack.add(node.id)
            for output in node.outputs:
                next_node = graph.get_node(output["toNodeId"])
                if next_node:
                    visit(next_node)
            stack.remove(node.id)

        for node in graph.nodes:
            if node.id not in visited:
                visit(node)

        for node in graph.nodes:
            if node.id not in visited:
                node.status = "error"
        if has_cycle:
            graph.status = "error"

    def build(self) -> Graph:
        graph = Graph(self._filter_components(), self.tools)
        self.validate_graph(graph)
        return graph

    def _filter_components(self) -> List[writer.core_ui.Component]:
        if not self.start_ids:
            return self.components
        component_map = {component.id: component for component in self.components}
        # todo: remove duplicates
        filtered_components = set()
        queue = [component_map[component_id] for component_id in self.start_ids if component_id in component_map] 
        while queue:
            component = queue.pop(0)
            filtered_components.add(component.id)
            if component.outs is None:
                continue
            for out in component.outs:
                next_component_id = out["toNodeId"]
                if next_component_id in component_map and next_component_id not in filtered_components:
                    queue.append(component_map[next_component_id])

        return [ 
            component_map[component_id] for component_id in filtered_components
            if component_id in component_map
        ]


class StatusLogger:
    def __init__(self,
        graph: Graph,
        runner: BlueprintRunner,
        run_id: str,
        title: str = "Blueprint execution"
    ):
        self.runner = runner
        self.graph = graph
        self.title = title
        self.run_id = run_id
        self.log_id = self._generate_run_id()
        self.lock = threading.Lock()

    def log(
        self,
        msg: str = "",
        entry_type: Literal["info", "error"] = "info",
        exit: Optional[str] = None,
    ):
        if not writer.core.Config.is_mail_enabled_for_log:
            return
        log_id = self.log_id
        exec_log: BlueprintExecutionLog = BlueprintExecutionLog(runId=self.run_id, summary=[], exit=exit)
        for node in self.graph.nodes:
            #print(node.debug_info())
            if node.tool is None:
                if node.outcome is None:
                    exec_log.summary.append({"componentId": node.id })
                    continue
                else:
                    exec_log.summary.append({
                        "componentId": node.id,
                        "outcome": node.outcome,
                        "message": node.message,
                        "result": None,
                        "returnValue": None,
                        "executionEnvironment": {},
                        "executionTimeInSeconds": 0,
                    })
                    continue
            if node.outcome == "stopped":
                exec_log.summary.append(
                    {
                        "componentId": node.id,
                        "outcome": node.outcome,
                        "message": node.message,
                        "executionTimeInSeconds": node.tool.execution_time_in_seconds,
                    }
                )
                continue
            if node.outcome == "in_progress":
                exec_log.summary.append(
                    {
                        "componentId": node.id,
                        "outcome": node.outcome,
                        "message": node.message,
                        "executionTimeInSeconds": node.tool.execution_time_in_seconds,
                    }
                )
                continue

            exec_log.summary.append(
                {
                    "componentId": node.id,
                    "outcome": node.outcome,
                    "message": node.message,
                    "result": self._summarize_data_for_log(node.result),
                    "returnValue": self._summarize_data_for_log(node.return_value),
                    "executionEnvironment": self._summarize_data_for_log(getattr(node.tool, "execution_environment_snapshot", None)),
                    "executionTimeInSeconds": node.tool.execution_time_in_seconds,
                }
            )
        self.runner.session.session_state.add_log_entry(
            entry_type, self.title, msg, blueprint_execution=exec_log, id=log_id
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

        if isinstance(data, list):
            return [self._summarize_data_for_log(item) for item in data[:MAX_LOG_ITERABLE_SIZE]]
        if isinstance(data, dict):
            return {
                k: self._summarize_data_for_log(v)
                for k, v in itertools.islice(data.items(), MAX_LOG_ITERABLE_SIZE)
            }
        if isinstance(data, str):
            if len(data) <= MAX_LOG_STRING_LENGTH:
                return data
            return f"{data[:MAX_LOG_STRING_LENGTH]}... <truncated>"
        if isinstance(data, (int, float, bool, type(None))):
            return data

        try:
            return json.loads(json.dumps(data))
        except (TypeError, OverflowError):
            return f"Can't be displayed in the log. Value of type: {str(type(data))}."

class GraphRunner:
    CANCELATION_CHECK_INTERVAL = 0.1

    def __init__(self, 
        graph: Graph,
        execution_environment: Dict,
        runner,
        title: str = "Blueprint execution"
    ):
        self.runner = runner
        self.graph = graph
        self.execution_environment = execution_environment
        self.run_id = execution_environment.get("blueprint_run_id", self._generate_run_id())
        execution_environment["blueprint_run_id"] = self.run_id
        self.status_logger = StatusLogger(self.graph, self.runner, self.run_id, title)

        self.queue = self.graph.get_start_nodes()
        self.futures: List[Future[GraphNode]] = []

    def run(self) -> Optional[Any]:
        if self.graph.status == "error":
            self.status_logger.log("Execution failed due to graph validation errors.", entry_type="error", exit="graph_validation_error")
            return None
        if not self.queue:
            raise WriterConfigurationError("No start nodes found in the blueprint.")

        with self.runner._get_executor() as executor:
            with self.runner.run_manager.register(self.run_id) as event:
                return self._execute(executor, event)

    def _execute(self, executor: ThreadPoolExecutor, abort_event: threading.Event) -> Optional[Any]:
        while self.queue or self.futures:
            while self.queue:
                node: GraphNode = self.queue.pop(0)
                if node.can_run() and node.outcome is None:
                    self.futures.append(node.run(self.execution_environment, self.runner, executor))

            self.status_logger.log("Executing...")
            done, _ = wait(self.futures, timeout=self.CANCELATION_CHECK_INTERVAL, return_when=FIRST_COMPLETED)
            if not done:
                if abort_event.is_set():
                    self._cancel_all_jobs()
                    self.status_logger.log("Terminated.", entry_type="info", exit="aborted")
                    return None
                else:
                    continue
            self.status_logger.log("Executing...")
            for future in done:
                if future in self.futures:
                    self.futures.remove(future)
                try:
                    result_node: GraphNode = future.result()
                except BlueprintExecutionError as e:
                    self._cancel_all_jobs()
                    self.status_logger.log("Execution failed", entry_type="error", exit=str(e))
                    raise e
                except BaseException as e:
                    abort_event.set()
                    self._cancel_all_jobs()
                    self.status_logger.log("Execution failed.", entry_type="error", exit=str(e))
                    raise BlueprintExecutionError(
                        f"Blueprint execution was stopped due to an error - {e.__class__.__name__}: {e}"
                    ) from e 
                if result_node.outcome == "stopped":
                    continue 
                if result_node.return_value is not None:
                    self._cancel_local_jobs()
                    self.status_logger.log(
                        f"Execution completed, node {result_node.id} returned value: {result_node.return_value}",
                        entry_type="info",
                        exit="return"
                    )
                    return result_node.return_value
                for output in result_node.outputs:
                    to_node_id = output.get("toNodeId")
                    next_node = self.graph.get_node(to_node_id)
                    if next_node:
                        self.queue.append(next_node)

        self.status_logger.log("Execution completed.", entry_type="info", exit="completed")
        return None

    def _cancel_local_jobs(self):
        self.queue.clear()
        for node in self.graph.nodes:
            if node.outcome == "in_progress":
                node.status = "stopped"
        self.status_logger.log("Stopped")
        for future in self.futures:
            if not future.done():
                future.cancel()

    def _cancel_all_jobs(self):
        self._cancel_local_jobs()
        self.runner.cancel_blueprint_execution(self.run_id)

    def _generate_run_id(self):
        timestamp = str(int(time.time() * 1000))
        salt = os.urandom(8).hex()
        raw_id = f"{self.runner.session.session_id}_{timestamp}_{salt}"
        hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()[:24]
        return hashed_id


def get_current_block() -> Optional[writer.blocks.base_block.BlueprintBlock]:
    return _current_block.get(None)


@contextmanager
def use_current_block(block: writer.blocks.base_block.BlueprintBlock):
    token = _current_block.set(block)
    yield
    _current_block.reset(token)
