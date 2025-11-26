"""
Shared blueprint registry for loading and managing user-created shared blueprints.

Shared blueprints are stored in .wf/shared_blueprints/ directory with the following structure:
  .wf/shared_blueprints/
    blueprint_name/
      block.json  # Metadata
      blueprint.json  # Blueprint component structure
"""

import copy
import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate

logger = logging.getLogger(__name__)


def make_shared_blueprints_dir(app_path: str) -> Path:
    """
    Get the path to the shared blueprints directory for a given app path.

    Args:
        app_path: Path to user's application directory

    Returns:
        Path to the .wf/shared_blueprints directory
    """
    return Path(app_path) / ".wf" / "shared_blueprints"


@dataclass
class SharedBlueprintMetadata:
    """Metadata for a shared blueprint."""

    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    state_inputs: List[str] = field(default_factory=list)
    state_outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    vault_keys: List[str] = field(default_factory=list)


# Registry of loaded shared blueprints
_shared_blueprints: Dict[str, SharedBlueprintMetadata] = {}
_blueprint_components: Dict[str, List[Dict[str, Any]]] = {}


def sanitize_shared_blueprint_name(name: str) -> str:
    """
    Convert blueprint name to valid type identifier.

    Example: "Extract File Text" -> "shared_extract_file_text"
    
    If the input contains no valid characters, returns "shared_blueprint" as a safe default
    to prevent empty slugs and root-directory collisions.
    """
    sanitized = re.sub(r"[^a-z0-9_]", "_", name.lower())
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip("_")
    # Ensure we never have an empty slug to prevent root-directory collisions
    if not sanitized:
        sanitized = "blueprint"
    return f"shared_{sanitized}"


def _generate_short_id() -> str:
    """Generate a short unique ID similar to the format used by components."""
    return uuid.uuid4().hex[:16]


