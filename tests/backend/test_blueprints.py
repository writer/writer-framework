from concurrent.futures import Future, ThreadPoolExecutor, wait
from contextlib import contextmanager
from threading import Event
from typing import Dict, Optional
from unittest.mock import MagicMock

import pytest
from writer.blocks.base_block import BlueprintBlock, BlueprintBlock_T
from writer.blueprints import MAX_DAG_DEPTH, BlueprintRunManager, Graph, GraphBuilder, GraphRunner
from writer.core_ui import Component


def run_graph(graph: Graph, env: Optional[Dict] = None, runner = None) -> None:
    if runner is None:
        runner = MockRunner()
    run = GraphRunner(graph=graph, execution_environment=env if env is not None else {}, runner=runner, title="Test Execution")
    run.CANCELATION_CHECK_INTERVAL = 0.001
    return run.run()

def run_graph_async(executor, graph: Graph, env: Optional[Dict] = None, runner = None) -> Future:
    if runner is None:
        runner = MockRunner()
    run = GraphRunner(graph=graph, execution_environment=env if env is not None else {}, runner=runner, title="Test Execution")
    run.CANCELATION_CHECK_INTERVAL = 0.001
    return executor.submit(run.run)


tools: Dict[str,BlueprintBlock_T]  = {}

class MockState:
    def __init__(self):
        self.data = {}

    def add_log_entry(self, entry):
        self.data['last_log'] = entry

