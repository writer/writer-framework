"""
Tests for custom blocks functionality.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

from writer.blocks.base_block import block_map
from writer.blocks.custom_block import CustomBlock
from writer.blocks.custom_block_registry import (
    CustomBlockMetadata,
    get_block_code,
    get_block_metadata,
    get_registered_custom_blocks,
    load_block_from_directory,
    load_custom_blocks_from_project,
    make_blocks_dir,
    register_custom_block,
    sanitize_block_name,
)


def test_sanitize_block_name():
    """Test block name sanitization."""
    assert sanitize_block_name("Extract File Text") == "custom_extract_file_text"
    assert sanitize_block_name("My Block!") == "custom_my_block_"
    assert sanitize_block_name("test-block_123") == "custom_test_block_123"
    assert sanitize_block_name("  Spaces  ") == "custom_spaces"
    # Test empty slug case - should default to "block" to prevent root-directory collisions
    assert sanitize_block_name("!!!") == "custom_block"
    assert sanitize_block_name("   ") == "custom_block"
    assert sanitize_block_name("---") == "custom_block"


def test_load_block_from_directory():
    """Test loading a block from directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        block_dir = Path(tmpdir) / "test_block"
        block_dir.mkdir()

        # Create block.json
        metadata = {
            "name": "Test Block",
            "description": "A test block",
            "version": "1.0.0",
        }
        json_path = block_dir / "block.json"
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Create block.py
        code = 'state["result"] = "test"'
        py_path = block_dir / "block.py"
        with open(py_path, "w") as f:
            f.write(code)

        # Load block
        loaded_metadata, loaded_code = load_block_from_directory(block_dir)

        assert loaded_metadata.name == "Test Block"
        assert loaded_metadata.description == "A test block"
        assert loaded_code == code


def test_load_block_from_directory_missing_files():
    """Test loading block with missing files raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        block_dir = Path(tmpdir) / "test_block"
        block_dir.mkdir()

        # Missing block.json
        with pytest.raises(ValueError, match="missing block.json"):
            load_block_from_directory(block_dir)

        # Create block.json but missing block.py
        json_path = block_dir / "block.json"
        with open(json_path, "w") as f:
            json.dump({"name": "Test"}, f)

        with pytest.raises(ValueError, match="missing block.py"):
            load_block_from_directory(block_dir)


def test_register_custom_block():
    """Test registering a custom block."""
    # Clear any existing registrations
    block_type = "custom_test_block"
    if block_type in block_map:
        del block_map[block_type]

    metadata = CustomBlockMetadata(
        name="Test Block",
        description="A test block",
    )
    code = 'state["result"] = "test"'

    register_custom_block(block_type, metadata, code)

    # Check block is registered
    assert block_type in block_map
    assert block_map[block_type] == CustomBlock

    # Check metadata and code are stored
    assert get_block_metadata(block_type) == metadata
    assert get_block_code(block_type) == code

    # Check AbstractTemplate is registered
    from writer.abstract import templates

    assert block_type in templates
    template = templates[block_type]
    assert template.writer["name"] == "Test Block"
    assert template.writer["category"] == "Custom Blocks"


def test_load_custom_blocks_from_project():
    """Test loading custom blocks from project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        app_path = Path(tmpdir)
        blocks_dir = make_blocks_dir(str(app_path))
        blocks_dir.mkdir(parents=True)

        # Create a test block
        block_dir = blocks_dir / "test_block"
        block_dir.mkdir()

        metadata = {
            "name": "Test Block",
            "description": "A test block",
        }
        json_path = block_dir / "block.json"
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)

        code = 'state["result"] = "test"'
        py_path = block_dir / "block.py"
        with open(py_path, "w") as f:
            f.write(code)

        # Load blocks
        load_custom_blocks_from_project(str(app_path))

        # Check block is registered
        block_type = "custom_test_block"
        assert block_type in block_map
        assert get_block_code(block_type) == code


def test_load_custom_blocks_from_project_nonexistent():
    """Test loading from non-existent directory doesn't error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        app_path = Path(tmpdir)
        # No .wf/blocks directory

        # Should not raise error
        load_custom_blocks_from_project(str(app_path))

        # No blocks should be registered
        custom_blocks = get_registered_custom_blocks()
        assert len(custom_blocks) == 0


def test_custom_block_execution(session, runner, monkeypatch):
    """Test custom block execution."""
    import types

    fake_module = types.ModuleType("fake_writeruserapp")
    monkeypatch.setitem(sys.modules, "writeruserapp", fake_module)

    # Register a test block
    block_type = "custom_test_execution"
    metadata = CustomBlockMetadata(
        name="Test Execution",
        description="Test block execution",
    )
    code = """
state["test_value"] = "executed"
set_output("success")
"""
    register_custom_block(block_type, metadata, code)

    # Create component
    component = session.add_fake_component({}, type=block_type)

    # Create block instance
    block = CustomBlock(component, runner, {"test_thing_ee": 26})

    # Execute block
    block.run()

    # Check execution
    assert block.outcome == "success"
    assert block.result == "success"
    assert runner.session.session_state.get("test_value") == "executed"


def test_custom_block_execution_error(session, runner, monkeypatch):
    """Test custom block error handling."""
    import types

    fake_module = types.ModuleType("fake_writeruserapp")
    monkeypatch.setitem(sys.modules, "writeruserapp", fake_module)

    # Register a test block that raises an error
    block_type = "custom_test_error"
    metadata = CustomBlockMetadata(
        name="Test Error",
        description="Test block error",
    )
    code = """
raise ValueError("Test error")
"""
    register_custom_block(block_type, metadata, code)

    # Create component
    component = session.add_fake_component({}, type=block_type)

    # Create block instance
    block = CustomBlock(component, runner, {})

    # Execute block - should raise error
    with pytest.raises(ValueError, match="Test error"):
        block.run()

    # Check error outcome
    assert block.outcome == "error"
    assert "Test error" in block.message