def remap_component_ids(components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate new unique IDs for components and update all internal references.
    
    This prevents ID collisions when the same shared blueprint is used multiple times
    or when component IDs clash with existing components in the project.
    
    Args:
        components: List of component dictionaries
        
    Returns:
        New list of components with remapped IDs and removed parentId
    """
    # Build old_id -> new_id mapping
    id_mapping: Dict[str, str] = {}
    for comp in components:
        old_id = comp.get("id")
        if old_id:
            id_mapping[old_id] = _generate_short_id()
    
    # Deep copy and update components
    remapped = []
    for comp in components:
        new_comp = copy.deepcopy(comp)
        
        # Update component ID
        old_id = new_comp.get("id")
        if old_id and old_id in id_mapping:
            new_comp["id"] = id_mapping[old_id]
        
        # Remove parentId (not needed for execution, and references original blueprint)
        new_comp.pop("parentId", None)
        
        # Update toNodeId references in outs
        if "outs" in new_comp and isinstance(new_comp["outs"], list):
            for out in new_comp["outs"]:
                if isinstance(out, dict) and "toNodeId" in out:
                    old_target = out["toNodeId"]
                    if old_target and old_target in id_mapping:
                        out["toNodeId"] = id_mapping[old_target]
        
        remapped.append(new_comp)
    
    return remapped


def analyze_dependencies(components: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Analyze components for external dependencies that may need attention.
    
    Detects:
    - State variable references (@{variable_name} pattern)
    - Vault key usage
    - Run Blueprint references (other blueprint keys)
    - Shared blueprint references
    
    Args:
        components: List of component dictionaries
        
    Returns:
        Dictionary with dependency categories and their values
    """
    state_vars: Set[str] = set()
    vault_keys: Set[str] = set()
    blueprint_refs: Set[str] = set()
    shared_blueprint_refs: Set[str] = set()
    
    # Pattern for state variable references: @{variable_name}
    state_var_pattern = re.compile(r'@\{([^}]+)\}')
    
    for comp in components:
        comp_type = comp.get("type", "")
        content = comp.get("content", {})
        
        # Scan all string values in content for state variable references
        for key, value in content.items():
            if isinstance(value, str):
                matches = state_var_pattern.findall(value)
                state_vars.update(matches)
        
        # Check for vault key usage (WriterSecret block or vault-related fields)
        if comp_type == "blueprints_writersecret":
            secret_name = content.get("secretName", "")
            if secret_name:
                vault_keys.add(secret_name)
        
        # Check for Run Blueprint references
        if comp_type == "blueprints_runblueprint":
            blueprint_key = content.get("blueprintKey", "")
            if blueprint_key:
                blueprint_refs.add(blueprint_key)
        
        # Check for shared blueprint references (blocks starting with shared_)
        if comp_type.startswith("shared_"):
            shared_blueprint_refs.add(comp_type)
    
    result: Dict[str, List[str]] = {}
    
    if state_vars:
        result["state_variables"] = sorted(state_vars)
    if vault_keys:
        result["vault_keys"] = sorted(vault_keys)
    if blueprint_refs:
        result["blueprint_references"] = sorted(blueprint_refs)
    if shared_blueprint_refs:
        result["shared_blueprint_references"] = sorted(shared_blueprint_refs)
    
    return result


def load_shared_blueprint_from_directory(blueprint_dir: Path) -> Tuple[SharedBlueprintMetadata, List[Dict[str, Any]]]:
    """
    Load shared blueprint metadata and components from directory.

    Args:
        blueprint_dir: Path to blueprint directory containing block.json and blueprint.json

    Returns:
        Tuple of (metadata, blueprint_components)

    Raises:
        ValueError: If block.json or blueprint.json is missing
        json.JSONDecodeError: If block.json or blueprint.json is invalid
    """
    json_path = blueprint_dir / "block.json"
    blueprint_path = blueprint_dir / "blueprint.json"

    if not json_path.exists():
        raise ValueError(f"Blueprint directory {blueprint_dir} missing block.json")
    if not blueprint_path.exists():
        raise ValueError(f"Blueprint directory {blueprint_dir} missing blueprint.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            metadata_dict = json.load(f)
        if not metadata_dict:
            raise ValueError(f"Blueprint {blueprint_dir} has empty block.json")
        metadata = SharedBlueprintMetadata(**metadata_dict)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {json_path}: {e}") from e
    except TypeError as e:
        raise ValueError(f"Invalid metadata structure in {json_path}: {e}") from e

    try:
        with open(blueprint_path, "r", encoding="utf-8") as f:
            blueprint_components = json.load(f)
        if not isinstance(blueprint_components, list):
            raise ValueError(f"Blueprint {blueprint_dir} blueprint.json must contain a list of components")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {blueprint_path}: {e}") from e

    return metadata, blueprint_components


def _generate_abstract_template(metadata: SharedBlueprintMetadata) -> AbstractTemplate:
    """
    Generate AbstractTemplate from SharedBlueprintMetadata.

    Args:
        metadata: Blueprint metadata

    Returns:
        AbstractTemplate for the shared blueprint
    """
    return AbstractTemplate(
        baseType="blueprints_node",
        writer={
            "name": metadata.name,
            "description": metadata.description,
            "category": "Shared Blueprints",
            "toolkit": "blueprints",
            "fields": {},
            "outs": {
                "success": {
                    "name": "Success",
                    "description": "Blueprint executed successfully.",
                    "style": "success",
                },
                "error": {
                    "name": "Error",
                    "description": "Blueprint execution failed.",
                    "style": "error",
                },
            },
        },
    )


def register_shared_blueprint(blueprint_type: str, metadata: SharedBlueprintMetadata, blueprint_components: List[Dict[str, Any]]) -> None:
    """
    Register a shared blueprint.

    Args:
        blueprint_type: Blueprint type identifier (e.g., "shared_extract_file_text")
        metadata: Blueprint metadata
        blueprint_components: List of blueprint component dictionaries
    """
    from writer.blocks.shared_blueprint import SharedBlueprint
    SharedBlueprint.register(blueprint_type)

    _shared_blueprints[blueprint_type] = metadata
    _blueprint_components[blueprint_type] = blueprint_components

    abstract_template = _generate_abstract_template(metadata)
    register_abstract_template(blueprint_type, abstract_template)

    logger.info(f"Registered shared blueprint: {blueprint_type} ({metadata.name})")


def load_shared_blueprints_from_project(app_path: str) -> None:
    """
    Load all shared blueprints from project's .wf/shared_blueprints/ directory.

    Args:
        app_path: Path to user's application directory
    """
    blueprints_dir = make_shared_blueprints_dir(app_path)

    if not blueprints_dir.exists():
        logger.debug(f"No .wf/shared_blueprints directory found at {blueprints_dir}")
        return

    if not blueprints_dir.is_dir():
        logger.warning(f".wf/shared_blueprints exists but is not a directory: {blueprints_dir}")
        return

    loaded_count = 0
    for blueprint_dir in blueprints_dir.iterdir():
        if not blueprint_dir.is_dir():
            continue

        try:
            metadata, blueprint_components = load_shared_blueprint_from_directory(blueprint_dir)
            blueprint_type = sanitize_shared_blueprint_name(metadata.name)
            register_shared_blueprint(blueprint_type, metadata, blueprint_components)
            loaded_count += 1
        except Exception as e:
            logger.warning(f"Failed to load shared blueprint from {blueprint_dir}: {e}")

    if loaded_count > 0:
        logger.info(f"Loaded {loaded_count} shared blueprint(s) from {blueprints_dir}")


def get_registered_shared_blueprints() -> Dict[str, SharedBlueprintMetadata]:
    """
    Get all registered shared blueprints.

    Returns:
        Dictionary mapping blueprint_type to metadata
    """
    return _shared_blueprints.copy()


def get_shared_blueprint_components(blueprint_type: str) -> List[Dict[str, Any]]:
    """
    Get blueprint components for a registered shared blueprint.

    Args:
        blueprint_type: Blueprint type identifier

    Returns:
        List of blueprint component dictionaries, or empty list if not found
    """
    return _blueprint_components.get(blueprint_type, [])


def get_shared_blueprint_metadata(blueprint_type: str) -> SharedBlueprintMetadata:
    """
    Get metadata for a registered shared blueprint.

    Args:
        blueprint_type: Blueprint type identifier

    Returns:
        Blueprint metadata

    Raises:
        KeyError: If blueprint is not registered
    """
    return _shared_blueprints[blueprint_type]


def unregister_shared_blueprint(blueprint_type: str) -> None:
    """
    Unregister a shared blueprint.

    Args:
        blueprint_type: Blueprint type identifier (e.g., "shared_extract_file_text")
    """
    from writer.abstract import templates
    from writer.blocks.base_block import block_map

    # Remove from block_map
    if blueprint_type in block_map:
        del block_map[blueprint_type]

    # Remove from registries
    if blueprint_type in _shared_blueprints:
        del _shared_blueprints[blueprint_type]
    if blueprint_type in _blueprint_components:
        del _blueprint_components[blueprint_type]

    # Remove from abstract templates
    if blueprint_type in templates:
        del templates[blueprint_type]

    logger.info(f"Unregistered shared blueprint: {blueprint_type}")

