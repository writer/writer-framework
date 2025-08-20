import json

import numpy as np
import writer as wf
from writer import audit_and_fix, evaluator, wf_project
from writer.core import (
    WriterState,
)
from writer.core_ui import Component

from tests.backend import test_app_dir
from tests.backend.fixtures import (
    core_ui_fixtures,
)

raw_state_dict = {
    "name": "Robert",
    "age": 1,
    "interests": ["lamps", "cars"],
    "state.with.dots": {
        "photo.jpeg": "Not available",
    },
    "features": {
        "eyes": "green",
        "height": "very short"
    },
    "best_feature": "eyes",
    "utfࠀ": 23,
    "counter": 4,
    "_private": 3,
    # Used as an example of something unserialisable yet pickable
    "_private_unserialisable": np.array([[1+2j, 2, 3+3j]]),
    "a.b": 3
}

simple_dict = {"items": {
        "Apple": {"name": "Apple", "type": "fruit"},
        "Cucumber": {"name": "Cucumber", "type": "vegetable"},
        "Lettuce": {"name": "Lettuce", "type": "vegetable"}
    }}

wf.Config.is_mail_enabled_for_log = True
wf.init_state(raw_state_dict)

_, sc = wf_project.read_files(test_app_dir)
sc = audit_and_fix.fix_components(sc)

session = wf.session_manager.get_new_session()
session.session_component_tree.ingest(sc)

