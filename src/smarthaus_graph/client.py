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

import base64
import json
import os
import re
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import quote

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError, GraphRequestError
from smarthaus_common.logging import get_logger
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config

try:
    from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
except ImportError:
    F = TypeVar("F", bound=Callable[..., Any])

    class _WaitExponential:
        def __init__(self, *, multiplier: float, min: float, max: float):
            self.multiplier = multiplier
            self.min = min
            self.max = max

        def delay(self, attempt: int) -> float:
            computed = self.multiplier * (2 ** max(0, attempt - 1))
            return min(self.max, max(self.min, computed))

    def retry_if_exception_type(exc_type: type[BaseException]) -> tuple[type[BaseException], ...]:
        return (exc_type,)

    def wait_exponential(*, multiplier: float, min: float, max: float) -> _WaitExponential:
        return _WaitExponential(multiplier=multiplier, min=min, max=max)

    def stop_after_attempt(attempts: int) -> int:
        return attempts

    def retry(
        *, retry: tuple[type[BaseException], ...], wait: _WaitExponential, stop: int, reraise: bool
    ) -> Callable[[F], F]:
        exc_types = retry
        max_attempts = int(stop)

        def decorator(func: F) -> F:
            @wraps(func)
            def wrapped(*args: Any, **kwargs: Any) -> Any:
                last_error: BaseException | None = None
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except exc_types as exc:  # pragma: no cover - exercised in live runtime
                        last_error = exc
                        if attempt >= max_attempts:
                            if reraise:
                                raise
                            raise exc
                        time.sleep(wait.delay(attempt))
                if last_error is not None:
                    raise last_error
                return func(*args, **kwargs)

            return wrapped  # type: ignore[return-value]

        return decorator


try:
    from msal import (
        ConfidentialClientApplication,
        PublicClientApplication,
    )
    from msal import (
        SerializableTokenCache as MsalSerializableTokenCache,
    )

    _MSAL_IMPORT_ERROR: ImportError | None = None
except ImportError as exc:
    ConfidentialClientApplication = None
    PublicClientApplication = None
    _MSAL_IMPORT_ERROR = exc

    class _FallbackSerializableTokenCache:
        """Minimal fallback so app-only token flow can run without msal installed."""

        has_state_changed = False

        def deserialize(self, _state: str) -> None:
            return None

        def serialize(self) -> str:
            return "{}"

        def add(self, _event: dict[str, Any], **_kwargs: Any) -> None:
            return None

        def modify(
            self,
            _credential_type: str,
            _old_entry: dict[str, Any],
            _new_key_value_pairs: dict[str, Any] | None = None,
        ) -> None:
            return None

        def remove(self, _credential_type: str, _target: dict[str, Any]) -> None:
            return None

    MsalSerializableTokenCache = _FallbackSerializableTokenCache


log = get_logger(__name__)
_PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)
_CERTIFICATE_PATTERN = re.compile(
    r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
    re.DOTALL,
)
_ALIAS_PARTNUMBERS = {
    "E3": ["ENTERPRISEPACK", "SPE_E3", "M365_E3"],
    "E5": ["ENTERPRISEPREMIUM", "SPE_E5", "M365_E5"],
    "E1": ["STANDARDPACK", "SPE_E1"],
    "BusinessBasic": ["STANDARDPACK"],
    "BusinessStandard": ["STANDARDWOFFPACK"],
    "Developer": ["DEVELOPERPACK", "DEVELOPERPACK_E5", "M365_DEVELOPER"],
}