class MockBlock(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        tools[type] = cls

    def run(self):
        event = self.component.content.get("event")
        if isinstance(event, Event):
            event.wait(timeout=1)

        callback = self.component.content.get("callback")
        if callback is not None:
            try:
                callback(self.execution_environment)
            except Exception as e:
                self.outcome = "error"
                self.message = str(e)
                raise e

        code = self.component.content.get("code")
        if code is not None:
            try:
                exec(code, self.execution_environment | {"set_output": self.set_output, "state": self.runner.session.session_state})
                self.outcome = "success"
                return
            except Exception as e:
                self.outcome = "error"
                self.message = str(e)
                raise e

        ret = self.component.content.get("return_value")
        if ret is not None:
            self.return_value = ret

        # Handle different behaviors based on content
        should_fail = self.component.content.get("should_fail", False)
        if should_fail:
            raise Exception("Error")

        should_pass_result = self.component.content.get("should_pass_result", False)
        if should_pass_result:
            self.result = self.execution_environment.get("result")
            if self.result is None:
                self.result = self.execution_environment.get("message")
            if self.result is None:
                self.result = "No value"
        else:
            self.result = "test result"
        
        should_return_result = self.component.content.get("should_return_result", False)
        if should_return_result:
            self.return_value = self.execution_environment.get("result", "No value")
        
        self.outcome = "success"

    def set_output(self, output):
        self.result = output

class MockRunner:
    def __init__(self):
        self.session = MagicMock()
        self.session.session_state = MagicMock()
        self.session.session_state.add_log_entry = MagicMock()
        self.run_manager = BlueprintRunManager()

    def _generate_run_id(self):
        return "mock_run_id"

    @contextmanager
    def _get_executor(self):
        new_executor = None
        try:
            new_executor = ThreadPoolExecutor(20)  # New executor for debugging/testing
            executor = new_executor

            yield executor
        finally:
            if new_executor:
                new_executor.shutdown()
    def cancel_blueprint_execution(self, run_id: str):
        self.run_manager.cancel_run(run_id)

MockBlock.register("mock_block")

def create_component(id: str, outs=[], fields=None):
    return Component(
        id=id,
        type="mock_block",
        outs=outs,
        content=fields or {}
    )


class TestBasicExecution:
    """Tests for basic graph execution scenarios"""
    
    def test_single_component_execution(self):
        builder = GraphBuilder(components=[
            create_component("N1")
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)
        graph_node = graph.get_node("N1")
        assert graph_node is not None
        assert graph_node.outcome == "success"

    def test_multiple_start_components(self):
        builder = GraphBuilder(components=[
            create_component("N1"),
            create_component("N2")
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        node1 = graph.get_node("N1")
        node2 = graph.get_node("N2")
        
        assert node1 is not None
        assert node1.outcome == "success"
        
        assert node2 is not None
        assert node2.outcome == "success"

    def test_component_with_output(self):
        builder = GraphBuilder(components=[
            create_component("N1", outs=[{"toNodeId": "N2", "outId": "success"}]),
            create_component("N2")
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        graph_node = graph.get_node("N1")
        next_graph_node = graph.get_node("N2")
        
        assert graph_node is not None
        assert graph_node.outcome == "success"
        
        assert next_graph_node is not None
        assert next_graph_node.outcome == "success"


class TestDataFlow:
    """Tests for data passing between components"""
    
    def test_result_passing(self):
        # Create a mock component that passes a result
        builder = GraphBuilder(components=[
            create_component("N1", outs=[{"toNodeId": "N2", "outId": "success"}]),
            create_component("N2", fields={"should_pass_result": True})
        ], tools=tools)
        
        graph = builder.build()
        run_graph(graph)

        graph_node = graph.get_node("N1")
        next_graph_node = graph.get_node("N2")
        
        assert graph_node is not None
        assert graph_node.result == "test result"
        
        assert next_graph_node is not None
        assert next_graph_node.result == "test result"  # Assuming it uses the return value from the previous block

    def test_all_results(self):
        builder = GraphBuilder(components=[
            create_component("N1", outs=[{"toNodeId": "N2", "outId": "success"}]),
            create_component("N2", fields={"should_pass_result": True})
        ], tools=tools)
        
        graph = builder.build()
        run_graph(graph)

        assert graph.get_results().get("N1") == "test result"
        assert graph.get_results().get("N2") == "test result"

    def test_code_block_execution(self):
        builder = GraphBuilder(components=[
            create_component("N1", fields={"code": "set_output('Hello, World!')"})
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        node = graph.get_node("N1")
        assert node is not None
        assert node.message is None
        assert node.outcome == "success"
        assert node.result == "Hello, World!"

    def test_return_value(self):
        builder = GraphBuilder(components=[
            create_component("N1", fields={
                "code": "set_output('Hello, World!')"
            }, outs=[{"toNodeId": "N2", "outId": "success"}]),
            create_component("N2", fields={"should_return_result": True}),
        ], tools=tools)

        graph = builder.build()
        value = run_graph(graph)

        assert value == "Hello, World!"


class TestErrorHandling:
    """Tests for error scenarios and edge cases"""
    
    def test_error_handling(self):
        builder = GraphBuilder(components=[
            create_component("N1", fields={"should_fail": True}, outs=[{"toNodeId": "N2", "outId": "error"}]),
            create_component("N2", fields={"should_pass_result": True})
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        node = graph.get_node("N2")
        assert node is not None
        assert node.outcome == "success"
        assert node.result == "Exception('Error')"

    def test_error_unhandled(self):
        builder = GraphBuilder(components=[
            create_component("N1", fields={"should_fail": True}),
        ], tools=tools)

        graph = builder.build()
        try:
            run_graph(graph)
        except Exception as e:
            assert str(e) == "Blueprint execution was cancelled due to an error - Exception: Error"
        else:
            assert False, "Expected an exception to be raised"

    def test_node_requirements_not_met(self):
        builder = GraphBuilder(components=[
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "error"},
            ]),
            create_component("N2"),
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        node = graph.get_node("N2")
        assert node is not None
        assert node.outcome == "skipped"

    def test_circular_dependency(self):
        builder = GraphBuilder(components=[
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "success"},
            ]),
            create_component("N2", outs=[
                {"toNodeId": "N1", "outId": "success"},
            ]),
        ], tools=tools)
        graph = builder.build()
        assert graph.status == "error"
        node = graph.get_node("N1")
        assert node is not None
        assert node.outcome == "error"
        assert node.message == "Circular dependency detected."

    def test_max_dag_deplth(self):
        local_tools = tools.copy()

        components = [
            create_component("N1", fields={"callback": lambda env: call_graph(env)})
        ]

        def call_graph(env):
            builder = GraphBuilder(components=components, tools=local_tools)
            graph = builder.build()
            return run_graph(graph, env)
        
        with pytest.raises(Exception) as exc_info:
           call_graph({})
        assert type(exc_info.value).__name__ == "BlueprintExecutionError"
        assert str(exc_info.value) == "Blueprint execution was cancelled due to an error - RuntimeError: Maximum call depth ({0}) exceeded. Check that you don't have any unintended circular references.".format(MAX_DAG_DEPTH)


class TestComplexGraphs:
    """Tests for complex graph structures and multi-node scenarios"""
    
    def test_two_inputs_from_one_node(self):
        builder = GraphBuilder(components=[
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "success"},
                {"toNodeId": "N2", "outId": "error"},
            ]),
            create_component("N2", fields={"should_pass_result": True})
        ], tools=tools)
        
        graph = builder.build()
        run_graph(graph)
        
        node = graph.get_node("N2")
        assert node is not None
        assert node.outcome == "success"
        assert node.result == "test result"

    def test_two_inputs(self):
        ''' next-component should be executed only if both inputs are resolved and at least one of them is success '''
        builder = GraphBuilder(components=[
            create_component("N1", outs=[
                {"toNodeId": "N3", "outId": "success"},
            ]),
            create_component("N2", outs=[
                {"toNodeId": "N3", "outId": "success"},
            ]),
            create_component("N3", fields={
                "code": "set_output('N1' in results and 'N2' in results)"
            })
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        node = graph.get_node("N3")
        assert node is not None
        assert node.outcome == "success"
        assert node.result == True

    def test_two_routes_of_different_length(self):
        builder = GraphBuilder(components=[
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "success"},
                {"toNodeId": "N3", "outId": "success"},
            ]),
            create_component("N2", outs=[
                {"toNodeId": "N3", "outId": "success"},
            ]),
            create_component("N3", fields={
                "code": "set_output('N2' in results and 'N1' in results)"
            }),
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        node3 = graph.get_node("N3")
        assert node3 is not None
        assert node3.outcome == "success"
        assert node3.result == True

    def test_deep_tree(self):
        builder = GraphBuilder(components=[
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "success"},
            ]),
            create_component("N2", outs=[
                {"toNodeId": "N3", "outId": "success"},
            ]),
            create_component("N3", outs=[
                {"toNodeId": "N4", "outId": "success"},
            ]),
            create_component("N4", fields={"should_pass_result": True}),
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        node = graph.get_node("N4")
        assert node is not None
        assert node.outcome == "success"
        assert node.result == "test result"

    def test_error_deep_in_branch(self):
        builder = GraphBuilder(components=[
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "success"},
                {"toNodeId": "N4", "outId": "success"},
            ]),
            create_component("N2", fields={"should_fail": True}, outs=[
                {"toNodeId": "N3", "outId": "success"},
                {"toNodeId": "N5", "outId": "error"},
            ]),
            create_component("N3", outs=[
                {"toNodeId": "N4", "outId": "success"},
            ]),
            create_component("N4", fields={"should_pass_result": True}),
            create_component("N5", fields={"should_pass_result": True}),
        ], tools=tools)

        graph = builder.build()
        run_graph(graph)

        node = graph.get_node("N3")
        assert node is not None
        assert node.outcome == "skipped"
        node = graph.get_node("N4")
        assert node is not None
        assert node.outcome == "success"
        assert node.result == "test result"


