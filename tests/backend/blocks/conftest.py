from typing import Dict, List

import pytest
from writer.blueprints import BlueprintRunner
from writer.core import WriterSession, WriterState
from writer.core_ui import Branch, Component, ComponentTree, ComponentTreeBranch


class BlockTesterMockSession(WriterSession):
    def __init__(self):
        self.session_state = WriterState({})
        self.bmc_branch = ComponentTreeBranch(Branch.bmc)
        component_tree = ComponentTree([self.bmc_branch])
        self.session_component_tree = component_tree

    def add_fake_component(self, content={}, id="fake_id", type="fake_type"):
        component = Component(id=id, type=type, content=content)
        self.bmc_branch.attach(component)
        return component


class BlockTesterMockBlueprintRunner(BlueprintRunner):
    def __init__(self, session):
        super().__init__(session)

    def run_branch_pool(
        self, base_component_id: str, base_outcome: str, execution_environments: List[Dict]
    ):
        return len(execution_environments) * [4]

    def run_branch(
        self,
        component_id: str,
        base_outcome_id: str,
        execution_environment: Dict,
        title: str = "Branch execution",
    ):
        return f"Branch run {component_id} {base_outcome_id}"

    def run_blueprint_by_key(self, blueprint_key: str, execution_environment: Dict):
        payload = execution_environment.get("payload")
        if "env_injection_test" in payload:
            return payload.get("env_injection_test")
        if blueprint_key == "blueprint1":
            return 1
        if blueprint_key == "blueprintDict":
            return {"a": "b"}
        if blueprint_key == "duplicator":
            return payload.get("item") * 2
        if blueprint_key == "showId":
            return payload.get("itemId")
        if blueprint_key == "boom":
            return 1 / 0
        raise ValueError("Blueprint not found.")


@pytest.fixture
def session():
    yield BlockTesterMockSession()


@pytest.fixture
def runner(session):
    yield BlockTesterMockBlueprintRunner(session)