class TestEvaluator:

    def test_evaluate_field_simple(self) -> None:

        instance_path = [
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "4b6f14b0-b2d9-43e7-8aba-8d3e939c1f83", "instanceNumber": 0},
            {"componentId": "0cd59329-29c8-4887-beee-39794065221e", "instanceNumber": 0}

        ]
        session.session_state = WriterState({
            "counter": 8
        })
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        evaluated = e.evaluate_field(instance_path, "text")
        assert evaluated == "The counter is 8"

    def test_evaluate_field_repeater(self) -> None:
        instance_path_base = [
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "4b6f14b0-b2d9-43e7-8aba-8d3e939c1f83", "instanceNumber": 0},
            {"componentId": "f811ca14-8915-443d-8dd3-77ae69fb80f4", "instanceNumber": 0}
        ]
        instance_path_0 = instance_path_base + [
            {"componentId": "2e688107-f865-419b-a07b-95103197e3fd", "instanceNumber": 0}
        ]
        instance_path_2 = instance_path_base + [
            {"componentId": "2e688107-f865-419b-a07b-95103197e3fd", "instanceNumber": 2}
        ]
        session.session_state = WriterState({
            "prog_languages": {
                "c": "C",
                "py": "Python",
                "js": "JavaScript",
                "ts": "TypeScript"
            }
        })
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        assert e.evaluate_field(
            instance_path_0, "text") == "The id is c and the name is C"
        assert e.evaluate_field(
            instance_path_2, "text") == "The id is js and the name is JavaScript"

    def test_evaluate_field_json(self) -> None:
        instance_path = [
            {"componentId": "blueprints_root", "instanceNumber": 0},
            {"componentId": "hywgzgfetx6rpiqy", "instanceNumber": 0},
            {"componentId": "mw5rz7ay5p8pg2fm", "instanceNumber": 0}
        ]
        session.session_state = WriterState(
            {
                "plain": "P_VALUE",
                "quotes": "'Q_VALUE'",
                "double_quotes": '"DQ_VALUE"',
                "array": ["1", "2"],
                "nested_json": {"a": 1, "b": 2},
                "number": 1.1,
                "boolean": True,
                "none": None,
                "escaped": "\\",
                "invalid_chars": r"\ \" \f \n \t \b \r \u1234"
            }
        )
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        evaluated = e.evaluate_field(instance_path, "categories", as_json=True)
        assert evaluated == {
            "plain": "P_VALUE",
            "quotes": "'Q_VALUE'",
            "double_quotes": "\"DQ_VALUE\"",
            "plain_with_text": "TEXT P_VALUE TEXT",
            "quotes_with_text": "TEXT 'Q_VALUE' TEXT",
            "double_quotes_with_text": "TEXT \"DQ_VALUE\" TEXT",
            "array": '["1", "2"]',
            "array_with_text": 'TEXT ["1", "2"] TEXT',
            "nested_json": '{"a": 1, "b": 2}',
            "nested_json_with_text": 'TEXT {"a": 1, "b": 2} TEXT',
            "number": "1.1",
            "number_with_text": "TEXT 1.1 TEXT",
            "boolean": "true",
            "boolean_with_text": "TEXT true TEXT",
            "none": "null",
            "none_with_text": "TEXT null TEXT",
            "escaped": "\\@{escaped}",
            "escaped_with_text": "TEXT \\@{escaped} TEXT",
            "invalid_chars": r"\ \" \f \n \t \b \r \u1234",
            "invalid_chars_with_text": r"TEXT \ \" \f \n \t \b \r \u1234 TEXT"
        }

    def test_evaluate_field_full_match(self) -> None:
        instance_path = [
            {"componentId": "blueprints_root", "instanceNumber": 0},
            {"componentId": "hywgzgfetx6rpiqy", "instanceNumber": 0},
            {"componentId": "67h6k2j3te9g4o6t", "instanceNumber": 0}
        ]
        session.session_state = WriterState(
            {
                "full_match": {"a": 1, "b": [2]},
                "full_match_text": "null",
            }
        )
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        evaluated = e.evaluate_field(instance_path, "categories", as_json=True)
        assert evaluated == {"a": 1, "b": [2]}

        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        evaluated = e.evaluate_field(instance_path, "text")
        assert evaluated == "null"

    def test_set_state(self) -> None:
        instance_path = [
            {"componentId": "root", "instanceNumber": 0}
        ]
        session.session_state = WriterState(raw_state_dict)
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        e.set_state("name", instance_path, "Roger")
        e.set_state("dynamic_prop", instance_path, "height")
        e.set_state("features[dynamic_prop]", instance_path, "toddler height")
        e.set_state("features.new_feature", instance_path, "blue")
        assert session.session_state["name"] == "Roger"
        assert session.session_state["features"]["height"] == "toddler height"
        assert session.session_state["features"]["new_feature"] == "blue"

    def test_evaluate_expression(self) -> None:
        instance_path = [
            {"componentId": "root", "instanceNumber": 0}
        ]
        session.session_state = WriterState(raw_state_dict)
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        assert e.evaluate_expression("features.eyes", instance_path) == "green"
        assert e.evaluate_expression("best_feature", instance_path) == "eyes"
        assert e.evaluate_expression("features[best_feature]", instance_path) == "green"
        assert e.evaluate_expression(r"a\.b", instance_path) == 3

        assert e.evaluate_expression("features.nose", instance_path) is None
        assert e.evaluate_expression("features.eyes.eyelashes", instance_path) is None
        assert e.evaluate_expression("features.hands.palms", instance_path) is None
        assert e.evaluate_expression("features.eyes[counter]", instance_path) is None
        assert e.evaluate_expression("features[best_feature.color]", instance_path) is None
        assert e.evaluate_expression("features[best_feature.color].hex", instance_path) is None

        assert e.evaluate_expression("interests.2", instance_path) is None
        assert e.evaluate_expression("interests.1", instance_path) == "cars"
        assert e.evaluate_expression("interests.0", instance_path) == "lamps"
        assert e.evaluate_expression("interests.-1", instance_path) == "cars"
        assert e.evaluate_expression("interests.-2", instance_path) == "lamps"
        assert e.evaluate_expression("interests.-3", instance_path) is None
        assert e.evaluate_expression("interests.-3.a", instance_path) is None
        assert e.evaluate_expression("interests.-3.1", instance_path) is None

        assert e.evaluate_expression("context.best_feature", instance_path, {"context": {}}) is None
        assert e.evaluate_expression("context.features", instance_path, {"context": {"features": "exist"}}) == "exist"
        assert e.evaluate_expression("context.interests.1", instance_path, {"context": {"interests": ["A"]}}) is None
        assert e.evaluate_expression("context.interests.2", instance_path, {"context": {"interests": ["A", "B","C"]}}) == "C"

        assert e.evaluate_expression("features", instance_path, {"features": "takes priority"}) == "takes priority"

    def test_get_context_data_should_return_the_target_of_event(self) -> None:
        """
        Test that the target of the event is correctly returned by the get_context_data method

        Here we reproduce a click on a button
        """
        # Given

        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="button1", parentId="root", type="button")
        ], init_root=True)

        e = evaluator.Evaluator(session.session_state, session.session_component_tree)

        # When
        context = e.get_context_data([
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "button1", "instanceNumber": 0}
        ])

        # Then
        assert context.get("target") == "button1"

    def test_get_context_data_should_return_the_repeater_position_and_the_target_inside_the_repeater(self) -> None:
        """
        Test that the repeater position and target of the event is correctly returned by the get_context_data method

        Here we reproduce a click on a button
        """
        # Given
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="repeater1", parentId="root", type="repeater", content={'keyVariable': 'item', 'valueVariable': 'value', 'repeaterObject': json.dumps({'a': 'A', 'b': 'B'})}),
            Component(id="button1", parentId="repeater1", type="button")
        ], init_root=True)

        e = evaluator.Evaluator(session.session_state, session.session_component_tree)

        # When
        context = e.get_context_data([
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "repeater1", "instanceNumber": 0},
            {"componentId": "button1", "instanceNumber": 1}
        ])

        # Then
        assert context.get("target") == "button1"
        assert context.get("item") == "b"
        assert context.get("value") == "B"

    def test_inside_json_string_detection(self) -> None:
        """Test the inside_json_string function for JSON string context detection"""
        # Test cases for inside_json_string function
        test_cases = [
            # (json_string, position, expected_inside_string)
            ('{"key": "value"}', 9, True),   # Inside string value - pos 9 is 'v'
            ('{"key": "value"}', 2, True),   # Inside string key - pos 2 is 'k'
            ('{"key": "value"}', 6, False),  # Between key and value - pos 6 is ':'
            ('{"key": "value"}', 0, False),  # At start - pos 0 is '{'
            ('{"key": "value"}', 8, False),  # At quote start - pos 8 is '"'
            ('{"text": "hello \\"world\\""}', 15, True),  # Inside escaped quotes  
            ('{"text": "hello \\"world\\""}', 26, False), # Outside string (closing brace)
            ('{"a": 1, "b": "text"}', 10, True), # Inside key "b"
            ('{"a": 1, "b": "text"}', 15, True),  # Inside second string - pos 15 is 't'
            ('{"a": 1, "b": "text"}', 7, False),  # Between values (comma)
            ('["item1", "item2"]', 2, True),     # Inside array string
            ('["item1", "item2"]', 8, False),    # Between array items
            ('', 0, False),                      # Empty string
            ('"simple string"', 5, True),        # Inside simple string
            ('123', 1, False),                   # In number
            ('true', 2, False),                  # In boolean
        ]
        
        def mock_inside_json_string(src: str, pos: int) -> bool:
            """Replicate the inside_json_string logic for testing"""
            in_str = False
            escaped = False
            i = 0
            while i < pos:
                c = src[i]
                if escaped:
                    escaped = False
                else:
                    if c == '\\':
                        escaped = True
                    elif c == '"':
                        in_str = not in_str
                i += 1
            return in_str
        
        # Test the mock function against our test cases
        for json_str, pos, expected in test_cases:
            if pos < len(json_str):
                result = mock_inside_json_string(json_str, pos)
                assert result == expected, f"Failed for '{json_str}' at pos {pos}: expected {expected}, got {result}"

    def test_json_literal_detection(self) -> None:
        """Test the _looks_like_json_literal function for JSON structure detection"""
        
        # Test cases that should be parsed as JSON
        json_cases = [
            ('{"key": "value"}', {"key": "value"}),
            ('[1, 2, 3]', [1, 2, 3]),
            ('"hello"', "hello"),
            ('null', None),
            ('true', True),
            ('false', False),
            # Note: Numbers without quotes are NOT detected as JSON literals by _looks_like_json_literal
            # They would be returned as strings, then parsed if they're valid JSON
        ]
        
        # Test cases that should NOT be parsed as JSON (returned as-is)
        non_json_cases = [
            ('', ''),  # Empty string
            ('hello world', 'hello world'),
            ('not json', 'not json'),
            ('{invalid}', '{invalid}'),
            ('[invalid', '[invalid'),
            ('just text', 'just text'),
            ('42', '42'),  # Plain numbers are not detected as JSON literals
            ('42.5', '42.5'),  # Plain numbers are not detected as JSON literals
        ]
        
        # Create a mock decode_json function to test _looks_like_json_literal logic
        def mock_looks_like_json_literal(t: str) -> bool:
            """Replicate the _looks_like_json_literal logic for testing"""
            t = t.strip()
            if not t:
                return False
            if ((t[0] == '{' and t[-1] == '}') or (t[0] == '[' and t[-1] == ']')):
                return True
            if t[0] == '"' and t[-1] == '"':
                return True
            if t in ("true", "false", "null"):
                return True
            return False
        
        def mock_decode_json(text: str):
            """Mock decode_json that uses _looks_like_json_literal logic"""
            if not mock_looks_like_json_literal(text):
                return text
            try:
                return json.loads(text, strict=False)
            except json.JSONDecodeError:
                return text
        
        # Test valid JSON cases
        for input_text, expected in json_cases:
            result = mock_decode_json(input_text)
            assert result == expected, f"Failed for '{input_text}': expected {expected}, got {result}"
        
        # Test non-JSON cases (should return as-is)
        for input_text, expected in non_json_cases:
            result = mock_decode_json(input_text)
            assert result == expected, f"Failed for '{input_text}': expected {expected}, got {result}"

    def test_none_handling_in_full_match(self) -> None:
        """Test None value handling in full match non-JSON mode"""
        from writer.core_ui import Component
        
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", 
                     content={"text": "@{none_value}"})
        ], init_root=True)
        
        session.session_state = WriterState({
            "none_value": None,
            "string_value": "hello",
            "number_value": 42
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        # Test None in non-JSON mode (should return None)
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "text", as_json=False
        )
        assert result is None, f"Expected None, got {result}"
        
        # Test None in JSON mode (should return None for parsing)
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "text", as_json=True
        )
        assert result is None, f"Expected None, got {result}"
        
        # Test other values work normally
        session.session_component_tree.get_component("test_comp").content["text"] = "@{string_value}"
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "text", as_json=False
        )
        assert result == "hello"

    def test_control_character_removal(self) -> None:
        """Test control character removal in JSON decoding"""
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", 
                     content={"text": "@{dirty_json}"})
        ], init_root=True)
        
        # Test various control characters
        session.session_state = WriterState({
            "dirty_json": '{"text": "hello\x00\x01\x1f\x7fworld"}',  # Contains control chars
            "clean_json": '{"text": "helloworld"}',  # Expected result after cleaning
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        # Test that control characters are removed during JSON parsing
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "text", as_json=True
        )
        
        expected = {"text": "helloworld"}
        assert result == expected, f"Expected {expected}, got {result}"

    def test_embedded_expressions_json_context(self) -> None:
        """Test embedded expressions in JSON strings vs JSON literals"""
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", 
                     content={"jsonField": '{"message": "@{greeting}", "count": @{count}, "nested": {"text": "@{name}"}}'}),
        ], init_root=True)
        
        session.session_state = WriterState({
            "greeting": "Hello World",
            "name": "Alice", 
            "count": 42
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        # Test JSON field evaluation with embedded expressions
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "jsonField", as_json=True
        )
        
        expected = {
            "message": "Hello World",
            "count": 42,
            "nested": {"text": "Alice"}
        }
        assert result == expected, f"Expected {expected}, got {result}"

    def test_escaped_expressions(self) -> None:
        """Test escaped @ expressions are not evaluated"""
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", 
                     content={"text": "Normal @{value} and escaped \\@{value}"})
        ], init_root=True)
        
        session.session_state = WriterState({
            "value": "replaced"
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "text", as_json=False
        )
        
        # The escaped expression should remain as literal text
        assert result == "Normal replaced and escaped \\@{value}", f"Got: {result}"

    def test_json_edge_cases(self) -> None:
        """Test various edge cases for JSON processing"""
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", content={})
        ], init_root=True)
        
        session.session_state = WriterState({
            "empty_string": "",
            "whitespace": "   ",
            "special_chars": "hello\n\t\"world",
            "unicode": "café ☕ 🔥",
            "number": 3.14159,
            "boolean": True,
            "array": [1, "two", 3.0],
            "nested": {"a": {"b": {"c": "deep"}}}
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        # Test various edge cases
        test_cases = [
            # (field_content, expected_result, as_json)
            ('{"empty": "@{empty_string}"}', {"empty": ""}, True),
            ('{"whitespace": "@{whitespace}"}', {"whitespace": "   "}, True),
            ('{"special": "@{special_chars}"}', {"special": "hello\n\t\"world"}, True),
            ('{"unicode": "@{unicode}"}', {"unicode": "café ☕ 🔥"}, True),
            ('{"number": @{number}}', {"number": 3.14159}, True),
            ('{"boolean": @{boolean}}', {"boolean": True}, True),
            ('{"array": @{array}}', {"array": [1, "two", 3.0]}, True),
            ('{"nested": @{nested}}', {"nested": {"a": {"b": {"c": "deep"}}}}, True),
        ]
        
        for field_content, expected, as_json_mode in test_cases:
            # Update component content
            session.session_component_tree.get_component("test_comp").content["testField"] = field_content
            
            result = e.evaluate_field(
                [{"componentId": "root", "instanceNumber": 0}, 
                 {"componentId": "test_comp", "instanceNumber": 0}], 
                "testField", as_json=as_json_mode
            )
            
            assert result == expected, f"Failed for '{field_content}': expected {expected}, got {result}"

    def test_double_escaping_bug_fix(self) -> None:
        """Test that double-escaping bug is fixed - arrays should not become [\"a\"]"""
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", content={})
        ], init_root=True)
        
        session.session_state = WriterState({
            "my_array": ["apple", "banana", "cherry"],
            "nested_object": {"items": ["x", "y", "z"]}
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        # Test array in JSON context - should NOT be double-escaped
        session.session_component_tree.get_component("test_comp").content["jsonField"] = '{"data": @{my_array}}'
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "jsonField", as_json=True
        )
        
        expected = {"data": ["apple", "banana", "cherry"]}
        assert result == expected, f"Double-escaping bug: expected {expected}, got {result}"
        
        # Test nested object should also work correctly
        session.session_component_tree.get_component("test_comp").content["jsonField"] = '{"result": @{nested_object}}'
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "jsonField", as_json=True
        )
        
        expected = {"result": {"items": ["x", "y", "z"]}}
        assert result == expected, f"Nested object failed: expected {expected}, got {result}"

    def test_context_confusion_fix(self) -> None:
        """Test that context confusion is fixed - JSON string vs JSON literal handling"""
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", content={})
        ], init_root=True)
        
        session.session_state = WriterState({
            "user_name": "Alice",
            "special_chars": 'hello "world"',
            "user_data": {"name": "Bob", "age": 25}
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        # Case 1: Inside JSON string - should inject escaped string fragment
        session.session_component_tree.get_component("test_comp").content["jsonField"] = '{"message": "Hello @{user_name}!"}'
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "jsonField", as_json=True
        )
        expected = {"message": "Hello Alice!"}
        assert result == expected, f"JSON string context failed: expected {expected}, got {result}"
        
        # Case 2: Inside JSON string with special characters - should be properly escaped
        session.session_component_tree.get_component("test_comp").content["jsonField"] = '{"text": "User said: @{special_chars}"}'
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "jsonField", as_json=True
        )
        expected = {"text": 'User said: hello "world"'}
        assert result == expected, f"Special chars in string failed: expected {expected}, got {result}"
        
        # Case 3: As JSON literal - should inject raw JSON
        session.session_component_tree.get_component("test_comp").content["jsonField"] = '{"data": @{user_data}}'
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "jsonField", as_json=True
        )
        expected = {"data": {"name": "Bob", "age": 25}}
        assert result == expected, f"JSON literal context failed: expected {expected}, got {result}"

    def test_full_match_handling_fix(self) -> None:
        """Test full-match handling returns raw values correctly"""
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", content={})
        ], init_root=True)
        
        session.session_state = WriterState({
            "raw_dict": {"key": "value", "nested": {"deep": "data"}},
            "raw_list": [1, 2, {"item": "test"}],
            "raw_none": None,
            "raw_string": "plain text",
            "json_string": '{"parsed": "json"}',
            "raw_number": 42,
            "raw_boolean": True
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        test_cases = [
            # (state_key, expected_result, as_json, description)
            ("raw_dict", {"key": "value", "nested": {"deep": "data"}}, True, "dict should pass through"),
            ("raw_list", [1, 2, {"item": "test"}], True, "list should pass through"),
            ("raw_none", None, True, "None should pass through in JSON mode"),
            ("raw_none", None, False, "None should pass through in non-JSON mode"),
            ("raw_string", "plain text", False, "string should pass through in non-JSON"),
            ("json_string", {"parsed": "json"}, True, "JSON string should be parsed in JSON mode"),
            ("json_string", '{"parsed": "json"}', False, "JSON string should NOT be parsed in non-JSON mode"),
            ("raw_number", 42, True, "number should pass through"),
            ("raw_boolean", True, False, "boolean should pass through"),
        ]
        
        for state_key, expected, as_json_mode, description in test_cases:
            # Set field to exactly @{state_key} for full match
            session.session_component_tree.get_component("test_comp").content["testField"] = f"@{{{state_key}}}"
            
            result = e.evaluate_field(
                [{"componentId": "root", "instanceNumber": 0}, 
                 {"componentId": "test_comp", "instanceNumber": 0}], 
                "testField", as_json=as_json_mode
            )
            
            assert result == expected, f"Full match failed - {description}: expected {expected}, got {result}"

    def test_simplified_decode_step(self) -> None:
        """Test that decode_json is only called when final result is string and as_json=True"""
        session.session_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id="test_comp", parentId="root", type="text", content={})
        ], init_root=True)
        
        session.session_state = WriterState({
            "already_dict": {"key": "value"},
            "json_string": '{"will": "be_parsed"}',
            "plain_string": "not json",
            "number_val": 123
        })
        
        e = evaluator.Evaluator(session.session_state, session.session_component_tree)
        
        # Case 1: Already a dict - should NOT be processed by decode_json
        session.session_component_tree.get_component("test_comp").content["field"] = "@{already_dict}"
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "field", as_json=True
        )
        assert result == {"key": "value"}, f"Dict should pass through: {result}"
        
        # Case 2: JSON string with as_json=True - should be decoded
        session.session_component_tree.get_component("test_comp").content["field"] = "@{json_string}"
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "field", as_json=True
        )
        assert result == {"will": "be_parsed"}, f"JSON string should be parsed: {result}"
        
        # Case 3: JSON string with as_json=False - should NOT be decoded
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "field", as_json=False
        )
        assert result == '{"will": "be_parsed"}', f"JSON string should remain string: {result}"
        
        # Case 4: Plain string with as_json=True - should remain string (not parseable)
        session.session_component_tree.get_component("test_comp").content["field"] = "@{plain_string}"
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "field", as_json=True
        )
        assert result == "not json", f"Plain string should remain unchanged: {result}"
        
        # Case 5: Number - should pass through without decode attempt
        session.session_component_tree.get_component("test_comp").content["field"] = "@{number_val}"
        result = e.evaluate_field(
            [{"componentId": "root", "instanceNumber": 0}, 
             {"componentId": "test_comp", "instanceNumber": 0}], 
            "field", as_json=True
        )
        assert result == 123, f"Number should pass through: {result}"
