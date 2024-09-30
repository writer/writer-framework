from typing import Dict
import writer.workflows_blocks
from writer.core_ui import Component
import writer.core

def _get_workflow_nodes(component_id):
    return writer.core.base_component_tree.get_descendents(component_id)

def run_workflow_by_key(session, workflow_key: str, execution_env: Dict):
    state = session.session_state
    state.add_log_entry("info", "Workflow", f"""Running workflow "{workflow_key}".""")

    all_components = writer.core.base_component_tree.components.values()
    workflows = list(filter(lambda c: c.type == "workflows_workflow" and c.content.get("key") == workflow_key, all_components))
    if len(workflows) == 0:
        return
    workflow = workflows[0]

    run_workflow(session, workflow.id, execution_env)
    state.add_log_entry("info", "Workflow", f"""Finished executing workflow "{workflow_key}".""")


def run_workflow(session, component_id: "Component", execution_env: Dict):
    final_nodes = _get_final_nodes(component_id)
    execution = {}
    for node in final_nodes:
        _run_node(node, execution, session, execution_env)


def _get_final_nodes(component_id):
    final_nodes = []
    nodes = _get_workflow_nodes(component_id)
    for node in nodes:
        if not node.outs:
            final_nodes.append(node)
    return final_nodes

def _get_dependencies(target_node: "Component"):
    dependencies = []
    parent_id = target_node.parentId
    if not parent_id:
        return dependencies
    nodes = _get_workflow_nodes(parent_id)
    for node in nodes:
        if not node.outs:
            continue
        for out in node.outs:
            to_node_id = out.get("toNodeId")
            out_id = out.get("outId")
            if to_node_id == target_node.id:
                dependencies.append((node, out_id))
    return dependencies
    

def _run_node(target_node: "Component", execution, session, execution_env: Dict):
    tool_class = writer.workflows_blocks.blocks.block_map.get(target_node.type)
    if not tool_class:
        raise RuntimeError(f"Couldn't find tool for {target_node.type}.")
    session.session_state.add_log_entry("info", "Workflow", f"""Running node "{target_node.id}".""")
    dependencies = _get_dependencies(target_node)

    tool = execution.get(target_node.id)
    if tool:
        return tool 

    result = None
    matched_dependencies = 0
    for node, out_id in dependencies:
        tool = _run_node(node, execution, session, execution_env)
        if not tool:
            continue
        if tool.outcome == out_id:
            matched_dependencies += 1
        result = tool.result

    if len(dependencies) > 0 and matched_dependencies == 0:
        return

    tool = tool_class(target_node, execution, session, (execution_env | {"result": result}))
    tool.run()
    execution[target_node.id] = tool
    return tool