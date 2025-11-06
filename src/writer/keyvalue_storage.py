import logging
import os
from functools import partial
from typing import Any, Dict, Literal, Optional, Protocol

import httpx

logger = logging.getLogger("kv_storage")


class _WrappedRequestFunc(Protocol):
    def __call__(
        self,
        headers: Dict[str, str],
        timeout: int,
    ) -> httpx.Response: ...


class KeyValueStorage:
    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        base_url = os.getenv("WRITER_BASE_URL")
        self.api_key = os.getenv("WRITER_API_KEY")
        if None in (base_url, self.api_key):
            logger.warning("Missing required environment variables for KV storage access")
        self.api_url = f"{base_url}/v1" if base_url else None

        self._client = client if client is not None else httpx

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

    def get(self, key: str, type_: Literal["data", "secret"]) -> Dict[str, Any]:
        return self._request(partial(self._client.get, url=f"{self.api_url}/agent_{type_}/{key}")).json()
    
    def save(self, key: str, data: Any) -> Dict[str, Any]:
        try:
            return self._create(key, data).json()
        except httpx.HTTPStatusError as e:
            if "already exists" in e.response.text:
                return self._update(key, data).json()
            raise e

    def _create(self, key: str, data: Any) -> httpx.Response:
        return self._request(partial(self._client.post, url=f"{self.api_url}/agent_data", json={"key": key, "data": data}))

    def _update(self, key: str, data: Any) -> httpx.Response:
        return self._request(partial(self._client.put, url=f"{self.api_url}/agent_data/{key}", json={"data": data}))

    def delete(self, key: str) -> Dict[str, str]:
        self._request(partial(self._client.delete, url=f"{self.api_url}/agent_data/{key}"))
        return {"key": key}

    def _request(self, request_func: _WrappedRequestFunc) -> httpx.Response:

        agent_id, org_id = self._get_agent_ids()
        if None in (agent_id, org_id):
            raise ValueError("Can't access KV storage. Missing agent id or org id")

        if None in (self.api_key, self.api_url):
            raise ValueError("Can't access KV storage. Missing required env vars")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Organization-Id": org_id,
            "X-Agent-Id": agent_id,
        }

        response = request_func(headers=headers, timeout=3)
        response.raise_for_status()
        return response

writer_kv_storage = KeyValueStorage()