class TestBranchExecution:
    """Tests for branch execution and start node scenarios"""
    
    def test_run_branch_deep_tree(self):
        builder = GraphBuilder(components=[
            create_component("dummy", outs=[
                {"toNodeId": "next-component", "outId": "success"},
            ]),
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "success"},
            ]),
            create_component("N2", outs=[
                {"toNodeId": "N3", "outId": "success"},
            ]),
            create_component("N3", outs=[
                {"toNodeId": "N4", "outId": "success"},
            ]),
            create_component("N4", fields={"should_pass_result": True}),
        ], tools=tools)
        builder.set_start_node("N1")

        graph = builder.build()
        run_graph(graph)
        start_node = graph.get_node("N4")
        assert start_node is not None
        assert start_node.outcome == "success"
        assert start_node.result == "test result"

        dummy_node = graph.get_node("dummy")
        assert dummy_node is None

    def test_run_branch(self):
        builder = GraphBuilder(components=[
            create_component("dummy", outs=[
                {"toNodeId": "N2", "outId": "success"},
            ]),
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "success"},
            ]),
            create_component("N2", fields={"should_pass_result": True}),
        ], tools=tools)
        builder.set_start_node("N1")

        graph = builder.build()
        run_graph(graph)
        start_node = graph.get_node("N1")
        assert start_node is not None
        assert start_node.outcome == "success"
        assert start_node.result == "test result"

        node = graph.get_node("N2")
        assert node is not None
        assert node.outcome == "success"
        assert node.result == "test result"
        assert node.inputs == [{"fromNodeId": "N1", "outId": "success"}]
        dummy_node = graph.get_node("dummy")
        assert dummy_node is None

    def test_run_branch_with_out_id(self):
        builder = GraphBuilder(components=[
            create_component("dummy", outs=[
                {"toNodeId": "N2", "outId": "success"},
            ]),
            create_component("N1", outs=[
                {"toNodeId": "N2", "outId": "success"},
            ]),
            create_component("N2", fields={"should_pass_result": True}),
        ], tools=tools)
        builder.set_start_edge("N1", "success")

        graph = builder.build()
        run_graph(graph)
        start_node = graph.get_node("N1")
        assert start_node is None
        node = graph.get_node("N2")
        assert node is not None
        assert node.outcome == "success"
        assert node.result == "No value"
        assert node.inputs == []
        dummy_node = graph.get_node("dummy")
        assert dummy_node is None


