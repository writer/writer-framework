from typing import TYPE_CHECKING
import writer.workflows_blocks
from writer.core_ui import Component
import writer.core

def _get_workflow_nodes(component_id):
    return writer.core.base_component_tree.get_descendents(component_id)

def run_workflow_by_key(session, state: "writer.core.WriterState", workflow_key: str):
    state.add_log_entry("info", "Workflow", f"""Running workflow "{workflow_key}".""")

    # workflows = .get_descendents("workflows_root")
    all_components = writer.core.base_component_tree.components.values()
    workflows = list(filter(lambda c: c.type == "workflows_workflow" and c.content.get("key") == workflow_key, all_components))
    if len(workflows) == 0:
        return
    workflow = workflows[0]

    run_workflow(session, workflow.id)
    state.add_log_entry("info", "Workflow", f"""Finished executing workflow "{workflow_key}".""")


def run_workflow(session_info, component_id):
    final_nodes = _get_final_nodes(component_id)
    execution = {}
    session = writer.core.session_manager.get_session(session_info.get("id")) 
    for node in final_nodes:
        _run_node(node, execution, session)


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
    

def _run_node(target_node: "Component", execution, session):
    tool_class = writer.workflows_blocks.blocks.block_map.get(target_node.type)
    if not tool_class:
        raise RuntimeError(f"Couldn't find tool for {target_node.type}.")
    dependencies = _get_dependencies(target_node)

    tool = execution.get(target_node.id)
    if tool:
        return tool 

    result = None
    matched_dependencies = 0
    for node, out_id in dependencies:
        tool = _run_node(node, execution, session)
        if not tool:
            continue
        if tool.outcome == out_id:
            matched_dependencies += 1
        result = tool.result

    if len(dependencies) > 0 and matched_dependencies == 0:
        return

    tool = tool_class(target_node, execution, session, result)
    tool.run()
    execution[target_node.id] = tool
    return tool