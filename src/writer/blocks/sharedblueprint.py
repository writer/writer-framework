"""
Shared blueprint implementation for user-created reusable blueprints.

Shared blueprints execute stored blueprint components by loading them from the component tree.
The component's content.sourceBlueprintId field references the source blueprint.
"""

from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate


class SharedBlueprint(BlueprintBlock):
    """
    Shared blueprint that executes components from a source blueprint in the component tree.

    The source blueprint is identified by the sourceBlueprintId content field.
    """

    @classmethod
    def register(cls, type: str):
        """Register the blueprints_shared type with its abstract template."""
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
                    "featureFlags": ["shared_blueprints"],
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

    def run(self):
        """Execute the source blueprint's components."""
        source_blueprint_id = self.component.content.get("sourceBlueprintId", "")

        if not source_blueprint_id:
            raise ValueError("No source blueprint ID specified")

        try:
            payload = self._get_field("payload")
            expanded_execution_environment = self.execution_environment | {"payload": payload}

            # Get blueprint name for title (matching run_blueprint_by_key pattern)
            source_blueprint = self.runner.session.session_component_tree.get_component(
                source_blueprint_id
            )
            blueprint_name = source_blueprint.content.get("key", "Shared Blueprint") if source_blueprint else "Shared Blueprint"

            return_value = self.runner.run_blueprint(
                source_blueprint_id,
                expanded_execution_environment,
                title=f"Shared blueprint execution ({blueprint_name})"
            )

            self.result = return_value
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
