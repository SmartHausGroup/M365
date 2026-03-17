from __future__ import annotations

import os
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class KeyVault:
    def __init__(self, vault_url: Optional[str] = None):
        url = vault_url or os.getenv("KEYVAULT_URL") or ""
        if not url:
            raise ValueError("KEYVAULT_URL not set")
        # DefaultAzureCredential supports managed identity, env vars, etc.
        cred = DefaultAzureCredential()
        self._client = SecretClient(vault_url=url, credential=cred)

    def get_secret(self, name: str) -> str:
        return self._client.get_secret(name).value

