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
        assert e.evaluate_expression("a\.b", instance_path) == 3

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