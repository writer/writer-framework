"""
Shared Blueprint Service - matches the Scala SharedBlueprintService API.

This module provides:
1. DTOs that match the Scala case classes
2. A Protocol defining the service interface
3. An in-memory mock implementation

To switch to the real Scala service, implement a new class that:
- Inherits from SharedBlueprintService protocol
- Makes HTTP calls to the template-service API
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# =============================================================================
# DTOs - Match Scala case classes exactly
# =============================================================================


@dataclass
class SharedBlueprintMetadata:
    """
    Metadata for a shared blueprint.
    
    Matches Scala: com.writer.template.model.ApplicationData.SharedBlueprintMetadata
    """

    state_inputs: List[str] = field(default_factory=list)
    state_outputs: List[str] = field(default_factory=list)
    vault_keys: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    author: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stateInputs": self.state_inputs,
            "stateOutputs": self.state_outputs,
            "vaultKeys": self.vault_keys,
            "dependencies": self.dependencies,
            "author": self.author,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SharedBlueprintMetadata":
        return cls(
            state_inputs=data.get("stateInputs", data.get("state_inputs", [])),
            state_outputs=data.get("stateOutputs", data.get("state_outputs", [])),
            vault_keys=data.get("vaultKeys", data.get("vault_keys", [])),
            dependencies=data.get("dependencies", []),
            author=data.get("author"),
        )


@dataclass
class PublishSharedBlueprintRequest:
    """
    Request DTO for publishing a shared blueprint.
    
    Matches Scala: com.writer.template.service.PublishSharedBlueprintRequest
    """

    name: str
    description: str
    components: List[Dict[str, Any]]
    metadata: SharedBlueprintMetadata
    snippet_id: Optional[str] = None  # If provided, updates existing; otherwise creates new


@dataclass
class PublishSharedBlueprintResponse:
    """
    Response DTO for publish operation.
    
    Matches Scala: com.writer.template.service.PublishSharedBlueprintResponse
    """

    snippet_id: str
    version_number: int


@dataclass
class SharedBlueprintResponse:
    """
    Response DTO for shared blueprint list and get operations.
    
    Matches Scala: com.writer.template.service.SharedBlueprintResponse
    """

    id: str
    title: str
    description: Optional[str]
    version_number: int
    organization_id: str
    created_by: int
    created_at: datetime
    updated_at: datetime


@dataclass
class SharedBlueprintWithDataResponse:
    """
    Response DTO for shared blueprint with full data.
    
    Matches Scala: com.writer.template.service.SharedBlueprintWithDataResponse
    """

    id: str
    title: str
    description: Optional[str]
    version_number: int
    organization_id: str
    components: List[Dict[str, Any]]
    metadata: SharedBlueprintMetadata
    created_by: int
    created_at: datetime


@dataclass
class SharedBlueprintVersionResponse:
    """
    Response DTO for shared blueprint version.
    
    Matches Scala: com.writer.template.service.SharedBlueprintVersionResponse
    """

    id: str
    version_number: int
    description: Optional[str]
    created_by: int
    created_at: datetime


# =============================================================================
# Service Interface - Abstract base class matching Scala trait
# =============================================================================


class SharedBlueprintService(ABC):
    """
    Abstract service interface for shared blueprints.
    
    Matches Scala: com.writer.template.service.SharedBlueprintService trait
    
    To implement the real service, create a class that:
    - Extends this ABC
    - Makes HTTP calls to /api/template/organization/{orgId}/shared-blueprints
    """

    @abstractmethod
    def publish(
        self,
        organization_id: str,
        user_id: int,
        request: PublishSharedBlueprintRequest,
    ) -> PublishSharedBlueprintResponse:
        """
        Publish a shared blueprint (create new or add version to existing).
        """
        pass

    @abstractmethod
    def list(self, organization_id: str) -> List[SharedBlueprintResponse]:
        """
        List all shared blueprints for an organization.
        """
        pass

    @abstractmethod
    def get(self, blueprint_id: str) -> SharedBlueprintWithDataResponse:
        """
        Get a shared blueprint by ID with its latest version data.
        
        Raises:
            KeyError: If blueprint not found
        """
        pass

    @abstractmethod
    def get_versions(self, blueprint_id: str) -> List[SharedBlueprintVersionResponse]:
        """
        Get all versions of a shared blueprint.
        
        Raises:
            KeyError: If blueprint not found
        """
        pass


# =============================================================================
# In-Memory Mock Implementation
# =============================================================================


@dataclass
class _ApplicationRecord:
    """Internal: Simulates Application table row."""

    id: str
    organization_id: str
    live_version_id: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime


@dataclass
class _VersionRecord:
    """Internal: Simulates ApplicationVersion + ApplicationVersionData."""

    id: str
    application_id: str
    name: str
    description: str
    components: List[Dict[str, Any]]
    metadata: SharedBlueprintMetadata
    created_by: int
    created_at: datetime


class InMemorySharedBlueprintService(SharedBlueprintService):
    """
    In-memory mock implementation of SharedBlueprintService.
    
    For development and testing. Replace with HTTP-based implementation
    that calls the Scala template-service API in production.
    """

    def __init__(self):
        self._applications: Dict[str, _ApplicationRecord] = {}
        self._versions: Dict[str, List[_VersionRecord]] = {}

    def publish(
        self,
        organization_id: str,
        user_id: int,
        request: PublishSharedBlueprintRequest,
    ) -> PublishSharedBlueprintResponse:
        now = datetime.now(timezone.utc)

        if request.snippet_id and request.snippet_id in self._applications:
            # Add new version to existing blueprint
            app = self._applications[request.snippet_id]
            versions = self._versions.get(request.snippet_id, [])
            new_version_number = len(versions) + 1

            version_id = str(uuid.uuid4())
            version = _VersionRecord(
                id=version_id,
                application_id=request.snippet_id,
                name=request.name,
                description=request.description,
                components=request.components,
                metadata=request.metadata,
                created_by=user_id,
                created_at=now,
            )

            self._versions.setdefault(request.snippet_id, []).append(version)
            app.live_version_id = version_id
            app.updated_at = now

            return PublishSharedBlueprintResponse(
                snippet_id=request.snippet_id,
                version_number=new_version_number,
            )
        else:
            # Create new blueprint
            application_id = str(uuid.uuid4())
            version_id = str(uuid.uuid4())

            app = _ApplicationRecord(
                id=application_id,
                organization_id=organization_id,
                live_version_id=version_id,
                created_by=user_id,
                created_at=now,
                updated_at=now,
            )

            version = _VersionRecord(
                id=version_id,
                application_id=application_id,
                name=request.name,
                description=request.description,
                components=request.components,
                metadata=request.metadata,
                created_by=user_id,
                created_at=now,
            )

            self._applications[application_id] = app
            self._versions[application_id] = [version]

            return PublishSharedBlueprintResponse(
                snippet_id=application_id,
                version_number=1,
            )

    def list(self, organization_id: str) -> List[SharedBlueprintResponse]:
        results = []
        for app in self._applications.values():
            if app.organization_id != organization_id:
                continue

            versions = self._versions.get(app.id, [])
            latest = versions[-1] if versions else None

            results.append(
                SharedBlueprintResponse(
                    id=app.id,
                    title=latest.name if latest else "Untitled",
                    description=latest.description if latest else None,
                    version_number=len(versions),
                    organization_id=app.organization_id,
                    created_by=app.created_by,
                    created_at=app.created_at,
                    updated_at=app.updated_at,
                )
            )

        # Sort by created_at descending (newest first)
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    def get(self, blueprint_id: str) -> SharedBlueprintWithDataResponse:
        app = self._applications.get(blueprint_id)
        if not app:
            raise KeyError(f"Shared blueprint {blueprint_id} not found")

        versions = self._versions.get(blueprint_id, [])
        if not versions:
            raise KeyError(f"Shared blueprint {blueprint_id} has no versions")

        latest = versions[-1]

        return SharedBlueprintWithDataResponse(
            id=app.id,
            title=latest.name,
            description=latest.description,
            version_number=len(versions),
            organization_id=app.organization_id,
            components=latest.components,
            metadata=latest.metadata,
            created_by=app.created_by,
            created_at=app.created_at,
        )

    def get_versions(self, blueprint_id: str) -> List[SharedBlueprintVersionResponse]:
        if blueprint_id not in self._applications:
            raise KeyError(f"Shared blueprint {blueprint_id} not found")

        versions = self._versions.get(blueprint_id, [])
        total = len(versions)

        # Return in reverse order (newest first), with correct version numbers
        return [
            SharedBlueprintVersionResponse(
                id=v.id,
                version_number=total - idx,  # Newest is highest version
                description=v.description,
                created_by=v.created_by,
                created_at=v.created_at,
            )
            for idx, v in enumerate(reversed(versions))
        ]

    def clear(self) -> None:
        """Clear all data (useful for testing)."""
        self._applications.clear()
        self._versions.clear()


# =============================================================================
# Global service instance - replace with real implementation in production
# =============================================================================

_service: Optional[SharedBlueprintService] = None


def get_shared_blueprint_service() -> SharedBlueprintService:
    """
    Get the shared blueprint service instance.
    
    Returns the configured service implementation. By default, returns
    an in-memory mock. In production, configure this to return an
    HTTP-based implementation that calls the Scala template-service.
    """
    global _service
    if _service is None:
        _service = InMemorySharedBlueprintService()
    return _service


def set_shared_blueprint_service(service: SharedBlueprintService) -> None:
    """
    Set the shared blueprint service implementation.
    
    Use this to inject a different implementation (e.g., HTTP client
    to the Scala template-service) in production.
    """
    global _service
    _service = service

