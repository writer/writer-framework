from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Dict, Type
import pytest
from unittest.mock import MagicMock, patch
from writer.blueprints.executor import Graph, GraphNode, GraphRunner
from writer.core import WriterSession
from writer.core_ui import Component
from writer.blocks.base_block import BlueprintBlock, BlueprintBlock_T
from writer.blocks.code import CodeBlock

tools: Dict[str,BlueprintBlock_T]  = {}
tools['code_block'] = CodeBlock

def test_code_block_execution():
    mock_runner = MagicMock()
    mock_runner.session = WriterSession('test', {}, {})
    mock_executor = MagicMock()

    component = Component(
        id="test-component",
        type="code_block",
        outs=[],
        content={
            "code": "set_output('a sample result')"
        }
    )

    graph = Graph(nodes=[component], tools=tools)

    node = graph.get_node(component.id)
    assert node is not None
    node.run({}, mock_runner, mock_executor)
    assert node.outcome == "in_progress"
    mock_executor.submit.assert_called_once()
    callback = mock_executor.submit.call_args[0][1]
    tool = mock_executor.submit.call_args[0][2]
    callback(tool)
    assert node.message is None
    assert node.outcome == "success"



