"""
Mock in-memory database for block library snippets.

Simulates Postgres snippets and snippet_versions tables using in-memory dictionaries.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SnippetRecord:
    """Record representing a snippet (block) in the library."""

    id: str  # UUID
    visibility: str  # "ORG" for organization-level visibility
    title: str
    org_id: str = ""  # Organization ID
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SnippetVersionRecord:
    """Record representing a version of a snippet."""

    id: str  # UUID
    snippet_id: str
    version_number: int
    blueprint_components: List[Dict[str, Any]]  # Blueprint component structure
    description: str
    metadata: dict  # name, state_inputs, state_outputs, etc.
    created_at: datetime = field(default_factory=datetime.utcnow)


# In-memory storage
_snippets: Dict[str, SnippetRecord] = {}
_snippet_versions: Dict[str, List[SnippetVersionRecord]] = {}


def create_snippet(
    title: str,
    visibility: str = "ORG",
    org_id: str = "",
) -> str:
    """
    Create a new snippet record.

    Args:
        title: Snippet title
        visibility: Visibility level (default: "ORG")
        org_id: Organization ID

    Returns:
        snippet_id (UUID string)
    """
    snippet_id = str(uuid.uuid4())
    snippet = SnippetRecord(
        id=snippet_id,
        visibility=visibility,
        title=title,
        org_id=org_id,
    )
    _snippets[snippet_id] = snippet
    _snippet_versions[snippet_id] = []
    logger.debug(f"Created snippet: {snippet_id} ({title})")
    return snippet_id


def create_snippet_version(
    snippet_id: str, blueprint_components: List[Dict[str, Any]], description: str, metadata: dict
) -> int:
    """
    Create a new version for a snippet.

    Args:
        snippet_id: ID of the snippet
        blueprint_components: Blueprint component structure (list of component dicts)
        description: Block description
        metadata: Block metadata (name, state_inputs, etc.)

    Returns:
        version_number (auto-incremented)

    Raises:
        ValueError: If snippet_id doesn't exist
    """
    if snippet_id not in _snippets:
        raise ValueError(f"Snippet {snippet_id} not found")

    versions = _snippet_versions.get(snippet_id, [])
    # Auto-increment version number
    version_number = len(versions) + 1

    version_id = str(uuid.uuid4())
    version = SnippetVersionRecord(
        id=version_id,
        snippet_id=snippet_id,
        version_number=version_number,
        blueprint_components=blueprint_components,
        description=description,
        metadata=metadata,
    )

    if snippet_id not in _snippet_versions:
        _snippet_versions[snippet_id] = []
    _snippet_versions[snippet_id].append(version)

    logger.debug(f"Created version {version_number} for snippet {snippet_id}")
    return version_number


def get_snippet(snippet_id: str) -> Optional[SnippetRecord]:
    """
    Get a snippet by ID.

    Args:
        snippet_id: Snippet ID

    Returns:
        SnippetRecord or None if not found
    """
    return _snippets.get(snippet_id)


def get_latest_version(snippet_id: str) -> Optional[SnippetVersionRecord]:
    """
    Get the latest version of a snippet.

    Args:
        snippet_id: Snippet ID

    Returns:
        Latest SnippetVersionRecord or None if not found
    """
    versions = _snippet_versions.get(snippet_id, [])
    if not versions:
        return None
    # Versions are appended in order, so the last one is the latest
    return versions[-1]


def get_all_versions(snippet_id: str) -> List[SnippetVersionRecord]:
    """
    Get all versions of a snippet.

    Args:
        snippet_id: Snippet ID

    Returns:
        List of SnippetVersionRecord, sorted by version_number
    """
    return _snippet_versions.get(snippet_id, []).copy()


def list_snippets(
    search_query: Optional[str] = None
) -> List[SnippetRecord]:
    """
    List all snippets, optionally filtered by search query.

    Args:
        search_query: Optional search string to filter by title/description

    Returns:
        List of SnippetRecord matching the filters
    """
    results = list(_snippets.values())

    # Filter by search query if provided
    if search_query:
        search_lower = search_query.lower()
        filtered_results = []
        for snippet in results:
            # Search in title
            if search_lower in snippet.title.lower():
                filtered_results.append(snippet)
                continue

            # Search in description/metadata
            latest_version = get_latest_version(snippet.id)
            if latest_version:
                if search_lower in latest_version.description.lower():
                    filtered_results.append(snippet)
                    continue
                if search_lower in latest_version.metadata.get("name", "").lower():
                    filtered_results.append(snippet)
        results = filtered_results

    # Sort by created_at (newest first)
    results.sort(key=lambda s: s.created_at, reverse=True)
    return results


def delete_snippet(snippet_id: str) -> bool:
    """
    Delete a snippet and all its versions.

    Args:
        snippet_id: Snippet ID

    Returns:
        True if deleted, False if not found
    """
    if snippet_id not in _snippets:
        return False

    del _snippets[snippet_id]
    if snippet_id in _snippet_versions:
        del _snippet_versions[snippet_id]
    logger.debug(f"Deleted snippet: {snippet_id}")
    return True


def clear_all() -> None:
    """
    Clear all snippets and versions (useful for testing).
    """
    _snippets.clear()
    _snippet_versions.clear()

