"""
Observability integration module with adapter pattern support.
"""
import logging
from typing import Optional

from writer.observability.base import ObservabilityProvider, ObservabilityRegistry

logger = logging.getLogger(__name__)

__all__ = [
    "ObservabilityProvider",
    "ObservabilityRegistry",
]

observability_registry = ObservabilityRegistry()


def _register_sentry_adapter(app_path: Optional[str] = None):
    try:
        from writer.observability.sentry_adapter import SentryAdapter
        sentry_adapter = SentryAdapter(app_path=app_path)
        if sentry_adapter.is_enabled():
            observability_registry.register("sentry", sentry_adapter)
            __all__.append("SentryAdapter")
    except Exception as e:
        logger.debug(f"Sentry adapter not available: {e}")


def get_registry(app_path: Optional[str] = None):
    _register_sentry_adapter(app_path=app_path)
    return observability_registry
