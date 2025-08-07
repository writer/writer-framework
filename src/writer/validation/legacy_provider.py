"""
Legacy schema validation provider - wraps the existing custom validator.
"""
from typing import Any, Dict, List, Tuple

from .base import SchemaProvider, ValidationError, ValidationResult


class LegacySchemaProvider(SchemaProvider):
    """Schema provider that wraps the original custom validation logic."""
    
    @property
    def name(self) -> str:
        return "legacy"
    
    def validate_field_definitions(
        self, 
        field_definitions: List[Dict[str, Any]]
    ) -> ValidationResult:
        """Validate field definitions format."""
        try:
            for field_def in field_definitions:
                # Check required keys
                if not isinstance(field_def, dict):
                    return ValidationResult.failure(
                        "Field definition must be an object"
                    )
                
                if "name" not in field_def or "type" not in field_def:
                    return ValidationResult.failure(
                        "Field definition must have 'name' and 'type'"
                    )
                
                # Validate field type
                field_type = field_def.get("type")
                valid_types = {
                    "string", "number", "integer", "boolean", 
                    "array", "object", "null"
                }
                if field_type not in valid_types:
                    return ValidationResult.failure(
                        f"Unknown field type: '{field_type}'"
                    )
            
            return ValidationResult.success()
            
        except Exception as e:
            return ValidationResult.failure(f"Field definition error: {str(e)}")
    
    def validate_payload(
        self, 
        payload: Dict[str, Any], 
        field_definitions: List[Dict[str, Any]],
        strict: bool = False
    ) -> ValidationResult:
        """Validate payload using original validation logic."""
        # First validate the field definitions
        field_validation = self.validate_field_definitions(field_definitions)
        if not field_validation.is_valid:
            return field_validation
        
        # Then validate the payload
        is_valid, error_msg = self._legacy_validate_payload(
            payload, field_definitions, strict
        )
        
        if is_valid:
            return ValidationResult.success()
        else:
            return ValidationResult.failure(error_msg)
    
    @staticmethod
    def _legacy_validate_payload(
        payload: Dict[str, Any], 
        field_definitions: List[Dict[str, Any]],
        strict: bool = False
    ) -> Tuple[bool, str]:
        """Original validation logic from apitrigger.py."""
        if not isinstance(payload, dict):
            return False, "Payload must be a JSON object"
        
        # Get list of defined field names for strict validation
        defined_fields = {field_def.get("name") for field_def in field_definitions}
        
        # If strict mode, check for unknown fields
        if strict:
            payload_fields = set(payload.keys())
            unknown_fields = payload_fields - defined_fields
            if unknown_fields:
                unknown_list = sorted(unknown_fields)
                return False, f"Unknown fields not allowed: {', '.join(unknown_list)}"
            
        for field_def in field_definitions:
            field_name = field_def.get("name")
            is_required = field_def.get("required", False)
            
            # Check presence
            if is_required and field_name not in payload:
                return False, f"Missing required field: '{field_name}'"
            if field_name not in payload:
                continue
                
            # Validate field
            is_valid, error_msg = LegacySchemaProvider._validate_field(
                payload[field_name], field_def
            )
            if not is_valid:
                return False, error_msg
                
        return True, "Valid"
    
    @staticmethod
    def _validate_field(
        value: Any, 
        field_def: Dict[str, Any]
    ) -> Tuple[bool, str]:
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
                return False, (
                    f"Field '{field_name}' too short "
                    f"(min {field_def['minLength']})"
                )
            if "maxLength" in field_def and len(value) > field_def["maxLength"]:
                return False, (
                    f"Field '{field_name}' too long "
                    f"(max {field_def['maxLength']})"
                )
        elif field_type in ("number", "integer"):
            if "minValue" in field_def and value < field_def["minValue"]:
                return False, (
                    f"Field '{field_name}' below minimum "
                    f"({field_def['minValue']})"
                )
            if "maxValue" in field_def and value > field_def["maxValue"]:
                return False, (
                    f"Field '{field_name}' above maximum "
                    f"({field_def['maxValue']})"
                )
        
        return True, "Valid"