class TestCancellation:
    """Tests for execution cancellation scenarios"""
    
    #def test_cancellation_simple(self):
    #    runner = MockRunner()
    #    event = Event()

    #    graph  = GraphBuilder(components=[
    #        create_component("N1", fields={
    #            "event": event 
    #        }),
    #    ], tools=tools).build()
    #    
    #    with runner._get_executor() as executor:
    #        future = run_graph_async(executor, graph, {"blueprint_run_id": "test"}, runner)
    #        wait([future], timeout=0.1)
    #        runner.cancel_blueprint_execution("test")
    #        wait([future], timeout=0.1)

    #        event.set()
    #        wait([future], timeout=0.1)

    #    node = graph.get_node("N1")
    #    assert node is not None
    #    assert node.outcome == "cancelled"

    def test_cancel_nodes_on_error(self):
        runner = MockRunner()
        event = Event()

        graph = GraphBuilder(components=[
            create_component("N1", fields={
                "event": event 
            }),
            create_component("N2", fields={
                "should_fail": True
            })
        ], tools=tools).build()

        with runner._get_executor() as executor:
            future = run_graph_async(executor, graph, {"run_id": "test"}, runner)
            wait([future], timeout=0.01)
            event.set()
            wait([future], timeout=0.01)

        node1 = graph.get_node("N1")
        node2 = graph.get_node("N2")
        
        assert node1 is not None
        assert node1.outcome == "cancelled"
        
        assert node2 is not None
        assert node2.outcome == "error"
    
    def test_cancelation_of_nested_workflows_on_error(self):
        runner = MockRunner()
        event = Event()
        nested_event = Event()

        nested_graph = GraphBuilder(components=[
            create_component("nested", fields={
                "event": nested_event 
            }),
        ], tools=tools).build()

        graph = GraphBuilder(components=[
            create_component('next', fields= {
                "callback": lambda env: run_graph(nested_graph, env, runner)
            }),
            create_component("N1", fields={
                "event": event,
                "should_fail": True
            }),
        ], tools=tools).build()
        
        with runner._get_executor() as executor:
            future = run_graph_async(executor, graph, {"run_id": "test"}, runner)
            wait([future], timeout=0.01)
            event.set()
            wait([future], timeout=0.01)
            nested_event.set()
            wait([future], timeout=0.01)

        node = nested_graph.get_node("nested")
        assert node is not None
        assert node.outcome == "cancelled"

    def test_cancelation_on_nested_workflows_error(self):
        runner = MockRunner()
        event = Event()

        nested_graph = GraphBuilder(components=[
            create_component("nested", fields={
                "should_fail": True
            }),
        ], tools=tools).build()

        graph = GraphBuilder(components=[
            create_component('next', fields= {
                "callback": lambda env: run_graph(nested_graph, env, runner)
            }),
            create_component("N1", fields={
                "event": event,
            }),
        ], tools=tools).build()

        with runner._get_executor() as executor:
            future = run_graph_async(executor, graph, {"run_id": "test"}, runner)
            wait([future], timeout=0.01)
            event.set()
            wait([future], timeout=0.1)

        node = graph.get_node("N1")
        assert node is not None
        assert node.outcome == "cancelled"
    def test_nested_cancel(self):
        runner = MockRunner()
        event = Event()
        nested_event = Event()

        nested_graph = GraphBuilder(components=[
            create_component("nested", fields={
                "event": nested_event
            }),
        ], tools=tools).build()

        graph = GraphBuilder(components=[
            create_component('next', fields= {
                "callback": lambda env: run_graph(nested_graph, env, runner)
            }),
            create_component("N1", fields={
                "event": event,
            }),
        ], tools=tools).build()

        with runner._get_executor() as executor:
            future = run_graph_async(executor, graph, {"blueprint_run_id": "test"}, runner)
            wait([future], timeout=0.01)
            runner.cancel_blueprint_execution("test")
            wait([future], timeout=0.01)
            nested_event.set()
            event.set()
            wait([future], timeout=0.1)

        node = graph.get_node("N1")
        nested = nested_graph.get_node("nested")
        assert node is not None
        assert node.outcome == "cancelled"
        assert nested is not None
        assert nested.outcome == "cancelled"
