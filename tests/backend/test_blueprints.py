from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Dict, Optional, Type
from unittest.mock import MagicMock, patch

import pytest
from writer.blocks.base_block import BlueprintBlock, BlueprintBlock_T
from writer.blueprints import Graph, GraphBuilder, GraphRunner, MAX_DAG_DEPTH
from writer.core_ui import Component


def run_graph(graph: Graph, env: Optional[Dict] = None) -> None:
    return GraphRunner(graph=graph, execution_environment=env if env is not None else {}, runner=MockRunner(), title="Test Execution").run()

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
        self.result = "test result"
        self.outcome = "success"

class MockReturnBlock(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        tools[type] = cls

    def run(self):
        self.return_value = self.execution_environment.get("result", "No value")
        self.outcome = "success"

class MockPassBlock(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        tools[type] = cls

    def run(self):
        self.result = self.execution_environment.get("result")
        if self.result is None:
            self.result = self.execution_environment.get("message")
        if self.result is None:
            self.result = "No value"
        self.outcome = "success"

class CodeBlock(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        tools[type] = cls

    def run(self):
        code = self.component.content.get("code", "")
        try:
            exec(code, self.execution_environment | {"set_output": self.set_output, "state": self.runner.session.session_state})
            self.outcome = "success"
        except Exception as e:
            self.outcome = "error"
            self.message = str(e)
            raise e

    def set_output(self, output):
        self.result = output

class MockFailingBlock(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        tools[type] = cls

    def run(self):
        raise Exception("Error")

class MockRunner:
    def __init__(self):
        self.session = MagicMock()
        self.session.session_state = MagicMock()
        self.session.session_state.add_log_entry = MagicMock()

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

CodeBlock.register("code")
MockReturnBlock.register("return")
MockFailingBlock.register("mock_failing_block")
MockBlock.register("mock_block")
MockPassBlock.register("mock_pass_block")

def create_component(id: str, type: str, outs=None, fields=None):
    if outs is None:
        outs = []
    return Component(
        id=id,
        type=type,
        outs=outs,
        content=fields or {}
    )

def test_single_component_execution():
    graph = Graph(nodes=[
        create_component("test-component", "mock_block", outs=[])
    ], tools=tools)

    run_graph(graph)

    graph_node = graph.get_node("test-component")
    assert graph_node is not None
    assert graph_node.outcome == "success"

def test_multiple_start_components():
    graph = Graph(nodes=[
        create_component("test-component-1", "mock_block", outs=[]),
        create_component("test-component-2", "mock_block", outs=[])
    ], tools=tools)

    run_graph(graph)

    node1 = graph.get_node("test-component-1")
    node2 = graph.get_node("test-component-2")
    
    assert node1 is not None
    assert node1.outcome == "success"
    
    assert node2 is not None
    assert node2.outcome == "success"

def test_component_with_output():
    graph = Graph(nodes=[
        create_component("test-component", "mock_block", outs=[{"toNodeId": "next-component", "outId": "success"}]),
        create_component("next-component", "mock_block", outs=[])
    ], tools=tools)

    run_graph(graph)

    graph_node = graph.get_node("test-component")
    next_graph_node = graph.get_node("next-component")
    
    assert graph_node is not None
    assert graph_node.outcome == "success"
    
    assert next_graph_node is not None
    assert next_graph_node.outcome == "success"

def test_result_passing():
    # Create a mock component that passes a result
    graph = Graph(nodes=[
        create_component("test-component", "mock_block", outs=[{"toNodeId": "next-component", "outId": "success"}]),
        create_component("next-component", "mock_pass_block", outs=[])
    ], tools=tools)
    
    run_graph(graph)

    graph_node = graph.get_node("test-component")
    next_graph_node = graph.get_node("next-component")
    
    assert graph_node is not None
    assert graph_node.result == "test result"
    
    assert next_graph_node is not None
    assert next_graph_node.result == "test result"  # Assuming it uses the return value from the previous block

def test_all_results():
    graph = Graph(nodes=[
        create_component("test-component", "mock_block", outs=[{"toNodeId": "next-component", "outId": "success"}]),
        create_component("next-component", "mock_pass_block", outs=[])
    ], tools=tools)
    
    run_graph(graph)

    assert graph.get_results().get("test-component") == "test result"
    assert graph.get_results().get("next-component") == "test result"

def test_code_block_execution():
    graph = Graph(nodes=[
        create_component("test-component", "code", fields={"code": "set_output('Hello, World!')"})
    ], tools=tools)

    run_graph(graph)

    node = graph.get_node("test-component")
    assert node is not None
    assert node.message is None
    assert node.outcome == "success"
    assert node.result == "Hello, World!"

def test_error_handling():
    graph = Graph(nodes=[
        create_component("test-component", "mock_failing_block", outs=[{"toNodeId": "next-component", "outId": "error"}]),
        create_component("next-component", "mock_pass_block", outs=[])
    ], tools=tools)

    run_graph(graph)

    node = graph.get_node("next-component")
    assert node is not None
    assert node.outcome == "success"
    assert node.result == "Exception('Error')"

def test_error_unhandled():
    graph = Graph(nodes=[
        create_component("test-component", "mock_failing_block"),
    ], tools=tools)

    try:
        run_graph(graph)
    except Exception as e:
        assert str(e) == "Blueprint execution was cancelled due to an error - Exception: Error"
    else:
        assert False, "Expected an exception to be raised"

def test_two_inputs_from_one_node():
    graph = Graph(nodes=[
        create_component("test-component", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
            {"toNodeId": "next-component", "outId": "error"},
        ]),
        create_component("next-component", "mock_pass_block", outs=[])
    ], tools=tools)
    
    run_graph(graph)
    
    node = graph.get_node("next-component")
    assert node is not None
    assert node.outcome == "success"
    assert node.result == "test result"

def test_two_inputs():
    ''' next-component should be executed only if both inputs are resolved and at least one of them is success '''
    graph = Graph(nodes=[
        create_component("test-component", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
        ]),
        create_component("test-component-2", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
        ]),
        create_component("next-component", "code", fields={
            "code": "set_output('test-component' in results and 'test-component-2' in results)"
        }, outs=[])
    ], tools=tools)

    run_graph(graph)

    node = graph.get_node("next-component")
    assert node is not None
    assert node.outcome == "success"
    assert node.result == True

def test_two_routes_of_different_length():
    graph = Graph(nodes=[
        create_component("test1", "mock_block", outs=[
            {"toNodeId": "test2", "outId": "success"},
            {"toNodeId": "test3", "outId": "success"},
        ]),
        create_component("test2", "mock_block", outs=[
            {"toNodeId": "test3", "outId": "success"},
        ]),
        create_component("test3", "code", fields={
            "code": "set_output('test2' in results and 'test1' in results)"
        }, outs=[]),
    ], tools=tools)

    run_graph(graph)

    node3 = graph.get_node("test3")
    assert node3 is not None
    assert node3.outcome == "success"
    assert node3.result == True

def test_return_value():
    graph = Graph(nodes=[
        create_component("test-component", "code", fields={
            "code": "set_output('Hello, World!')"
        }, outs=[{"toNodeId": "return-component", "outId": "success"}]),
        create_component("return-component", "return"),
    ], tools=tools)

    value = run_graph(graph)

    assert value == "Hello, World!"

def test_node_requirements_not_met():
    graph = Graph(nodes=[
        create_component("test-component", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "error"},
        ]),
        create_component("next-component", "mock_block", outs=[]),
    ], tools=tools)

    run_graph(graph)

    node = graph.get_node("next-component")
    assert node is not None
    assert node.outcome == "skipped"

