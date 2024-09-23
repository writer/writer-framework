from typing import List

from writer import core_ui
from writer.ss_types import ComponentDefinition

from backend.fixtures import load_fixture_content


def test_lookup_parent_type_for_component_should_retrieve_the_page_for_a_specific_component_id():
    # Given
    components_list: List[ComponentDefinition] = load_fixture_content('components/components-page-1.jsonl')
    components = {c['id']: c for c in components_list}

    # When
    page_id = core_ui.lookup_parent_type_for_component(components, '42ab5c3d-21fc-4e88-befd-33e52fd15e8b', parent_type="page")

    # Then
    assert page_id == '23bc1387-26ed-4ff2-8565-b027c2960c3c'


def test_lookup_parent_type_for_component_should_return_nothing_when_the_component_match_nothing():
    # Given
    components_list: List[ComponentDefinition] = load_fixture_content('components/components-page-1.jsonl')
    components = {c['id']: c for c in components_list}

    # When
    page_id = core_ui.lookup_parent_type_for_component(components, 'xxxxxxxxx-xxxxx-4e88-befd-33e52fd15e8b', parent_type="page")

    # Then
    assert page_id is None
