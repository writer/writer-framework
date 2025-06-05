import logging
import os
from typing import Any, Optional

import httpx

from writer.ss_types import WriterConfigurationError


class BaseAPIClient:
    API_BASE_URL = os.getenv("WRITER_BASE_URL", "https://api.writer.com")
    API_VERSION = os.getenv("WRITER_API_VERSION", "v1")

    def __init__(self):
        self.client = httpx.Client(
            base_url=f"{self.API_BASE_URL}/{self.API_VERSION}",
            timeout=httpx.Timeout(10.0, connect=5.0),
            )
        self.headers = {
            'X-Agent-Id': os.getenv("WRITER_APP_ID"),
            'X-Organization-Id': os.getenv("WRITER_ORG_ID"),
            'Authorization': f"Bearer {os.getenv('WRITER_API_KEY')}",
        }
        env_var_mapping = {
            'X-Agent-Id': 'WRITER_APP_ID',
            'X-Organization-Id': 'WRITER_ORG_ID',
            'Authorization': 'WRITER_API_KEY'
        }
        missing_env_vars = [env_var_mapping[k] for k, v in self.headers.items() if v is None]
        if missing_env_vars:
            raise WriterConfigurationError(
                "Missing required environment variables for API client: "
                f"{', '.join(missing_env_vars)}."
            )

    def request(
            self,
            method: str,
            endpoint: str,
            data: Optional[dict] = None,
            user_id: Optional[str] = None
    ) -> Optional[dict]:
        url = endpoint
        request_headers = self.headers.copy()
        if user_id:
            request_headers['X-User-Id'] = user_id

        response = self.client.request(
            method,
            url,
            headers=request_headers,
            json=data
            )
        if response.status_code != 200:
            logging.error(
                f"API request failed: {response.status_code}, "
                f"{response.text}"
                )
            return None
        return response.json()


class KeyValueAPIClient(BaseAPIClient):
    def _set(self, key: str, value: Any, user_id: Optional[str] = None) -> Optional[dict]:
        """
        Internal method to set a key-value pair in the agent data.
        :param key: The key to set.
        :param value: The value to set for the key.
        :param user_id: Optional user ID for the request.
        :return: The response from the API or None if failed.
        """
        data = {"key": key, "data": value}

        url = "agent_data"
        response = self.request("POST", url, data, user_id)
        if response is None:
            logging.error(f"Failed to set value for key: {key}")
            return None
        return response

    def set_value(self, key: str, value: Any, user_id: Optional[str] = None):
        """
        Set a key-value pair in the agent data.
        :param key: The key to set.
        :param value: The value to set for the key.
        :param user_id: Optional user ID for the request.
        :return: The response from the API.
        """
        response = self._set(key, value, user_id)
        if response is not None:
            logging.info(f"Successfully set value for key: {key}")
            return response.get("data")

    def _get(self, key: str, user_id: Optional[str] = None) -> Optional[dict]:
        """
        Internal method to get a value for a specific key.
        :param key: The key to retrieve.
        :param user_id: Optional user ID for the request.
        :return: The response from the API or None if not found.
        """
        url = f"agent_data/{key}"
        response = self.request("GET", url, user_id=user_id)
        if response is None:
            logging.error(f"Failed to get value for key: {key}")
            return None
        return response

    def get_value(self, key: str, user_id: Optional[str] = None) -> Any:
        """
        Get the value for a specific key from the agent data.
        :param key: The key to retrieve.
        :param user_id: Optional user ID for the request.
        :return: The value associated with the key, or None if not found.
        """
        response = self._get(key, user_id)
        if response is not None:
            logging.info(f"Successfully retrieved value for key: {key}")
            return response.get("data")

    def _put(self, key: str, value: Any, user_id: Optional[str] = None) -> Optional[dict]:
        """
        Internal method to update a value for a specific key.
        :param key: The key to update.
        :param value: The new value to set for the key.
        :param user_id: Optional user ID for the request.
        :return: The response from the API or None if failed.
        """
        data = {"key": key, "data": value}

        url = f"agent_data/{key}"
        response = self.request("PUT", url, data, user_id)
        if response is None:
            logging.error(f"Failed to update value for key: {key}")
            return None
        return response

    def put_value(self, key: str, value: Any, user_id: Optional[str] = None):
        """
        Update the value for a specific key in the agent data.
        :param key: The key to update.
        :param value: The new value to set for the key.
        :param user_id: Optional user ID for the request.
        :return: The response from the API.
        """
        response = self._put(key, value, user_id)
        if response is not None:
            logging.info(f"Successfully updated value for key: {key}")
            return response.get("data")

    def delete_value(self, key: str, user_id: Optional[str] = None):
        url = f"agent_data/{key}"
        response = self.request("DELETE", url, user_id=user_id)
        if response is not None:
            logging.info(f"Successfully deleted value for key: {key}")
            return True
        return False