def _is_guid(value: str) -> bool:
    import uuid

    try:
        uuid.UUID(str(value))
        return True
    except Exception:
        return False


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


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _build_client_assertion(
    *,
    cert_credential: dict[str, Any],
    client_id: str,
    token_url: str,
) -> str:
    private_key_pem = cert_credential.get("private_key")
    thumbprint = cert_credential.get("thumbprint")
    if not private_key_pem or not thumbprint:
        raise AuthConfigurationError(
            "Direct certificate app auth requires a PEM certificate containing a private key."
        )

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"),
        password=None,
    )
    now = int(time.time())
    header = {
        "alg": "RS256",
        "typ": "JWT",
        "x5t": _base64url_encode(bytes.fromhex(str(thumbprint))),
    }
    payload = {
        "aud": token_url,
        "iss": client_id,
        "sub": client_id,
        "jti": str(uuid.uuid4()),
        "nbf": now - 60,
        "exp": now + 600,
    }
    signing_input = ".".join(
        [
            _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = private_key.sign(
        signing_input.encode("ascii"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return f"{signing_input}.{_base64url_encode(signature)}"


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


class PersistentTokenCache(MsalSerializableTokenCache):
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

    def _acquire_app_token_direct(self, scope: str) -> Token:
        cfg = self._tenant_config.azure
        if not (cfg.tenant_id and cfg.client_id):
            raise AuthConfigurationError(
                "Tenant config missing azure.tenant_id and/or azure.client_id. "
                "Set these in your tenant YAML or via environment variables."
            )

        token_url = f"https://login.microsoftonline.com/{cfg.tenant_id}/oauth2/v2.0/token"
        request_data: dict[str, str] = {
            "client_id": cfg.client_id,
            "grant_type": "client_credentials",
            "scope": scope,
        }
        if cfg.client_certificate_path and os.path.exists(cfg.client_certificate_path):
            cert_credential = _load_client_certificate_credential(cfg.client_certificate_path)
            request_data["client_assertion_type"] = (
                "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
            )
            request_data["client_assertion"] = _build_client_assertion(
                cert_credential=cert_credential,
                client_id=cfg.client_id,
                token_url=token_url,
            )
        elif cfg.client_certificate_path:
            raise AuthConfigurationError(
                "Tenant config certificate path does not exist. "
                "Set azure.client_certificate_path to a readable PEM file."
            )
        elif cfg.client_secret:
            request_data["client_secret"] = cfg.client_secret
        else:
            raise AuthConfigurationError(
                "Tenant config missing azure.client_secret or azure.client_certificate_path. "
                "Set these in your tenant YAML or via environment variables."
            )

        with httpx.Client(timeout=30.0) as client:
            response = client.post(token_url, data=request_data)

        try:
            payload = response.json()
        except ValueError:
            payload = {}

        if response.status_code >= 400 or "access_token" not in payload:
            raise AuthConfigurationError(
                f"Failed to acquire app token: "
                f"{payload.get('error_description') or response.text or response.reason_phrase}"
            )

        return Token(
            access_token=payload["access_token"],
            expires_at=time.time() + int(payload.get("expires_in", 3600)),
            auth_mode="app_only",
        )

    def _ensure_cca(self) -> ConfidentialClientApplication:
        if ConfidentialClientApplication is None:
            raise AuthConfigurationError(
                "App-only auth via msal is unavailable in this runtime. "
                "Install msal or use client-secret direct app-only fallback."
            )
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

        scopes = [self._tenant_config.auth.app_only.scope]

        if ConfidentialClientApplication is None:
            self._app_token = self._acquire_app_token_direct(scopes[0])
            return self._app_token.access_token

        cca = self._ensure_cca()

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
        if PublicClientApplication is None:
            raise AuthConfigurationError(
                "Delegated auth requires msal in this runtime. "
                "Install msal or use app_only auth mode."
            ) from _MSAL_IMPORT_ERROR
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

    def create_user(
        self,
        user_principal_name: str,
        *,
        display_name: str | None = None,
        mail_nickname: str | None = None,
        password: str,
        account_enabled: bool = True,
        job_title: str | None = None,
        department: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "accountEnabled": account_enabled,
            "displayName": display_name or mail_nickname or user_principal_name.split("@")[0],
            "mailNickname": mail_nickname or user_principal_name.split("@")[0],
            "userPrincipalName": user_principal_name,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": password,
            },
        }
        if job_title:
            body["jobTitle"] = job_title
        if department:
            body["department"] = department
        r = self._request("POST", "/users", json=body)
        return r.json()

    def update_user(self, user_id_or_upn: str, patch: dict[str, Any]) -> dict[str, Any]:
        self._request("PATCH", f"/users/{user_id_or_upn}", json=patch)
        return self.get_user(user_id_or_upn)

    def disable_user(self, user_id_or_upn: str) -> dict[str, Any]:
        self._request("PATCH", f"/users/{user_id_or_upn}", json={"accountEnabled": False})
        return {"user": user_id_or_upn, "disabled": True}

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

    def _resolve_user_scoped_path(
        self,
        *,
        user_id_or_upn: str | None,
        me_suffix: str,
        user_suffix: str | None = None,
        error_message: str,
    ) -> tuple[str, bool]:
        scoped_user = (user_id_or_upn or "").strip()
        if scoped_user:
            suffix = (user_suffix or me_suffix).lstrip("/")
            return f"/users/{quote(scoped_user, safe='')}/{suffix}", False
        if self.can_use_me_endpoint:
            return f"/me/{me_suffix.lstrip('/')}", True
        raise GraphRequestError(error_message)

    def list_messages(
        self,
        *,
        user_id_or_upn: str | None = None,
        top: int = 25,
        select: str | None = "id,subject,from,receivedDateTime,isRead",
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="messages",
            user_suffix="messages",
            error_message="userId is required for app-only auth (cannot use /me mailbox).",
        )
        r = self._request(
            "GET",
            path,
            prefer_delegated=prefer_delegated,
            params={
                "$select": select or "id,subject,from,receivedDateTime,isRead",
                "$top": min(max(1, top), 999),
                "$orderby": "receivedDateTime desc",
            },
        )
        return r.json()

    def get_message(self, message_id: str, *, user_id_or_upn: str | None = None) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"messages/{message_id}",
            user_suffix=f"messages/{message_id}",
            error_message="userId is required for app-only auth (cannot use /me mailbox).",
        )
        r = self._request("GET", path, prefer_delegated=prefer_delegated)
        return r.json()

    def send_mail(
        self,
        recipient_or_to: list[str] | str,
        subject: str,
        body: str | dict[str, Any],
        *,
        user_id_or_upn: str | None = None,
        content_type: str = "Text",
        save_to_sent_items: bool = True,
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="sendMail",
            user_suffix="sendMail",
            error_message="userId is required for app-only auth (cannot use /me mailbox).",
        )
        recipients = (
            recipient_or_to
            if isinstance(recipient_or_to, list)
            else [
                item.strip()
                for item in str(recipient_or_to).replace(";", ",").split(",")
                if item.strip()
            ]
        )
        if isinstance(body, dict):
            body_payload = body
        else:
            body_payload = {"contentType": content_type, "content": str(body)}
        message: dict[str, Any] = {
            "subject": subject,
            "body": body_payload,
            "toRecipients": [{"emailAddress": {"address": addr}} for addr in recipients],
        }
        self._request(
            "POST",
            path,
            prefer_delegated=prefer_delegated,
            json={"message": message, "saveToSentItems": save_to_sent_items},
        )
        return {
            "sent": True,
            "to": recipients,
            "subject": subject,
            "from": user_id_or_upn or "me",
            "saveToSentItems": save_to_sent_items,
        }

    def move_message(
        self,
        message_id: str,
        destination_id: str,
        *,
        user_id_or_upn: str | None = None,
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"messages/{message_id}/move",
            user_suffix=f"messages/{message_id}/move",
            error_message="userId is required for app-only auth (cannot use /me mailbox).",
        )
        r = self._request(
            "POST",
            path,
            prefer_delegated=prefer_delegated,
            json={"destinationId": destination_id},
        )
        return {
            "moved": True,
            "messageId": message_id,
            "destinationId": destination_id,
            "message": r.json() if r.content else None,
        }

    def delete_message(
        self, message_id: str, *, user_id_or_upn: str | None = None
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"messages/{message_id}",
            user_suffix=f"messages/{message_id}",
            error_message="userId is required for app-only auth (cannot use /me mailbox).",
        )
        self._request("DELETE", path, prefer_delegated=prefer_delegated)
        return {"deleted": True, "messageId": message_id}

    def list_mail_folders(
        self, *, user_id_or_upn: str | None = None, top: int = 100
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="mailFolders",
            user_suffix="mailFolders",
            error_message="userId is required for app-only auth (cannot use /me mailbox).",
        )
        r = self._request(
            "GET",
            path,
            prefer_delegated=prefer_delegated,
            params={"$top": min(max(1, top), 999)},
        )
        return r.json()

    def get_mailbox_settings(self, *, user_id_or_upn: str | None = None) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="mailboxSettings",
            user_suffix="mailboxSettings",
            error_message="userId is required for app-only auth (cannot use /me mailbox).",
        )
        r = self._request("GET", path, prefer_delegated=prefer_delegated)
        return r.json()

    def update_mailbox_settings(
        self, body: dict[str, Any], *, user_id_or_upn: str | None = None
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="mailboxSettings",
            user_suffix="mailboxSettings",
            error_message="userId is required for app-only auth (cannot use /me mailbox).",
        )
        self._request("PATCH", path, prefer_delegated=prefer_delegated, json=body)
        return self.get_mailbox_settings(user_id_or_upn=user_id_or_upn)

    def list_events(
        self,
        *,
        user_id_or_upn: str | None = None,
        top: int = 25,
        select: str = "id,subject,start,end,organizer,attendees,location",
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="events",
            user_suffix="events",
            error_message="userId is required for app-only auth (cannot use /me calendar).",
        )
        r = self._request(
            "GET",
            path,
            prefer_delegated=prefer_delegated,
            params={
                "$select": select,
                "$top": min(max(1, top), 999),
                "$orderby": "start/dateTime",
            },
        )
        return r.json()

    def create_event(
        self, body: dict[str, Any], *, user_id_or_upn: str | None = None
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="events",
            user_suffix="events",
            error_message="userId is required for app-only auth (cannot use /me calendar).",
        )
        r = self._request("POST", path, prefer_delegated=prefer_delegated, json=body)
        return r.json()

    def get_event(self, event_id: str, *, user_id_or_upn: str | None = None) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"events/{event_id}",
            user_suffix=f"events/{event_id}",
            error_message="userId is required for app-only auth (cannot use /me calendar).",
        )
        r = self._request("GET", path, prefer_delegated=prefer_delegated)
        return r.json()

    def update_event(
        self,
        event_id: str,
        patch: dict[str, Any],
        *,
        user_id_or_upn: str | None = None,
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"events/{event_id}",
            user_suffix=f"events/{event_id}",
            error_message="userId is required for app-only auth (cannot use /me calendar).",
        )
        self._request("PATCH", path, prefer_delegated=prefer_delegated, json=patch)
        return self.get_event(event_id, user_id_or_upn=user_id_or_upn)

    def delete_event(self, event_id: str, *, user_id_or_upn: str | None = None) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"events/{event_id}",
            user_suffix=f"events/{event_id}",
            error_message="userId is required for app-only auth (cannot use /me calendar).",
        )
        self._request("DELETE", path, prefer_delegated=prefer_delegated)
        return {"deleted": True, "eventId": event_id}

    def get_schedule(
        self,
        schedules: list[str],
        start_time: dict[str, Any],
        end_time: dict[str, Any],
        *,
        user_id_or_upn: str | None = None,
        availability_view_interval: int = 30,
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="calendar/getSchedule",
            user_suffix="calendar/getSchedule",
            error_message="userId is required for app-only auth (cannot use /me calendar).",
        )
        r = self._request(
            "POST",
            path,
            prefer_delegated=prefer_delegated,
            json={
                "schedules": schedules,
                "startTime": start_time,
                "endTime": end_time,
                "availabilityViewInterval": availability_view_interval,
            },
        )
        return r.json()

    def list_contacts(self, *, user_id_or_upn: str | None = None, top: int = 100) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="contacts",
            user_suffix="contacts",
            error_message="userId is required for app-only auth (cannot use /me contacts).",
        )
        r = self._request(
            "GET",
            path,
            prefer_delegated=prefer_delegated,
            params={"$top": min(max(1, top), 999)},
        )
        return r.json()

    def get_contact(self, contact_id: str, *, user_id_or_upn: str | None = None) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"contacts/{contact_id}",
            user_suffix=f"contacts/{contact_id}",
            error_message="userId is required for app-only auth (cannot use /me contacts).",
        )
        r = self._request("GET", path, prefer_delegated=prefer_delegated)
        return r.json()

    def create_contact(
        self, body: dict[str, Any], *, user_id_or_upn: str | None = None
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="contacts",
            user_suffix="contacts",
            error_message="userId is required for app-only auth (cannot use /me contacts).",
        )
        r = self._request("POST", path, prefer_delegated=prefer_delegated, json=body)
        return r.json()

    def update_contact(
        self,
        contact_id: str,
        patch: dict[str, Any],
        *,
        user_id_or_upn: str | None = None,
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"contacts/{contact_id}",
            user_suffix=f"contacts/{contact_id}",
            error_message="userId is required for app-only auth (cannot use /me contacts).",
        )
        self._request("PATCH", path, prefer_delegated=prefer_delegated, json=patch)
        return self.get_contact(contact_id, user_id_or_upn=user_id_or_upn)

    def delete_contact(
        self, contact_id: str, *, user_id_or_upn: str | None = None
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix=f"contacts/{contact_id}",
            user_suffix=f"contacts/{contact_id}",
            error_message="userId is required for app-only auth (cannot use /me contacts).",
        )
        self._request("DELETE", path, prefer_delegated=prefer_delegated)
        return {"deleted": True, "contactId": contact_id}

    def list_contact_folders(
        self, *, user_id_or_upn: str | None = None, top: int = 100
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_user_scoped_path(
            user_id_or_upn=user_id_or_upn,
            me_suffix="contactFolders",
            user_suffix="contactFolders",
            error_message="userId is required for app-only auth (cannot use /me contacts).",
        )
        r = self._request(
            "GET",
            path,
            prefer_delegated=prefer_delegated,
            params={"$top": min(max(1, top), 999)},
        )
        return r.json()

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

    def list_groups(self, top: int = 100) -> dict[str, Any]:
        r = self._request(
            "GET",
            "/groups",
            params={
                "$select": "id,displayName,mail,mailNickname,groupTypes,securityEnabled",
                "$top": min(max(1, top), 999),
            },
        )
        return r.json()

    def get_group(
        self, *, group_id: str | None = None, mail_nickname: str | None = None
    ) -> dict[str, Any]:
        if group_id:
            r = self._request(
                "GET",
                f"/groups/{group_id}",
                params={"$select": "id,displayName,mail,mailNickname,groupTypes,securityEnabled"},
            )
            return r.json()
        if mail_nickname:
            group = self.find_group_by_mailnickname(mail_nickname)
            if group:
                return group
        raise GraphRequestError("group lookup requires group_id or mail_nickname")

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

    def _supports_delegated_self_drive(self) -> bool:
        return self._tenant_config.auth.mode in {"delegated", "hybrid"}

    def _resolve_drive_collection_path(
        self,
        *,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
    ) -> tuple[str, bool]:
        if group_id:
            return f"/groups/{group_id}/drives", False
        if site_id:
            return f"/sites/{site_id}/drives", False
        if user_id_or_upn:
            return f"/users/{user_id_or_upn}/drives", False
        if self._supports_delegated_self_drive():
            return "/me/drives", True
        raise GraphRequestError(
            "drive listing requires group_id, site_id, or user_id_or_upn when delegated /me is unavailable"
        )

    def _resolve_drive_base_path(
        self,
        *,
        drive_id: str | None = None,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
    ) -> tuple[str, bool]:
        if drive_id:
            return f"/drives/{drive_id}", False
        if group_id:
            return f"/groups/{group_id}/drive", False
        if site_id:
            return f"/sites/{site_id}/drive", False
        if user_id_or_upn:
            return f"/users/{user_id_or_upn}/drive", False
        if self._supports_delegated_self_drive():
            return "/me/drive", True
        raise GraphRequestError(
            "drive operation requires drive_id, group_id, site_id, or user_id_or_upn when delegated /me is unavailable"
        )

    # ---------- Site & List Helpers ----------

    def create_group(
        self,
        display_name: str,
        mail_nickname: str,
        description: str | None = None,
        *,
        mail_enabled: bool = True,
        security_enabled: bool = False,
        group_types: list[str] | None = None,
        owners: list[str] | None = None,
        members: list[str] | None = None,
    ) -> dict:
        body = {
            "displayName": display_name,
            "mailEnabled": mail_enabled,
            "mailNickname": mail_nickname,
            "securityEnabled": security_enabled,
            "groupTypes": group_types or ["Unified"],
        }
        if description:
            body["description"] = description
        if owners:
            body["owners@odata.bind"] = [
                f"https://graph.microsoft.com/v1.0/users/{owner}" for owner in owners
            ]
        if members:
            body["members@odata.bind"] = [
                f"https://graph.microsoft.com/v1.0/users/{member}" for member in members
            ]
        r = self._request("POST", "/groups", json=body)
        return r.json()

    def list_group_members(self, group_id: str) -> dict[str, Any]:
        r = self._request(
            "GET",
            f"/groups/{group_id}/members",
            params={"$select": "id,displayName,userPrincipalName"},
        )
        return r.json()

    def add_group_member(self, group_id: str, member_id: str) -> None:
        self._request(
            "POST",
            f"/groups/{group_id}/members/$ref",
            json={"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{member_id}"},
        )

    def remove_group_member(self, group_id: str, member_id: str) -> None:
        self._request("DELETE", f"/groups/{group_id}/members/{member_id}/$ref")

    def list_directory_roles(self, top: int = 100) -> dict[str, Any]:
        r = self._request(
            "GET",
            "/directoryRoles",
            params={"$select": "id,displayName,description"},
        )
        return r.json()

    def list_directory_role_members(self, role_id: str) -> dict[str, Any]:
        r = self._request(
            "GET",
            f"/directoryRoles/{role_id}/members",
            params={"$select": "id,displayName,userPrincipalName"},
        )
        return r.json()

    def list_domains(self) -> dict[str, Any]:
        r = self._request("GET", "/domains")
        return r.json()

    def list_applications(self, top: int = 100) -> dict[str, Any]:
        r = self._request(
            "GET",
            "/applications",
            params={"$select": "id,displayName,appId", "$top": min(max(1, top), 999)},
        )
        return r.json()

    def get_application(self, app_id: str) -> dict[str, Any]:
        r = self._request("GET", f"/applications/{app_id}")
        return r.json()

    def update_application(self, app_id: str, body: dict[str, Any]) -> None:
        self._request("PATCH", f"/applications/{app_id}", json=body)

    def list_service_principals(self, top: int = 100) -> dict[str, Any]:
        r = self._request(
            "GET",
            "/servicePrincipals",
            params={"$select": "id,displayName,appId", "$top": min(max(1, top), 999)},
        )
        return r.json()

    def _get_subscribed_skus(self) -> list[dict[str, Any]]:
        response = self._request("GET", "/subscribedSkus").json()
        skus = response.get("value", [])
        for sku in skus:
            prepaid = (sku.get("prepaidUnits") or {}).get("enabled") or 0
            consumed = sku.get("consumedUnits") or 0
            sku["availableUnits"] = max(0, prepaid - consumed)
        return skus

    def _resolve_user_id(self, user_id_or_upn: str) -> str:
        if _is_guid(user_id_or_upn):
            return user_id_or_upn
        return str(self.get_user(user_id_or_upn).get("id") or "")

    def _get_user_assigned_skus(self, user_id: str) -> list[str]:
        response = self._request(
            "GET", f"/users/{user_id}/licenseDetails", params={"$select": "skuId"}
        ).json()
        return [str(item.get("skuId")).lower() for item in response.get("value", [])]

    def assign_user_license(
        self,
        user_id_or_upn: str,
        licenses: list[str],
        *,
        disabled_plans: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        subscribed = self._get_subscribed_skus()
        by_id = {str(sku["skuId"]).lower(): sku for sku in subscribed}
        by_part = {str(sku["skuPartNumber"]).upper(): sku for sku in subscribed}

        resolved: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        for raw in licenses:
            if _is_guid(raw):
                sku = by_id.get(str(raw).lower())
            else:
                key = str(raw).upper().replace(" ", "").replace("-", "_")
                sku = by_part.get(key)
                if sku is None:
                    aliases = _ALIAS_PARTNUMBERS.get(str(raw)) or _ALIAS_PARTNUMBERS.get(key) or []
                    sku = next((by_part[item] for item in aliases if item in by_part), None)
            if not sku:
                skipped.append(
                    {
                        "skuId": None,
                        "skuPartNumber": raw,
                        "reason": "unknown_license_or_unsubscribed",
                    }
                )
                continue
            resolved.append(sku)

        user_id = self._resolve_user_id(user_id_or_upn)
        already_assigned = set(self._get_user_assigned_skus(user_id))
        add_licenses: list[dict[str, Any]] = []
        assigned: list[str] = []
        disabled_plans = disabled_plans or {}

        for sku in resolved:
            sku_id = str(sku["skuId"]).lower()
            if sku_id in already_assigned:
                skipped.append(
                    {
                        "skuId": sku["skuId"],
                        "skuPartNumber": sku["skuPartNumber"],
                        "reason": "already_assigned",
                    }
                )
                continue
            if sku.get("availableUnits", 0) <= 0:
                skipped.append(
                    {
                        "skuId": sku["skuId"],
                        "skuPartNumber": sku["skuPartNumber"],
                        "reason": "insufficient_seats",
                    }
                )
                continue
            key_id = str(sku["skuId"]).lower()
            key_part = str(sku["skuPartNumber"]).upper()
            add_licenses.append(
                {
                    "skuId": sku["skuId"],
                    "disabledPlans": disabled_plans.get(key_id)
                    or disabled_plans.get(key_part)
                    or [],
                }
            )
            assigned.append(str(sku["skuId"]))

        if add_licenses:
            self._request(
                "POST",
                f"/users/{user_id}/assignLicense",
                json={"addLicenses": add_licenses, "removeLicenses": []},
            )

        return {
            "user": user_id_or_upn,
            "assigned": assigned,
            "skipped": skipped,
        }

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

    def get_site(self, site_id: str) -> dict[str, Any]:
        r = self._request(
            "GET",
            f"/sites/{site_id}",
            params={"$select": "id,displayName,webUrl,description"},
        )
        return r.json()

    def list_site_lists(self, site_id: str, top: int = 100) -> list[dict]:
        r = self._request(
            "GET",
            f"/sites/{site_id}/lists",
            params={
                "$select": "id,displayName,list",
                "$top": min(max(1, top), 999),
            },
        )
        data = r.json()
        return data.get("value", [])

    def get_list(self, site_id: str, list_id: str) -> dict[str, Any]:
        r = self._request(
            "GET",
            f"/sites/{site_id}/lists/{list_id}",
            params={"$select": "id,displayName,list,webUrl"},
        )
        return r.json()

    def list_list_items(self, site_id: str, list_id: str, top: int = 50) -> dict[str, Any]:
        r = self._request(
            "GET",
            f"/sites/{site_id}/lists/{list_id}/items",
            params={"$expand": "fields", "$top": min(max(1, top), 999)},
        )
        return r.json()

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

    def list_drives(
        self,
        *,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
        top: int = 100,
    ) -> dict[str, Any]:
        path, prefer_delegated = self._resolve_drive_collection_path(
            group_id=group_id,
            site_id=site_id,
            user_id_or_upn=user_id_or_upn,
        )
        r = self._request(
            "GET",
            path,
            params={"$top": min(max(1, top), 999)},
            prefer_delegated=prefer_delegated,
        )
        return r.json()

    def get_drive(self, drive_id: str) -> dict[str, Any]:
        r = self._request("GET", f"/drives/{drive_id}")
        return r.json()

    def list_drive_items(
        self,
        *,
        drive_id: str | None = None,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
        folder_id: str | None = None,
        folder_path: str | None = None,
        top: int = 100,
    ) -> dict[str, Any]:
        base_path, prefer_delegated = self._resolve_drive_base_path(
            drive_id=drive_id,
            group_id=group_id,
            site_id=site_id,
            user_id_or_upn=user_id_or_upn,
        )
        if folder_id and folder_id != "root":
            path = f"{base_path}/items/{folder_id}/children"
        elif folder_path:
            encoded_path = quote(folder_path.strip("/"), safe="/")
            path = f"{base_path}/root:/{encoded_path}:/children"
        else:
            path = f"{base_path}/root/children"
        r = self._request(
            "GET",
            path,
            params={"$top": min(max(1, top), 999)},
            prefer_delegated=prefer_delegated,
        )
        return r.json()

    def get_drive_item(self, drive_id: str, item_id: str) -> dict[str, Any]:
        r = self._request("GET", f"/drives/{drive_id}/items/{item_id}")
        return r.json()

    def create_folder(
        self,
        name: str,
        *,
        drive_id: str | None = None,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
        parent_id: str = "root",
        conflict_behavior: str = "rename",
    ) -> dict[str, Any]:
        base_path, prefer_delegated = self._resolve_drive_base_path(
            drive_id=drive_id,
            group_id=group_id,
            site_id=site_id,
            user_id_or_upn=user_id_or_upn,
        )
        if parent_id == "root":
            path = f"{base_path}/root/children"
        else:
            path = f"{base_path}/items/{parent_id}/children"
        r = self._request(
            "POST",
            path,
            json={
                "name": name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": conflict_behavior,
            },
            prefer_delegated=prefer_delegated,
        )
        return r.json()

    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        *,
        drive_id: str | None = None,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
        conflict_behavior: str = "replace",
        content_type: str | None = None,
    ) -> dict[str, Any]:
        file_path = Path(local_path)
        if not file_path.exists():
            raise GraphRequestError(f"Local file not found: {local_path}")
        return self.upload_bytes(
            file_bytes=file_path.read_bytes(),
            remote_path=remote_path,
            drive_id=drive_id,
            group_id=group_id,
            site_id=site_id,
            user_id_or_upn=user_id_or_upn,
            conflict_behavior=conflict_behavior,
            content_type=content_type,
            source_name=file_path.name,
        )

    def upload_bytes(
        self,
        *,
        file_bytes: bytes,
        remote_path: str,
        drive_id: str | None = None,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
        conflict_behavior: str = "replace",
        content_type: str | None = None,
        source_name: str = "generated.bin",
    ) -> dict[str, Any]:
        normalized_remote_path = remote_path.strip("/")
        if not normalized_remote_path:
            raise GraphRequestError("remote_path is required")

        base_path, prefer_delegated = self._resolve_drive_base_path(
            drive_id=drive_id,
            group_id=group_id,
            site_id=site_id,
            user_id_or_upn=user_id_or_upn,
        )
        token = self._token_provider.get_token(prefer_delegated=prefer_delegated)
        headers = {"Authorization": f"Bearer {token}"}
        if content_type:
            headers["Content-Type"] = content_type

        encoded_path = quote(normalized_remote_path, safe="/")
        if len(file_bytes) <= 4 * 1024 * 1024:
            upload_url = f"{self.base_url}{base_path}/root:/{encoded_path}:/content"
            if conflict_behavior != "replace":
                upload_url += f"?@microsoft.graph.conflictBehavior={conflict_behavior}"
            resp = self._client.request(
                "PUT",
                upload_url,
                headers=headers,
                content=file_bytes,
                timeout=60,
            )
            if resp.status_code in (429, 503, 504):
                raise GraphRequestError(f"Transient error {resp.status_code}: {resp.text}")
            if resp.status_code >= 400:
                raise GraphRequestError(f"Graph error {resp.status_code}: {resp.text}")
            return resp.json() if resp.content else {}

        session_url = f"{self.base_url}{base_path}/root:/{encoded_path}:/createUploadSession"
        session_resp = self._client.request(
            "POST",
            session_url,
            headers={**headers, "Content-Type": "application/json"},
            json={
                "item": {
                    "@microsoft.graph.conflictBehavior": conflict_behavior,
                    "name": source_name,
                }
            },
            timeout=60,
        )
        if session_resp.status_code in (429, 503, 504):
            raise GraphRequestError(
                f"Transient error {session_resp.status_code}: {session_resp.text}"
            )
        if session_resp.status_code >= 400:
            raise GraphRequestError(f"Graph error {session_resp.status_code}: {session_resp.text}")
        upload_url = str(session_resp.json().get("uploadUrl") or "")
        if not upload_url:
            raise GraphRequestError("Upload session response missing uploadUrl")

        chunk_size = 3200 * 1024
        offset = 0
        completed: dict[str, Any] = {}
        while offset < len(file_bytes):
            chunk_end = min(offset + chunk_size, len(file_bytes)) - 1
            chunk = file_bytes[offset : chunk_end + 1]
            chunk_resp = self._client.request(
                "PUT",
                upload_url,
                headers={
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {offset}-{chunk_end}/{len(file_bytes)}",
                },
                content=chunk,
                timeout=120,
            )
            if chunk_resp.status_code in (429, 503, 504):
                raise GraphRequestError(
                    f"Transient error {chunk_resp.status_code}: {chunk_resp.text}"
                )
            if chunk_resp.status_code >= 400:
                raise GraphRequestError(f"Graph error {chunk_resp.status_code}: {chunk_resp.text}")
            if chunk_resp.status_code in (200, 201):
                completed = chunk_resp.json() if chunk_resp.content else {}
            offset = chunk_end + 1
        return completed

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

    def _resolve_group_id(
        self,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> str:
        if group_id:
            return group_id
        if mail_nickname:
            group = self.find_group_by_mailnickname(mail_nickname)
            resolved = str((group or {}).get("id") or "").strip()
            if resolved:
                return resolved
            raise GraphRequestError(f"group_not_found:{mail_nickname}")
        raise GraphRequestError("group lookup requires group_id or mail_nickname")

    def get_team(
        self,
        team_id: str | None = None,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> dict:
        resolved_team_id = team_id or self._resolve_group_id(
            group_id=group_id,
            mail_nickname=mail_nickname,
        )
        r = self._request("GET", f"/teams/{resolved_team_id}")
        return r.json()

    def list_team_channels(
        self,
        team_id: str | None = None,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> list[dict]:
        resolved_team_id = team_id or self._resolve_group_id(
            group_id=group_id,
            mail_nickname=mail_nickname,
        )
        r = self._request("GET", f"/teams/{resolved_team_id}/channels")
        data = r.json()
        return data.get("value", [])

    def create_team_channel(
        self,
        team_id: str | None,
        display_name: str,
        description: str | None = None,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> dict:
        resolved_team_id = team_id or self._resolve_group_id(
            group_id=group_id,
            mail_nickname=mail_nickname,
        )
        body = {"displayName": display_name}
        if description:
            body["description"] = description
        r = self._request("POST", f"/teams/{resolved_team_id}/channels", json=body)
        return r.json()

    def list_channels(
        self,
        team_id: str | None = None,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> list[dict]:
        return self.list_team_channels(
            team_id,
            group_id=group_id,
            mail_nickname=mail_nickname,
        )

    def create_channel(
        self,
        display_name: str,
        *,
        team_id: str | None = None,
        group_id: str | None = None,
        mail_nickname: str | None = None,
        description: str | None = None,
    ) -> dict:
        return self.create_team_channel(
            team_id,
            display_name,
            description=description,
            group_id=group_id,
            mail_nickname=mail_nickname,
        )

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

    def list_plans(
        self,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> list[dict]:
        resolved_group_id = self._resolve_group_id(
            group_id=group_id,
            mail_nickname=mail_nickname,
        )
        return self.list_group_plans(resolved_group_id)

    def create_plan(
        self,
        group_id: str | None,
        title: str,
        *,
        mail_nickname: str | None = None,
    ) -> dict:
        resolved_group_id = self._resolve_group_id(
            group_id=group_id,
            mail_nickname=mail_nickname,
        )
        body = {"owner": resolved_group_id, "title": title}
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

    def create_plan_bucket(self, plan_id: str, name: str, order_hint: str = " !") -> dict:
        return self.create_bucket(plan_id, name, order_hint=order_hint)

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

    def create_plan_task(
        self,
        plan_id: str,
        bucket_id: str,
        title: str,
        *,
        description: str | None = None,
        reference_url: str | None = None,
        percent_complete: int | None = None,
    ) -> dict:
        return self.create_task(
            plan_id,
            bucket_id,
            title,
            description=description,
            reference_url=reference_url,
            percent_complete=percent_complete,
        )

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
