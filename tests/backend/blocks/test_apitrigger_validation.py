"""
Tests for API trigger input validation functionality.
"""
import pytest
from writer.blocks.apitrigger import APITrigger


class TestAPITriggerValidation:
    """Test cases for API trigger payload validation."""

    def test_validate_payload_basic_types(self):
        """Test validation with all basic JSON types."""
        field_defs = [
            {"name": "user_id", "type": "string", "required": True},
            {"name": "age", "type": "integer", "required": False},
            {"name": "score", "type": "number", "required": False},
            {"name": "is_active", "type": "boolean", "required": True},
            {"name": "preferences", "type": "object", "required": False},
            {"name": "tags", "type": "array", "required": False},
            {"name": "optional_null", "type": "null", "required": False}
        ]
        
        # Valid payload with all types
        valid_payload = {
            "user_id": "abc123",
            "age": 25,
            "score": 85.5,
            "is_active": True,
            "preferences": {"theme": "dark"},
            "tags": ["premium", "beta"],
            "optional_null": None
        }
        is_valid, error_msg = APITrigger.validate_payload(valid_payload, field_defs)
        assert is_valid == True
        assert error_msg == "Valid"

    def test_validate_payload_required_fields(self):
        """Test required field validation."""
        field_defs = [
            {"name": "user_id", "type": "string", "required": True},
            {"name": "email", "type": "string", "required": True},
            {"name": "age", "type": "integer", "required": False}
        ]
        
        # Missing required field
        payload = {"user_id": "test123"}  # Missing email
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "Missing required field: 'email'" in error_msg
        
        # All required fields present
        payload = {"user_id": "test123", "email": "test@example.com"}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == True

    def test_validate_payload_type_validation(self):
        """Test type validation for each JSON type."""
        field_defs = [
            {"name": "name", "type": "string", "required": True},
            {"name": "age", "type": "integer", "required": False},
            {"name": "score", "type": "number", "required": False},
            {"name": "active", "type": "boolean", "required": False},
            {"name": "data", "type": "object", "required": False},
            {"name": "items", "type": "array", "required": False},
            {"name": "nullable", "type": "null", "required": False}
        ]
        
        # Wrong string type
        payload = {"name": 123}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "must be a string" in error_msg
        
        # Wrong integer type
        payload = {"name": "test", "age": "twenty"}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "must be a integer" in error_msg
        
        # Wrong number type
        payload = {"name": "test", "score": "eighty-five"}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "must be a number" in error_msg
        
        # Wrong boolean type (integer 1 should not be valid boolean)
        payload = {"name": "test", "active": 1}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "must be a boolean" in error_msg
        
        # Wrong object type
        payload = {"name": "test", "data": []}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "must be a object" in error_msg
        
        # Wrong array type
        payload = {"name": "test", "items": {}}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "must be a array" in error_msg
        
        # Wrong null type
        payload = {"name": "test", "nullable": "not_null"}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "must be a null" in error_msg

    def test_validate_payload_string_constraints(self):
        """Test string length constraints."""
        field_defs = [
            {"name": "username", "type": "string", "required": True, "minLength": 3, "maxLength": 20},
            {"name": "bio", "type": "string", "required": False, "maxLength": 500}
        ]
        
        # String too short
        payload = {"username": "ab"}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "too short" in error_msg
        assert "min 3" in error_msg
        
        # String too long
        payload = {"username": "this_username_is_way_too_long_for_our_constraints"}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "too long" in error_msg
        assert "max 20" in error_msg
        
        # Valid string lengths
        payload = {"username": "validuser", "bio": "Short bio"}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == True

    def test_validate_payload_numeric_constraints(self):
        """Test numeric range constraints for both number and integer types."""
        field_defs = [
            {"name": "age", "type": "integer", "required": True, "minValue": 0, "maxValue": 150},
            {"name": "score", "type": "number", "required": False, "minValue": 0.0, "maxValue": 100.0}
        ]
        
        # Integer below minimum
        payload = {"age": -5}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "below minimum" in error_msg
        assert "(0)" in error_msg
        
        # Integer above maximum
        payload = {"age": 200}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "above maximum" in error_msg
        assert "(150)" in error_msg
        
        # Number below minimum
        payload = {"age": 25, "score": -10.5}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "below minimum" in error_msg
        assert "(0.0)" in error_msg
        
        # Number above maximum
        payload = {"age": 25, "score": 110.5}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == False
        assert "above maximum" in error_msg
        assert "(100.0)" in error_msg
        
        # Valid numeric ranges
        payload = {"age": 25, "score": 85.5}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == True

    def test_validate_payload_edge_cases(self):
        """Test edge cases and boundary conditions."""
        field_defs = [
            {"name": "flag", "type": "boolean", "required": True}
        ]
        
        # Non-dict payload
        is_valid, error_msg = APITrigger.validate_payload("not_a_dict", field_defs)
        assert is_valid == False
        assert "must be a JSON object" in error_msg
        
        # Empty field definitions (should pass any payload)
        payload = {"anything": "goes"}
        is_valid, error_msg = APITrigger.validate_payload(payload, [])
        assert is_valid == True
        
        # Empty payload with no required fields
        field_defs = [{"name": "optional", "type": "string", "required": False}]
        is_valid, error_msg = APITrigger.validate_payload({}, field_defs)
        assert is_valid == True
        
        # Boolean edge cases (Python bool is subclass of int)
        payload = {"flag": True}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == True
        
        payload = {"flag": False}
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == True

    def test_validate_payload_no_nested_validation(self):
        """Test that arrays and objects are not validated recursively (by design)."""
        field_defs = [
            {"name": "config", "type": "object", "required": True},
            {"name": "items", "type": "array", "required": True}
        ]
        
        # Any object structure should be valid
        payload = {
            "config": {
                "nested": {"deeply": {"anything": "goes"}},
                "mixed_types": [1, "string", True, None]
            },
            "items": [
                "strings",
                123,
                {"objects": "allowed"},
                [1, 2, 3],
                None
            ]
        }
        is_valid, error_msg = APITrigger.validate_payload(payload, field_defs)
        assert is_valid == True