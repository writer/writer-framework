import json

from writer import audit_and_fix

from backend.fixtures import load_fixture_content


def test_fix_components_should_fix_visible_fields():
    # Given
    obsolete_components = load_fixture_content('obsoletes/ui_obsolete_visible.json')

    # When
    final_components = audit_and_fix.fix_components(obsolete_components)

    # Then
    assert "visible" not in final_components["root"]
    assert final_components['bb4d0e86-619e-4367-a180-be28ab6059f4']['visible'] == {
        'expression': True,
        'binding': "",
        'reversed': False
    }
    assert final_components['bb4d0e86-619e-4367-a180-be28abxxxx']['visible'] == {
        'expression': "custom",
        'binding': "value",
        'reversed': False
    }