def test_deep_tree():
    graph = Graph(nodes=[
        create_component("t1", "mock_block", outs=[
            {"toNodeId": "t2", "outId": "success"},
        ]),
        create_component("t2", "mock_block", outs=[
            {"toNodeId": "t3", "outId": "success"},
        ]),
        create_component("t3", "mock_block", outs=[
            {"toNodeId": "t4", "outId": "success"},
        ]),
        create_component("t4", "mock_pass_block"),
    ], tools=tools)

    run_graph(graph)

    node = graph.get_node("t4")
    assert node is not None
    assert node.outcome == "success"
    assert node.result == "test result"

def test_run_branch_deep_tree():
    builder = GraphBuilder(components=[
        create_component("dummy", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
        ]),
        create_component("t1", "mock_block", outs=[
            {"toNodeId": "t2", "outId": "success"},
        ]),
        create_component("t2", "mock_block", outs=[
            {"toNodeId": "t3", "outId": "success"},
        ]),
        create_component("t3", "mock_block", outs=[
            {"toNodeId": "t4", "outId": "success"},
        ]),
        create_component("t4", "mock_pass_block"),
    ], tools=tools)
    builder.set_start_node("t1")

    graph = builder.build()
    run_graph(graph)
    start_node = graph.get_node("t4")
    assert start_node is not None
    assert start_node.outcome == "success"
    assert start_node.result == "test result"

    dummy_node = graph.get_node("dummy")
    assert dummy_node is None


