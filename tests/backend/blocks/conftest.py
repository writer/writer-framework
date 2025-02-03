from typing import Dict

import pytest
from writer.core import WriterSession, WriterState
from writer.core_ui import Branch, Component, ComponentTree, ComponentTreeBranch
from writer.workflows import WorkflowRunner


class BlockTesterMockSession(WriterSession):

    def __init__(self):
        self.session_state = WriterState({})
        self.bmc_branch = ComponentTreeBranch(Branch.bmc)
        component_tree = ComponentTree([self.bmc_branch])
        self.session_component_tree = component_tree

    def add_fake_component(self, content={}, id="fake_id", type="fake_type"):
        self.bmc_branch.attach(Component(id=id, type=type, content=content))


class BlockTesterMockWorkflowRunner(WorkflowRunner):

    def __init__(self, session):
        super().__init__(session)

    def run_branch(self, component_id: str, base_outcome_id: str, execution_environment: Dict, title: str):
        return f"Branch run {component_id} {base_outcome_id}"

    def run_workflow_by_key(self, workflow_key: str, execution_environment: Dict):
        payload = execution_environment.get("payload")
        if "env_injection_test" in payload:
            return payload.get("env_injection_test")
        if workflow_key == "workflow1":
            return 1
        if workflow_key == "workflowDict":
            return { "a": "b" }
        if workflow_key == "duplicator":
            return payload.get("item") * 2
        if workflow_key == "showId":
            return payload.get("itemId")
        if workflow_key == "boom":
            return 1/0
        raise ValueError("Workflow not found.")


@pytest.fixture
def session():
    yield BlockTesterMockSession()


@pytest.fixture
def runner(session):
    yield BlockTesterMockWorkflowRunner(session)
