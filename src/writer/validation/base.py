"""
Base classes for schema validation providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ValidationError:
    """Standardized validation error format."""
    field_path: str
    message: str
    schema_path: Optional[str] = None
    
    def __str__(self) -> str:
        return self.message


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    errors: List[ValidationError]
    
    @property
    def error_message(self) -> str:
        """Get first error message for backward compatibility."""
        return self.errors[0].message if self.errors else "Valid"
    
    @classmethod
    def success(cls) -> 'ValidationResult':
        """Create successful validation result."""
        return cls(is_valid=True, errors=[])
    
    @classmethod
    def failure(cls, message: str, field_path: str = "") -> 'ValidationResult':
        """Create failed validation result with single error."""
        error = ValidationError(field_path=field_path, message=message)
        return cls(is_valid=False, errors=[error])


class SchemaProvider(ABC):
    """
    Abstract base class for schema validation providers.
    
    This allows different validation backends (custom, JSON Schema, 
    JSON Typedef, etc.) to be plugged into the API trigger system.
    """
    
    @abstractmethod
    def validate_payload(
        self, 
        payload: Dict[str, Any], 
        field_definitions: List[Dict[str, Any]],
        strict: bool = False
    ) -> ValidationResult:
        """
        Validate a payload against field definitions.
        
        Args:
            payload: JSON data to validate
            field_definitions: Field definition schema
            strict: If True, reject payloads with undefined fields
            
        Returns:
            ValidationResult with success/failure and errors
        """
        pass
    
    @abstractmethod
    def validate_field_definitions(
        self, 
        field_definitions: List[Dict[str, Any]]
    ) -> ValidationResult:
        """
        Validate that field definitions themselves are well-formed.
        
        Args:
            field_definitions: Field definitions to validate
            
        Returns:
            ValidationResult indicating if definitions are valid
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this provider."""
        pass
    
    @property
    def supports_advanced_features(self) -> bool:
        """Whether this provider supports advanced validation features."""
        return False


class SchemaProviderRegistry:
    """Registry for schema validation providers."""
    
    _providers: Dict[str, SchemaProvider] = {}
    _default_provider: Optional[str] = None
    
    @classmethod
    def register(cls, provider: SchemaProvider, make_default: bool = False):
        """Register a schema provider."""
        cls._providers[provider.name] = provider
        if make_default or cls._default_provider is None:
            cls._default_provider = provider.name
    
    @classmethod
    def get_provider(cls, name: Optional[str] = None) -> SchemaProvider:
        """Get a provider by name, or the default provider."""
        provider_name = name or cls._default_provider
        if not provider_name or provider_name not in cls._providers:
            raise ValueError(f"Unknown schema provider: {provider_name}")
        return cls._providers[provider_name]
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List all registered provider names."""
        return list(cls._providers.keys())
    
    @classmethod
    def set_default(cls, name: str):
        """Set the default provider."""
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' not registered")
        cls._default_provider = name