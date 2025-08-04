from typing import Any, Dict, List, Tuple

from writer.abstract import register_abstract_template
from writer.blocks.base_trigger import BlueprintTrigger
from writer.ss_types import AbstractTemplate


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
                    },
                    "outs": {
                        "trigger": {
                            "name": "Trigger",
                            "style": "success",
                        },
                    },
                    "settingsArtifacts": [
                        {"key": "apiTriggerDetails", "position": "bottom"}
                    ]
                },
            ),
        )

    def run(self):
        super().run()
        self.outcome = "trigger"
    
    @staticmethod
    def validate_payload(payload: Dict[str, Any], field_definitions: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate API payload against field definitions."""
        if not isinstance(payload, dict):
            return False, "Payload must be a JSON object"
            
        for field_def in field_definitions:
            field_name = field_def.get("name")
            is_required = field_def.get("required", False)
            
            # Check presence
            if is_required and field_name not in payload:
                return False, f"Missing required field: '{field_name}'"
            if field_name not in payload:
                continue
                
            # Validate field
            is_valid, error_msg = APITrigger._validate_field(payload[field_name], field_def)
            if not is_valid:
                return False, error_msg
                
        return True, "Valid"
    
    @staticmethod
    def _validate_field(value: Any, field_def: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate single field with type and constraint checks."""
        field_name = field_def.get("name")
        field_type = field_def.get("type")
        
        # Type validators
        type_checks = {
            "string": lambda v: isinstance(v, str),
            "number": lambda v: isinstance(v, (int, float)),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict),
            "null": lambda v: v is None,
        }
        
        if field_type not in type_checks or not type_checks[field_type](value):
            return False, f"Field '{field_name}' must be a {field_type}"
        
        # Constraint checks
        if field_type == "string":
            if "minLength" in field_def and len(value) < field_def["minLength"]:
                return False, f"Field '{field_name}' too short (min {field_def['minLength']})"
            if "maxLength" in field_def and len(value) > field_def["maxLength"]:
                return False, f"Field '{field_name}' too long (max {field_def['maxLength']})"
        elif field_type in ("number", "integer"):
            if "minValue" in field_def and value < field_def["minValue"]:
                return False, f"Field '{field_name}' below minimum ({field_def['minValue']})"
            if "maxValue" in field_def and value > field_def["maxValue"]:
                return False, f"Field '{field_name}' above maximum ({field_def['maxValue']})"
        
        return True, "Valid"
