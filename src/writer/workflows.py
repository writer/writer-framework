from typing import Dict, List, Literal, Tuple

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
    nodes = _get_workflow_nodes(component_id)
    try:
        for node in get_terminal_nodes(nodes):
            run_node(node, nodes, execution, session, execution_env)
    except BaseException as e:
        _generate_run_log(session, execution, "error")
        raise e
    else:
        _generate_run_log(session, execution, "info")

def _generate_run_log(session: "writer.core.WriterSession", execution: Dict[str, WorkflowBlock], entry_type: Literal["info", "error"]):
    msg = ""
    exec_log = []
    for component_id, tool in execution.items():
        exec_log.append({
            "componentId": component_id,
            "outcome": tool.outcome
        })
    state = session.session_state
    state.add_log_entry(entry_type, "Workflow execution", msg, workflow_execution=exec_log)


def get_terminal_nodes(nodes):
    return [node for node in nodes if not node.outs]

def _get_node_dependencies(target_node: "Component", nodes: List["Component"]):
    dependencies:List[Tuple] = []
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
    

def get_branch_nodes(root_node_id: "Component"):
    root_node = writer.core.base_component_tree.get_component(root_node_id)
    branch_nodes = [root_node]
    if not root_node.outs:
        return branch_nodes
    for out in root_node.outs:
        branch_nodes += get_branch_nodes(out.get("toNodeId"))
    return branch_nodes


def _is_outcome_managed(target_node: "Component", target_out_id: str):
    if not target_node.outs:
        return False
    for out in target_node.outs:
        if out.get("outId") == target_out_id:
            return True
    return False


def run_node(target_node: "Component", nodes: List["Component"], execution: Dict, session: "writer.core.WriterSession", execution_env: Dict):
    tool_class = writer.workflows_blocks.blocks.block_map.get(target_node.type)
    if not tool_class:
        raise RuntimeError(f"Couldn't find tool for {target_node.type}.")
    dependencies = _get_node_dependencies(target_node, nodes)

    tool = execution.get(target_node.id)
    if tool:
        return tool

    result = None
    matched_dependencies = 0
    for node, out_id in dependencies:
        tool = run_node(node, nodes, execution, session, execution_env)
        if not tool:
            continue
        if tool.outcome == out_id:
            matched_dependencies += 1
        result = tool.result

    if len(dependencies) > 0 and matched_dependencies == 0:
        return

    tool = tool_class(target_node, execution, session, execution_env | {"result": result})
    
    try:
        tool.run()
    except BaseException as e:
        if tool and not tool.result:
            tool.result = repr(e)
        if not tool.outcome or not _is_outcome_managed(target_node, tool.outcome):
            raise e
    finally:
        execution[target_node.id] = tool
    
    return tool