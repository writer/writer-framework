"""
Writer Vault module for managing secret retrieval and caching.

This module provides the WriterVault class which handles fetching and caching
secrets from the Writer vault service, with support for environment-based
configuration and error handling.
"""

import logging
import os
from typing import Dict, Optional

import requests


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

    def _get_agent_ids(self):
        from writer.core import get_session
        current_session = get_session()

        if current_session:
            headers = current_session.headers or {}
            agent_id = headers.get("x-agent-id") or os.getenv("WRITER_APP_ID")
            org_id = headers.get("x-organization-id") or os.getenv("WRITER_ORG_ID")
            return (agent_id, org_id)

        agent_id = os.getenv("WRITER_APP_ID")
        org_id = os.getenv("WRITER_ORG_ID")
        return (agent_id, org_id)

    def _fetch(self) -> Dict:
        # TODO: move the API call to a service
        base_url = os.getenv("WRITER_BASE_URL")
        api_key = os.getenv("WRITER_API_KEY")
        (agent_id, org_id) = self._get_agent_ids()

        if None in (base_url, api_key):
            logging.warning("Missing required environment variables for vault access")
            return {}

        if None in (agent_id, org_id):
            logging.warning("Missing Org Id or Agent Id for vault access")
            return {}

        url = f"{base_url}/v1/agent_secret/vault"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Organization-Id": org_id,
            "X-Agent-Id": agent_id,
        }

        try:
            logging.debug("fetching Writer Vault secrets")
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                secrets = data.get("secret")
                if isinstance(secrets, dict):
                    return secrets
                logging.warning("Invalid vault response format: expected dict in 'secret' field")
            else:
                logging.warning("Vault API returned status %s", response.status_code)
        except requests.RequestException as e:
            logging.error("Failed to fetch vault secrets: %s", e)
        return {}


writer_vault = WriterVault()
