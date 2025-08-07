#!/usr/bin/env python3

import json
import sys

sys.path.append('src')

from writer.blocks.apitrigger import APITrigger

# Test different ways the strictValidation field might be stored
test_cases = [
    {"strictValidation": "yes", "description": "String 'yes'"},
    {"strictValidation": "no", "description": "String 'no'"},
    {"strictValidation": True, "description": "Boolean True"},
    {"strictValidation": False, "description": "Boolean False"},
    {"strictValidation": "true", "description": "String 'true'"},
    {"strictValidation": "false", "description": "String 'false'"},
    {"strictValidation": "", "description": "Empty string"},
    {"strictValidation": None, "description": "None"},
]

class MockAPITrigger(APITrigger):
    def __init__(self, strict_validation_value):
        self.content = {
            "enableValidation": "yes",
            "strictValidation": strict_validation_value,
            "defaultResult": '{"tebst": "test"}',
            "inputFields": '[{"name": "test", "type": "string", "required": false}]'
        }
        self.execution_environment = {}
        
    def _get_field(self, field_name, is_code_field=False, default=None):
        return self.content.get(field_name, default)

print("Testing different strictValidation values:")
print("=" * 60)

for case in test_cases:
    value = case["strictValidation"]
    description = case["description"]
    
    print(f"\nTesting {description}: {repr(value)}")
    
    trigger = MockAPITrigger(value)
    
    # Check what the comparison evaluates to
    strict_check = trigger._get_field("strictValidation", False, "no") == "yes"
    print(f"  _get_field result: {repr(trigger._get_field('strictValidation', False, 'no'))}")
    print(f"  Strict check (== 'yes'): {strict_check}")
    
    try:
        trigger.run()
        print("  Result: ✅ SUCCESS (validation passed)")
    except ValueError as e:
        print(f"  Result: ❌ FAILED (validation caught error: {e})")
    except Exception as e:
        print(f"  Result: ❓ ERROR ({type(e).__name__}: {e})")

print("\n" + "=" * 60)
print("Expected behavior: Only 'String yes' should fail with validation error")