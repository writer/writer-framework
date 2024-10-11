from typing import List

from writer import core_ui
from writer.ss_types import ComponentDefinition

from backend.fixtures import load_fixture_content


def test_filter_components_by_should_retrieve_a_list_of_components_that_fit_the_parent():
    # Given
    components_list: List[ComponentDefinition] = load_fixture_content('components/components-page-1.jsonl')
    components = {c['id']: c for c in components_list}

    # When
    components_filtered = core_ui.filter_components_by(components, '23bc1387-26ed-4ff2-8565-b027c2960c3c')

    # Then
    assert '23bc1387-26ed-4ff2-8565-b027c2960c3c' in components_filtered
