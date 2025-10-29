"""
Writer Vault module for managing secret retrieval and caching.

This module provides the WriterVault class which handles fetching and caching
secrets from the Writer vault service, with support for environment-based
configuration and error handling.
"""

import logging
from typing import Dict, Optional

import httpx

from writer.keyvalue_storage import writer_kv_storage

logger = logging.getLogger("vault")


class WriterVault:
    """Manages retrieval and caching of secrets from the Writer vault service."""

    def __init__(self) -> None:
        """Initialize vault with empty cache."""
        self.secrets: Optional[Dict] = None

    def get_secrets(self) -> Dict:
        """Get cached secrets, fetching from vault if not already loaded."""
        if self.secrets is None:
            self.secrets = self._fetch()
        return self.secrets

    def refresh(self):
        """Force refresh of secrets from the vault service."""
        self.secrets = self._fetch()

    def _fetch(self) -> Dict:
        try:
            data = writer_kv_storage.get("vault", "secret")
            secrets = data.get("secret")
            if isinstance(secrets, dict):
                return secrets
            logger.warning("Invalid vault response format: expected dict in 'secret' field")
        except (httpx.HTTPStatusError, ValueError) as e:
            logger.error("Failed to fetch vault secrets: %s", e)
        return {}


writer_vault = WriterVault()
