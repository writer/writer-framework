"""
Tests for shared blueprints functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest

from writer.blocks.base_block import block_map
from writer.blocks.shared_blueprint import SharedBlueprint
from writer.blocks.shared_blueprint_registry import (
    SharedBlueprintMetadata,
    analyze_dependencies,
    filter_problematic_components,
    get_shared_blueprint_components,
    get_shared_blueprint_metadata,
    get_registered_shared_blueprints,
    load_shared_blueprint_from_directory,
    load_shared_blueprints_from_project,
    make_shared_blueprints_dir,
    register_shared_blueprint,
    remap_component_ids,
    sanitize_shared_blueprint_name,
)


def test_sanitize_shared_blueprint_name():
    """Test blueprint name sanitization."""
    assert sanitize_shared_blueprint_name("Extract File Text") == "shared_extract_file_text"
    assert sanitize_shared_blueprint_name("My Blueprint!") == "shared_my_blueprint"
    assert sanitize_shared_blueprint_name("test-blueprint_123") == "shared_test_blueprint_123"
    assert sanitize_shared_blueprint_name("  Spaces  ") == "shared_spaces"
    # Test empty slug case - should default to "blueprint" to prevent root-directory collisions
    assert sanitize_shared_blueprint_name("!!!") == "shared_blueprint"
    assert sanitize_shared_blueprint_name("   ") == "shared_blueprint"
    assert sanitize_shared_blueprint_name("---") == "shared_blueprint"


def test_load_shared_blueprint_from_directory():
    """Test loading a shared blueprint from directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        blueprint_dir = Path(tmpdir) / "test_blueprint"
        blueprint_dir.mkdir()

        # Create block.json
        metadata = {
            "name": "Test Blueprint",
            "description": "A test shared blueprint",
            "version": "1.0.0",
        }
        json_path = blueprint_dir / "block.json"
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Create blueprint.json with sample blueprint components
        blueprint_components = [
            {
                "id": "node1",
                "type": "blueprints_httprequest",
                "content": {"method": "GET", "url": "https://example.com"},
                "outs": [],
            }
        ]
        blueprint_path = blueprint_dir / "blueprint.json"
        with open(blueprint_path, "w") as f:
            json.dump(blueprint_components, f, indent=2)

        # Load blueprint
        loaded_metadata, loaded_blueprint = load_shared_blueprint_from_directory(blueprint_dir)

        assert loaded_metadata.name == "Test Blueprint"
        assert loaded_metadata.description == "A test shared blueprint"
        assert loaded_blueprint == blueprint_components


def test_load_shared_blueprint_from_directory_missing_files():
    """Test loading blueprint with missing files raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        blueprint_dir = Path(tmpdir) / "test_blueprint"
        blueprint_dir.mkdir()

        # Missing block.json
        with pytest.raises(ValueError, match="missing block.json"):
            load_shared_blueprint_from_directory(blueprint_dir)

        # Create block.json but missing blueprint.json
        json_path = blueprint_dir / "block.json"
        with open(json_path, "w") as f:
            json.dump({"name": "Test", "description": "Test"}, f)

        with pytest.raises(ValueError, match="missing blueprint.json"):
            load_shared_blueprint_from_directory(blueprint_dir)


def test_register_shared_blueprint():
    """Test registering a shared blueprint."""
    # Clear any existing registrations
    blueprint_type = "shared_test_blueprint"
    if blueprint_type in block_map:
        del block_map[blueprint_type]

    metadata = SharedBlueprintMetadata(
        name="Test Blueprint",
        description="A test shared blueprint",
    )
    blueprint_components = [
        {
            "id": "node1",
            "type": "blueprints_httprequest",
            "content": {"method": "GET", "url": "https://example.com"},
            "outs": [],
        }
    ]

    register_shared_blueprint(blueprint_type, metadata, blueprint_components)

    # Check blueprint is registered
    assert blueprint_type in block_map
    assert block_map[blueprint_type] == SharedBlueprint

    # Check metadata and blueprint components are stored
    assert get_shared_blueprint_metadata(blueprint_type) == metadata
    assert get_shared_blueprint_components(blueprint_type) == blueprint_components

    # Check AbstractTemplate is registered
    from writer.abstract import templates

    assert blueprint_type in templates
    template = templates[blueprint_type]
    assert template.writer["name"] == "Test Blueprint"
    assert template.writer["category"] == "Shared Blueprints"


def test_load_shared_blueprints_from_project():
    """Test loading shared blueprints from project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        app_path = Path(tmpdir)
        blueprints_dir = make_shared_blueprints_dir(str(app_path))
        blueprints_dir.mkdir(parents=True)

        # Create a test blueprint
        blueprint_dir = blueprints_dir / "test_blueprint"
        blueprint_dir.mkdir()

        metadata = {
            "name": "Test Blueprint",
            "description": "A test shared blueprint",
        }
        json_path = blueprint_dir / "block.json"
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)

        blueprint_components = [
            {
                "id": "node1",
                "type": "blueprints_httprequest",
                "content": {"method": "GET", "url": "https://example.com"},
                "outs": [],
            }
        ]
        blueprint_path = blueprint_dir / "blueprint.json"
        with open(blueprint_path, "w") as f:
            json.dump(blueprint_components, f, indent=2)

        # Load blueprints
        load_shared_blueprints_from_project(str(app_path))

        # Check blueprint is registered
        blueprint_type = "shared_test_blueprint"
        assert blueprint_type in block_map
        assert get_shared_blueprint_components(blueprint_type) == blueprint_components


