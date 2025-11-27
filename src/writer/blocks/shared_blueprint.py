"""
Shared blueprint implementation for user-created reusable blueprints.

Shared blueprints execute stored blueprint components by loading them from the component tree.
The component's content.sourceBlueprintId field references the source blueprint.
"""

import traceback
from typing import TYPE_CHECKING, Dict, List

import writer.core_ui
from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate

if TYPE_CHECKING:
    from writer.blueprints import BlueprintRunner


class SharedBlueprint(BlueprintBlock):
    """
    Shared blueprint that executes components from a source blueprint in the component tree.

    The source blueprint is identified by the sourceBlueprintId content field.
    """

    @classmethod
    def register(cls, type: str):
        """Register the shared_blueprint type with its abstract template."""
        super(SharedBlueprint, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Shared Blueprint",
                    "description": "Executes a shared blueprint from the component tree.",
                    "category": "Logic",
                    "toolkit": "blueprints",
                    "fields": {
                        "payload": {
                            "name": "Payload",
                            "desc": "The value specified will be available using the template syntax, e.g. @{payload}.",
                            "default": "{}",
                            "type": "Text",
                            "control": "Textarea",
                        },
                    },
                    "outs": {
                        "success": {
                            "name": "Success",
                            "description": "Blueprint executed successfully.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "Blueprint execution failed.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def __init__(
        self,
        component: writer.core_ui.Component,
        runner: "BlueprintRunner",
        execution_environment: Dict,
    ):
        super().__init__(component, runner, execution_environment)
        self.source_blueprint_id = component.content.get("sourceBlueprintId", "")

    def _get_blueprint_components(self) -> List[Dict]:
        """
        Load blueprint components from the session's component tree.
        
        Returns:
            List of component dictionaries from the source blueprint.
        """
        if not self.source_blueprint_id:
            return []
        
        try:
            # Use the session's component tree which has the latest components
            # (including changes made during the current session)
            session_component_tree = self.runner.session.session_component_tree
            descendants = session_component_tree.get_descendents(self.source_blueprint_id)
            
            # Convert Component objects to dicts and filter out notes
            children = [
                comp.model_dump() for comp in descendants
                if comp.type != "note" and comp.parentId == self.source_blueprint_id
            ]
            
            return children
        except Exception:
            # Fallback to app_process.bmc_components if session approach fails
            try:
                from writer.core import get_app_process
                app_process = get_app_process()
                bmc_components = app_process.bmc_components or {}
                
                children = [
                    comp for comp in bmc_components.values()
                    if comp.get("parentId") == self.source_blueprint_id
                    and comp.get("type") != "note"
                ]
                
                return children
            except RuntimeError:
                return []

    def run(self):
        """Execute the source blueprint's components."""
        blueprint_components = self._get_blueprint_components()
        
        if not blueprint_components:
            raise ValueError(
                f"No blueprint components found for source blueprint: {self.source_blueprint_id}"
            )

        try:
            # Get payload and expand execution environment
            payload = self._get_field("payload")
            expanded_execution_environment = self.execution_environment | {"payload": payload}
            
            # Convert blueprint component dicts to Component objects
            components = [
                writer.core_ui.Component(**comp_dict)
                for comp_dict in blueprint_components
            ]
            
            # Get the source blueprint name for the title
            try:
                session_component_tree = self.runner.session.session_component_tree
                source_blueprint = session_component_tree.get_component(self.source_blueprint_id)
                blueprint_name = source_blueprint.content.get("key", "Unknown") if source_blueprint else "Unknown"
            except Exception:
                blueprint_name = "Unknown"
            
            # Execute the blueprint with the expanded environment
            return_value = self.runner.run_blueprint_from_components(
                components,
                expanded_execution_environment,
                title=f"Shared blueprint execution ({blueprint_name})"
            )
            
            self.result = return_value
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            self.message = f"<pre>{traceback.format_exc()}</pre>"
            raise e


# Register the shared_blueprint type
SharedBlueprint.register("shared_blueprint")
