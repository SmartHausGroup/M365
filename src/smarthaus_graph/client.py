"""UCP Graph API Client — dual-mode authentication.

Supports both app-only (client credentials) and delegated (device code flow)
authentication, driven by tenant configuration. No hardcoded credentials.

Auth modes:
  - app_only:   Client credentials flow via MSAL ConfidentialClientApplication.
                Cannot use /me endpoints. Uses site-scoped paths for file ops.
  - delegated:  Device code flow via MSAL PublicClientApplication.
                User signs in once, tokens cached and auto-refreshed.
                Full access to /me endpoints.
  - hybrid:     Starts with app_only, promotes to delegated on demand when
                a /me-scoped operation is requested.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from msal import ConfidentialClientApplication, PublicClientApplication, SerializableTokenCache
from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError, GraphRequestError
from smarthaus_common.logging import get_logger
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

log = get_logger(__name__)
_PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)
_CERTIFICATE_PATTERN = re.compile(
    r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
    re.DOTALL,
)


def _load_client_certificate_credential(cert_path: str) -> dict[str, Any]:
    """Build an MSAL-compatible certificate credential from a PEM or PFX file."""
    path = Path(cert_path)
    suffix = path.suffix.lower()

    if suffix in {".pfx", ".p12"}:
        return {"private_key_pfx_path": str(path)}

    pem_text = path.read_text(encoding="utf-8")
    key_match = _PRIVATE_KEY_PATTERN.search(pem_text)
    cert_matches = _CERTIFICATE_PATTERN.findall(pem_text)
    if not key_match or not cert_matches:
        raise AuthConfigurationError(
            "Certificate path must contain a private key and certificate in PEM format."
        )

    leaf_certificate = x509.load_pem_x509_certificate(cert_matches[0].encode("utf-8"))
    return {
        "private_key": key_match.group(0),
        "thumbprint": leaf_certificate.fingerprint(hashes.SHA1()).hex().upper(),
        "public_certificate": "\n".join(cert_matches),
    }


# ---------------------------------------------------------------------------
# Token wrapper
# ---------------------------------------------------------------------------


@dataclass
class Token:
    access_token: str
    expires_at: float
    auth_mode: str  # "app_only" or "delegated"

    def valid(self) -> bool:
        return time.time() < (self.expires_at - 60)


# ---------------------------------------------------------------------------
# Token cache persistence (for delegated auth)
# ---------------------------------------------------------------------------


class PersistentTokenCache(SerializableTokenCache):
    """MSAL token cache that persists to disk.

    Token cache files are per-tenant and stored in ~/.ucp/tokens/.
    """

    def __init__(self, cache_path: str):
        super().__init__()
        self._cache_path = cache_path
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._cache_path):
            try:
                with open(self._cache_path, encoding="utf-8") as f:
                    self.deserialize(f.read())
                log.debug("Token cache loaded from %s", self._cache_path)
            except Exception as e:
                log.warning("Failed to load token cache: %s", e)

    def _save(self) -> None:
        cache_dir = os.path.dirname(self._cache_path)
        os.makedirs(cache_dir, mode=0o700, exist_ok=True)
        with open(self._cache_path, "w", encoding="utf-8") as f:
            f.write(self.serialize())
        # Restrict permissions on the cache file
        os.chmod(self._cache_path, 0o600)

    def add(self, event: dict[str, Any], **kwargs: Any) -> None:
        super().add(event, **kwargs)
        if self.has_state_changed:
            self._save()

    def modify(
        self,
        credential_type: str,
        old_entry: dict[str, Any],
        new_key_value_pairs: dict[str, Any] | None = None,
    ) -> None:
        super().modify(credential_type, old_entry, new_key_value_pairs)
        if self.has_state_changed:
            self._save()

    def remove(self, credential_type: str, target: dict[str, Any]) -> None:
        super().remove(credential_type, target)
        if self.has_state_changed:
            self._save()


# ---------------------------------------------------------------------------
# Dual-mode token provider
# ---------------------------------------------------------------------------


class GraphTokenProvider:
    """Acquires Graph API tokens using either app-only or delegated auth.

    Driven entirely by TenantConfig — no hardcoded values.
    """

    def __init__(
        self, tenant_config: TenantConfig | None = None, legacy_config: AppConfig | None = None
    ):
        self._tenant_config = tenant_config or get_tenant_config()
        self._legacy_config = legacy_config

        # MSAL clients (lazily initialized)
        self._cca: ConfidentialClientApplication | None = None  # app-only
        self._pca: PublicClientApplication | None = None  # delegated
        self._token_cache: PersistentTokenCache | None = None

        # Cached tokens
        self._app_token: Token | None = None
        self._delegated_token: Token | None = None

    # --- App-only (client credentials) ---

    def _ensure_cca(self) -> ConfidentialClientApplication:
        if self._cca is not None:
            return self._cca

        cfg = self._tenant_config.azure
        if not (cfg.tenant_id and cfg.client_id):
            raise AuthConfigurationError(
                "Tenant config missing azure.tenant_id and/or azure.client_id. "
                "Set these in your tenant YAML or via environment variables."
            )

        credential: str | dict[str, Any]
        if cfg.client_certificate_path and os.path.exists(cfg.client_certificate_path):
            credential = _load_client_certificate_credential(cfg.client_certificate_path)
            log.info("Using certificate auth for tenant %s", cfg.tenant_id)
        elif cfg.client_secret:
            credential = cfg.client_secret
        else:
            raise AuthConfigurationError(
                "Tenant config missing azure.client_secret or azure.client_certificate_path. "
                "Set these in your tenant YAML or via environment variables."
            )

        authority = f"https://login.microsoftonline.com/{cfg.tenant_id}"
        self._cca = ConfidentialClientApplication(
            client_id=cfg.client_id,
            client_credential=credential,
            authority=authority,
        )
        return self._cca

    def get_app_token(self) -> str:
        """Acquire an app-only token (client credentials flow)."""
        if self._app_token and self._app_token.valid():
            return self._app_token.access_token

        cca = self._ensure_cca()
        scopes = [self._tenant_config.auth.app_only.scope]

        result = cca.acquire_token_silent(scopes=scopes, account=None)
        if not result:
            result = cca.acquire_token_for_client(scopes=scopes)
        if "access_token" not in result:
            raise AuthConfigurationError(
                f"Failed to acquire app token: {result.get('error_description')}"
            )

        self._app_token = Token(
            access_token=result["access_token"],
            expires_at=time.time() + int(result.get("expires_in", 3600)),
            auth_mode="app_only",
        )
        return self._app_token.access_token

    # --- Delegated (device code flow) ---

    def _ensure_pca(self) -> PublicClientApplication:
        if self._pca is not None:
            return self._pca

        cfg = self._tenant_config.azure
        if not (cfg.tenant_id and cfg.client_id):
            raise AuthConfigurationError(
                "Tenant config missing azure.tenant_id and/or azure.client_id."
            )

        # Persistent token cache
        cache_path = self._tenant_config.auth.delegated.token_cache_path
        if not cache_path:
            cache_dir = Path.home() / ".ucp" / "tokens"
            cache_path = str(cache_dir / f"{cfg.tenant_id}.cache")

        self._token_cache = PersistentTokenCache(cache_path)

        authority = f"https://login.microsoftonline.com/{cfg.tenant_id}"
        self._pca = PublicClientApplication(
            client_id=cfg.client_id,
            authority=authority,
            token_cache=self._token_cache,
        )
        return self._pca

    def get_delegated_token(self) -> str:
        """Acquire a delegated token (device code flow).

        On first call, prints a device code URL and waits for user sign-in.
        Subsequent calls use cached/refreshed tokens silently.
        """
        if self._delegated_token and self._delegated_token.valid():
            return self._delegated_token.access_token

        pca = self._ensure_pca()
        scopes = list(self._tenant_config.auth.delegated.scopes)

        # Try silent acquisition first (cached or refresh token)
        accounts = pca.get_accounts()
        if accounts:
            result = pca.acquire_token_silent(scopes=scopes, account=accounts[0])
            if result and "access_token" in result:
                self._delegated_token = Token(
                    access_token=result["access_token"],
                    expires_at=time.time() + int(result.get("expires_in", 3600)),
                    auth_mode="delegated",
                )
                log.info("Delegated token acquired silently (cached/refreshed)")
                return self._delegated_token.access_token

        # No cached token — initiate device code flow
        if not self._tenant_config.auth.delegated.auto_prompt:
            raise AuthConfigurationError(
                "Delegated auth required but auto_prompt is disabled in tenant config. "
                "Set auth.delegated.auto_prompt: true or sign in manually."
            )

        flow = pca.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise AuthConfigurationError(
                f"Failed to initiate device code flow: {flow.get('error_description')}"
            )

        # Display sign-in instructions to the user
        print("\n" + "=" * 60)
        print("UCP — Microsoft 365 Sign-In Required")
        print("=" * 60)
        print(f"\n  1. Open: {flow['verification_uri']}")
        print(f"  2. Enter code: {flow['user_code']}")
        print(f"\n  Waiting for sign-in (expires in {flow.get('expires_in', 900)}s)...")
        print("=" * 60 + "\n")

        result = pca.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            raise AuthConfigurationError(
                f"Device code auth failed: {result.get('error_description')}"
            )

        self._delegated_token = Token(
            access_token=result["access_token"],
            expires_at=time.time() + int(result.get("expires_in", 3600)),
            auth_mode="delegated",
        )
        log.info("Delegated token acquired via device code flow")
        return self._delegated_token.access_token

    # --- Unified token getter ---

    def get_token(self, prefer_delegated: bool = False) -> str:
        """Get a token based on the tenant's configured auth mode.

        Args:
            prefer_delegated: If True and mode is "hybrid", use delegated auth.
                              If False and mode is "hybrid", use app-only.
        """
        mode = self._tenant_config.auth.mode

        if mode == "delegated":
            return self.get_delegated_token()
        elif mode == "app_only":
            return self.get_app_token()
        elif mode == "hybrid":
            if prefer_delegated:
                return self.get_delegated_token()
            return self.get_app_token()
        else:
            raise AuthConfigurationError(f"Unknown auth mode: {mode}")

    @property
    def auth_mode(self) -> str:
        """Return the currently active auth mode."""
        return self._tenant_config.auth.mode

    @property
    def has_delegated_token(self) -> bool:
        """Check if a valid delegated token is available."""
        return self._delegated_token is not None and self._delegated_token.valid()

    @property
    def has_app_token(self) -> bool:
        """Check if a valid app-only token is available."""
        return self._app_token is not None and self._app_token.valid()


# ---------------------------------------------------------------------------
# Graph Client (dual-mode)
# ---------------------------------------------------------------------------


class GraphClient:
    """Microsoft Graph API client with dual-mode auth and tenant-aware routing.

    All configuration is driven by TenantConfig — no hardcoded values.
    The client automatically routes /me requests through delegated auth
    and falls back to site-scoped paths when only app-only auth is available.
    """

    def __init__(
        self,
        tenant_config: TenantConfig | None = None,
        config: AppConfig | None = None,
        base_url: str | None = None,
    ):
        self._tenant_config = tenant_config or get_tenant_config()
        self.config = config or AppConfig()  # Legacy compat

        self.base_url = (
            base_url or self._tenant_config.graph.base_url or "https://graph.microsoft.com/v1.0"
        ).rstrip("/")

        self._token_provider = GraphTokenProvider(
            tenant_config=self._tenant_config,
            legacy_config=self.config,
        )
        self._client = httpx.Client(timeout=self._tenant_config.graph.timeout_seconds)

    @property
    def tenant_config(self) -> TenantConfig:
        return self._tenant_config

    @property
    def auth_mode(self) -> str:
        return self._token_provider.auth_mode

    @property
    def can_use_me_endpoint(self) -> bool:
        """Whether /me endpoints are available (delegated auth active)."""
        mode = self._tenant_config.auth.mode
        if mode == "delegated":
            return True
        if mode == "hybrid" and self._token_provider.has_delegated_token:
            return True
        return False

    def _headers(self, prefer_delegated: bool = False) -> dict[str, str]:
        token = self._token_provider.get_token(prefer_delegated=prefer_delegated)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    @retry(
        retry=retry_if_exception_type(GraphRequestError),
        wait=wait_exponential(
            multiplier=1,
            min=1,
            max=20,
        ),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _request(
        self,
        method: str,
        path: str,
        *,
        correlation_id: str | None = None,
        prefer_delegated: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers.update(self._headers(prefer_delegated=prefer_delegated))
        if correlation_id:
            headers["X-Request-ID"] = correlation_id
        resp = self._client.request(method, url, headers=headers, **kwargs)
        if resp.status_code in (429, 503, 504):
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

    # ---------- Core endpoints ----------

    def get_organization(self) -> dict[str, Any]:
        r = self._request("GET", "/organization")
        data: dict[str, Any] = r.json()
        return data

    def list_teams(self) -> dict[str, Any]:
        r = self._request("GET", "/teams")
        return r.json()

    def list_users(
        self,
        top: int = 100,
        select: str | None = "id,displayName,userPrincipalName,mail,jobTitle,accountEnabled",
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"$top": min(max(1, top), 999)}
        if select:
            params["$select"] = select
        r = self._request("GET", "/users", params=params)
        return r.json()

    def get_user(self, user_id_or_upn: str) -> dict[str, Any]:
        r = self._request(
            "GET",
            f"/users/{user_id_or_upn}",
            params={
                "$select": "id,displayName,userPrincipalName,mail,jobTitle,department,accountEnabled"
            },
        )
        return r.json()

    def list_sites(self, top: int = 100) -> dict[str, Any]:
        params = {"$top": min(max(1, top), 999)}
        r = self._request("GET", "/sites", params=params)
        return r.json()

    def reset_user_password(
        self,
        user_id_or_upn: str,
        temporary_password: str,
        force_change_next_sign_in: bool = True,
    ) -> dict[str, Any]:
        body = {
            "passwordProfile": {
                "password": temporary_password,
                "forceChangePasswordNextSignIn": force_change_next_sign_in,
            }
        }
        self._request("PATCH", f"/users/{user_id_or_upn}", json=body)
        return {"user": user_id_or_upn, "password_reset": True}

    # ---------- M365 Helpers ----------

    def find_group_by_mailnickname(self, mail_nickname: str) -> dict | None:
        params = {"$filter": f"mailNickname eq '{mail_nickname}'", "$top": "1"}
        r = self._request("GET", "/groups", params=params)
        data = r.json()
        items = data.get("value", [])
        return items[0] if items else None

    def find_group_by_display_name(self, display_name: str) -> dict | None:
        escaped = display_name.replace("'", "''")
        params = {"$filter": f"displayName eq '{escaped}'", "$top": "1"}
        r = self._request("GET", "/groups", params=params)
        data = r.json()
        items = data.get("value", [])
        return items[0] if items else None

    # ---------- File Operations (auth-mode aware) ----------

    def upload_file_to_drive(
        self,
        drive_owner: str,
        owner_id: str,
        path_in_drive: str,
        file_bytes: bytes,
        content_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ) -> dict[str, Any]:
        """Upload or replace a file in any M365 drive.

        drive_owner: one of 'group', 'site', 'user'.
        owner_id: the group id, site id, or user id.
        """
        drive_owner = drive_owner.lower().strip()
        if drive_owner not in ("group", "site", "user"):
            raise ValueError("drive_owner must be one of: group, site, user")

        # Route user drives through delegated auth when available
        prefer_delegated = drive_owner == "user"

        segment = (
            "groups" if drive_owner == "group" else "sites" if drive_owner == "site" else "users"
        )
        path_encoded = quote(path_in_drive.strip("/"), safe="/")
        url = f"{self.base_url}/{segment}/{owner_id}/drive/root:/{path_encoded}:/content"
        token = self._token_provider.get_token(prefer_delegated=prefer_delegated)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": content_type}
        resp = self._client.request("PUT", url, headers=headers, content=file_bytes, timeout=60)
        if resp.status_code in (429, 503, 504):
            raise GraphRequestError(f"Transient error {resp.status_code}: {resp.text}")
        if resp.status_code >= 400:
            raise GraphRequestError(f"Graph error {resp.status_code}: {resp.text}")
        return resp.json() if resp.content else {}

    def upload_file_to_group_drive(
        self,
        group_id: str,
        path_in_drive: str,
        file_bytes: bytes,
        content_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ) -> dict[str, Any]:
        return self.upload_file_to_drive("group", group_id, path_in_drive, file_bytes, content_type)

    def upload_file_to_site_drive(
        self,
        site_id: str,
        path_in_drive: str,
        file_bytes: bytes,
        content_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ) -> dict[str, Any]:
        return self.upload_file_to_drive("site", site_id, path_in_drive, file_bytes, content_type)

    def upload_file_to_user_drive(
        self,
        user_id: str,
        path_in_drive: str,
        file_bytes: bytes,
        content_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ) -> dict[str, Any]:
        return self.upload_file_to_drive("user", user_id, path_in_drive, file_bytes, content_type)

    # ---------- Site & List Helpers ----------

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
        p = f"/sites/{hostname}:/sites/{site_path}"
        r = self._request("GET", p)
        return r.json()

    def get_group_root_site(self, group_id: str) -> dict:
        r = self._request("GET", f"/groups/{group_id}/sites/root")
        return r.json()

    def get_root_site(self) -> dict:
        r = self._request("GET", "/sites/root")
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

    def create_list(
        self, site_id: str, display_name: str, columns: list[dict] | None = None
    ) -> dict:
        body: dict[str, Any] = {
            "displayName": display_name,
            "list": {"template": "genericList"},
        }
        if columns:
            body["columns"] = columns
        r = self._request("POST", f"/sites/{site_id}/lists", json=body)
        return r.json()

    def add_column_to_list(self, site_id: str, list_id: str, column_definition: dict) -> dict:
        r = self._request(
            "POST", f"/sites/{site_id}/lists/{list_id}/columns", json=column_definition
        )
        return r.json()

    def create_list_item(self, site_id: str, list_id: str, fields: dict) -> dict:
        r = self._request(
            "POST",
            f"/sites/{site_id}/lists/{list_id}/items",
            json={"fields": fields},
        )
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

    # ---------- Teams Messaging ----------

    def find_channel_by_name(self, team_id: str, display_name: str) -> dict | None:
        channels = self.list_team_channels(team_id)
        for ch in channels:
            if (ch.get("displayName") or "").lower() == display_name.lower():
                return ch
        return None

    def post_channel_message_html(self, team_id: str, channel_id: str, html: str) -> dict:
        body = {
            "body": {
                "contentType": "html",
                "content": html,
            }
        }
        r = self._request("POST", f"/teams/{team_id}/channels/{channel_id}/messages", json=body)
        return r.json()

    # ---------- Planner Helpers ----------

    def list_group_plans(self, group_id: str) -> list[dict]:
        r = self._request("GET", f"/groups/{group_id}/planner/plans")
        data = r.json()
        return data.get("value", [])

    def create_plan(self, group_id: str, title: str) -> dict:
        body = {"owner": group_id, "title": title}
        r = self._request("POST", "/planner/plans", json=body)
        return r.json()

    def list_plan_buckets(self, plan_id: str) -> list[dict]:
        r = self._request("GET", f"/planner/plans/{plan_id}/buckets")
        data = r.json()
        return data.get("value", [])

    def create_bucket(self, plan_id: str, name: str, order_hint: str = " !") -> dict:
        body = {"name": name, "planId": plan_id, "orderHint": order_hint}
        r = self._request("POST", "/planner/buckets", json=body)
        return r.json()

    def create_task(
        self,
        plan_id: str,
        bucket_id: str,
        title: str,
        description: str | None = None,
        reference_url: str | None = None,
        percent_complete: int | None = None,
    ) -> dict:
        body: dict[str, Any] = {
            "planId": plan_id,
            "bucketId": bucket_id,
            "title": title,
        }
        if percent_complete is not None:
            body["percentComplete"] = max(0, min(100, percent_complete))
        task = self._request("POST", "/planner/tasks", json=body).json()

        if description or reference_url:
            task_id = task.get("id")
            if task_id:
                details_resp = self._request("GET", f"/planner/tasks/{task_id}/details")
                etag = details_resp.headers.get("ETag")
                details = details_resp.json()
                if description:
                    details["description"] = description
                if reference_url:
                    refs = details.get("references") or {}
                    refs[reference_url] = {
                        "@odata.type": "microsoft.graph.plannerExternalReference",
                        "alias": "source",
                        "type": "other",
                    }
                    details["references"] = refs
                headers = {"If-Match": etag} if etag else {}
                self._request(
                    "PATCH", f"/planner/tasks/{task_id}/details", headers=headers, json=details
                )
        return task

    # ---------- Ops Adapter Integration ----------

    def invoke_adapter_action(
        self,
        adapter_url: str,
        agent: str,
        action: str,
        payload: dict[str, Any],
        correlation_id: str | None = None,
        timeout: float = 20.0,
    ) -> dict[str, Any]:
        adapter_url = adapter_url.rstrip("/")
        url = f"{adapter_url}/actions/{agent}/{action}"
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if correlation_id:
            headers["X-Request-ID"] = correlation_id
        r = httpx.post(url, headers=headers, json={"params": payload}, timeout=timeout)
        r.raise_for_status()
        return r.json()
