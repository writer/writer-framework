import logging
from typing import Dict, List, Tuple

import writer.core
import writer.workflows_blocks
from writer.core_ui import Component
from writer.workflows_blocks.blocks import WorkflowBlock


def _get_workflow_nodes(component_id):
    return writer.core.base_component_tree.get_descendents(component_id)

def run_workflow_by_key(session, workflow_key: str, execution_env: Dict):
    all_components = writer.core.base_component_tree.components.values()
    workflows = list(filter(lambda c: c.type == "workflows_workflow" and c.content.get("key") == workflow_key, all_components))
    if len(workflows) == 0:
        return
    workflow = workflows[0]

    run_workflow(session, workflow.id, execution_env)


def run_workflow(session, component_id: str, execution_env: Dict):
    execution: Dict[str, WorkflowBlock] = {}
    for node in _get_origin_nodes(component_id):
        _run_node(node, execution, session, execution_env)
    _generate_run_log(session, execution)

def _generate_run_log(session: "writer.core.WriterSession", execution: Dict[str, WorkflowBlock]):
    msg = """Workflow executed

"""
    exec_log = []
    for component_id, tool in execution.items():
        exec_log.append({
            "componentId": component_id,
            "outcome": tool.outcome
        })
    state = session.session_state
    state.add_log_entry("info", "Workflow", msg, workflow_execution=exec_log)


def _get_origin_nodes(component_id):
    nodes = _get_workflow_nodes(component_id)
    # called_nodes_ids contains the ids of all the nodes that are considered dependencies by one or more nodes
    called_nodes_ids = [out.get("toNodeId") for node in nodes if node.outs for out in node.outs if out.get("toNodeId")]
    origin_nodes = [node for node in nodes if node.id not in called_nodes_ids]
    return origin_nodes


def _run_node(target_node: "Component", execution: Dict, session: "writer.core.WriterSession", execution_env: Dict):
    tool_class = writer.workflows_blocks.blocks.block_map.get(target_node.type)
    if not tool_class:
        raise RuntimeError(f"Couldn't find tool for {target_node.type}.")

    tool = execution.get(target_node.id)
    if tool:
        return tool
    outcome_handled = False
    stored_exception = None
    
    tool = tool_class(target_node, execution, session, execution_env)

    try:
        tool.run()
    except BaseException as e:
        if not tool.result:
            tool.result = repr(e)
        stored_exception = e

    execution[target_node.id] = tool

    for out in target_node.outs if target_node.outs else []:
        if tool.outcome != out.get("outId"):
            continue
        outcome_handled = True
        to_node_id = out.get("toNodeId")
        node = writer.core.base_component_tree.get_component(to_node_id)
        if not node:
            state = session.session_state
            state.add_log_entry("error", "Missing node in workflow", f"Missing node {to_node_id}")
            continue
        _run_node(node, execution, session, (execution_env | {"result": tool.result} ))
    
    if stored_exception and not outcome_handled:
        raise stored_exception 

    return tool