def test_load_shared_blueprints_from_project_nonexistent():
    """Test loading from non-existent directory doesn't error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        app_path = Path(tmpdir)
        # No .wf/shared_blueprints directory

        # Should not raise error
        load_shared_blueprints_from_project(str(app_path))


def test_shared_blueprint_no_components(session, runner):
    """Test shared blueprint raises error when no blueprint components found."""
    # Create component with shared_blueprint type but no sourceBlueprintId
    component = session.add_fake_component({}, type="shared_blueprint")

    # Create block instance - should fail when run because no source blueprint is set
    block = SharedBlueprint(component, runner, {})

    with pytest.raises(ValueError, match="No blueprint components found"):
        block.run()


def test_remap_component_ids():
    """Test remapping component IDs."""
    components = [
        {
            "id": "node1",
            "type": "blueprints_httprequest",
            "parentId": "blueprint1",
            "content": {"url": "https://example.com"},
            "outs": [{"toNodeId": "node2"}],
        },
        {
            "id": "node2",
            "type": "blueprints_code",
            "parentId": "blueprint1",
            "content": {"code": "print('hello')"},
            "outs": [],
        },
    ]

    remapped = remap_component_ids(components)

    # Check IDs are remapped
    assert remapped[0]["id"] != "node1"
    assert remapped[1]["id"] != "node2"

    # Check parentId is removed
    assert "parentId" not in remapped[0]
    assert "parentId" not in remapped[1]

    # Check toNodeId is updated to new ID
    assert remapped[0]["outs"][0]["toNodeId"] == remapped[1]["id"]

    # Check original components are not modified (deep copy)
    assert components[0]["id"] == "node1"
    assert components[0]["parentId"] == "blueprint1"


def test_filter_problematic_components():
    """Test filtering out problematic components."""
    components = [
        {
            "id": "node1",
            "type": "blueprints_httprequest",
            "content": {"url": "https://example.com"},
        },
        {
            "id": "node2",
            "type": "blueprints_uieventtrigger",
            "content": {"alias": "Button Click Handler"},
        },
        {
            "id": "node3",
            "type": "blueprints_crontrigger",
            "content": {},
        },
        {
            "id": "node4",
            "type": "blueprints_code",
            "content": {"code": "print('hello')"},
        },
    ]

    filtered, removed = filter_problematic_components(components)

    # Check correct components are kept
    assert len(filtered) == 2
    assert filtered[0]["id"] == "node1"
    assert filtered[1]["id"] == "node4"

    # Check removed descriptions
    assert len(removed) == 2
    assert any("Button Click Handler" in r for r in removed)
    assert any("crontrigger" in r for r in removed)


def test_analyze_dependencies():
    """Test analyzing component dependencies."""
    components = [
        {
            "id": "node1",
            "type": "blueprints_httprequest",
            "content": {
                "url": "https://api.example.com/@{customer_id}",
                "headers": '{"Authorization": "@{api_key}"}',
            },
        },
        {
            "id": "node2",
            "type": "blueprints_writersecret",
            "content": {"secretName": "my_secret_key"},
        },
        {
            "id": "node3",
            "type": "blueprints_runblueprint",
            "content": {"blueprintKey": "data_processor"},
        },
        {
            "id": "node4",
            "type": "shared_my_utility",
            "content": {},
        },
    ]

    dependencies = analyze_dependencies(components)

    # Check state variables detected
    assert "state_variables" in dependencies
    assert "customer_id" in dependencies["state_variables"]
    assert "api_key" in dependencies["state_variables"]

    # Check vault keys detected
    assert "vault_keys" in dependencies
    assert "my_secret_key" in dependencies["vault_keys"]

    # Check blueprint references detected
    assert "blueprint_references" in dependencies
    assert "data_processor" in dependencies["blueprint_references"]

    # Check shared blueprint references detected
    assert "shared_blueprint_references" in dependencies
    assert "shared_my_utility" in dependencies["shared_blueprint_references"]


def test_analyze_dependencies_empty():
    """Test analyzing components with no external dependencies."""
    components = [
        {
            "id": "node1",
            "type": "blueprints_code",
            "content": {"code": "x = 1 + 1"},
        },
    ]

    dependencies = analyze_dependencies(components)

    # Should return empty dict
    assert dependencies == {}

