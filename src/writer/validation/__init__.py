"""
Validation framework for Writer Framework.

This module provides a pluggable architecture for schema validation with 
multiple provider backends.

Basic usage:
    from writer.blocks.apitrigger import APITrigger
    
    # Uses default provider (legacy for backward compatibility)
    is_valid, error = APITrigger.validate_payload(payload, field_definitions)
    
    # Use specific provider
    is_valid, error = APITrigger.validate_payload(
        payload, field_definitions, provider_name="jtd"
    )

Available providers:
    - "legacy": Original custom validation with constraints support
    - "jtd": JSON Typedef (RFC 8927) validation (requires 'jtd' package)
"""

from .base import SchemaProvider, SchemaProviderRegistry, ValidationError, ValidationResult
from .legacy_provider import LegacySchemaProvider

__all__ = [
    "SchemaProvider",
    "SchemaProviderRegistry", 
    "ValidationError",
    "ValidationResult",
    "LegacySchemaProvider"
]

# JTD provider is optional
try:
    from .jtd_provider import JTDSchemaProvider
    __all__.append("JTDSchemaProvider")
except ImportError:
    pass