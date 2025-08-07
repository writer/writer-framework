#!/usr/bin/env python3

import json
import sys

sys.path.append('src')

from writer.blocks.apitrigger import APITrigger


# Create a mock API trigger to test the exact scenario
class MockAPITrigger(APITrigger):
    def __init__(self):
        # Mock the component fields
        self.content = {
            "enableValidation": "yes",
            "strictValidation": "yes", 
            "defaultResult": '{"tebst": "test"}',  # Wrong field name
            "inputFields": '[{"name": "test", "type": "string", "required": false}]'
        }
        # Mock execution environment (no payload, so it should use defaultResult)
        self.execution_environment = {}
        
    def _get_field(self, field_name, is_code_field=False, default=None):
        """Mock the _get_field method"""
        return self.content.get(field_name, default)

# Test the scenario
print("Testing API Trigger validation with 'Run blueprint'...")
print("Settings:")
print("- enableValidation: yes")  
print("- strictValidation: yes")
print("- field definition: test (string)")
print("- defaultResult: {\"tebst\": \"test\"} (wrong field name)")
print()

trigger = MockAPITrigger()

try:
    trigger.run()
    print("❌ ERROR: Blueprint run succeeded when it should have failed!")
    print(f"Result: {trigger.result}")
    print(f"Outcome: {getattr(trigger, 'outcome', 'unknown')}")
except ValueError as e:
    print("✅ SUCCESS: Blueprint run failed as expected")
    print(f"Error: {e}")
    print(f"Outcome: {getattr(trigger, 'outcome', 'unknown')}")
except Exception as e:
    print(f"❓ UNEXPECTED ERROR: {type(e).__name__}: {e}")
    print(f"Outcome: {getattr(trigger, 'outcome', 'unknown')}")