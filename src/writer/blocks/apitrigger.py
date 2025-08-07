from typing import Any, Dict, List, Optional, Tuple

from writer.abstract import register_abstract_template
from writer.blocks.base_trigger import BlueprintTrigger
from writer.ss_types import AbstractTemplate
from writer.validation.base import SchemaProviderRegistry
from writer.validation.legacy_provider import LegacySchemaProvider

# Register providers with legacy as default for backward compatibility
SchemaProviderRegistry.register(LegacySchemaProvider(), make_default=True)
try:
    from writer.validation.jtd_provider import JTDSchemaProvider
    # Register JTD as optional provider if available
    SchemaProviderRegistry.register(JTDSchemaProvider())
except ImportError:
    # JTD not available, that's fine - legacy will handle everything
    pass


class APITrigger(BlueprintTrigger):
    @classmethod
    def register(cls, type: str):
        super(APITrigger, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "API Trigger",
                    "description": "Triggers an event via API call.",
                    "category": "Triggers",
                    "fields": {
                        "blueprintId": {
                            "name": "Blueprint ID",
                            "type": "Blueprint Id",
                        },
                        "defaultResult": {
                            "name": "Default result",
                            "type": "Code",
                            "desc": 'The result that is used when the blueprint is triggered from the "Run blueprint" button',
                            "isArtifactField": True,
                        },
                        "enableValidation": {
                            "name": "Enable input validation",
                            "type": "Boolean",
                            "default": False,
                            "desc": "Enable validation of incoming API payloads",
                        },
                        "inputFields": {
                            "name": "Input fields",
                            "type": "Object",
                            "default": "[]",
                            "desc": "Define expected input fields for validation",
                            "isArtifactField": True,
                        },
                        "strictValidation": {
                            "name": "Reject unknown fields",
                            "type": "Boolean",
                            "default": "no",
                            "desc": ("Reject payloads that contain fields not "
                                     "defined in the schema"),
                            "isArtifactField": True,
                        },
                    },
                    "outs": {
                        "trigger": {
                            "name": "Trigger",
                            "style": "success",
                        },
                    },
                    "settingsArtifacts": [
                        {"key": "apiFieldDefinitions", "position": "bottom"},
                        {"key": "apiTriggerDetails", "position": "bottom"}
                    ]
                },
            ),
        )

    def run(self):
        super().run()

        # If validation is enabled and we have a payload, validate it
        enable_validation = self._get_field("enableValidation", False, "no")
        if self.result is not None and enable_validation == "yes":
            try:
                input_fields_str = self._get_field(
                    "inputFields", False, "[]")
                if isinstance(input_fields_str, str):
                    import json
                    input_fields = json.loads(input_fields_str)
                else:
                    input_fields = input_fields_str

                # Convert result to dict if it's a JSON string
                payload = self.result
                if isinstance(payload, str):
                    payload = json.loads(payload)

                # Check if strict validation is enabled
                strict_validation_raw = self._get_field("strictValidation", False, "no")
                strict_validation = strict_validation_raw == "yes"

                # Validate the payload
                is_valid, error_message = self.validate_payload(
                    payload, input_fields, strict_validation)
                if not is_valid:
                    raise ValueError(
                        f"Payload validation failed: {error_message}")
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in payload or input fields: {str(e)}")
            except ValueError:
                self.outcome = "error"
                # Re-raise validation errors as-is
                raise
            except Exception as e:
                self.outcome = "error"
                raise RuntimeError(f"Validation error: {str(e)}")
        self.outcome = "trigger"
    
    @staticmethod
    def validate_payload(
        payload: Dict[str, Any],
        field_definitions: List[Dict[str, Any]],
        strict: bool = False,
        provider_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validate API payload against field definitions using pluggable providers.
        
        Args:
            payload: JSON data to validate
            field_definitions: Field definition schema
            strict: If True, reject payloads with undefined fields
            provider_name: Optional provider name ("legacy", "jtd", etc.)
            
        Returns:
            Tuple of (is_valid, error_message) for backward compatibility
        """
        try:
            provider = SchemaProviderRegistry.get_provider(provider_name)
            result = provider.validate_payload(payload, field_definitions, strict)
            return result.is_valid, result.error_message
        except Exception as e:
            return False, f"Validation error: {str(e)}"