def test_run_branch():
    builder = GraphBuilder(components=[
        create_component("dummy", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
        ]),
        create_component("test-component", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
        ]),
        create_component("next-component", "mock_pass_block", outs=[]),
    ], tools=tools)
    builder.set_start_node("test-component")

    graph = builder.build()
    run_graph(graph)
    start_node = graph.get_node("test-component")
    assert start_node is not None
    assert start_node.outcome == "success"
    assert start_node.result == "test result"

    node = graph.get_node("next-component")
    assert node is not None
    assert node.outcome == "success"
    assert node.result == "test result"
    assert node.inputs == [{"fromNodeId": "test-component", "outId": "success"}]
    dummy_node = graph.get_node("dummy")
    assert dummy_node is None

def test_run_branch_with_out_id():
    builder = GraphBuilder(components=[
        create_component("dummy", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
        ]),
        create_component("test-component", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
        ]),
        create_component("next-component", "mock_pass_block", outs=[]),
    ], tools=tools)
    builder.set_start_edge("test-component", "success")

    graph = builder.build()
    run_graph(graph)
    start_node = graph.get_node("test-component")
    assert start_node is None
    node = graph.get_node("next-component")
    assert node is not None
    assert node.outcome == "success"
    assert node.result == "No value"
    assert node.inputs == []
    dummy_node = graph.get_node("dummy")
    assert dummy_node is None

def test_error_deep_in_branch():
    builder = GraphBuilder(components=[
        create_component("t1", "mock_block", outs=[
            {"toNodeId": "t2", "outId": "success"},
            {"toNodeId": "t4", "outId": "success"},
        ]),
        create_component("t2", "mock_failing_block", outs=[
            {"toNodeId": "t3", "outId": "success"},
            {"toNodeId": "error_handling", "outId": "error"},
        ]),
        create_component("t3", "mock_block", outs=[
            {"toNodeId": "t4", "outId": "success"},
        ]),
        create_component("t4", "mock_pass_block"),
        create_component("error_handling", "mock_pass_block"),
    ], tools=tools)

    graph = builder.build()
    run_graph(graph)

    node = graph.get_node("t3")
    assert node is not None
    assert node.outcome == "skipped"
    node = graph.get_node("t4")
    assert node is not None
    assert node.outcome == "success"
    assert node.result == "test result"

def test_circular_dependency():
    builder = GraphBuilder(components=[
        create_component("test-component", "mock_block", outs=[
            {"toNodeId": "next-component", "outId": "success"},
        ]),
        create_component("next-component", "mock_block", outs=[
            {"toNodeId": "test-component", "outId": "success"},
        ]),
    ], tools=tools)
    graph = builder.build()
    assert graph.status == "error"
    node = graph.get_node("test-component")
    assert node is not None
    assert node.outcome == "error"
    assert node.message == "Circular dependency detected."

def test_max_dag_deplth():
    class MockCallGraph(BlueprintBlock):
        def run(self):
            call_graph(self.execution_environment)
            self.result = "test result"
            self.outcome = "success"
    local_tools = tools.copy()
    local_tools["call_graph"] = MockCallGraph

    components = [
        create_component(f"test", "call_graph")
    ]

    def call_graph(env):
        builder = GraphBuilder(components=components, tools=local_tools)
        graph = builder.build()
        return run_graph(graph, env)
    
    with pytest.raises(Exception) as exc_info:
       call_graph({})
    assert type(exc_info.value).__name__ == "BlueprintExecutionError"
    assert str(exc_info.value) == "Blueprint execution was cancelled due to an error - RuntimeError: Maximum call depth ({0}) exceeded. Check that you don't have any unintended circular references.".format(MAX_DAG_DEPTH)


