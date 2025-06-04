import os
from typing import Dict, Union

import requests


# TODO: move in a better place?
class WriterVault:
    def __init__(self) -> None:
        self.secrets: Union[Dict, None] = None

    def get_secrets(self) -> Dict:
        if self.secrets is None:
            self.secrets = self._fetch()
        return self.secrets

    def refresh(self):
        self.secrets = self._fetch()

    def _fetch(self) -> Dict:
        # TODO: move the API call to a service
        base_url = os.getenv("WRITER_BASE_URL")
        api_key = os.getenv("WRITER_API_KEY")
        ord_id = os.getenv("WRITER_ORG_ID")
        app_id = os.getenv("WRITER_APP_ID")

        if None in (base_url, api_key, ord_id, app_id):
            return {}

        url = f"{base_url}/v1/agent_secret/vault"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Organization-Id": ord_id,
            "X-Agent-Id": app_id,
        }

        response = requests.get(url, headers=headers, timeout=3)

        if response.status_code == 200:
            return response.json().get("secret")
        else:
            return {}


writer_vault = WriterVault()
