from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from msal import ConfidentialClientApplication
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError, GraphRequestError
from smarthaus_common.logging import get_logger

log = get_logger(__name__)


@dataclass
class Token:
    access_token: str
    expires_at: float

    def valid(self) -> bool:
        # Consider a 60s buffer
        return time.time() < (self.expires_at - 60)


class GraphTokenProvider:
    def __init__(self, config: AppConfig):
        self._config = config
        self._cca: ConfidentialClientApplication | None = None
        self._token: Token | None = None

    def _ensure_client(self) -> None:
        cfg = self._config.graph
        if not (cfg.tenant_id and cfg.client_id and cfg.client_secret):
            raise AuthConfigurationError("GRAPH_TENANT_ID/CLIENT_ID/CLIENT_SECRET must be set")
        if self._cca is None:
            authority = f"https://login.microsoftonline.com/{cfg.tenant_id}"
            self._cca = ConfidentialClientApplication(
                client_id=cfg.client_id,
                client_credential=cfg.client_secret,
                authority=authority,
            )

    def get_token(self) -> str:
        if self._token and self._token.valid():
            return self._token.access_token

        self._ensure_client()
        assert self._cca is not None
        scopes = [self._config.graph.scope]
        result = self._cca.acquire_token_silent(scopes=scopes, account=None)
        if not result:
            result = self._cca.acquire_token_for_client(scopes=scopes)
        if "access_token" not in result:
            raise AuthConfigurationError(
                f"Failed to acquire token: {result.get('error_description')}"
            )
        self._token = Token(
            access_token=result["access_token"],
            expires_at=time.time() + int(result.get("expires_in", 3600)),
        )
        return self._token.access_token


class GraphClient:
    def __init__(
        self, config: AppConfig | None = None, base_url: str = "https://graph.microsoft.com/v1.0"
    ):
        self.config = config or AppConfig()
        self.base_url = base_url.rstrip("/")
        self._token_provider = GraphTokenProvider(self.config)
        self._client = httpx.Client(timeout=30)

    def _headers(self) -> dict[str, str]:
        token = self._token_provider.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    @retry(
        retry=retry_if_exception_type(GraphRequestError),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers.update(self._headers())
        resp = self._client.request(method, url, headers=headers, **kwargs)
        if resp.status_code in (429, 503, 504):
            # Honor Retry-After if present
            ra = resp.headers.get("Retry-After")
            if ra:
                try:
                    sleep_for = int(ra)
                    log.warning("Graph throttled (%s). Sleeping %ss", resp.status_code, sleep_for)
                    time.sleep(sleep_for)
                except ValueError:
                    pass
            raise GraphRequestError(f"Transient error {resp.status_code}: {resp.text}")
        if resp.status_code >= 400:
            raise GraphRequestError(f"Graph error {resp.status_code}: {resp.text}")
        return resp

    # Example endpoints
    def get_organization(self) -> dict[str, Any]:
        r = self._request("GET", "/organization")
        data: dict[str, Any] = r.json()
        return data

    def list_teams(self) -> dict[str, Any]:
        r = self._request("GET", "/teams")  # Note: requires proper app permissions
        return r.json()

    # ---------- M365 Helpers ----------
    def find_group_by_mailnickname(self, mail_nickname: str) -> dict | None:
        params = {"$filter": f"mailNickname eq '{mail_nickname}'", "$top": "1"}
        r = self._request("GET", "/groups", params=params)
        data = r.json()
        items = data.get("value", [])
        return items[0] if items else None

    def create_group(
        self, display_name: str, mail_nickname: str, description: str | None = None
    ) -> dict:
        body = {
            "displayName": display_name,
            "mailEnabled": True,
            "mailNickname": mail_nickname,
            "securityEnabled": False,
            "groupTypes": ["Unified"],
        }
        if description:
            body["description"] = description
        r = self._request("POST", "/groups", json=body)
        return r.json()

    def get_site_by_path(self, hostname: str, site_path: str) -> dict:
        # Example: /sites/{hostname}:/sites/{site_path}
        p = f"/sites/{hostname}:/sites/{site_path}"
        r = self._request("GET", p)
        return r.json()

    def list_site_lists(self, site_id: str) -> list[dict]:
        r = self._request("GET", f"/sites/{site_id}/lists", params={"$top": "999"})
        data = r.json()
        return data.get("value", [])

    def create_document_library(self, site_id: str, display_name: str) -> dict:
        body = {
            "displayName": display_name,
            "list": {"template": "documentLibrary"},
        }
        r = self._request("POST", f"/sites/{site_id}/lists", json=body)
        return r.json()

    # ---------- Teams Helpers ----------
    def teamify_group(self, group_id: str) -> None:
        body = {
            "memberSettings": {"allowCreateUpdateChannels": True},
            "messagingSettings": {
                "allowUserEditMessages": True,
                "allowUserDeleteMessages": True,
            },
            "funSettings": {"allowGiphy": True, "giphyContentRating": "moderate"},
        }
        self._request("PUT", f"/groups/{group_id}/team", json=body)

    def get_team(self, team_id: str) -> dict:
        r = self._request("GET", f"/teams/{team_id}")
        return r.json()

    def list_team_channels(self, team_id: str) -> list[dict]:
        r = self._request("GET", f"/teams/{team_id}/channels")
        data = r.json()
        return data.get("value", [])

    def create_team_channel(
        self, team_id: str, display_name: str, description: str | None = None
    ) -> dict:
        body = {"displayName": display_name}
        if description:
            body["description"] = description
        r = self._request("POST", f"/teams/{team_id}/channels", json=body)
        return r.json()
