import copy
import hashlib
import json
import logging
import os
import threading
import time
from collections import OrderedDict, deque
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from contextlib import contextmanager
from contextvars import copy_context
from typing import Any, Dict, Generator, List, Literal, Optional

import writer.blocks
import writer.blocks.base_block
from writer.blueprints.executor import GraphBuilder, GraphRunner, Graph
import writer.core
import writer.core_ui
from writer.ss_types import BlueprintExecutionError, BlueprintExecutionLog, WriterConfigurationError


class BlueprintRunner:
    MAX_DAG_DEPTH = 32

    def __init__(self, session: writer.core.WriterSession):
        self.session = session
        self.executor_lock = threading.Lock()

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
        self, blueprint_key: str
    ):
        """
        Checks if a blueprint with the given key is available for API execution.

        :param blueprint_key: The blueprint identifier.
        :return: True if the blueprint is available for API execution, False otherwise.
        """
        return blueprint_key in self.api_blueprints

    def get_blueprint_api_trigger(
        self, blueprint_key: str
    ):
        """
        Retrieves the API trigger for a given blueprint key.

        :param blueprint_key: The blueprint identifier.
        :return: The API trigger component.
        """
        if not self.is_blueprint_api_available(blueprint_key):
            raise ValueError(
                f'API trigger not found for blueprint "{blueprint_key}".'
            )
        return self.api_blueprints[blueprint_key]

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
                api_blueprints[parent_blueprint.content.get("key")] = \
                    trigger.id

        return api_blueprints

    def run_blueprint_via_api(
        self,
        blueprint_key: str,
        execution_environment: Optional[Dict[str, Any]] = None
    ):
        """
        Executes a blueprint by its key via the API.

        :param blueprint_key: The blueprint identifier.
        :param execution_environment: The execution environment for
        the blueprint.
        :return: The result of the blueprint execution.
        """
        if execution_environment is None:
            execution_environment = {}

        trigger_id = self.get_blueprint_api_trigger(blueprint_key)

        return self.run_branch(
            trigger_id,
            None,
            execution_environment,
            f"API trigger execution ({blueprint_key})"
        )

    def run_blueprint_pool(self, blueprint_key: str, execution_environments: List[Dict]):
        """
        Executes the same blueprint multiple times in parallel with different execution environments.

        :param blueprint_key: The blueprint identifier (same blueprint for all executions).
        :param execution_environments: A list of execution environments, one per execution.
        :return: A list of results in the same order as execution_environments.
        """

        with self._get_executor() as executor:
            futures = [
                executor.submit(self.run_blueprint_by_key, blueprint_key, env)
                for env in execution_environments
            ]

        wait(futures)  # Important to preserve order, don't switch to as_completed

        results = []
        for future in futures:
            results.append(future.result())

        return results

    def _get_blueprint_nodes(self, component_id):
        current_node_id = component_id
        while current_node_id is not None:
            node = self.session.session_component_tree.get_component(current_node_id)
            if not node:
                break
            if node.type == "blueprints_blueprint":
                return self.session.session_component_tree.get_descendents(current_node_id)
            current_node_id = node.parentId
        return []


    def run_branch_pool(
        self, base_component_id: str, base_outcome: str, execution_environments: List[Dict]
    ):
        """
        Executes the same branch multiple times in parallel with different execution environments.
        """

        with self._get_executor() as executor:
            futures = [
                executor.submit(self.run_branch, base_component_id, base_outcome, env)
                for env in execution_environments
            ]

        wait(futures)  # Important to preserve order, don't switch to as_completed

        results = []
        for future in futures:
            results.append(future.result())

        return results

    def run_branch(
        self,
        start_node_id: str,
        branch_out_id: Optional[str],
        execution_environment: Dict,
        title: str = "Branch execution",
    ):
        print(f"Running branch from {start_node_id} with out {branch_out_id}")
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

    def run_blueprint(
        self, component_id: str, execution_environment: Dict, title="Blueprint execution"
    ):
        graph = Graph(
            nodes=self._get_blueprint_nodes(component_id),
            tools=writer.blocks.base_block.block_map
        )
        return GraphRunner(
            graph,
            execution_environment,
            self,
            title=title
        ).run()

