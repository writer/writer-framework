"""
Mock in-memory database for block library snippets.

Simulates the application tables structure using in-memory dictionaries:
- SnippetRecord -> Application (with type='shared-blueprint')
- SnippetVersionRecord -> ApplicationVersion + ApplicationVersionData combined

Version numbers are simple integers, derived from the count of versions.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SnippetRecord:
    """
    Record representing a snippet (block) in the library.
    
    Maps to: Application table with type='shared-blueprint'
    """

    id: str  # UUID (application.id)
    visibility: str  # "ORGANIZATION" for org-level visibility
    title: str  # Stored in the associated ApplicationVersion.name
    org_id: str = ""  # Organization ID (application.organization_id)
    live_version_id: Optional[str] = None  # Points to latest version (application.live_version_id)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SnippetVersionRecord:
    """
    Record representing a version of a snippet.
    
    Maps to: ApplicationVersion + ApplicationVersionData combined
    """

    id: str  # UUID (application_version.id)
    snippet_id: str  # application_id
    version_number: int  # Derived from count of versions
    blueprint_components: List[Dict[str, Any]]  # From application_version_data.data.components
    description: str  # application_version.description
    metadata: dict  # Stored in application_version_data.data.metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


# In-memory storage
_snippets: Dict[str, SnippetRecord] = {}
_snippet_versions: Dict[str, List[SnippetVersionRecord]] = {}


def create_snippet(
    title: str,
    visibility: str = "ORGANIZATION",
    org_id: str = "",
) -> str:
    """
    Create a new snippet record.

    Args:
        title: Snippet title
        visibility: Visibility level (default: "ORGANIZATION")
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
        live_version_id=None,
    )
    _snippets[snippet_id] = snippet
    _snippet_versions[snippet_id] = []
    logger.debug(f"Created snippet: {snippet_id} ({title})")
    return snippet_id


def create_snippet_version(
    snippet_id: str,
    blueprint_components: List[Dict[str, Any]],
    description: str,
    metadata: dict,
) -> int:
    """
    Create a new version for a snippet.

    Args:
        snippet_id: ID of the snippet
        blueprint_components: Blueprint component structure (list of component dicts)
        description: Block description
        metadata: Block metadata (name, state_inputs, etc.)

    Returns:
        version_number (integer, starting from 1)

    Raises:
        ValueError: If snippet_id doesn't exist
    """
    if snippet_id not in _snippets:
        raise ValueError(f"Snippet {snippet_id} not found")

    versions = _snippet_versions.get(snippet_id, [])
    
    # Version number is simply the count + 1
    new_version_number = len(versions) + 1

    version_id = str(uuid.uuid4())
    version_record = SnippetVersionRecord(
        id=version_id,
        snippet_id=snippet_id,
        version_number=new_version_number,
        blueprint_components=blueprint_components,
        description=description,
        metadata=metadata,
    )

    if snippet_id not in _snippet_versions:
        _snippet_versions[snippet_id] = []
    _snippet_versions[snippet_id].append(version_record)

    # Update the snippet's live_version_id to point to this new version
    _snippets[snippet_id].live_version_id = version_id

    logger.debug(f"Created version {new_version_number} for snippet {snippet_id}")
    return new_version_number


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
        List of SnippetVersionRecord, in chronological order
    """
    return _snippet_versions.get(snippet_id, []).copy()


def list_snippets(
    search_query: Optional[str] = None,
    org_id: Optional[str] = None,
) -> List[SnippetRecord]:
    """
    List all snippets, optionally filtered by search query and org_id.

    Args:
        search_query: Optional search string to filter by title/description
        org_id: Optional organization ID to filter by

    Returns:
        List of SnippetRecord matching the filters
    """
    results = list(_snippets.values())

    # Filter by org_id if provided
    if org_id:
        results = [s for s in results if s.org_id == org_id]

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
