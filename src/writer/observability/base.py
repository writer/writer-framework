import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ObservabilityProvider(ABC):
    """Abstract base class for observability providers."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the observability provider."""
        pass
    
    @abstractmethod
    def instrument_fastapi_app(self, app: Any) -> None:
        """Instrument FastAPI application with observability."""
        pass
    
    def get_name(self) -> str:
        """Get the name of the provider."""
        return self.__class__.__name__.lower().replace("adapter", "").replace("provider", "")
    
    def is_enabled(self) -> bool:
        """Check if the provider is enabled."""
        return True


class ObservabilityRegistry:
    """Registry for managing observability providers."""
    
    def __init__(self):
        self._providers: Dict[str, ObservabilityProvider] = {}
        self._initialized_provider: Optional[ObservabilityProvider] = None
    
    def register(self, name: str, provider: ObservabilityProvider) -> None:
        """Register an observability provider."""
        if name in self._providers:
            logger.warning(f"Overwriting existing provider '{name}'")
        self._providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[ObservabilityProvider]:
        """Get a provider by name."""
        return self._providers.get(name)
    
    def list_providers(self) -> List[str]:
        """List all registered provider names."""
        return list(self._providers.keys())
    
    def initialize_provider(self, name: Optional[str] = None) -> bool:
        """Initialize a provider."""
        if name is None:
            name = os.getenv("OBSERVABILITY_PROVIDER")
            if name is None:
                for provider_name, provider in self._providers.items():
                    if provider.is_enabled():
                        name = provider_name
                        break
        
        if name is None:
            logger.info("No observability provider configured")
            return False
        
        provider = self.get_provider(name)
        if provider is None:
            logger.warning(f"Observability provider '{name}' not found. Available: {self.list_providers()}")
            return False
        
        if not provider.is_enabled():
            logger.info(f"Observability provider '{name}' is disabled")
            return False
        
        try:
            if provider.initialize():
                self._initialized_provider = provider
                logger.info(f"Initialized observability provider: {name}")
                return True
            else:
                logger.warning(f"Failed to initialize observability provider: {name}")
                return False
        except Exception as e:
            logger.error(f"Error initializing observability provider '{name}': {e}", exc_info=True)
            return False
    
    def instrument_app(self, app: Any) -> None:
        """Instrument the app with the initialized provider."""
        if self._initialized_provider is None:
            logger.debug("No observability provider initialized, skipping instrumentation")
            return
        try:
            self._initialized_provider.instrument_fastapi_app(app)
        except Exception as e:
            logger.error(f"Error instrumenting app with observability provider: {e}", exc_info=True)
    
    def get_initialized_provider(self) -> Optional[ObservabilityProvider]:
        """Get the currently initialized provider."""
        return self._initialized_provider

