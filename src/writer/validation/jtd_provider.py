"""
JSON Typedef (JTD) schema validation provider.
"""
from typing import Any, Dict, List, Optional

from .base import SchemaProvider, ValidationError, ValidationResult

try:
    import jtd  # type: ignore[import-untyped]
    JTD_AVAILABLE = True
except ImportError:
    JTD_AVAILABLE = False


class JTDSchemaProvider(SchemaProvider):
    """Schema provider using JSON Typedef (RFC 8927) validation."""
    
    def __init__(self, max_depth: int = 5):
        """
        Initialize JTD provider.
        
        Args:
            max_depth: Maximum recursion depth for refs (security limit)
        """
        if not JTD_AVAILABLE:
            raise ImportError(
                "JTD provider requires 'jtd' package. "
                "Install with: pip install jtd"
            )
        self.max_depth = max_depth
    
    @property
    def name(self) -> str:
        return "jtd"
    
    @property
    def supports_advanced_features(self) -> bool:
        return True
    
    def validate_field_definitions(
        self, 
        field_definitions: List[Dict[str, Any]]
    ) -> ValidationResult:
        """Validate that field definitions can be converted to valid JTD."""
        try:
            # Try to convert to JTD schema
            jtd_schema_dict = self._field_definitions_to_jtd_schema(
                field_definitions
            )
            
            # Validate the resulting JTD schema
            schema = jtd.Schema.from_dict(jtd_schema_dict)
            schema.validate()
            
            return ValidationResult.success()
            
        except ValueError as e:
            # Our conversion errors (unknown types, etc.)
            return ValidationResult.failure(str(e))
        except (AttributeError, TypeError) as e:
            # JTD schema validation errors
            return ValidationResult.failure(f"Invalid schema: {str(e)}")
        except Exception as e:
            return ValidationResult.failure(f"Schema validation error: {str(e)}")
    
    def validate_payload(
        self, 
        payload: Dict[str, Any], 
        field_definitions: List[Dict[str, Any]],
        strict: bool = False
    ) -> ValidationResult:
        """Validate payload using JTD."""
        if not isinstance(payload, dict):
            return ValidationResult.failure(
                "Payload must be a JSON object"
            )
        
        # If strict mode, check for unknown fields first
        if strict:
            defined_fields = {field_def.get("name") for field_def in field_definitions}
            payload_fields = set(payload.keys())
            unknown_fields = payload_fields - defined_fields
            if unknown_fields:
                unknown_list = sorted(unknown_fields)
                return ValidationResult.failure(
                    f"Unknown fields not allowed: {', '.join(unknown_list)}"
                )
        
        # First validate field definitions
        field_validation = self.validate_field_definitions(field_definitions)
        if not field_validation.is_valid:
            return field_validation
        
        try:
            # Convert to JTD schema
            jtd_schema_dict = self._field_definitions_to_jtd_schema(
                field_definitions
            )
            schema = jtd.Schema.from_dict(jtd_schema_dict)
            
            # Validate payload
            options = jtd.ValidationOptions(max_depth=self.max_depth)
            errors = jtd.validate(
                schema=schema, 
                instance=payload, 
                options=options
            )
            
            if not errors:
                return ValidationResult.success()
            
            # Convert JTD errors to our format
            validation_errors = []
            for error in errors:
                field_path = "/".join(str(p) for p in error.instance_path) \
                    if error.instance_path else ""
                schema_path = "/".join(str(p) for p in error.schema_path) \
                    if error.schema_path else ""
                
                # Create user-friendly error message
                if field_path:
                    if "properties" in schema_path:
                        message = f"Invalid value for field: '{field_path}'"
                    else:
                        message = f"Validation error at field: '{field_path}'"
                else:
                    if "properties" in schema_path:
                        message = "Missing required field"
                    else:
                        message = "Validation error"
                
                validation_errors.append(ValidationError(
                    field_path=field_path,
                    message=message,
                    schema_path=schema_path
                ))
            
            return ValidationResult(is_valid=False, errors=validation_errors)
            
        except jtd.MaxDepthExceededError:
            return ValidationResult.failure(
                "Schema too complex (max depth exceeded)"
            )
        except Exception as e:
            return ValidationResult.failure(f"Validation error: {str(e)}")
    
    def _field_definitions_to_jtd_schema(
        self, 
        field_definitions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Convert field definitions to JTD schema format."""
        properties = {}
        optional_properties = {}
        
        # Map field types to JTD types
        type_mapping = {
            "string": "string",
            "number": "float64",
            "integer": "int32", 
            "boolean": "boolean",
            "array": {"elements": {}},  # Generic array
            "object": {"values": {}},   # Generic object (dictionary)
            "null": {"nullable": {}}    # Null handled via nullable wrapper
        }
        
        for field_def in field_definitions:
            field_name = field_def.get("name")
            field_type = field_def.get("type")
            is_required = field_def.get("required", False)
            
            if not field_name or not field_type:
                continue
                
            # Handle type mapping
            if field_type in type_mapping:
                type_value = type_mapping[field_type]
                if isinstance(type_value, dict):
                    # Complex types
                    schema_def = type_value.copy()
                else:
                    # Simple types
                    schema_def = {"type": type_value}
            else:
                raise ValueError(
                    f"Unknown field type: '{field_type}' for field '{field_name}'"
                )
            
            # Place in appropriate properties dict
            if is_required:
                properties[field_name] = schema_def
            else:
                optional_properties[field_name] = schema_def
        
        # Build JTD schema
        schema = {}
        if properties:
            schema["properties"] = properties
        if optional_properties:
            schema["optionalProperties"] = optional_properties
            
        return schema