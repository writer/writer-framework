"""
Custom block registry for loading and managing user-created custom blocks.

Custom blocks are stored in .wf/blocks/ directory with the following structure:
  .wf/blocks/
    block_name/
      block.json  # Metadata
      block.py    # Python code
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate

logger = logging.getLogger(__name__)


def make_blocks_dir(app_path: str) -> Path:
    """
    Get the path to the custom blocks directory for a given app path.

    Args:
        app_path: Path to user's application directory

    Returns:
        Path to the .wf/blocks directory
    """
    return Path(app_path) / ".wf" / "blocks"


@dataclass
class CustomBlockMetadata:
    """Metadata for a custom block."""

    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    state_inputs: List[str] = field(default_factory=list)
    state_outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    vault_keys: List[str] = field(default_factory=list)


# Registry of loaded custom blocks
_custom_blocks: Dict[str, CustomBlockMetadata] = {}
_block_code: Dict[str, str] = {}


def sanitize_block_name(name: str) -> str:
    """
    Convert block name to valid type identifier.

    Example: "Extract File Text" -> "custom_extract_file_text"
    """
    sanitized = re.sub(r"[^a-z0-9_]", "_", name.lower())
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip("_")
    return f"custom_{sanitized}"


def load_block_from_directory(block_dir: Path) -> Tuple[CustomBlockMetadata, str]:
    """
    Load block metadata and code from directory.

    Args:
        block_dir: Path to block directory containing block.json and block.py

    Returns:
        Tuple of (metadata, code)

    Raises:
        ValueError: If block.json or block.py is missing
        json.JSONDecodeError: If block.json is invalid
    """
    json_path = block_dir / "block.json"
    py_path = block_dir / "block.py"

    if not json_path.exists():
        raise ValueError(f"Block directory {block_dir} missing block.json")
    if not py_path.exists():
        raise ValueError(f"Block directory {block_dir} missing block.py")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            metadata_dict = json.load(f)
        if not metadata_dict:
            raise ValueError(f"Block {block_dir} has empty block.json")
        metadata = CustomBlockMetadata(**metadata_dict)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {json_path}: {e}") from e
    except TypeError as e:
        raise ValueError(f"Invalid metadata structure in {json_path}: {e}") from e

    with open(py_path, "r", encoding="utf-8") as f:
        code = f.read()

    return metadata, code


def _generate_abstract_template(metadata: CustomBlockMetadata, code: str) -> AbstractTemplate:
    """
    Generate AbstractTemplate from CustomBlockMetadata.

    Args:
        metadata: Block metadata
        code: Block Python code

    Returns:
        AbstractTemplate for the block
    """
    return AbstractTemplate(
        baseType="blueprints_node",
        # TODO: code field is not visible
        writer={
            "name": metadata.name,
            "description": metadata.description,
            "category": "Custom Blocks",
            "toolkit": "blueprints",
            "fields": {
                "code": {
                    "name": "Code",
                    "type": "Code",
                    "control": "Textarea",
                    "desc": "The block code.",
                    "init": code,
                },
            },
            "outs": {
                "success": {
                    "name": "Success",
                    "description": "Block executed successfully.",
                    "style": "success",
                },
                "error": {
                    "name": "Error",
                    "description": "Block execution failed.",
                    "style": "error",
                },
            },
        },
    )


def register_custom_block(block_type: str, metadata: CustomBlockMetadata, code: str) -> None:
    """
    Register a custom block.

    Args:
        block_type: Block type identifier (e.g., "custom_extract_file_text")
        metadata: Block metadata
        code: Block Python code
    """
    from writer.blocks.custom_block import CustomBlock
    CustomBlock.register(block_type)

    _custom_blocks[block_type] = metadata
    _block_code[block_type] = code

    abstract_template = _generate_abstract_template(metadata, code)
    register_abstract_template(block_type, abstract_template)

    logger.info(f"Registered custom block: {block_type} ({metadata.name})")


def load_custom_blocks_from_project(app_path: str) -> None:
    """
    Load all custom blocks from project's .wf/blocks/ directory.

    Args:
        app_path: Path to user's application directory
    """
    blocks_dir = make_blocks_dir(app_path)

    if not blocks_dir.exists():
        logger.debug(f"No .wf/blocks directory found at {blocks_dir}")
        return

    if not blocks_dir.is_dir():
        logger.warning(f".wf/blocks exists but is not a directory: {blocks_dir}")
        return

    loaded_count = 0
    for block_dir in blocks_dir.iterdir():
        if not block_dir.is_dir():
            continue

        try:
            metadata, code = load_block_from_directory(block_dir)
            block_type = sanitize_block_name(metadata.name)
            register_custom_block(block_type, metadata, code)
            loaded_count += 1
        except Exception as e:
            logger.warning(f"Failed to load custom block from {block_dir}: {e}")

    if loaded_count > 0:
        logger.info(f"Loaded {loaded_count} custom block(s) from {blocks_dir}")


def get_registered_custom_blocks() -> Dict[str, CustomBlockMetadata]:
    """
    Get all registered custom blocks.

    Returns:
        Dictionary mapping block_type to metadata
    """
    return _custom_blocks.copy()


def get_block_code(block_type: str) -> str:
    """
    Get code for a registered block.

    Args:
        block_type: Block type identifier

    Returns:
        Block Python code, or empty string if not found
    """
    return _block_code.get(block_type, "")


def get_block_metadata(block_type: str) -> CustomBlockMetadata:
    """
    Get metadata for a registered block.

    Args:
        block_type: Block type identifier

    Returns:
        Block metadata

    Raises:
        KeyError: If block is not registered
    """
    return _custom_blocks[block_type]


def unregister_custom_block(block_type: str) -> None:
    """
    Unregister a custom block.

    Args:
        block_type: Block type identifier (e.g., "custom_extract_file_text")
    """
    from writer.abstract import templates
    from writer.blocks.base_block import block_map

    # Remove from block_map
    if block_type in block_map:
        del block_map[block_type]

    # Remove from registries
    if block_type in _custom_blocks:
        del _custom_blocks[block_type]
    if block_type in _block_code:
        del _block_code[block_type]

    # Remove from abstract templates
    if block_type in templates:
        del templates[block_type]

    logger.info(f"Unregistered custom block: {block_type}")

