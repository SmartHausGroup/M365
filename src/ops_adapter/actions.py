from __future__ import annotations

import csv
import io
import os
import random
import string
import time
from contextvars import ContextVar
from typing import Any

import httpx
import yaml
from smarthaus_common.auth_model import AuthResolution, resolve_action_auth
from smarthaus_common.errors import AuthConfigurationError, GraphRequestError
from smarthaus_common.executor_routing import executor_route_for_action as resolve_route_for_action

from .audit import recent_admin_events, record_admin_event

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# ---------------------------------------------------------------------------
# Tenant-aware token provider (lazy-loaded singleton)
# ---------------------------------------------------------------------------

_token_providers: dict[str, Any] = {}
_current_executor_name: ContextVar[str | None] = ContextVar(
    "ops_adapter_executor_name",
    default=None,
)
_current_auth_resolution: ContextVar[AuthResolution | None] = ContextVar(
    "ops_adapter_auth_resolution",
    default=None,
)


def executor_route_for_action(agent: str | None, action: str) -> str:
    return resolve_route_for_action(agent, action)


def resolve_execution_target_for_action(
    agent: str,
    action: str,
    tenant_config: Any,
) -> tuple[str, str]:
    route_key = executor_route_for_action(agent, action)
    fallback_keys = ["sharepoint"] if route_key == "approvals" else []
    executor_name = tenant_config.resolve_executor_name(
        route_key,
        action_name=action,
        fallback_keys=fallback_keys,
    )
    return executor_name, route_key


def resolve_executor_name_for_action(agent: str, action: str, tenant_config: Any) -> str:
    return resolve_execution_target_for_action(agent, action, tenant_config)[0]


def build_executor_identity(
    tenant_config: Any,
    executor_name: str,
    *,
    logical_domain: str | None = None,
) -> dict[str, Any]:
    projected_config = tenant_config.project_executor(executor_name)
    executor_cfg = tenant_config.executors[executor_name]
    route_domain = str(logical_domain or executor_cfg.domain or "").strip() or "default"
    physical_domain = str(executor_cfg.domain or "").strip() or "default"
    return {
        "type": "service_principal",
        "name": executor_name,
        "domain": route_domain,
        "logical_domain": route_domain,
        "physical_domain": physical_domain,
        "mode": projected_config.auth.mode,
        "tenant": projected_config.tenant.id,
        "azure_tenant_id": projected_config.azure.tenant_id,
        "client_id": projected_config.azure.client_id,
    }


def _tenant_aware_context_active(executor_name: str | None = None) -> bool:
    del executor_name
    return bool(os.getenv("UCP_TENANT", "").strip())


def _graph_auth_error(exc: Exception, *, init_failure: bool = False) -> GraphAPIError:
    if isinstance(exc, GraphAPIError):
        return exc
    if isinstance(exc, FileNotFoundError):
        code = "tenant_config_missing"
    elif isinstance(exc, ValueError):
        code = "tenant_config_invalid"
    elif isinstance(exc, AuthConfigurationError):
        code = "auth_configuration_error"
    else:
        code = "token_provider_init_failed" if init_failure else "token_provider_failed"
    return GraphAPIError(500, code, str(exc))


def _direct_client_secret_token(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    scope: str,
) -> str:
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            token_url,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
                "scope": scope,
            },
        )

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if response.status_code >= 400 or "access_token" not in payload:
        raise GraphAPIError(
            500,
            "auth_configuration_error",
            payload.get("error_description") or response.text or response.reason_phrase,
        )

    return str(payload["access_token"])


def _get_token_provider(executor_name: str | None = None) -> Any | None:
    """Get or create the tenant-aware token provider."""
    try:
        from smarthaus_common.tenant_config import get_tenant_config
        from smarthaus_graph.client import GraphTokenProvider

        tenant_cfg = get_tenant_config()
        selected_executor = executor_name or _current_executor_name.get()
        projected_cfg = (
            tenant_cfg.project_executor(selected_executor) if selected_executor else tenant_cfg
        )
        cache_key = (
            f"{projected_cfg.tenant.id}:"
            f"{selected_executor or projected_cfg.default_executor_name}:"
            f"{projected_cfg.azure.client_id}:"
            f"{projected_cfg.auth.mode}"
        )
        provider = _token_providers.get(cache_key)
        if provider is None:
            provider = GraphTokenProvider(tenant_config=projected_cfg)
            _token_providers[cache_key] = provider
        return provider
    except Exception as exc:
        if _tenant_aware_context_active(executor_name):
            raise _graph_auth_error(exc, init_failure=True) from exc
        return None


class GraphAPIError(Exception):
    def __init__(self, status: int, code: str | None, message: str):
        super().__init__(f"GraphAPIError {status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


def _stub_mode() -> bool:
    return os.getenv("GRAPH_STUB_MODE", "0").lower() in ("1", "true", "yes", "on")


def _effective_prefer_delegated(prefer_delegated: bool | None = None) -> bool:
    if prefer_delegated is not None:
        return prefer_delegated
    resolution = _current_auth_resolution.get()
    return bool(resolution and resolution.prefer_delegated)


def _graph_token(prefer_delegated: bool | None = None) -> str | None:
    """Acquire a Graph API token.

    Uses the tenant-aware token provider when available (supports both
    app-only and delegated auth modes). Falls back to legacy env-var
    credential resolution for backward compatibility.

    Args:
        prefer_delegated: If True and tenant is in hybrid mode, use delegated auth.
    """
    # Try tenant-aware provider first
    effective_preference = _effective_prefer_delegated(prefer_delegated)

    if _tenant_aware_context_active():
        provider = _get_token_provider()
        if provider is not None:
            try:
                return provider.get_token(prefer_delegated=effective_preference)
            except Exception as exc:
                raise _graph_auth_error(exc) from exc

    # Legacy fallback: resolve credentials from environment variables
    tenant_id = (
        os.getenv("AZURE_TENANT_ID")
        or os.getenv("MICROSOFT_TENANT_ID")
        or os.getenv("GRAPH_TENANT_ID")
    )
    client_id = (
        os.getenv("AZURE_CLIENT_ID")
        or os.getenv("MICROSOFT_CLIENT_ID")
        or os.getenv("AZURE_APP_CLIENT_ID_TAI")
        or os.getenv("GRAPH_CLIENT_ID")
    )

    # Prefer certificate auth if provided
    cert_path = os.getenv("AZURE_CLIENT_CERTIFICATE_PATH")
    if tenant_id and client_id and cert_path and os.path.exists(cert_path):
        try:
            from azure.identity import ClientCertificateCredential

            cred = ClientCertificateCredential(
                tenant_id=tenant_id, client_id=client_id, certificate_path=cert_path
            )
            token = cred.get_token(GRAPH_SCOPE)
            return token.token
        except Exception:
            pass

    # Fallback to client secret if available
    client_secret = (
        os.getenv("AZURE_CLIENT_SECRET")
        or os.getenv("MICROSOFT_CLIENT_SECRET")
        or os.getenv("AZURE_APP_CLIENT_SECRET_TAI")
        or os.getenv("GRAPH_CLIENT_SECRET")
    )
    if tenant_id and client_id and client_secret:
        try:
            from azure.identity import ClientSecretCredential

            cred = ClientSecretCredential(
                tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
            )
            token = cred.get_token(GRAPH_SCOPE)
            return token.token
        except ImportError:
            return _direct_client_secret_token(tenant_id, client_id, client_secret, GRAPH_SCOPE)
        except Exception:
            try:
                return _direct_client_secret_token(tenant_id, client_id, client_secret, GRAPH_SCOPE)
            except GraphAPIError:
                raise
            except Exception:
                pass

    return None


def _can_use_me_endpoint() -> bool:
    """Check whether /me endpoints are available (delegated auth active)."""
    provider = _get_token_provider()
    if provider is None:
        return False
    try:
        from smarthaus_common.tenant_config import get_tenant_config

        cfg = get_tenant_config()
        return cfg.auth.mode in ("delegated", "hybrid") and provider.has_delegated_token
    except Exception:
        return False


def _first_explicit_identity(params: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        raw = params.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if text and text.lower() not in {"me", "self", "current"}:
            return text
    return None


def _resolve_user_scoped_url(
    action_name: str,
    params: dict[str, Any],
    *,
    me_suffix: str,
    user_suffix: str,
    identity_keys: tuple[str, ...],
    error_message: str,
) -> tuple[str, bool]:
    resolution = resolve_action_auth(None, action_name, params)
    explicit_identity = _first_explicit_identity(params, *identity_keys)
    if resolution.prefer_delegated and _can_use_me_endpoint():
        return f"{GRAPH_BASE}/me/{me_suffix.lstrip('/')}", True
    if explicit_identity:
        return (
            f"{GRAPH_BASE}/users/{explicit_identity}/{user_suffix.lstrip('/')}",
            False,
        )
    raise GraphAPIError(400, "no_user_context", error_message)


def _gen_password(length: int = 24) -> str:
    chars = string.ascii_letters + string.digits + "!@#%^*()-_=+"
    return "".join(random.choice(chars) for _ in range(length))


async def _graph_request(
    method: str,
    url: str,
    correlation_id: str,
    json_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    prefer_delegated: bool | None = None,
) -> dict[str, Any] | None:
    token = _graph_token(prefer_delegated=prefer_delegated)
    if not token:
        if _stub_mode():
            return {"stub": True, "url": url, "method": method, "params": params, "body": json_body}
        raise GraphAPIError(500, "credentials_missing", "Graph credentials not configured")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Correlation-ID": correlation_id,
    }

    retries = 5
    backoff = 0.5
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.request(
                    method, url, headers=headers, json=json_body, params=params
                )
                if resp.status_code in (429, 503, 502):
                    retry_after = resp.headers.get("Retry-After")
                    sleep_s = (
                        float(retry_after) if retry_after and retry_after.isdigit() else backoff
                    )
                    if attempt < retries:
                        time.sleep(sleep_s)
                        backoff = min(8.0, backoff * 2)
                        continue
                resp.raise_for_status()
                if resp.content and resp.headers.get("Content-Type", "").startswith(
                    "application/json"
                ):
                    return resp.json()
                return None
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
                err = body.get("error", {})
                code = err.get("code")
                msg = err.get("message") or e.response.text
            except Exception:
                code = None
                msg = e.response.text
            if e.response.status_code in (429, 503, 502) and attempt < retries:
                continue
            raise GraphAPIError(e.response.status_code, code, msg) from e
        except httpx.RequestError as e:
            if attempt < retries:
                time.sleep(backoff)
                backoff = min(8.0, backoff * 2)
                continue
            raise GraphAPIError(503, "request_error", str(e)) from e
    raise GraphAPIError(503, "request_error", "graph_request_exhausted_retries")


async def _graph_request_raw(
    method: str,
    url: str,
    correlation_id: str,
    params: dict[str, Any] | None = None,
    prefer_delegated: bool | None = None,
) -> str:
    """Like _graph_request but returns raw text (for CSV report endpoints)."""
    token = _graph_token(prefer_delegated=prefer_delegated)
    if not token:
        if _stub_mode():
            return ""
        raise GraphAPIError(500, "credentials_missing", "Graph credentials not configured")

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Correlation-ID": correlation_id,
    }

    retries = 5
    backoff = 0.5
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.request(method, url, headers=headers, params=params)
                if resp.status_code in (429, 503, 502):
                    retry_after = resp.headers.get("Retry-After")
                    sleep_s = (
                        float(retry_after) if retry_after and retry_after.isdigit() else backoff
                    )
                    if attempt < retries:
                        time.sleep(sleep_s)
                        backoff = min(8.0, backoff * 2)
                        continue
                resp.raise_for_status()
                return resp.text
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
                err = body.get("error", {})
                code = err.get("code")
                msg = err.get("message") or e.response.text
            except Exception:
                code = None
                msg = e.response.text
            if e.response.status_code in (429, 503, 502) and attempt < retries:
                continue
            raise GraphAPIError(e.response.status_code, code, msg) from e
        except httpx.RequestError as e:
            if attempt < retries:
                time.sleep(backoff)
                backoff = min(8.0, backoff * 2)
                continue
            raise GraphAPIError(503, "request_error", str(e)) from e
    return ""


def _csv_to_dicts(raw_csv: str) -> list[dict[str, str]]:
    """Parse CSV text (as returned by Graph report endpoints) into a list of dicts."""
    if not raw_csv or not raw_csv.strip():
        return []
    reader = csv.DictReader(io.StringIO(raw_csv))
    return [dict(row) for row in reader]


def _slugify_mail_nickname(value: str | None) -> str:
    raw = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    while "--" in raw:
        raw = raw.replace("--", "-")
    return raw.strip("-") or "workspace"


def _graph_client_for_route(route_key: str) -> Any:
    from smarthaus_common.config import AppConfig, has_selected_tenant
    from smarthaus_common.tenant_config import get_tenant_config
    from smarthaus_graph.client import GraphClient

    if has_selected_tenant():
        tenant_cfg = get_tenant_config()
        selected_executor = _current_executor_name.get()
        if selected_executor:
            tenant_cfg = tenant_cfg.project_executor(selected_executor)
        elif route_key and len(getattr(tenant_cfg, "executors", {}) or {}) > 1:
            executor_name = tenant_cfg.resolve_executor_name(route_key, fallback_keys=[route_key])
            tenant_cfg = tenant_cfg.project_executor(executor_name)
        return GraphClient(tenant_config=tenant_cfg)
    return GraphClient(config=AppConfig())


async def sites_provision(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    if _stub_mode():
        return {
            "status": "provisioned",
            "site_id": "stub-site-id",
            "site_url": "https://stub.sharepoint.com/sites/workspace",
            "group_created": True,
            "libraries_created": list(params.get("libraries") or ["Documents"]),
        }
    from provisioning_api.m365_provision import provision_group_site

    display_name = (
        params.get("displayName")
        or params.get("name")
        or params.get("siteName")
        or "Provisioned Site"
    )
    mail_nickname = (
        params.get("mailNickname")
        or params.get("mail_nickname")
        or _slugify_mail_nickname(display_name)
    )
    libraries = params.get("libraries") or ["Documents"]
    description = params.get("description")
    wait_secs = int(params.get("wait_secs") or params.get("waitSecs") or 60)
    try:
        result = provision_group_site(
            display_name=display_name,
            mail_nickname=mail_nickname,
            libraries=libraries,
            description=description,
            wait_secs=wait_secs,
        )
    except GraphRequestError as exc:
        raise GraphAPIError(500, "site_provision_failed", str(exc)) from exc
    return {"status": "provisioned", **result}


async def planner_list_plans(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    if _stub_mode():
        return {
            "plans": [{"id": "plan-stub-001", "title": "Stub Plan"}],
            "count": 1,
        }
    client = _graph_client_for_route("collaboration")
    plans = client.list_plans(
        group_id=params.get("groupId") or params.get("group_id"),
        mail_nickname=params.get("mailNickname") or params.get("mail_nickname"),
    )
    return {"plans": plans, "count": len(plans)}


async def planner_create_plan(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    del correlation_id
    if _stub_mode():
        return {
            "plan": {"id": "plan-stub-001", "title": params.get("title", "Stub Plan")},
            "status": "created",
        }
    client = _graph_client_for_route("collaboration")
    plan = client.create_plan(
        params.get("groupId") or params.get("group_id"),
        params.get("title") or "New Plan",
        mail_nickname=params.get("mailNickname") or params.get("mail_nickname"),
    )
    return {"plan": plan, "status": "created"}


async def planner_list_buckets(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    del correlation_id
    if _stub_mode():
        return {
            "buckets": [{"id": "bucket-stub-001", "name": "Stub Bucket"}],
            "count": 1,
        }
    client = _graph_client_for_route("collaboration")
    buckets = client.list_plan_buckets(params["planId"])
    return {"buckets": buckets, "count": len(buckets)}


async def planner_create_bucket(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    del correlation_id
    if _stub_mode():
        return {
            "bucket": {"id": "bucket-stub-001", "name": params.get("name", "Stub Bucket")},
            "status": "created",
        }
    client = _graph_client_for_route("collaboration")
    bucket = client.create_bucket(
        params["planId"],
        params.get("name") or params.get("displayName") or "New Bucket",
        order_hint=params.get("orderHint", " !"),
    )
    return {"bucket": bucket, "status": "created"}


async def planner_create_task(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    del correlation_id
    if _stub_mode():
        return {
            "task": {"id": "task-stub-001", "title": params.get("title", "Stub Task")},
            "status": "created",
        }
    client = _graph_client_for_route("collaboration")
    task = client.create_task(
        params["planId"],
        params["bucketId"],
        params.get("title") or "New Task",
        description=params.get("description"),
        reference_url=params.get("referenceUrl"),
        percent_complete=params.get("percentComplete"),
    )
    return {"task": task, "status": "created"}


async def outreach_email_send_bulk(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    bulk_params = dict(params)
    if "to" not in bulk_params and "recipients" in bulk_params:
        bulk_params["to"] = bulk_params["recipients"]
    return await mail_send(bulk_params, correlation_id)


async def outreach_email_schedule(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    schedule_params = dict(params)
    if "userId" not in schedule_params and schedule_params.get("from"):
        schedule_params["userId"] = schedule_params["from"]
    return await calendar_create(schedule_params, correlation_id)


async def outreach_meeting_schedule(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    meeting_params = dict(params)
    meeting_params.setdefault("isOnlineMeeting", True)
    if "userId" not in meeting_params and meeting_params.get("from"):
        meeting_params["userId"] = meeting_params["from"]
    return await calendar_create(meeting_params, correlation_id)


# ==================== USERS (existing - preserved exactly) ====================


async def m365_users_read(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    upn = params.get("userPrincipalName")
    # If no UPN provided, list all users
    if not upn:
        return await m365_users_list(params, correlation_id)
    if _stub_mode():
        return {
            "user": {
                "id": "00000000-0000-0000-0000-000000000000",
                "displayName": params.get("displayName", "Stub User"),
                "userPrincipalName": upn or "stub.user@smarthaus.ai",
                "accountEnabled": True,
                "jobTitle": params.get("jobTitle", "Developer"),
                "department": params.get("department", "Engineering"),
            }
        }
    url = f"{GRAPH_BASE}/users/{upn}"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={"$select": "id,displayName,userPrincipalName,accountEnabled,jobTitle,department"},
    )
    return {"user": data}


async def m365_users_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List all users in the tenant."""
    if _stub_mode():
        return {
            "users": [
                {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "displayName": "Stub User",
                    "userPrincipalName": "stub.user@smarthaus.ai",
                    "accountEnabled": True,
                },
            ],
            "count": 1,
        }
    select = "id,displayName,userPrincipalName,accountEnabled,jobTitle,department,mail"
    url = f"{GRAPH_BASE}/users"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={"$select": select, "$top": str(params.get("limit", 100))},
    )
    users = data.get("value", []) if data else []
    return {"users": users, "count": len(users)}


async def m365_users_create(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    upn = params["userPrincipalName"]
    display_name = params.get("displayName")
    mail_nickname = params.get("mailNickname") or upn.split("@")[0]
    password = params.get("password") or _gen_password()
    account_enabled = bool(params.get("accountEnabled", True))
    if _stub_mode():
        return {
            "user": {
                "id": "11111111-1111-1111-1111-111111111111",
                "displayName": display_name or mail_nickname,
                "userPrincipalName": upn,
                "mailNickname": mail_nickname,
                "accountEnabled": account_enabled,
            },
            "temporaryPassword": password,
        }
    body = {
        "accountEnabled": account_enabled,
        "displayName": display_name,
        "mailNickname": mail_nickname,
        "userPrincipalName": upn,
        "passwordProfile": {
            "forceChangePasswordNextSignIn": True,
            "password": password,
        },
    }
    # Optional user attributes
    if params.get("jobTitle"):
        body["jobTitle"] = params["jobTitle"]
    if params.get("department"):
        body["department"] = params["department"]
    url = f"{GRAPH_BASE}/users"
    created = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"user": created, "temporaryPassword": password}


async def m365_users_update(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    upn = params["userPrincipalName"]
    patch: dict[str, Any] = {}
    for key in ("displayName", "jobTitle", "department", "accountEnabled"):
        if key in params and params[key] is not None:
            patch[key] = params[key]
    if not patch:
        return {"updated": False, "note": "no_fields_to_update"}
    if _stub_mode():
        return {"updated": True, "userPrincipalName": upn, "patch": patch}
    url = f"{GRAPH_BASE}/users/{upn}"
    await _graph_request("PATCH", url, correlation_id, json_body=patch)
    # Return the updated projection
    return await m365_users_read({"userPrincipalName": upn}, correlation_id)


async def m365_users_disable(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    upn = params["userPrincipalName"]
    url = f"{GRAPH_BASE}/users/{upn}"
    if _stub_mode():
        return {"disabled": True, "userPrincipalName": upn}
    await _graph_request("PATCH", url, correlation_id, json_body={"accountEnabled": False})
    return {"disabled": True, "userPrincipalName": upn}


# ==================== LICENSES (existing - preserved exactly) ====================

_ALIAS_PARTNUMBERS = {
    # Common enterprise SKUs; resolve to available skuPartNumbers in tenant
    "E3": ["ENTERPRISEPACK", "SPE_E3", "M365_E3"],
    "E5": ["ENTERPRISEPREMIUM", "SPE_E5", "M365_E5"],
    "E1": ["STANDARDPACK", "SPE_E1"],
    "BusinessBasic": ["STANDARDPACK"],
    "BusinessStandard": ["STANDARDWOFFPACK"],
    "Developer": ["DEVELOPERPACK", "DEVELOPERPACK_E5", "M365_DEVELOPER"],
}


def _is_guid(s: str) -> bool:
    try:
        import uuid

        uuid.UUID(s)
        return True
    except Exception:
        return False


async def _get_subscribed_skus(correlation_id: str) -> list[dict[str, Any]]:
    if _stub_mode():
        return [
            {
                "skuId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "skuPartNumber": "ENTERPRISEPACK",
                "prepaidUnits": {"enabled": 100},
                "consumedUnits": 10,
                "availableUnits": 90,
            },
            {
                "skuId": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "skuPartNumber": "M365_E5",
                "prepaidUnits": {"enabled": 50},
                "consumedUnits": 45,
                "availableUnits": 5,
            },
        ]
    url = f"{GRAPH_BASE}/subscribedSkus"
    data = await _graph_request("GET", url, correlation_id)
    # Normalize availability and map structures we need
    for sku in (data or {}).get("value", []):
        prepaid = (sku.get("prepaidUnits") or {}).get("enabled") or 0
        consumed = sku.get("consumedUnits") or 0
        sku["availableUnits"] = max(0, prepaid - consumed)
    return (data or {}).get("value", [])


def _build_sku_maps(
    subscribed: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_id = {str(s["skuId"]).lower(): s for s in subscribed}
    by_part = {str(s["skuPartNumber"]).upper(): s for s in subscribed}
    return by_id, by_part


def _resolve_requested_licenses(
    requested: list[str], by_id: dict[str, Any], by_part: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    resolved: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for key in requested:
        if _is_guid(key):
            sku = by_id.get(key.lower())
            if sku:
                resolved.append(sku)
            else:
                errors.append({"license": key, "reason": "sku_not_in_tenant"})
            continue
        partkey = key.upper().replace(" ", "").replace("-", "_")
        # Direct part number match
        if partkey in by_part:
            resolved.append(by_part[partkey])
            continue
        # Alias mapping
        candidates = _ALIAS_PARTNUMBERS.get(key) or _ALIAS_PARTNUMBERS.get(partkey)
        if candidates:
            chosen = next((by_part[p] for p in candidates if p in by_part), None)
            if chosen:
                resolved.append(chosen)
                continue
        errors.append({"license": key, "reason": "unknown_license_or_unsubscribed"})
    return resolved, errors


async def _get_user_id(upn: str, correlation_id: str) -> str:
    if _stub_mode():
        return "22222222-2222-2222-2222-222222222222"
    url = f"{GRAPH_BASE}/users/{upn}?$select=id"
    data = await _graph_request("GET", url, correlation_id)
    if not data or "id" not in data:
        raise GraphAPIError(404, "user_not_found", f"User '{upn}' not found")
    return str(data["id"])


async def _get_user_assigned_skus(user_id: str, correlation_id: str) -> list[str]:
    if _stub_mode():
        return []
    url = f"{GRAPH_BASE}/users/{user_id}/licenseDetails?$select=skuId"
    data = await _graph_request("GET", url, correlation_id)
    return [str(v.get("skuId")).lower() for v in (data or {}).get("value", [])]


async def m365_licenses_assign(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    upn = params["userPrincipalName"]
    req_licenses: list[str] = params.get("licenses") or []
    if not req_licenses:
        raise GraphAPIError(400, "invalid_request", "licenses_required")
    if _stub_mode():
        return {"userPrincipalName": upn, "assigned": list(req_licenses), "skipped": []}

    subscribed = await _get_subscribed_skus(correlation_id)
    by_id, by_part = _build_sku_maps(subscribed)
    resolved, res_errors = _resolve_requested_licenses(req_licenses, by_id, by_part)

    user_id = await _get_user_id(upn, correlation_id)
    assigned = set(await _get_user_assigned_skus(user_id, correlation_id))

    to_assign = []
    skipped = []
    for sku in resolved:
        sku_id = str(sku["skuId"]).lower()
        if sku_id in assigned:
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
        to_assign.append(sku)

    # Merge errors for unknown licenses
    for err in res_errors:
        skipped.append({"skuId": None, "skuPartNumber": err["license"], "reason": err["reason"]})

    addLicenses = []
    disabled_plans_map: dict[str, list[str]] = params.get("disabledPlans") or {}

    def _plans_for(sku: dict[str, Any]) -> list[str]:
        # Lookup plans using either skuId or partNumber key
        k1 = str(sku["skuId"]).lower()
        k2 = str(sku["skuPartNumber"]).upper()
        return disabled_plans_map.get(k1) or disabled_plans_map.get(k2) or []

    for sku in to_assign:
        addLicenses.append({"skuId": sku["skuId"], "disabledPlans": _plans_for(sku)})

    assigned_ids: list[str] = []
    if addLicenses:
        url = f"{GRAPH_BASE}/users/{user_id}/assignLicense"
        body = {"addLicenses": addLicenses, "removeLicenses": []}
        await _graph_request("POST", url, correlation_id, json_body=body)
        assigned_ids = [str(s["skuId"]) for s in to_assign]

    return {
        "userPrincipalName": upn,
        "assigned": assigned_ids,
        "skipped": skipped,
    }


# ==================== EMAIL / OUTREACH (existing send preserved, new operations added) ====================


async def outreach_email_send_individual(
    params: dict[str, Any], correlation_id: str
) -> dict[str, Any]:
    """Send an individual outreach email via Microsoft Graph.

    Expected params:
    - to: str | list[str]  Email address or list of addresses
    - subject: str         Subject line
    - html | text | body   Body content (prefers 'html', then 'text', then 'body')
    - from: str            Sender UPN/address (required for app-only auth)
    - saveToSent: bool     Save to Sent Items (default True)
    """
    to = params.get("to")
    subject = params.get("subject") or "(no subject)"
    html = params.get("html")
    text = params.get("text")
    body = params.get("body")
    save_to_sent = bool(params.get("saveToSent", True))

    # Normalize recipients
    if isinstance(to, str):
        # Support comma/semicolon separated lists
        parts = [p.strip() for p in to.replace(";", ",").split(",") if p.strip()]
        recipients: list[str] = parts or []
    elif isinstance(to, list):
        recipients = [str(x).strip() for x in to if str(x).strip()]
    else:
        recipients = []

    if not recipients:
        return {
            "email": "rejected",
            "error": "missing_recipients",
            "note": "Param 'to' is required",
        }

    # Choose content type
    if html is not None:
        content_type = "HTML"
        content = str(html)
    elif text is not None:
        content_type = "Text"
        content = str(text)
    else:
        content_type = "Text"
        content = str(body or "")

    sender = (
        params.get("from")
        or os.getenv("OUTREACH_SENDER")
        or os.getenv("DEFAULT_SENDER")
        or os.getenv("MAIL_SENDER")
    )

    resolution = resolve_action_auth(None, "email.send_individual", params)

    # In stub mode or without Graph credentials, accept but do not send
    token = _graph_token(prefer_delegated=resolution.prefer_delegated)
    if _stub_mode() or not token:
        return {
            "email": "accepted",
            "stub": True,
            "request": {
                "to": recipients,
                "subject": subject,
                "from": sender,
                "contentType": content_type,
                "length": len(content),
            },
        }

    delegated_self_send = (
        resolution.prefer_delegated
        and _can_use_me_endpoint()
        and not _first_explicit_identity(params, "from", "userId", "userPrincipalName")
    )

    if delegated_self_send:
        url = f"{GRAPH_BASE}/me/sendMail"
    elif (
        sender
        and str(sender).strip().lower() in {"me", "self", "current"}
        and _can_use_me_endpoint()
    ):
        url = f"{GRAPH_BASE}/me/sendMail"
        delegated_self_send = True
    elif sender:
        url = f"{GRAPH_BASE}/users/{sender}/sendMail"
    else:
        # For app-only tokens, /me is not supported; require an explicit sender
        return {
            "email": "rejected",
            "error": "sender_missing",
            "note": "Provide 'from' or set OUTREACH_SENDER",
        }

    # Build Graph sendMail payload
    msg = {
        "subject": subject,
        "body": {
            "contentType": content_type,
            "content": content,
        },
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in recipients],
    }

    await _graph_request(
        "POST",
        url,
        correlation_id,
        json_body={"message": msg, "saveToSentItems": save_to_sent},
        prefer_delegated=delegated_self_send,
    )

    return {
        "email": "sent",
        "to": recipients,
        "subject": subject,
        "from": sender or ("me" if delegated_self_send else None),
        "saveToSent": save_to_sent,
    }


async def mail_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List messages in a user's mailbox."""
    limit = int(params.get("limit", 25))
    if _stub_mode():
        return {
            "messages": [
                {
                    "id": "msg-stub-001",
                    "subject": "Stub email",
                    "from": {"emailAddress": {"address": "sender@example.com"}},
                    "receivedDateTime": "2024-01-15T10:00:00Z",
                    "isRead": True,
                },
            ],
            "count": 1,
        }
    url, prefer_delegated = _resolve_user_scoped_url(
        "mail.list",
        params,
        me_suffix="messages",
        user_suffix="messages",
        identity_keys=("userId", "userPrincipalName", "from"),
        error_message="userId is required for app-only auth (cannot use /me mailbox).",
    )
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,subject,from,receivedDateTime,isRead",
            "$top": str(limit),
            "$orderby": "receivedDateTime desc",
        },
        prefer_delegated=prefer_delegated,
    )
    messages = data.get("value", []) if data else []
    return {"messages": messages, "count": len(messages)}


async def mail_read(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Read a specific message."""
    message_id = params["messageId"]
    if _stub_mode():
        return {
            "message": {
                "id": message_id,
                "subject": "Stub email",
                "body": {"contentType": "Text", "content": "Stub body"},
                "from": {"emailAddress": {"address": "stub@example.com"}},
            }
        }
    url, prefer_delegated = _resolve_user_scoped_url(
        "mail.read",
        params,
        me_suffix=f"messages/{message_id}",
        user_suffix=f"messages/{message_id}",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me mailbox).",
    )
    data = await _graph_request("GET", url, correlation_id, prefer_delegated=prefer_delegated)
    return {"message": data}


async def mail_send(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Send mail (alias for outreach_email_send_individual with userId support)."""
    user_id = params.get("userId") or params.get("userPrincipalName") or params.get("from")
    if user_id and "from" not in params:
        params = {**params, "from": user_id}
    return await outreach_email_send_individual(params, correlation_id)


async def mail_reply(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Reply to a message."""
    message_id = params["messageId"]
    comment = params.get("comment") or params.get("body") or ""
    if _stub_mode():
        return {"replied": True, "messageId": message_id}
    url, prefer_delegated = _resolve_user_scoped_url(
        "mail.reply",
        params,
        me_suffix=f"messages/{message_id}/reply",
        user_suffix=f"messages/{message_id}/reply",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me mailbox).",
    )
    body: dict[str, Any] = {"comment": comment}
    await _graph_request(
        "POST",
        url,
        correlation_id,
        json_body=body,
        prefer_delegated=prefer_delegated,
    )
    return {"replied": True, "messageId": message_id}


async def mail_forward(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Forward a message."""
    message_id = params["messageId"]
    to_recipients = params.get("to") or params.get("toRecipients") or []
    comment = params.get("comment") or ""
    if isinstance(to_recipients, str):
        to_recipients = [r.strip() for r in to_recipients.replace(";", ",").split(",") if r.strip()]
    if _stub_mode():
        return {"forwarded": True, "messageId": message_id, "to": to_recipients}
    url, prefer_delegated = _resolve_user_scoped_url(
        "mail.forward",
        params,
        me_suffix=f"messages/{message_id}/forward",
        user_suffix=f"messages/{message_id}/forward",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me mailbox).",
    )
    body: dict[str, Any] = {
        "comment": comment,
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_recipients],
    }
    await _graph_request(
        "POST",
        url,
        correlation_id,
        json_body=body,
        prefer_delegated=prefer_delegated,
    )
    return {"forwarded": True, "messageId": message_id, "to": to_recipients}


async def mail_move(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Move a message to a different folder."""
    message_id = params["messageId"]
    destination_id = params.get("destinationId") or params.get("folderId")
    if _stub_mode():
        return {"moved": True, "messageId": message_id, "destinationId": destination_id}
    url, prefer_delegated = _resolve_user_scoped_url(
        "mail.move",
        params,
        me_suffix=f"messages/{message_id}/move",
        user_suffix=f"messages/{message_id}/move",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me mailbox).",
    )
    data = await _graph_request(
        "POST",
        url,
        correlation_id,
        json_body={"destinationId": destination_id},
        prefer_delegated=prefer_delegated,
    )
    return {
        "moved": True,
        "messageId": message_id,
        "destinationId": destination_id,
        "message": data,
    }


async def mail_delete(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Delete a message."""
    message_id = params["messageId"]
    if _stub_mode():
        return {"deleted": True, "messageId": message_id}
    url, prefer_delegated = _resolve_user_scoped_url(
        "mail.delete",
        params,
        me_suffix=f"messages/{message_id}",
        user_suffix=f"messages/{message_id}",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me mailbox).",
    )
    await _graph_request("DELETE", url, correlation_id, prefer_delegated=prefer_delegated)
    return {"deleted": True, "messageId": message_id}


async def mail_folders(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List mail folders."""
    if _stub_mode():
        return {
            "folders": [
                {"id": "inbox", "displayName": "Inbox", "totalItemCount": 42, "unreadItemCount": 5},
                {
                    "id": "sentitems",
                    "displayName": "Sent Items",
                    "totalItemCount": 100,
                    "unreadItemCount": 0,
                },
            ]
        }
    url, prefer_delegated = _resolve_user_scoped_url(
        "mail.folders",
        params,
        me_suffix="mailFolders",
        user_suffix="mailFolders",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me mailbox).",
    )
    data = await _graph_request("GET", url, correlation_id, prefer_delegated=prefer_delegated)
    folders = data.get("value", []) if data else []
    return {"folders": folders}


async def mailbox_settings(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get mailbox settings."""
    if _stub_mode():
        return {
            "settings": {
                "automaticRepliesSetting": {"status": "disabled"},
                "language": {"locale": "en-US"},
                "timeZone": "UTC",
            }
        }
    url, prefer_delegated = _resolve_user_scoped_url(
        "mailbox.settings",
        params,
        me_suffix="mailboxSettings",
        user_suffix="mailboxSettings",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me mailbox).",
    )
    data = await _graph_request("GET", url, correlation_id, prefer_delegated=prefer_delegated)
    return {"settings": data}


# ==================== TEAMS ====================


async def teams_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List all teams in the tenant."""
    if _stub_mode():
        return {
            "teams": [
                {
                    "id": "team-stub-001",
                    "displayName": "Stub Team",
                    "description": "A stub team",
                    "mail": "stubteam@smarthaus.ai",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/groups"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$filter": "resourceProvisioningOptions/Any(x:x eq 'Team')",
            "$select": "id,displayName,description,mail",
            "$top": str(params.get("limit", 100)),
        },
    )
    teams = data.get("value", []) if data else []
    return {"teams": teams, "count": len(teams)}


async def teams_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific team."""
    team_id = params.get("teamId") or params.get("id")
    if _stub_mode():
        return {
            "team": {
                "id": team_id,
                "displayName": "Stub Team",
                "description": "A stub team",
                "isArchived": False,
            }
        }
    url = f"{GRAPH_BASE}/teams/{team_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"team": data}


async def teams_create(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a new team."""
    import uuid as _uuid

    display_name = params.get("displayName") or params.get("name")
    description = params.get("description", "")
    owner = params.get("owner") or params.get("ownerUPN")
    if _stub_mode():
        tid = str(_uuid.uuid4())
        return {
            "team": {"id": tid, "displayName": display_name, "description": description},
            "status": "created",
        }
    body: dict[str, Any] = {
        "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
        "displayName": display_name,
        "description": description,
    }
    if owner:
        owner_id = await _get_user_id(owner, correlation_id) if not _is_guid(owner) else owner
        body["members"] = [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{owner_id}')",
            }
        ]
    url = f"{GRAPH_BASE}/teams"
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"team": data, "status": "created"}


async def teams_archive(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Archive a team."""
    team_id = params.get("teamId") or params.get("id")
    if _stub_mode():
        return {"archived": True, "teamId": team_id}
    url = f"{GRAPH_BASE}/teams/{team_id}/archive"
    await _graph_request("POST", url, correlation_id)
    return {"archived": True, "teamId": team_id}


async def teams_add_member(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Add a member to a team."""
    team_id = params.get("teamId") or params.get("id")
    user_id = params.get("userId") or params.get("userPrincipalName") or params.get("member")
    roles = params.get("roles") or []
    if _stub_mode():
        return {"added": True, "teamId": team_id, "userId": user_id, "roles": roles}
    # Resolve UPN to user ID if needed
    resolved_user_id = user_id
    if user_id and "@" in str(user_id):
        resolved_user_id = await _get_user_id(user_id, correlation_id)
    url = f"{GRAPH_BASE}/teams/{team_id}/members"
    body: dict[str, Any] = {
        "@odata.type": "#microsoft.graph.aadUserConversationMember",
        "roles": roles,
        "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{resolved_user_id}')",
    }
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"added": True, "teamId": team_id, "userId": user_id, "member": data}


async def teams_remove_member(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Remove a member from a team."""
    team_id = params.get("teamId") or params.get("id")
    membership_id = params.get("membershipId") or params.get("memberId")
    if _stub_mode():
        return {"removed": True, "teamId": team_id, "membershipId": membership_id}
    url = f"{GRAPH_BASE}/teams/{team_id}/members/{membership_id}"
    await _graph_request("DELETE", url, correlation_id)
    return {"removed": True, "teamId": team_id, "membershipId": membership_id}


async def channels_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List channels in a team."""
    team_id = params.get("teamId") or params.get("id")
    if _stub_mode():
        return {
            "channels": [
                {"id": "ch-stub-001", "displayName": "General", "membershipType": "standard"},
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/teams/{team_id}/channels"
    data = await _graph_request("GET", url, correlation_id)
    channels = data.get("value", []) if data else []
    return {"channels": channels, "count": len(channels)}


async def channels_create(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a channel in a team."""
    import uuid as _uuid

    team_id = params.get("teamId") or params.get("id")
    display_name = params.get("displayName") or params.get("name")
    description = params.get("description", "")
    membership_type = params.get("membershipType", "standard")
    if _stub_mode():
        return {
            "channel": {
                "id": str(_uuid.uuid4()),
                "displayName": display_name,
                "membershipType": membership_type,
            },
            "status": "created",
        }
    url = f"{GRAPH_BASE}/teams/{team_id}/channels"
    body: dict[str, Any] = {
        "displayName": display_name,
        "description": description,
        "membershipType": membership_type,
    }
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"channel": data, "status": "created"}


async def channels_send_message(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Send a message to a Teams channel.

    Params:
        teamId: The team ID
        channelId: The channel ID
        message: Message content (plain text or HTML)
        contentType: "text" or "html" (default "html")
    """
    team_id = params.get("teamId")
    channel_id = params.get("channelId")
    message = params.get("message") or params.get("content") or ""
    content_type = params.get("contentType", "html")
    if _stub_mode():
        return {"message": {"id": "msg-stub-001"}, "status": "sent"}
    if not team_id or not channel_id:
        raise GraphAPIError(400, "missing_params", "teamId and channelId are required")
    url = f"{GRAPH_BASE}/teams/{team_id}/channels/{channel_id}/messages"
    body: dict[str, Any] = {
        "body": {
            "contentType": content_type,
            "content": message,
        }
    }
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"message": data, "status": "sent"}


async def chat_create(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a 1:1 or group chat in Teams.

    Params:
        chatType: "oneOnOne" or "group"
        members: List of user IDs or UPNs to add to the chat
        topic: Optional display name for group chats
    """
    chat_type = params.get("chatType", "oneOnOne")
    members = params.get("members") or []
    topic = params.get("topic")
    if _stub_mode():
        return {"chat": {"id": "chat-stub-001", "chatType": chat_type}, "status": "created"}

    # Build members array — each needs @odata.type and roles
    member_entries = []
    for m in members:
        entry: dict[str, Any] = {
            "@odata.type": "#microsoft.graph.aadUserConversationMember",
            "roles": ["owner"],
            "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{m}')",
        }
        member_entries.append(entry)

    body: dict[str, Any] = {
        "chatType": chat_type,
        "members": member_entries,
    }
    if topic and chat_type == "group":
        body["topic"] = topic

    url = f"{GRAPH_BASE}/chats"
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"chat": data, "status": "created"}


async def chat_send_message(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Send a message to an existing Teams chat.

    Params:
        chatId: The chat ID (from chat_create or chat_list)
        message: Message content
        contentType: "text" or "html" (default "html")
    """
    chat_id = params.get("chatId")
    message = params.get("message") or params.get("content") or ""
    content_type = params.get("contentType", "html")
    if _stub_mode():
        return {"message": {"id": "msg-stub-001"}, "status": "sent"}
    if not chat_id:
        raise GraphAPIError(400, "missing_params", "chatId is required")
    url = f"{GRAPH_BASE}/chats/{chat_id}/messages"
    body: dict[str, Any] = {
        "body": {
            "contentType": content_type,
            "content": message,
        }
    }
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"message": data, "status": "sent"}


async def chat_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List chats for the current user or a specified user.

    Params:
        userId: User ID or UPN (required for app-only auth)
        top: Max results (default 50)
    """
    user_id = params.get("userId") or params.get("userPrincipalName")
    top = params.get("top", 50)
    if _stub_mode():
        return {"chats": [], "count": 0}
    resolution = resolve_action_auth(None, "chat.list", params)
    if user_id:
        url = f"{GRAPH_BASE}/users/{user_id}/chats"
        prefer_delegated = False
    elif resolution.prefer_delegated and _can_use_me_endpoint():
        url = f"{GRAPH_BASE}/me/chats"
        prefer_delegated = True
    else:
        raise GraphAPIError(
            400, "no_user_context", "userId is required for app-only auth (cannot use /me)."
        )
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={"$top": top},
        prefer_delegated=prefer_delegated,
    )
    chats = data.get("value", []) if data else []
    return {"chats": chats, "count": len(chats)}


async def chat_send(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """High-level: send a 1:1 Teams message to a user.

    Creates the chat if needed, then sends the message. This is the
    convenience action — use chat_create + chat_send_message for more control.

    Params:
        from: Sender user ID or UPN
        to: Recipient user ID or UPN
        message: Message content
        contentType: "text" or "html" (default "html")
    """
    sender = params.get("from") or params.get("userId") or params.get("senderId")
    recipient = params.get("to") or params.get("recipientId")
    message = params.get("message") or params.get("content") or ""
    content_type = params.get("contentType", "html")

    if not sender or not recipient:
        raise GraphAPIError(
            400, "missing_params", "'from' (sender) and 'to' (recipient) are required"
        )

    if _stub_mode():
        return {
            "chat": {"id": "chat-stub-001"},
            "message": {"id": "msg-stub-001"},
            "status": "sent",
        }

    # Step 1: Create (or get existing) 1:1 chat
    chat_result = await chat_create(
        {
            "chatType": "oneOnOne",
            "members": [sender, recipient],
        },
        correlation_id,
    )
    chat = chat_result.get("chat") or {}
    chat_id = chat.get("id")
    if not chat_id:
        raise GraphAPIError(500, "chat_create_failed", f"Failed to create chat: {chat_result}")

    # Step 2: Send the message
    msg_result = await chat_send_message(
        {
            "chatId": chat_id,
            "message": message,
            "contentType": content_type,
        },
        correlation_id,
    )

    return {
        "chat": {"id": chat_id},
        "message": msg_result.get("message"),
        "status": "sent",
    }


# Legacy workspace functions (preserved for backward compat)


async def create_workspace(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create workspace via Teams. Legacy alias."""
    result = await teams_create(
        {
            "displayName": params.get("name"),
            "description": params.get("description", ""),
            "owner": params.get("owner"),
        },
        correlation_id,
    )
    team = result.get("team") or {}
    team_id = team.get("id") or ""
    # Create additional channels if requested
    channels_out = []
    for ch_name in params.get("channels") or ["General"]:
        if ch_name.lower() == "general":
            channels_out.append({"name": ch_name, "id": "general"})
            continue
        ch_result = await channels_create(
            {"teamId": team_id, "displayName": ch_name}, correlation_id
        )
        ch = ch_result.get("channel") or {}
        channels_out.append({"name": ch_name, "id": ch.get("id", "")})
    # Add members if requested
    for member in params.get("members") or []:
        await teams_add_member({"teamId": team_id, "userId": member}, correlation_id)
    return {
        "workspaceId": team_id,
        "name": params.get("name"),
        "url": f"https://teams.microsoft.com/l/team/{team_id}",
        "channels": channels_out,
        "members": params.get("members", []),
        "status": "created",
        "correlationId": params.get("correlationId") or correlation_id,
    }


# ==================== GROUPS ====================


async def groups_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List groups."""
    limit = int(params.get("limit", 100))
    if _stub_mode():
        return {
            "groups": [
                {
                    "id": "grp-stub-001",
                    "displayName": "Stub Group",
                    "mail": "stubgroup@smarthaus.ai",
                    "groupTypes": ["Unified"],
                    "securityEnabled": False,
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/groups"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,displayName,mail,groupTypes,securityEnabled",
            "$top": str(limit),
        },
    )
    groups = data.get("value", []) if data else []
    return {"groups": groups, "count": len(groups)}


async def groups_create(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a group."""
    display_name = params.get("displayName") or params.get("name")
    mail_enabled = bool(params.get("mailEnabled", True))
    mail_nickname = (
        params.get("mailNickname") or display_name.replace(" ", "").lower()
        if display_name
        else "group"
    )
    security_enabled = bool(params.get("securityEnabled", False))
    group_types = params.get("groupTypes") or ["Unified"]
    if _stub_mode():
        import uuid as _uuid

        return {
            "group": {
                "id": str(_uuid.uuid4()),
                "displayName": display_name,
                "mailNickname": mail_nickname,
                "groupTypes": group_types,
                "securityEnabled": security_enabled,
            },
            "status": "created",
        }
    url = f"{GRAPH_BASE}/groups"
    body: dict[str, Any] = {
        "displayName": display_name,
        "mailEnabled": mail_enabled,
        "mailNickname": mail_nickname,
        "securityEnabled": security_enabled,
        "groupTypes": group_types,
    }
    if params.get("description"):
        body["description"] = params["description"]
    if params.get("owners"):
        body["owners@odata.bind"] = [
            f"https://graph.microsoft.com/v1.0/users/{o}" for o in params["owners"]
        ]
    if params.get("members"):
        body["members@odata.bind"] = [
            f"https://graph.microsoft.com/v1.0/users/{m}" for m in params["members"]
        ]
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"group": data, "status": "created"}


async def groups_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific group."""
    group_id = params.get("groupId") or params.get("id")
    if _stub_mode():
        return {"group": {"id": group_id, "displayName": "Stub Group", "mail": "stub@smarthaus.ai"}}
    url = f"{GRAPH_BASE}/groups/{group_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"group": data}


async def groups_add_member(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Add a member to a group."""
    group_id = params.get("groupId") or params.get("id")
    member_id = params.get("memberId") or params.get("userId") or params.get("userPrincipalName")
    if _stub_mode():
        return {"added": True, "groupId": group_id, "memberId": member_id}
    # Resolve UPN to user ID if needed
    resolved = member_id
    if member_id and "@" in str(member_id):
        resolved = await _get_user_id(member_id, correlation_id)
    url = f"{GRAPH_BASE}/groups/{group_id}/members/$ref"
    body = {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{resolved}"}
    await _graph_request("POST", url, correlation_id, json_body=body)
    return {"added": True, "groupId": group_id, "memberId": member_id}


async def groups_remove_member(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Remove a member from a group."""
    group_id = params.get("groupId") or params.get("id")
    member_id = params.get("memberId") or params.get("userId")
    if _stub_mode():
        return {"removed": True, "groupId": group_id, "memberId": member_id}
    url = f"{GRAPH_BASE}/groups/{group_id}/members/{member_id}/$ref"
    await _graph_request("DELETE", url, correlation_id)
    return {"removed": True, "groupId": group_id, "memberId": member_id}


async def groups_list_members(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List members of a group."""
    group_id = params.get("groupId") or params.get("id")
    if _stub_mode():
        return {
            "members": [
                {
                    "id": "usr-stub-001",
                    "displayName": "Stub User",
                    "userPrincipalName": "stub@smarthaus.ai",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/groups/{group_id}/members"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,displayName,userPrincipalName",
        },
    )
    members = data.get("value", []) if data else []
    return {"members": members, "count": len(members)}


# ==================== CALENDAR ====================


async def calendar_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List events on a user's calendar."""
    limit = int(params.get("limit", 25))
    if _stub_mode():
        return {
            "events": [
                {
                    "id": "evt-stub-001",
                    "subject": "Stub Meeting",
                    "start": {"dateTime": "2024-01-20T10:00:00", "timeZone": "UTC"},
                    "end": {"dateTime": "2024-01-20T11:00:00", "timeZone": "UTC"},
                    "organizer": {"emailAddress": {"address": "organizer@smarthaus.ai"}},
                },
            ],
            "count": 1,
        }
    url, prefer_delegated = _resolve_user_scoped_url(
        "calendar.list",
        params,
        me_suffix="events",
        user_suffix="events",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me calendar).",
    )
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,subject,start,end,organizer,attendees,location",
            "$top": str(limit),
            "$orderby": "start/dateTime",
        },
        prefer_delegated=prefer_delegated,
    )
    events = data.get("value", []) if data else []
    return {"events": events, "count": len(events)}


async def calendar_create(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a calendar event."""
    if _stub_mode():
        import uuid as _uuid

        return {
            "event": {
                "id": str(_uuid.uuid4()),
                "subject": params.get("subject", "Stub Event"),
                "status": "created",
            },
            "status": "created",
        }
    url, prefer_delegated = _resolve_user_scoped_url(
        "calendar.create",
        params,
        me_suffix="events",
        user_suffix="events",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me calendar).",
    )
    body: dict[str, Any] = {}
    for field in (
        "subject",
        "body",
        "start",
        "end",
        "location",
        "attendees",
        "isOnlineMeeting",
        "recurrence",
    ):
        if field in params:
            body[field] = params[field]
    data = await _graph_request(
        "POST",
        url,
        correlation_id,
        json_body=body,
        prefer_delegated=prefer_delegated,
    )
    return {"event": data, "status": "created"}


async def calendar_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific event."""
    event_id = params["eventId"]
    if _stub_mode():
        return {"event": {"id": event_id, "subject": "Stub Event"}}
    url, prefer_delegated = _resolve_user_scoped_url(
        "calendar.get",
        params,
        me_suffix=f"events/{event_id}",
        user_suffix=f"events/{event_id}",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me calendar).",
    )
    data = await _graph_request("GET", url, correlation_id, prefer_delegated=prefer_delegated)
    return {"event": data}


async def calendar_update(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Update a calendar event."""
    event_id = params["eventId"]
    if _stub_mode():
        return {"updated": True, "eventId": event_id}
    url, prefer_delegated = _resolve_user_scoped_url(
        "calendar.update",
        params,
        me_suffix=f"events/{event_id}",
        user_suffix=f"events/{event_id}",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me calendar).",
    )
    patch: dict[str, Any] = {}
    for field in (
        "subject",
        "body",
        "start",
        "end",
        "location",
        "attendees",
        "isOnlineMeeting",
        "recurrence",
    ):
        if field in params:
            patch[field] = params[field]
    await _graph_request(
        "PATCH",
        url,
        correlation_id,
        json_body=patch,
        prefer_delegated=prefer_delegated,
    )
    return {"updated": True, "eventId": event_id}


async def calendar_delete(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Delete a calendar event."""
    event_id = params["eventId"]
    if _stub_mode():
        return {"deleted": True, "eventId": event_id}
    url, prefer_delegated = _resolve_user_scoped_url(
        "calendar.delete",
        params,
        me_suffix=f"events/{event_id}",
        user_suffix=f"events/{event_id}",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me calendar).",
    )
    await _graph_request("DELETE", url, correlation_id, prefer_delegated=prefer_delegated)
    return {"deleted": True, "eventId": event_id}


async def calendar_availability(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Check availability / get schedule."""
    user_id = _first_explicit_identity(params, "userId", "userPrincipalName")
    schedules = params.get("schedules") or ([user_id] if user_id else [])
    start_time = params.get("startTime") or params.get("start")
    end_time = params.get("endTime") or params.get("end")
    if _stub_mode():
        return {
            "schedules": [
                {"scheduleId": s, "availabilityView": "0000000000", "scheduleItems": []}
                for s in schedules
            ]
        }
    url, prefer_delegated = _resolve_user_scoped_url(
        "calendar.availability",
        params,
        me_suffix="calendar/getSchedule",
        user_suffix="calendar/getSchedule",
        identity_keys=("userId", "userPrincipalName"),
        error_message="userId is required for app-only auth (cannot use /me calendar).",
    )
    body: dict[str, Any] = {
        "schedules": schedules or ["me"],
        "startTime": (
            start_time
            if isinstance(start_time, dict)
            else {"dateTime": start_time, "timeZone": "UTC"}
        ),
        "endTime": (
            end_time if isinstance(end_time, dict) else {"dateTime": end_time, "timeZone": "UTC"}
        ),
        "availabilityViewInterval": int(params.get("interval", 30)),
    }
    data = await _graph_request(
        "POST",
        url,
        correlation_id,
        json_body=body,
        prefer_delegated=prefer_delegated,
    )
    return {"schedules": data.get("value", []) if data else []}


# ==================== SHAREPOINT / SITES ====================


async def sites_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Search/list SharePoint sites."""
    query = params.get("query") or params.get("search") or "*"
    if _stub_mode():
        return {
            "sites": [
                {
                    "id": "site-stub-001",
                    "displayName": "Stub Site",
                    "webUrl": "https://smarthaus.sharepoint.com/sites/stub",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/sites"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "search": query,
            "$select": "id,displayName,webUrl",
        },
    )
    sites = data.get("value", []) if data else []
    return {"sites": sites, "count": len(sites)}


async def sites_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific site."""
    site_id = params.get("siteId") or params.get("id")
    if _stub_mode():
        return {
            "site": {
                "id": site_id,
                "displayName": "Stub Site",
                "webUrl": "https://smarthaus.sharepoint.com/sites/stub",
                "description": "",
            }
        }
    url = f"{GRAPH_BASE}/sites/{site_id}"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,displayName,webUrl,description",
        },
    )
    return {"site": data}


async def sites_root(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get the root site."""
    if _stub_mode():
        return {
            "site": {
                "id": "root-stub",
                "displayName": "Root Site",
                "webUrl": "https://smarthaus.sharepoint.com",
            }
        }
    url = f"{GRAPH_BASE}/sites/root"
    data = await _graph_request("GET", url, correlation_id)
    return {"site": data}


async def lists_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List SharePoint lists on a site."""
    site_id = params.get("siteId") or params.get("id")
    if _stub_mode():
        return {
            "lists": [
                {
                    "id": "list-stub-001",
                    "displayName": "Stub List",
                    "list": {"template": "genericList"},
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/sites/{site_id}/lists"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,displayName,list",
        },
    )
    lists = data.get("value", []) if data else []
    return {"lists": lists, "count": len(lists)}


async def lists_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific list."""
    site_id = params.get("siteId")
    list_id = params.get("listId") or params.get("id")
    if _stub_mode():
        return {"list": {"id": list_id, "displayName": "Stub List"}}
    url = f"{GRAPH_BASE}/sites/{site_id}/lists/{list_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"list": data}


async def lists_items(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get items from a list."""
    site_id = params.get("siteId")
    list_id = params.get("listId") or params.get("id")
    limit = int(params.get("limit", 50))
    if _stub_mode():
        return {"items": [{"id": "item-stub-001", "fields": {"Title": "Stub Item"}}], "count": 1}
    url = f"{GRAPH_BASE}/sites/{site_id}/lists/{list_id}/items"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$expand": "fields",
            "$top": str(limit),
        },
    )
    items = data.get("value", []) if data else []
    return {"items": items, "count": len(items)}


async def lists_create_item(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a list item."""
    site_id = params.get("siteId")
    list_id = params.get("listId") or params.get("id")
    fields = params.get("fields") or {}
    if _stub_mode():
        return {"item": {"id": "item-stub-new", "fields": fields}, "status": "created"}
    url = f"{GRAPH_BASE}/sites/{site_id}/lists/{list_id}/items"
    body: dict[str, Any] = {"fields": fields}
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"item": data, "status": "created"}


# ==================== FILES / ONEDRIVE ====================


async def files_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List files in a user's drive, site drive, or specific drive.

    Supports driveId, siteId, userId, or /me (delegated auth only).
    When no identifier is provided and delegated auth is available, uses /me.
    Otherwise falls back to the tenant's primary site from config.
    """
    user_id = params.get("userId") or params.get("userPrincipalName")
    drive_id = params.get("driveId")
    site_id = params.get("siteId")
    folder_path = params.get("folderPath") or params.get("path")
    folder_id = params.get("folderId")
    if _stub_mode():
        return {
            "files": [
                {
                    "id": "file-stub-001",
                    "name": "stub-document.docx",
                    "size": 12345,
                    "webUrl": "https://smarthaus.sharepoint.com/stub-document.docx",
                },
            ],
            "count": 1,
        }
    resolution = resolve_action_auth(None, "files.list", params)
    if drive_id:
        if folder_id and folder_id != "root":
            url = f"{GRAPH_BASE}/drives/{drive_id}/items/{folder_id}/children"
        elif folder_path:
            url = f"{GRAPH_BASE}/drives/{drive_id}/root:/{folder_path}:/children"
        else:
            url = f"{GRAPH_BASE}/drives/{drive_id}/root/children"
        prefer_delegated = False
    elif site_id:
        if folder_path:
            url = f"{GRAPH_BASE}/sites/{site_id}/drive/root:/{folder_path}:/children"
        else:
            url = f"{GRAPH_BASE}/sites/{site_id}/drive/root/children"
        prefer_delegated = False
    elif user_id:
        if folder_path:
            url = f"{GRAPH_BASE}/users/{user_id}/drive/root:/{folder_path}:/children"
        else:
            url = f"{GRAPH_BASE}/users/{user_id}/drive/root/children"
        prefer_delegated = False
    elif resolution.prefer_delegated and _can_use_me_endpoint():
        if folder_path:
            url = f"{GRAPH_BASE}/me/drive/root:/{folder_path}:/children"
        else:
            url = f"{GRAPH_BASE}/me/drive/root/children"
        prefer_delegated = True
    else:
        # No /me available — try tenant's primary site from config
        try:
            from smarthaus_common.tenant_config import get_tenant_config

            cfg = get_tenant_config()
            if cfg.org.primary_site_id:
                url = f"{GRAPH_BASE}/sites/{cfg.org.primary_site_id}/drive/root/children"
                prefer_delegated = False
            else:
                raise GraphAPIError(
                    400,
                    "no_drive_context",
                    "No driveId, siteId, or userId provided, and /me is not available "
                    "with app-only auth. Provide a siteId or configure org.primary_site_id "
                    "in your tenant config.",
                )
        except ImportError as err:
            raise GraphAPIError(
                400,
                "no_drive_context",
                "No driveId, siteId, or userId provided, and /me requires delegated auth.",
            ) from err
    data = await _graph_request("GET", url, correlation_id, prefer_delegated=prefer_delegated)
    files = data.get("value", []) if data else []
    return {"files": files, "count": len(files)}


async def files_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get file metadata."""
    drive_id = params.get("driveId")
    item_id = params.get("itemId") or params.get("id")
    if _stub_mode():
        return {"file": {"id": item_id, "name": "stub-file.docx", "size": 12345}}
    url = f"{GRAPH_BASE}/drives/{drive_id}/items/{item_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"file": data}


async def files_search(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Search for files across drives.

    Supports siteId, userId, driveId, or /me (delegated auth only).
    """
    user_id = params.get("userId") or params.get("userPrincipalName")
    site_id = params.get("siteId")
    drive_id = params.get("driveId")
    query = params.get("query") or params.get("q") or ""
    if _stub_mode():
        return {"files": [], "count": 0, "query": query}
    resolution = resolve_action_auth(None, "files.search", params)
    if drive_id:
        url = f"{GRAPH_BASE}/drives/{drive_id}/root/search(q='{query}')"
        prefer_delegated = False
    elif site_id:
        url = f"{GRAPH_BASE}/sites/{site_id}/drive/root/search(q='{query}')"
        prefer_delegated = False
    elif user_id:
        url = f"{GRAPH_BASE}/users/{user_id}/drive/root/search(q='{query}')"
        prefer_delegated = False
    elif resolution.prefer_delegated and _can_use_me_endpoint():
        url = f"{GRAPH_BASE}/me/drive/root/search(q='{query}')"
        prefer_delegated = True
    else:
        try:
            from smarthaus_common.tenant_config import get_tenant_config

            cfg = get_tenant_config()
            if cfg.org.primary_site_id:
                url = f"{GRAPH_BASE}/sites/{cfg.org.primary_site_id}/drive/root/search(q='{query}')"
                prefer_delegated = False
            else:
                raise GraphAPIError(
                    400,
                    "no_drive_context",
                    "No driveId, siteId, or userId provided, and /me requires delegated auth.",
                )
        except ImportError as err:
            raise GraphAPIError(
                400,
                "no_drive_context",
                "No driveId, siteId, or userId provided, and /me requires delegated auth.",
            ) from err
    data = await _graph_request("GET", url, correlation_id, prefer_delegated=prefer_delegated)
    files = data.get("value", []) if data else []
    return {"files": files, "count": len(files), "query": query}


async def files_create_folder(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a folder in a drive or site.

    Supports driveId, siteId, or falls back to tenant config.
    """
    drive_id = params.get("driveId")
    site_id = params.get("siteId")
    parent_id = params.get("parentId") or "root"
    folder_name = params.get("name") or params.get("folderName")
    if _stub_mode():
        import uuid as _uuid

        return {
            "folder": {"id": str(_uuid.uuid4()), "name": folder_name, "folder": {"childCount": 0}},
            "status": "created",
        }

    # Resolve the base path
    resolution = resolve_action_auth(None, "files.create_folder", params)
    if drive_id:
        base = f"{GRAPH_BASE}/drives/{drive_id}"
        prefer_delegated = False
    elif site_id:
        base = f"{GRAPH_BASE}/sites/{site_id}/drive"
        prefer_delegated = False
    elif resolution.prefer_delegated and _can_use_me_endpoint():
        base = f"{GRAPH_BASE}/me/drive"
        prefer_delegated = True
    else:
        try:
            from smarthaus_common.tenant_config import get_tenant_config

            cfg = get_tenant_config()
            if cfg.org.primary_site_id:
                base = f"{GRAPH_BASE}/sites/{cfg.org.primary_site_id}/drive"
                prefer_delegated = False
            else:
                raise GraphAPIError(
                    400,
                    "no_drive_context",
                    "No driveId or siteId provided, and /me requires delegated auth.",
                )
        except ImportError as err:
            raise GraphAPIError(
                400,
                "no_drive_context",
                "No driveId or siteId provided, and /me requires delegated auth.",
            ) from err

    if parent_id == "root":
        url = f"{base}/root/children"
    else:
        url = f"{base}/items/{parent_id}/children"

    body: dict[str, Any] = {
        "name": folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": params.get("conflictBehavior", "rename"),
    }
    data = await _graph_request(
        "POST",
        url,
        correlation_id,
        json_body=body,
        prefer_delegated=prefer_delegated,
    )
    return {"folder": data, "status": "created"}


async def files_upload(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Upload a file to a drive or site document library.

    Graph API supports simple upload for files ≤4MB via PUT to
    /drives/{driveId}/root:/{path}:/content.
    For larger files, creates an upload session and sends chunks.

    Supports driveId, siteId, or falls back to tenant config.
    Requires 'filePath' (local path to file) and 'remotePath' (destination path
    in the drive, e.g. 'Prospects/Zoetis/Research/doc.docx').
    """
    drive_id = params.get("driveId")
    site_id = params.get("siteId")
    local_path = params.get("filePath") or params.get("localPath") or params.get("local_path")
    remote_path = params.get("remotePath") or params.get("path") or params.get("fileName")
    conflict = params.get("conflictBehavior", "replace")

    if not local_path:
        raise GraphAPIError(
            400, "missing_param", "filePath is required — the local path to the file to upload."
        )
    if not remote_path:
        raise GraphAPIError(
            400,
            "missing_param",
            "remotePath is required — the destination path in the drive (e.g. 'Folder/file.docx').",
        )

    import pathlib

    file_path = pathlib.Path(local_path)
    if not file_path.exists():
        raise GraphAPIError(400, "file_not_found", f"Local file not found: {local_path}")

    file_size = file_path.stat().st_size
    file_bytes = file_path.read_bytes()

    if _stub_mode():
        return {
            "file": {"id": "uploaded-stub-001", "name": file_path.name, "size": file_size},
            "status": "uploaded",
        }

    # Resolve drive base path
    resolution = resolve_action_auth(None, "files.upload", params)
    if drive_id:
        base = f"{GRAPH_BASE}/drives/{drive_id}"
        prefer_delegated = False
    elif site_id:
        base = f"{GRAPH_BASE}/sites/{site_id}/drive"
        prefer_delegated = False
    elif resolution.prefer_delegated and _can_use_me_endpoint():
        base = f"{GRAPH_BASE}/me/drive"
        prefer_delegated = True
    else:
        try:
            from smarthaus_common.tenant_config import get_tenant_config

            cfg = get_tenant_config()
            if cfg.org.primary_site_id:
                base = f"{GRAPH_BASE}/sites/{cfg.org.primary_site_id}/drive"
                prefer_delegated = False
            else:
                raise GraphAPIError(
                    400,
                    "no_drive_context",
                    "No driveId or siteId provided, and /me requires delegated auth. "
                    "Provide a siteId or configure org.primary_site_id in your tenant config.",
                )
        except ImportError as err:
            raise GraphAPIError(
                400,
                "no_drive_context",
                "No driveId or siteId provided, and /me requires delegated auth.",
            ) from err

    token = _graph_token(prefer_delegated=prefer_delegated)
    if not token:
        raise GraphAPIError(500, "credentials_missing", "Graph credentials not configured")

    # Simple upload for files ≤ 4MB
    if file_size <= 4 * 1024 * 1024:
        from urllib.parse import quote as url_quote

        encoded_path = url_quote(remote_path, safe="/")
        url = f"{base}/root:/{encoded_path}:/content"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
            "X-Correlation-ID": correlation_id,
        }
        if conflict != "replace":
            url += f"?@microsoft.graph.conflictBehavior={conflict}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.put(url, headers=headers, content=file_bytes)
            if resp.status_code >= 400:
                try:
                    body = resp.json()
                except Exception as exc:
                    raise GraphAPIError(resp.status_code, "upload_failed", resp.text) from exc
                error_details = body.get("error", {})
                raise GraphAPIError(
                    resp.status_code,
                    error_details.get("code"),
                    error_details.get("message", resp.text),
                )
            data = resp.json() if resp.content else {}
            return {"file": data, "status": "uploaded"}

    # Large file: resumable upload session
    from urllib.parse import quote as url_quote

    encoded_path = url_quote(remote_path, safe="/")
    session_url = f"{base}/root:/{encoded_path}:/createUploadSession"
    session_body = {
        "item": {
            "@microsoft.graph.conflictBehavior": conflict,
            "name": file_path.name,
        }
    }
    session_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Correlation-ID": correlation_id,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(session_url, headers=session_headers, json=session_body)
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception as exc:
                raise GraphAPIError(resp.status_code, "session_create_failed", resp.text) from exc
            error_details = body.get("error", {})
            raise GraphAPIError(
                resp.status_code,
                error_details.get("code"),
                error_details.get("message", resp.text),
            )
        upload_url = resp.json().get("uploadUrl")

    # Upload in 3.2MB chunks
    chunk_size = 3200 * 1024  # ~3.2MB, must be multiple of 320KB
    offset = 0
    data = {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        while offset < file_size:
            chunk_end = min(offset + chunk_size, file_size) - 1
            chunk = file_bytes[offset : chunk_end + 1]
            chunk_headers = {
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {offset}-{chunk_end}/{file_size}",
            }
            resp = await client.put(upload_url, headers=chunk_headers, content=chunk)
            if resp.status_code >= 400:
                raise GraphAPIError(
                    resp.status_code,
                    "chunk_upload_failed",
                    f"Failed uploading bytes {offset}-{chunk_end}: {resp.text}",
                )
            if resp.status_code in (200, 201):
                # Upload complete
                data = resp.json() if resp.content else {}
            offset = chunk_end + 1

    return {"file": data, "status": "uploaded"}


async def files_share(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a sharing link for a file."""
    drive_id = params.get("driveId")
    item_id = params.get("itemId") or params.get("id")
    link_type = params.get("type", "view")
    scope = params.get("scope", "anonymous")
    if _stub_mode():
        return {
            "link": {
                "webUrl": f"https://smarthaus.sharepoint.com/share/{item_id}",
                "type": link_type,
                "scope": scope,
            }
        }
    url = f"{GRAPH_BASE}/drives/{drive_id}/items/{item_id}/createLink"
    body: dict[str, Any] = {"type": link_type, "scope": scope}
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"link": data.get("link") if data else None}


async def drives_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List drives for a user, group, site, or current user.

    Supports groupId, siteId, userId, or /me (delegated auth only).
    """
    user_id = params.get("userId") or params.get("userPrincipalName")
    group_id = params.get("groupId")
    site_id = params.get("siteId")
    if _stub_mode():
        return {
            "drives": [{"id": "drive-stub-001", "name": "OneDrive", "driveType": "personal"}],
            "count": 1,
        }
    resolution = resolve_action_auth(None, "drives.list", params)
    if group_id:
        url = f"{GRAPH_BASE}/groups/{group_id}/drives"
        prefer_delegated = False
    elif site_id:
        url = f"{GRAPH_BASE}/sites/{site_id}/drives"
        prefer_delegated = False
    elif user_id:
        url = f"{GRAPH_BASE}/users/{user_id}/drives"
        prefer_delegated = False
    elif resolution.prefer_delegated and _can_use_me_endpoint():
        url = f"{GRAPH_BASE}/me/drives"
        prefer_delegated = True
    else:
        try:
            from smarthaus_common.tenant_config import get_tenant_config

            cfg = get_tenant_config()
            if cfg.org.primary_site_id:
                url = f"{GRAPH_BASE}/sites/{cfg.org.primary_site_id}/drives"
                prefer_delegated = False
            else:
                raise GraphAPIError(
                    400,
                    "no_drive_context",
                    "No groupId, siteId, or userId provided, and /me requires delegated auth. "
                    "Provide a siteId or configure org.primary_site_id in your tenant config.",
                )
        except ImportError as err:
            raise GraphAPIError(
                400,
                "no_drive_context",
                "No groupId, siteId, or userId provided, and /me requires delegated auth.",
            ) from err
    data = await _graph_request("GET", url, correlation_id, prefer_delegated=prefer_delegated)
    drives = data.get("value", []) if data else []
    return {"drives": drives, "count": len(drives)}


# ==================== SECURITY ====================


async def security_alerts(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List security alerts."""
    limit = int(params.get("limit", 50))
    if _stub_mode():
        return {
            "alerts": [
                {
                    "id": "alert-stub-001",
                    "title": "Stub Alert",
                    "severity": "medium",
                    "status": "new",
                    "createdDateTime": "2024-01-15T10:00:00Z",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/security/alerts_v2"
    data = await _graph_request("GET", url, correlation_id, params={"$top": str(limit)})
    alerts = data.get("value", []) if data else []
    return {"alerts": alerts, "count": len(alerts)}


async def security_alert_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific alert."""
    alert_id = params.get("alertId") or params.get("id")
    if _stub_mode():
        return {
            "alert": {"id": alert_id, "title": "Stub Alert", "severity": "medium", "status": "new"}
        }
    url = f"{GRAPH_BASE}/security/alerts_v2/{alert_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"alert": data}


async def security_alert_update(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Update a security alert."""
    alert_id = params.get("alertId") or params.get("id")
    if _stub_mode():
        return {"updated": True, "alertId": alert_id}
    url = f"{GRAPH_BASE}/security/alerts_v2/{alert_id}"
    patch: dict[str, Any] = {}
    for field in ("status", "assignedTo", "classification", "determination", "comment"):
        if field in params:
            patch[field] = params[field]
    await _graph_request("PATCH", url, correlation_id, json_body=patch)
    return {"updated": True, "alertId": alert_id}


async def security_incidents(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List security incidents."""
    limit = int(params.get("limit", 50))
    if _stub_mode():
        return {
            "incidents": [
                {
                    "id": "inc-stub-001",
                    "displayName": "Stub Incident",
                    "severity": "high",
                    "status": "active",
                    "createdDateTime": "2024-01-15T10:00:00Z",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/security/incidents"
    data = await _graph_request("GET", url, correlation_id, params={"$top": str(limit)})
    incidents = data.get("value", []) if data else []
    return {"incidents": incidents, "count": len(incidents)}


async def security_incident_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific incident."""
    incident_id = params.get("incidentId") or params.get("id")
    if _stub_mode():
        return {
            "incident": {
                "id": incident_id,
                "displayName": "Stub Incident",
                "severity": "high",
                "status": "active",
            }
        }
    url = f"{GRAPH_BASE}/security/incidents/{incident_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"incident": data}


async def security_secure_score(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get the latest secure score."""
    if _stub_mode():
        return {
            "secureScore": {
                "id": "score-stub",
                "currentScore": 72.5,
                "maxScore": 100,
                "createdDateTime": "2024-01-15T10:00:00Z",
            }
        }
    url = f"{GRAPH_BASE}/security/secureScores"
    data = await _graph_request("GET", url, correlation_id, params={"$top": "1"})
    scores = data.get("value", []) if data else []
    return {"secureScore": scores[0] if scores else None}


# ==================== AUDIT LOGS ====================


async def audit_directory(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List directory audit logs."""
    limit = int(params.get("limit", 50))
    since = params.get("since") or params.get("startDate")
    if _stub_mode():
        return {
            "audits": [
                {
                    "id": "audit-stub-001",
                    "activityDisplayName": "Add user",
                    "activityDateTime": "2024-01-15T10:00:00Z",
                    "result": "success",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/auditLogs/directoryAudits"
    qparams: dict[str, str] = {"$top": str(limit)}
    if since:
        qparams["$filter"] = f"activityDateTime ge {since}"
    data = await _graph_request("GET", url, correlation_id, params=qparams)
    audits = data.get("value", []) if data else []
    return {"audits": audits, "count": len(audits)}


async def audit_signins(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List sign-in logs."""
    limit = int(params.get("limit", 50))
    since = params.get("since") or params.get("startDate")
    if _stub_mode():
        return {
            "signIns": [
                {
                    "id": "signin-stub-001",
                    "userPrincipalName": "stub@smarthaus.ai",
                    "createdDateTime": "2024-01-15T10:00:00Z",
                    "status": {"errorCode": 0},
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/auditLogs/signIns"
    qparams: dict[str, str] = {"$top": str(limit)}
    if since:
        qparams["$filter"] = f"createdDateTime ge {since}"
    data = await _graph_request("GET", url, correlation_id, params=qparams)
    signins = data.get("value", []) if data else []
    return {"signIns": signins, "count": len(signins)}


async def audit_provisioning(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List provisioning logs."""
    limit = int(params.get("limit", 50))
    if _stub_mode():
        return {
            "logs": [
                {
                    "id": "prov-stub-001",
                    "activityDateTime": "2024-01-15T10:00:00Z",
                    "provisioningAction": "create",
                    "statusInfo": {"status": "success"},
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/auditLogs/provisioning"
    data = await _graph_request("GET", url, correlation_id, params={"$top": str(limit)})
    logs = data.get("value", []) if data else []
    return {"logs": logs, "count": len(logs)}


# ==================== SERVICE HEALTH ====================


async def health_overview(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get service health overview."""
    if _stub_mode():
        return {
            "services": [
                {
                    "id": "Exchange Online",
                    "service": "Exchange Online",
                    "status": "serviceOperational",
                    "isActive": True,
                },
                {
                    "id": "Microsoft Teams",
                    "service": "Microsoft Teams",
                    "status": "serviceOperational",
                    "isActive": True,
                },
            ]
        }
    url = f"{GRAPH_BASE}/admin/serviceAnnouncement/healthOverviews"
    data = await _graph_request("GET", url, correlation_id)
    return {"services": data.get("value", []) if data else []}


async def health_issues(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List service health issues."""
    limit = int(params.get("limit", 50))
    if _stub_mode():
        return {"issues": [], "count": 0}
    url = f"{GRAPH_BASE}/admin/serviceAnnouncement/issues"
    data = await _graph_request("GET", url, correlation_id, params={"$top": str(limit)})
    issues = data.get("value", []) if data else []
    return {"issues": issues, "count": len(issues)}


async def health_issue_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific service health issue."""
    issue_id = params.get("issueId") or params.get("id")
    if _stub_mode():
        return {"issue": {"id": issue_id, "title": "Stub Issue", "status": "investigating"}}
    url = f"{GRAPH_BASE}/admin/serviceAnnouncement/issues/{issue_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"issue": data}


async def health_messages(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List service announcements / message center."""
    limit = int(params.get("limit", 50))
    if _stub_mode():
        return {"messages": [], "count": 0}
    url = f"{GRAPH_BASE}/admin/serviceAnnouncement/messages"
    data = await _graph_request("GET", url, correlation_id, params={"$top": str(limit)})
    messages = data.get("value", []) if data else []
    return {"messages": messages, "count": len(messages)}


# ==================== CONDITIONAL ACCESS ====================


async def ca_policies(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List conditional access policies."""
    if _stub_mode():
        return {
            "policies": [
                {"id": "ca-stub-001", "displayName": "Stub CA Policy", "state": "enabled"},
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/identity/conditionalAccess/policies"
    data = await _graph_request("GET", url, correlation_id)
    policies = data.get("value", []) if data else []
    return {"policies": policies, "count": len(policies)}


async def ca_policy_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific conditional access policy."""
    policy_id = params.get("policyId") or params.get("id")
    if _stub_mode():
        return {"policy": {"id": policy_id, "displayName": "Stub CA Policy", "state": "enabled"}}
    url = f"{GRAPH_BASE}/identity/conditionalAccess/policies/{policy_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"policy": data}


async def ca_policy_create(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create a conditional access policy."""
    if _stub_mode():
        import uuid as _uuid

        return {
            "policy": {
                "id": str(_uuid.uuid4()),
                "displayName": params.get("displayName", "Stub Policy"),
                "state": params.get("state", "disabled"),
            },
            "status": "created",
        }
    url = f"{GRAPH_BASE}/identity/conditionalAccess/policies"
    body: dict[str, Any] = {}
    for field in ("displayName", "state", "conditions", "grantControls", "sessionControls"):
        if field in params:
            body[field] = params[field]
    data = await _graph_request("POST", url, correlation_id, json_body=body)
    return {"policy": data, "status": "created"}


async def ca_policy_update(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Update a conditional access policy."""
    policy_id = params.get("policyId") or params.get("id")
    if _stub_mode():
        return {"updated": True, "policyId": policy_id}
    url = f"{GRAPH_BASE}/identity/conditionalAccess/policies/{policy_id}"
    patch: dict[str, Any] = {}
    for field in ("displayName", "state", "conditions", "grantControls", "sessionControls"):
        if field in params:
            patch[field] = params[field]
    await _graph_request("PATCH", url, correlation_id, json_body=patch)
    return {"updated": True, "policyId": policy_id}


async def ca_policy_delete(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Delete a conditional access policy."""
    policy_id = params.get("policyId") or params.get("id")
    if _stub_mode():
        return {"deleted": True, "policyId": policy_id}
    url = f"{GRAPH_BASE}/identity/conditionalAccess/policies/{policy_id}"
    await _graph_request("DELETE", url, correlation_id)
    return {"deleted": True, "policyId": policy_id}


async def ca_named_locations(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List named locations."""
    if _stub_mode():
        return {
            "locations": [
                {
                    "id": "loc-stub-001",
                    "displayName": "Trusted Network",
                    "@odata.type": "#microsoft.graph.ipNamedLocation",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/identity/conditionalAccess/namedLocations"
    data = await _graph_request("GET", url, correlation_id)
    locations = data.get("value", []) if data else []
    return {"locations": locations, "count": len(locations)}


# ==================== DIRECTORY / IDENTITY ====================


async def directory_roles(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List directory roles."""
    if _stub_mode():
        return {
            "roles": [
                {
                    "id": "role-stub-001",
                    "displayName": "Global Administrator",
                    "description": "Can manage all aspects of Azure AD",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/directoryRoles"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,displayName,description",
        },
    )
    roles = data.get("value", []) if data else []
    return {"roles": roles, "count": len(roles)}


async def directory_role_members(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List members of a directory role."""
    role_id = params.get("roleId") or params.get("id")
    if _stub_mode():
        return {
            "members": [
                {
                    "id": "usr-stub-001",
                    "displayName": "Stub Admin",
                    "userPrincipalName": "admin@smarthaus.ai",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/directoryRoles/{role_id}/members"
    data = await _graph_request("GET", url, correlation_id)
    members = data.get("value", []) if data else []
    return {"members": members, "count": len(members)}


async def directory_domains(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List domains."""
    if _stub_mode():
        return {
            "domains": [
                {"id": "smarthaus.ai", "isDefault": True, "isVerified": True},
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/domains"
    data = await _graph_request("GET", url, correlation_id)
    domains = data.get("value", []) if data else []
    return {"domains": domains, "count": len(domains)}


async def directory_org(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get organization info."""
    if _stub_mode():
        return {
            "organization": {
                "id": "org-stub",
                "displayName": "Smarthaus",
                "verifiedDomains": [{"name": "smarthaus.ai"}],
            }
        }
    url = f"{GRAPH_BASE}/organization"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,displayName,verifiedDomains,assignedPlans",
        },
    )
    orgs = data.get("value", []) if data else []
    return {"organization": orgs[0] if orgs else None}


async def apps_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List applications."""
    limit = int(params.get("limit", 100))
    if _stub_mode():
        return {
            "applications": [
                {
                    "id": "app-stub-001",
                    "displayName": "Stub App",
                    "appId": "00000000-0000-0000-0000-000000000000",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/applications"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,displayName,appId",
            "$top": str(limit),
        },
    )
    apps = data.get("value", []) if data else []
    return {"applications": apps, "count": len(apps)}


async def apps_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific application."""
    app_id = params.get("appId") or params.get("id")
    if _stub_mode():
        return {"application": {"id": app_id, "displayName": "Stub App", "appId": app_id}}
    url = f"{GRAPH_BASE}/applications/{app_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"application": data}


async def apps_update(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Update an application registration (PATCH)."""
    app_id = params.get("appId") or params.get("id")
    if not app_id:
        raise GraphAPIError(400, "missing_param", "Required: appId or id (object ID)")
    body = params.get("body", {})
    if not body:
        raise GraphAPIError(400, "missing_param", "Required: body (the PATCH payload)")
    if _stub_mode():
        return {"stub": True, "updated": app_id, "body": body}
    url = f"{GRAPH_BASE}/applications/{app_id}"
    await _graph_request("PATCH", url, correlation_id, json_body=body)
    return {"status": "updated", "appId": app_id}


async def service_principals_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List service principals."""
    limit = int(params.get("limit", 100))
    if _stub_mode():
        return {
            "servicePrincipals": [
                {
                    "id": "sp-stub-001",
                    "displayName": "Stub SP",
                    "appId": "00000000-0000-0000-0000-000000000000",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/servicePrincipals"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,displayName,appId",
            "$top": str(limit),
        },
    )
    sps = data.get("value", []) if data else []
    return {"servicePrincipals": sps, "count": len(sps)}


# ==================== REPORTS ====================


async def reports_users_active(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get Office 365 active user details."""
    period = params.get("period", "D7")
    if _stub_mode():
        return {
            "report": [
                {
                    "userPrincipalName": "stub@smarthaus.ai",
                    "hasExchangeLicense": "True",
                    "hasTeamsLicense": "True",
                }
            ],
            "period": period,
        }
    url = f"{GRAPH_BASE}/reports/getOffice365ActiveUserDetail(period='{period}')"
    raw = await _graph_request_raw("GET", url, correlation_id)
    return {"report": _csv_to_dicts(raw), "period": period}


async def reports_email_activity(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get email activity user details."""
    period = params.get("period", "D7")
    if _stub_mode():
        return {
            "report": [
                {"userPrincipalName": "stub@smarthaus.ai", "sendCount": "10", "receiveCount": "25"}
            ],
            "period": period,
        }
    url = f"{GRAPH_BASE}/reports/getEmailActivityUserDetail(period='{period}')"
    raw = await _graph_request_raw("GET", url, correlation_id)
    return {"report": _csv_to_dicts(raw), "period": period}


async def reports_teams_activity(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get Teams user activity details."""
    period = params.get("period", "D7")
    if _stub_mode():
        return {
            "report": [{"userPrincipalName": "stub@smarthaus.ai", "teamChatMessageCount": "5"}],
            "period": period,
        }
    url = f"{GRAPH_BASE}/reports/getTeamsUserActivityUserDetail(period='{period}')"
    raw = await _graph_request_raw("GET", url, correlation_id)
    return {"report": _csv_to_dicts(raw), "period": period}


async def reports_sharepoint_usage(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get SharePoint site usage details."""
    period = params.get("period", "D7")
    if _stub_mode():
        return {
            "report": [
                {"siteUrl": "https://smarthaus.sharepoint.com/sites/stub", "fileCount": "100"}
            ],
            "period": period,
        }
    url = f"{GRAPH_BASE}/reports/getSharePointSiteUsageDetail(period='{period}')"
    raw = await _graph_request_raw("GET", url, correlation_id)
    return {"report": _csv_to_dicts(raw), "period": period}


async def reports_onedrive_usage(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get OneDrive usage details."""
    period = params.get("period", "D7")
    if _stub_mode():
        return {
            "report": [{"ownerPrincipalName": "stub@smarthaus.ai", "storageUsedInBytes": "500000"}],
            "period": period,
        }
    url = f"{GRAPH_BASE}/reports/getOneDriveUsageAccountDetail(period='{period}')"
    raw = await _graph_request_raw("GET", url, correlation_id)
    return {"report": _csv_to_dicts(raw), "period": period}


# ==================== DEVICES / INTUNE ====================


async def devices_list(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List managed devices."""
    limit = int(params.get("limit", 50))
    if _stub_mode():
        return {
            "devices": [
                {
                    "id": "dev-stub-001",
                    "deviceName": "STUB-PC",
                    "operatingSystem": "Windows",
                    "osVersion": "10.0.19045",
                    "complianceState": "compliant",
                    "userPrincipalName": "stub@smarthaus.ai",
                },
            ],
            "count": 1,
        }
    url = f"{GRAPH_BASE}/deviceManagement/managedDevices"
    data = await _graph_request(
        "GET",
        url,
        correlation_id,
        params={
            "$select": "id,deviceName,operatingSystem,osVersion,complianceState,userPrincipalName",
            "$top": str(limit),
        },
    )
    devices = data.get("value", []) if data else []
    return {"devices": devices, "count": len(devices)}


async def devices_get(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get a specific managed device."""
    device_id = params.get("deviceId") or params.get("id")
    if _stub_mode():
        return {
            "device": {
                "id": device_id,
                "deviceName": "STUB-PC",
                "operatingSystem": "Windows",
                "complianceState": "compliant",
            }
        }
    url = f"{GRAPH_BASE}/deviceManagement/managedDevices/{device_id}"
    data = await _graph_request("GET", url, correlation_id)
    return {"device": data}


async def devices_compliance(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get device compliance policy setting summaries."""
    if _stub_mode():
        return {
            "summaries": [
                {
                    "settingName": "Require encryption",
                    "compliantDeviceCount": 45,
                    "nonCompliantDeviceCount": 5,
                },
            ]
        }
    url = f"{GRAPH_BASE}/deviceManagement/deviceCompliancePolicySettingStateSummaries"
    data = await _graph_request("GET", url, correlation_id)
    return {"summaries": data.get("value", []) if data else []}


async def devices_actions(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Execute a device action (syncDevice, rebootNow, etc.)."""
    device_id = params.get("deviceId") or params.get("id")
    action = params.get("action") or params.get("deviceAction") or "syncDevice"
    if _stub_mode():
        return {"executed": True, "deviceId": device_id, "action": action}
    url = f"{GRAPH_BASE}/deviceManagement/managedDevices/{device_id}/{action}"
    await _graph_request("POST", url, correlation_id)
    return {"executed": True, "deviceId": device_id, "action": action}


# ==================== LEGACY STUBS (preserved for backward compat) ====================


async def website_deployment_preview(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    token = os.getenv("VERCEL_API_TOKEN") or os.getenv("VERCEL_TOKEN")
    return {
        "status": "queued",
        "provider": "vercel",
        "note": (
            "Vercel token not configured; dry-run"
            if not token
            else "Request would be sent to Vercel"
        ),
    }


async def hr_employee_onboard(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    return {"onboarding": "accepted", "request": params}


# --------- Client Journey: Projects / Provisioning / Workspace ---------

_PROJECTS_MEM: list[dict[str, Any]] = []


async def create_project(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Create new M365 project with Teams workspace and SharePoint site (stub-friendly)."""
    import uuid as _uuid

    name = params["name"]
    description = params.get("description", "")
    client = params.get("client", {})
    config = params.get("config", {})
    project_id = str(_uuid.uuid4())

    if _stub_mode():
        channels = config.get("recommendedChannels", ["General", "Development", "Documentation"])
        proj = {
            "id": project_id,
            "name": name,
            "description": description,
            "client": client,
            "status": "active",
            "progress": 0,
            "teamsUrl": f"https://teams.microsoft.com/l/team/{project_id}",
            "sharepointUrl": f"https://smarthaus.sharepoint.com/sites/{project_id}",
            "channels": channels,
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "lastActivity": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        _PROJECTS_MEM.insert(0, proj)
        return {
            "projectId": project_id,
            "name": name,
            "status": "created",
            "teamsUrl": proj["teamsUrl"],
            "sharepointUrl": proj["sharepointUrl"],
            "channels": channels,
            "correlationId": params.get("correlationId") or correlation_id,
        }

    # Real Graph implementation placeholder
    return await create_project({**params, "_force_stub": True}, correlation_id)


async def list_projects(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    status_filter = params.get("status", "active")
    limit = int(params.get("limit", 50))
    if _stub_mode():
        items = _PROJECTS_MEM.copy()
        if not items:
            import uuid as _uuid

            items = [
                {
                    "id": str(_uuid.uuid4()),
                    "name": "Acme Corp - AIDF Implementation",
                    "client": "acme@example.com",
                    "status": "active",
                    "progress": 65,
                    "teamsUrl": "https://teams.microsoft.com/l/team/sample1",
                    "sharepointUrl": "https://smarthaus.sharepoint.com/sites/sample1",
                    "lastActivity": "2024-01-15T10:30:00Z",
                    "created": "2024-01-01T09:00:00Z",
                    "description": "AIDF deployment for Acme",
                },
                {
                    "id": str(_uuid.uuid4()),
                    "name": "TechStart Inc - AI Strategy",
                    "client": "tech@startup.com",
                    "status": "active",
                    "progress": 30,
                    "teamsUrl": "https://teams.microsoft.com/l/team/sample2",
                    "sharepointUrl": "https://smarthaus.sharepoint.com/sites/sample2",
                    "lastActivity": "2024-01-14T15:45:00Z",
                    "created": "2024-01-10T11:00:00Z",
                    "description": "Advisory + strategy",
                },
            ]
        projects = [
            p for p in items if (status_filter == "all" or p.get("status") == status_filter)
        ]
        return {
            "projects": projects[: max(1, min(limit, 100))],
            "total": len(projects),
            "status": status_filter,
        }
    return {"projects": [], "total": 0, "status": status_filter}


async def provision_client_services(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    client_id = params["clientId"]
    services = params.get("services", ["identity", "approval", "audit"])
    provisioned_services = []
    base_map = {"identity": "8082", "approval": "8083", "audit": "8084"}
    for svc in services:
        port = base_map.get(svc, None)
        provisioned_services.append(
            {
                "service": svc,
                "status": "provisioned",
                "endpoint": f"http://localhost:{port}" if port else None,
            }
        )
    return {
        "clientId": client_id,
        "services": provisioned_services,
        "status": "provisioned",
        "correlationId": params.get("correlationId") or correlation_id,
    }


# ==================== UCP ADMIN ACTIONS ====================


def _find_tenant_yaml(tenant_slug: str | None = None) -> str | None:
    """Locate the tenant YAML file for write-back operations."""
    slug = tenant_slug or os.getenv("UCP_TENANT", "smarthaus")
    search_paths = []

    mcp_root = os.getenv("UCP_ROOT", "")
    repos_root = os.getenv("REPOS_ROOT", os.getenv("UCP_REPOS_ROOT", ""))

    if mcp_root:
        search_paths.append(os.path.join(mcp_root, "tenants", f"{slug}.yaml"))
    if repos_root:
        search_paths.append(
            os.path.join(repos_root, "SMARTHAUS_MCPSERVER_core", "tenants", f"{slug}.yaml")
        )

    # Relative from this file: ops_adapter/ -> src/ -> M365/ -> ../SMARTHAUS_MCPSERVER_core/tenants/
    this_dir = os.path.dirname(__file__)
    search_paths.append(
        os.path.normpath(
            os.path.join(
                this_dir, "..", "..", "..", "SMARTHAUS_MCPSERVER_core", "tenants", f"{slug}.yaml"
            )
        )
    )

    for path in search_paths:
        if os.path.isfile(path):
            return path
    return None


def _find_permission_tiers_yaml() -> str | None:
    """Locate permission_tiers.yaml."""
    search_paths = [
        os.getenv("M365_PERMISSION_TIERS_PATH", ""),
        os.path.join(os.getenv("M365_REPO_ROOT", ""), "registry", "permission_tiers.yaml"),
    ]
    this_dir = os.path.dirname(__file__)
    search_paths.append(
        os.path.normpath(os.path.join(this_dir, "..", "..", "registry", "permission_tiers.yaml"))
    )

    for path in search_paths:
        path = path.strip()
        if path and os.path.isfile(path):
            return path
    return None


async def admin_list_tiers(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List all available permission tiers with their descriptions."""
    path = _find_permission_tiers_yaml()
    if not path:
        raise GraphAPIError(404, "tiers_not_found", "permission_tiers.yaml not found")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    tiers = data.get("tiers", {})
    result = []
    for tier_name, tier_def in tiers.items():
        result.append(
            {
                "tier": tier_name,
                "name": tier_def.get("name", tier_name),
                "description": tier_def.get("description", ""),
                "risk_tier": tier_def.get("risk_tier", "unknown"),
                "allowed_domain_count": len(tier_def.get("allowed_domains", [])),
                "blocked_action_count": len(tier_def.get("blocked_actions", [])),
            }
        )

    return {
        "tiers": result,
        "count": len(result),
        "defaults": data.get("defaults", {}),
    }


async def admin_get_tier(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get full details for a specific permission tier."""
    tier_name = params.get("tier")
    if not tier_name:
        raise GraphAPIError(400, "missing_param", "Required param: tier")

    path = _find_permission_tiers_yaml()
    if not path:
        raise GraphAPIError(404, "tiers_not_found", "permission_tiers.yaml not found")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    tier_def = data.get("tiers", {}).get(tier_name)
    if tier_def is None:
        raise GraphAPIError(404, "tier_not_found", f"Tier '{tier_name}' does not exist")

    return {"tier": tier_name, **tier_def}


async def admin_list_users(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """List all users with their assigned permission tiers."""
    tenant_slug = params.get("tenant") or os.getenv("UCP_TENANT", "smarthaus")
    path = _find_tenant_yaml(tenant_slug)
    if not path:
        raise GraphAPIError(
            404, "tenant_not_found", f"Tenant config '{tenant_slug}.yaml' not found"
        )

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    pt = data.get("permission_tiers", {})
    default_tier = pt.get("default_tier", "standard_user")
    users = pt.get("users", {})

    result = []
    for email, tier in users.items():
        result.append({"email": email, "tier": tier})

    return {
        "users": result,
        "count": len(result),
        "default_tier": default_tier,
        "tenant": tenant_slug,
        "config_path": path,
    }


async def admin_get_user_tier(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get the permission tier for a specific user."""
    email = params.get("email")
    if not email:
        raise GraphAPIError(400, "missing_param", "Required param: email")

    tenant_slug = params.get("tenant") or os.getenv("UCP_TENANT", "smarthaus")
    path = _find_tenant_yaml(tenant_slug)
    if not path:
        raise GraphAPIError(
            404, "tenant_not_found", f"Tenant config '{tenant_slug}.yaml' not found"
        )

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    pt = data.get("permission_tiers", {})
    default_tier = pt.get("default_tier", "standard_user")
    users = pt.get("users", {})

    # Case-insensitive lookup
    lower_email = email.lower()
    assigned_tier = default_tier
    explicitly_assigned = False
    for user_email, tier in users.items():
        if user_email.lower() == lower_email:
            assigned_tier = tier
            explicitly_assigned = True
            break

    return {
        "email": email,
        "tier": assigned_tier,
        "explicitly_assigned": explicitly_assigned,
        "default_tier": default_tier,
    }


async def admin_set_user_tier(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Set or update a user's permission tier. Writes back to tenant YAML.

    Requires confirmation gate (handled by MCP tool layer).
    """
    email = params.get("email")
    tier = params.get("tier")
    if not email or not tier:
        raise GraphAPIError(400, "missing_param", "Required params: email, tier")

    # Validate the tier exists
    tiers_path = _find_permission_tiers_yaml()
    if tiers_path:
        with open(tiers_path, encoding="utf-8") as f:
            tiers_data = yaml.safe_load(f) or {}
        valid_tiers = set(tiers_data.get("tiers", {}).keys())
        if tier not in valid_tiers:
            raise GraphAPIError(
                400,
                "invalid_tier",
                f"Tier '{tier}' does not exist. Valid tiers: {', '.join(sorted(valid_tiers))}",
            )

    # Load tenant config
    tenant_slug = str(params.get("tenant") or os.getenv("UCP_TENANT", "smarthaus"))
    path = _find_tenant_yaml(tenant_slug)
    if not path:
        raise GraphAPIError(
            404, "tenant_not_found", f"Tenant config '{tenant_slug}.yaml' not found"
        )

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Ensure permission_tiers section exists
    if "permission_tiers" not in data:
        data["permission_tiers"] = {"default_tier": "standard_user", "users": {}}
    if "users" not in data["permission_tiers"]:
        data["permission_tiers"]["users"] = {}

    # Track previous tier for audit
    prev_tier = data["permission_tiers"]["users"].get(
        email, data["permission_tiers"].get("default_tier", "standard_user")
    )

    # Set the tier
    data["permission_tiers"]["users"][email] = tier

    # Write back
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Force tenant config reload if available
    try:
        from smarthaus_common.tenant_config import reload_tenant_config

        reload_tenant_config()
    except Exception:
        pass

    record_admin_event(
        event_class="permission_tier_update",
        action="admin.set_user_tier",
        correlation_id=correlation_id,
        actor=params.get("requestor"),
        actor_tier=params.get("requestor_tier_info"),
        actor_groups=params.get("requestor_groups"),
        executor=params.get("executor_identity"),
        tenant=tenant_slug,
        status="updated",
        details={
            "email": email,
            "config_path": str(path),
            "operation": "set_user_tier",
        },
        before={"tier": prev_tier},
        after={"tier": tier},
    )

    return {
        "email": email,
        "previous_tier": prev_tier,
        "new_tier": tier,
        "tenant": tenant_slug,
        "status": "updated",
        "config_path": path,
        "note": "Tenant config reloaded. Change is effective immediately.",
    }


async def admin_remove_user_tier(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Remove a user's explicit tier assignment (reverts to default tier).

    Requires confirmation gate.
    """
    email = params.get("email")
    if not email:
        raise GraphAPIError(400, "missing_param", "Required param: email")

    tenant_slug = str(params.get("tenant") or os.getenv("UCP_TENANT", "smarthaus"))
    path = _find_tenant_yaml(tenant_slug)
    if not path:
        raise GraphAPIError(
            404, "tenant_not_found", f"Tenant config '{tenant_slug}.yaml' not found"
        )

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    pt = data.get("permission_tiers", {})
    users = pt.get("users", {})
    default_tier = pt.get("default_tier", "standard_user")

    # Case-insensitive find and remove
    removed = False
    prev_tier = default_tier
    lower_email = email.lower()
    keys_to_remove = []
    for user_email in users:
        if user_email.lower() == lower_email:
            prev_tier = users[user_email]
            keys_to_remove.append(user_email)
            removed = True

    for key in keys_to_remove:
        del users[key]

    if not removed:
        record_admin_event(
            event_class="permission_tier_update",
            action="admin.remove_user_tier",
            correlation_id=correlation_id,
            actor=params.get("requestor"),
            actor_tier=params.get("requestor_tier_info"),
            actor_groups=params.get("requestor_groups"),
            executor=params.get("executor_identity"),
            tenant=tenant_slug,
            status="not_found",
            details={
                "email": email,
                "config_path": str(path),
                "operation": "remove_user_tier",
            },
            before={"tier": default_tier},
            after={"tier": default_tier},
        )
        return {
            "email": email,
            "status": "not_found",
            "message": f"User '{email}' had no explicit tier assignment (already using default: {default_tier})",
        }

    # Write back
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    try:
        from smarthaus_common.tenant_config import reload_tenant_config

        reload_tenant_config()
    except Exception:
        pass

    record_admin_event(
        event_class="permission_tier_update",
        action="admin.remove_user_tier",
        correlation_id=correlation_id,
        actor=params.get("requestor"),
        actor_tier=params.get("requestor_tier_info"),
        actor_groups=params.get("requestor_groups"),
        executor=params.get("executor_identity"),
        tenant=tenant_slug,
        status="removed",
        details={
            "email": email,
            "config_path": str(path),
            "operation": "remove_user_tier",
        },
        before={"tier": prev_tier},
        after={"tier": default_tier},
    )

    return {
        "email": email,
        "previous_tier": prev_tier,
        "new_tier": default_tier,
        "status": "removed",
        "message": f"Explicit tier removed. User now falls back to default tier: {default_tier}",
    }


async def admin_get_tenant_config(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Get the current tenant configuration (redacted secrets)."""
    tenant_slug = str(params.get("tenant") or os.getenv("UCP_TENANT", "smarthaus"))
    path = _find_tenant_yaml(tenant_slug)
    if not path:
        raise GraphAPIError(
            404, "tenant_not_found", f"Tenant config '{tenant_slug}.yaml' not found"
        )

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Redact secrets
    if "azure" in data:
        if data["azure"].get("client_secret"):
            data["azure"]["client_secret"] = "***REDACTED***"
        if data["azure"].get("client_certificate_path"):
            data["azure"]["client_certificate_path"] = "***REDACTED***"

    record_admin_event(
        event_class="tenant_config_read",
        action="admin.get_tenant_config",
        correlation_id=correlation_id,
        actor=params.get("requestor"),
        actor_tier=params.get("requestor_tier_info"),
        actor_groups=params.get("requestor_groups"),
        executor=params.get("executor_identity"),
        tenant=tenant_slug,
        status="read",
        details={
            "config_path": str(path),
            "sections": sorted(data.keys()),
            "permission_tier_user_count": len(
                (data.get("permission_tiers") or {}).get("users", {})
            ),
            "redacted": True,
        },
    )

    return {"tenant": tenant_slug, "config": data, "config_path": path}


async def admin_reload_config(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Force reload tenant config and permission tier definitions from disk."""
    tenant_slug = str(params.get("tenant") or os.getenv("UCP_TENANT", "smarthaus"))
    reloaded = []

    try:
        from smarthaus_common.tenant_config import reload_tenant_config

        reload_tenant_config()
        reloaded.append("tenant_config")
    except Exception as e:
        reloaded.append(f"tenant_config:FAILED:{e}")

    # Force permission tiers reload by resetting the module cache
    try:
        from smarthaus_common import permission_enforcer

        permission_enforcer._TIERS = None
        permission_enforcer._TIERS_PATH = None
        permission_enforcer._TIERS_MTIME = 0.0
        permission_enforcer._load_tiers()
        reloaded.append("permission_tiers")
    except Exception as e:
        reloaded.append(f"permission_tiers:FAILED:{e}")

    record_admin_event(
        event_class="tenant_config_reload",
        action="admin.reload_config",
        correlation_id=correlation_id,
        actor=params.get("requestor"),
        actor_tier=params.get("requestor_tier_info"),
        actor_groups=params.get("requestor_groups"),
        executor=params.get("executor_identity"),
        tenant=tenant_slug,
        status="ok",
        details={"reloaded": reloaded},
    )

    return {"reloaded": reloaded, "status": "ok"}


async def admin_audit_log(params: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    """Return recent UCP admin operations from the append-only audit trail."""
    tenant_slug = str(params.get("tenant") or os.getenv("UCP_TENANT", "smarthaus"))
    limit = int(params.get("limit") or 50)
    action = params.get("action")
    event_class = params.get("event_class")
    include_snapshot = bool(params.get("include_snapshot"))

    events = recent_admin_events(
        tenant=tenant_slug,
        action=action,
        event_class=event_class,
        limit=limit,
    )

    result = {
        "tenant": tenant_slug,
        "status": "event_log",
        "count": len(events),
        "events": events,
    }

    if include_snapshot:
        path = _find_tenant_yaml(tenant_slug)
        if path:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            pt = data.get("permission_tiers", {})
            result["snapshot"] = {
                "default_tier": pt.get("default_tier", "standard_user"),
                "user_count": len(pt.get("users", {})),
                "config_file_mtime": os.path.getmtime(path),
            }
        else:
            result["snapshot_error"] = "tenant_config_not_found"

    if not events:
        result["note"] = "No admin audit events recorded yet for the current tenant/filter."
    return result


# ==================== EXECUTE DISPATCHER ====================


async def execute(
    agent: str,
    action: str,
    params: dict[str, Any],
    correlation_id: str,
    executor_name: str | None = None,
) -> dict[str, Any]:
    auth_resolution = resolve_action_auth(agent, action, params)
    context_token = _current_executor_name.set(executor_name)
    auth_token = _current_auth_resolution.set(auth_resolution)
    try:
        return await _execute_impl(agent, action, params, correlation_id)
    finally:
        _current_auth_resolution.reset(auth_token)
        _current_executor_name.reset(context_token)


async def _execute_impl(
    agent: str, action: str, params: dict[str, Any], correlation_id: str
) -> dict[str, Any]:
    if True:
        # ---- M365 Administrator ----
        if agent == "m365-administrator":
            # Users
            if action in ("users.read", "users.list"):
                return await m365_users_read(params, correlation_id)
            if action == "users.create":
                return await m365_users_create(params, correlation_id)
            if action == "users.update":
                return await m365_users_update(params, correlation_id)
            if action == "users.disable":
                return await m365_users_disable(params, correlation_id)
            # Licenses
            if action == "licenses.assign":
                return await m365_licenses_assign(params, correlation_id)
            # Groups
            if action == "groups.list":
                return await groups_list(params, correlation_id)
            if action == "groups.create":
                return await groups_create(params, correlation_id)
            if action == "groups.get":
                return await groups_get(params, correlation_id)
            if action == "groups.add_member":
                return await groups_add_member(params, correlation_id)
            if action == "groups.remove_member":
                return await groups_remove_member(params, correlation_id)
            if action == "groups.list_members":
                return await groups_list_members(params, correlation_id)
            # SharePoint / Sites
            if action == "sites.list":
                return await sites_list(params, correlation_id)
            if action == "sites.get":
                return await sites_get(params, correlation_id)
            if action == "sites.root":
                return await sites_root(params, correlation_id)
            if action == "lists.list":
                return await lists_list(params, correlation_id)
            if action == "lists.get":
                return await lists_get(params, correlation_id)
            if action == "lists.items":
                return await lists_items(params, correlation_id)
            if action == "lists.create_item":
                return await lists_create_item(params, correlation_id)
            if action == "sites.provision":
                return await sites_provision(params, correlation_id)
            # Files / OneDrive
            if action == "files.list":
                return await files_list(params, correlation_id)
            if action == "files.get":
                return await files_get(params, correlation_id)
            if action == "files.search":
                return await files_search(params, correlation_id)
            if action == "files.create_folder":
                return await files_create_folder(params, correlation_id)
            if action == "files.upload":
                return await files_upload(params, correlation_id)
            if action == "files.share":
                return await files_share(params, correlation_id)
            if action == "drives.list":
                return await drives_list(params, correlation_id)
            # Directory / Identity
            if action == "directory.roles":
                return await directory_roles(params, correlation_id)
            if action == "directory.role_members":
                return await directory_role_members(params, correlation_id)
            if action == "directory.domains":
                return await directory_domains(params, correlation_id)
            if action == "directory.org":
                return await directory_org(params, correlation_id)
            if action == "apps.list":
                return await apps_list(params, correlation_id)
            if action == "apps.get":
                return await apps_get(params, correlation_id)
            if action == "service_principals.list":
                return await service_principals_list(params, correlation_id)
            if action == "apps.update":
                return await apps_update(params, correlation_id)
            if action == "teams.add_channel":
                channel_params = dict(params)
                if "displayName" not in channel_params and channel_params.get("channelName"):
                    channel_params["displayName"] = channel_params["channelName"]
                return await channels_create(channel_params, correlation_id)

        # ---- Teams Manager ----
        if agent == "teams-manager":
            # New dotted names
            if action == "teams.list":
                return await teams_list(params, correlation_id)
            if action == "teams.get":
                return await teams_get(params, correlation_id)
            if action == "teams.create":
                return await teams_create(params, correlation_id)
            if action == "teams.archive":
                return await teams_archive(params, correlation_id)
            if action == "teams.add_member":
                return await teams_add_member(params, correlation_id)
            if action == "teams.remove_member":
                return await teams_remove_member(params, correlation_id)
            if action == "channels.list":
                return await channels_list(params, correlation_id)
            if action == "channels.create":
                return await channels_create(params, correlation_id)
            if action == "channels.send_message":
                return await channels_send_message(params, correlation_id)
            if action == "chat.create":
                return await chat_create(params, correlation_id)
            if action == "chat.send_message":
                return await chat_send_message(params, correlation_id)
            if action == "chat.send":
                return await chat_send(params, correlation_id)
            if action == "chat.list":
                return await chat_list(params, correlation_id)
            # Legacy action names
            if action == "create-workspace":
                return await create_workspace(params, correlation_id)
            if action == "add-workspace-members":
                members = params.get("members") or []
                team_id = params.get("teamId") or params.get("workspaceId")
                results = []
                for m in members:
                    r = await teams_add_member({"teamId": team_id, "userId": m}, correlation_id)
                    results.append(r)
                return {"status": "added", "members": members, "results": results}
            if action == "create-channels":
                team_id = params.get("teamId") or params.get("workspaceId")
                channel_names = params.get("channels") or []
                results = []
                for ch in channel_names:
                    r = await channels_create(
                        {"teamId": team_id, "displayName": ch}, correlation_id
                    )
                    results.append(r)
                return {"status": "created", "channels": channel_names, "results": results}
            if action == "get-team-status":
                team_id = params.get("teamId") or params.get("id")
                if team_id:
                    return await teams_get({"teamId": team_id}, correlation_id)
                return {"status": "ok", "members": (params.get("members") or [])}

        # ---- Website ----
        if agent == "website-manager":
            if action == "deployment.preview":
                return await website_deployment_preview(params, correlation_id)
            if action == "deployment.production":
                return {"status": "queued", "environment": "production", "provider": "vercel"}
            if action == "content.create":
                return {
                    "status": "stubbed",
                    "content_id": params.get("content_id"),
                    "created": True,
                }
            if action == "content.update":
                return {
                    "status": "stubbed",
                    "content_id": params.get("content_id"),
                    "updated": True,
                }
            if action == "analytics.read":
                return {"status": "stubbed", "analytics": {"visits": 0, "conversions": 0}}
            if action == "seo.update":
                return {"status": "stubbed", "updated": True, "targets": params.get("targets", [])}

        # ---- HR ----
        if agent == "hr-generalist":
            if action == "employee.onboard":
                return await hr_employee_onboard(params, correlation_id)
            if action == "employee.update_info":
                update_params = dict(params)
                if "userPrincipalName" not in update_params and update_params.get("email"):
                    update_params["userPrincipalName"] = update_params["email"]
                return await m365_users_update(update_params, correlation_id)
            if action == "employee.offboard":
                disable_params = dict(params)
                if "userPrincipalName" not in disable_params and disable_params.get("email"):
                    disable_params["userPrincipalName"] = disable_params["email"]
                return await m365_users_disable(disable_params, correlation_id)
            if action == "policy.create":
                return {"status": "stubbed", "policy_id": params.get("policy_id"), "created": True}
            if action == "review.initiate":
                return {
                    "status": "stubbed",
                    "review_id": params.get("review_id"),
                    "initiated": True,
                }

        # ---- Outreach Coordinator ----
        if agent == "outreach-coordinator":
            if action == "email.send_individual":
                return await outreach_email_send_individual(params, correlation_id)
            if action == "mail.send":
                return await mail_send(params, correlation_id)
            if action == "email.send_bulk":
                return await outreach_email_send_bulk(params, correlation_id)
            if action == "email.schedule":
                return await outreach_email_schedule(params, correlation_id)
            if action == "meeting.schedule":
                return await outreach_meeting_schedule(params, correlation_id)
            if action == "followup.create":
                return {
                    "status": "stubbed",
                    "followup_id": params.get("followup_id"),
                    "created": True,
                }
            if action == "campaign.create":
                return {
                    "status": "stubbed",
                    "campaign_id": params.get("campaign_id"),
                    "created": True,
                }

        # ---- Email Processing Agent ----
        if agent == "email-processing-agent":
            if action == "mail.list":
                return await mail_list(params, correlation_id)
            if action == "mail.read":
                return await mail_read(params, correlation_id)
            if action == "mail.send":
                return await mail_send(params, correlation_id)
            if action == "mail.reply":
                return await mail_reply(params, correlation_id)
            if action == "mail.forward":
                return await mail_forward(params, correlation_id)
            if action == "mail.move":
                return await mail_move(params, correlation_id)
            if action == "mail.delete":
                return await mail_delete(params, correlation_id)
            if action == "mail.folders":
                return await mail_folders(params, correlation_id)
            if action == "mailbox.settings":
                return await mailbox_settings(params, correlation_id)
            # Legacy action names
            if action == "email.classify":
                return {"classification": "inquiry", "priority": "medium", "category": "general"}
            if action == "email.respond":
                return await mail_reply(params, correlation_id)
            if action == "email.forward":
                return await mail_forward(params, correlation_id)
            if action == "email.archive":
                return await mail_move({**params, "destinationId": "archive"}, correlation_id)
            if action == "follow-up.schedule":
                return {"scheduled": True, "follow_up_date": params.get("date", "2024-02-01")}
            if action == "email.send_individual":
                return await outreach_email_send_individual(params, correlation_id)

        # ---- Calendar Management Agent ----
        if agent == "calendar-management-agent":
            if action == "calendar.list":
                return await calendar_list(params, correlation_id)
            if action == "calendar.create":
                return await calendar_create(params, correlation_id)
            if action == "calendar.get":
                return await calendar_get(params, correlation_id)
            if action == "calendar.update":
                return await calendar_update(params, correlation_id)
            if action == "calendar.delete":
                return await calendar_delete(params, correlation_id)
            if action == "calendar.availability":
                return await calendar_availability(params, correlation_id)
            # Legacy aliases
            if action == "calendar.schedule":
                return await calendar_create(params, correlation_id)
            if action == "meeting.organize":
                return await calendar_create(params, correlation_id)
            if action == "availability.check":
                return await calendar_availability(params, correlation_id)
            if action == "reminder.send":
                return {"reminder_sent": True, "recipient": params.get("recipient")}
            if action == "conflict.resolve":
                return {
                    "resolved": True,
                    "new_time": params.get("newTime", "2024-01-20T15:00:00Z"),
                }
    # ---- Project Manager ----
    if agent == "project-manager":
        if action == "create-project":
            return await create_project(params, correlation_id)
        if action == "list-projects":
            return await list_projects(params, correlation_id)
        if action == "update-project-status":
            pid = params.get("id")
            status = params.get("status")
            for p in _PROJECTS_MEM:
                if p.get("id") == pid:
                    if status:
                        p["status"] = status
                    p["lastActivity"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    return {"updated": True, "project": p}
            return {"updated": False}
        if action == "archive-project":
            pid = params.get("id")
            for p in _PROJECTS_MEM:
                if p.get("id") == pid:
                    p["status"] = "completed"
                    p["lastActivity"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    return {"archived": True, "project": p}
            return {"archived": False}

    # ---- Platform Manager ----
    if agent == "platform-manager":
        if action == "provision-client-services":
            return await provision_client_services(params, correlation_id)
        if action == "deprovision-client-services":
            return {"status": "deprovisioned", "clientId": params.get("clientId")}
        if action == "get-client-status":
            return {"status": "active", "clientId": params.get("clientId")}

    # ---- Security Operations ----
    if agent == "security-operations":
        if action == "security.alerts":
            return await security_alerts(params, correlation_id)
        if action == "security.alert_get":
            return await security_alert_get(params, correlation_id)
        if action == "security.alert_update":
            return await security_alert_update(params, correlation_id)
        if action == "security.incidents":
            return await security_incidents(params, correlation_id)
        if action == "security.incident_get":
            return await security_incident_get(params, correlation_id)
        if action == "security.secure_score":
            return await security_secure_score(params, correlation_id)

    # ---- Audit Operations ----
    if agent == "audit-operations":
        if action == "audit.directory":
            return await audit_directory(params, correlation_id)
        if action == "audit.signins":
            return await audit_signins(params, correlation_id)
        if action == "audit.provisioning":
            return await audit_provisioning(params, correlation_id)

    # ---- Service Health ----
    if agent == "service-health":
        if action == "health.overview":
            return await health_overview(params, correlation_id)
        if action == "health.issues":
            return await health_issues(params, correlation_id)
        if action == "health.issue_get":
            return await health_issue_get(params, correlation_id)
        if action == "health.messages":
            return await health_messages(params, correlation_id)

    # ---- Identity Security (Conditional Access) ----
    if agent == "identity-security":
        if action == "ca.policies":
            return await ca_policies(params, correlation_id)
        if action == "ca.policy_get":
            return await ca_policy_get(params, correlation_id)
        if action == "ca.policy_create":
            return await ca_policy_create(params, correlation_id)
        if action == "ca.policy_update":
            return await ca_policy_update(params, correlation_id)
        if action == "ca.policy_delete":
            return await ca_policy_delete(params, correlation_id)
        if action == "ca.named_locations":
            return await ca_named_locations(params, correlation_id)

    # ---- Reports ----
    if agent == "reports":
        if action == "reports.users_active":
            return await reports_users_active(params, correlation_id)
        if action == "reports.email_activity":
            return await reports_email_activity(params, correlation_id)
        if action == "reports.teams_activity":
            return await reports_teams_activity(params, correlation_id)
        if action == "reports.sharepoint_usage":
            return await reports_sharepoint_usage(params, correlation_id)
        if action == "reports.onedrive_usage":
            return await reports_onedrive_usage(params, correlation_id)

    # ---- Device Management ----
    if agent == "device-management":
        if action == "devices.list":
            return await devices_list(params, correlation_id)
        if action == "devices.get":
            return await devices_get(params, correlation_id)
        if action == "devices.compliance":
            return await devices_compliance(params, correlation_id)
        if action == "devices.actions":
            return await devices_actions(params, correlation_id)

    # ---- IT Operations Manager (legacy stubs) ----
    if agent == "it-operations-manager":
        if action == "infrastructure.monitor":
            return {"status": "monitoring", "infrastructure_health": "good"}
        if action == "system.health-check":
            return {"status": "checked", "system_health": "healthy"}
        if action == "alerts.respond":
            return {"status": "responded", "alert_id": params.get("alert_id")}
        if action == "backup.verify":
            return {"status": "verified", "backup_integrity": "intact"}
        if action == "security.scan":
            return {"status": "scanned", "vulnerabilities_found": 0}

    # ---- Website Operations Specialist (legacy stubs) ----
    if agent == "website-operations-specialist":
        if action == "website.deploy":
            return {"status": "deployed", "environment": params.get("environment")}
        if action == "cdn.purge":
            return {"status": "purged", "target": params.get("target")}
        if action == "dns.update":
            return {"status": "updated", "domain": params.get("domain")}
        if action == "ssl.renew":
            return {"status": "renewed", "certificate": params.get("certificate")}
        if action == "performance.optimize":
            return {"status": "optimized", "improvements": ["caching", "compression"]}
        if action == "backup.restore":
            return {"status": "restored", "backup_id": params.get("backup_id")}

    # ---- Project Coordination Agent (legacy stubs) ----
    if agent == "project-coordination-agent":
        if action == "list_plans":
            return await planner_list_plans(params, correlation_id)
        if action == "create_plan":
            return await planner_create_plan(params, correlation_id)
        if action == "list_buckets":
            return await planner_list_buckets(params, correlation_id)
        if action == "create_bucket":
            return await planner_create_bucket(params, correlation_id)
        if action == "create_task":
            return await planner_create_task(params, correlation_id)
        if action == "task.create":
            return {"created": True, "task_id": "task_456", "assignee": params.get("assignee")}
        if action == "task.assign":
            return {
                "assigned": True,
                "task_id": params.get("task_id"),
                "assignee": params.get("assignee"),
            }
        if action == "deadline.track":
            return {"tracked": True, "deadline": params.get("deadline"), "status": "on_track"}
        if action == "status.update":
            return {
                "updated": True,
                "project_id": params.get("project_id"),
                "status": params.get("status"),
            }
        if action == "report.generate":
            return {
                "generated": True,
                "report_type": "weekly",
                "download_url": "/reports/weekly.pdf",
            }

    # ---- Client Relationship Agent (legacy stubs) ----
    if agent == "client-relationship-agent":
        if action == "client.follow-up":
            return {"follow_up_scheduled": True, "client_id": params.get("client_id")}
        if action == "satisfaction.survey":
            return {"survey_sent": True, "client_id": params.get("client_id")}
        if action == "feedback.analyze":
            return {"analyzed": True, "sentiment": "positive", "insights": ["happy with service"]}
        if action == "relationship.score":
            return {"score": 8.5, "client_id": params.get("client_id"), "trend": "improving"}
        if action == "engagement.plan":
            return {
                "plan_created": True,
                "client_id": params.get("client_id"),
                "actions": ["send newsletter", "schedule call"],
            }

    # ---- Compliance Monitoring Agent (legacy stubs) ----
    if agent == "compliance-monitoring-agent":
        if action == "compliance.check":
            return {"compliant": True, "regulations_checked": ["GDPR", "HIPAA"]}
        if action == "policy.validate":
            return {"validated": True, "policy_id": params.get("policy_id")}
        if action == "audit.prepare":
            return {"prepared": True, "audit_type": params.get("audit_type")}
        if action == "violation.report":
            return {"reported": True, "violation_id": params.get("violation_id")}
        if action == "remediation.plan":
            return {"plan_created": True, "violation_id": params.get("violation_id")}

    # ---- Recruitment Assistance Agent (legacy stubs) ----
    if agent == "recruitment-assistance-agent":
        if action == "candidate.screen":
            return {
                "screened": True,
                "candidate_id": params.get("candidate_id"),
                "recommendation": "interview",
            }
        if action == "interview.schedule":
            return {
                "scheduled": True,
                "candidate_id": params.get("candidate_id"),
                "interviewer": params.get("interviewer"),
            }
        if action == "feedback.collect":
            return {"collected": True, "interview_id": params.get("interview_id")}
        if action == "offer.prepare":
            return {"prepared": True, "candidate_id": params.get("candidate_id")}
        if action == "onboarding.initiate":
            return {"initiated": True, "candidate_id": params.get("candidate_id")}

    # ---- Financial Operations Agent (legacy stubs) ----
    if agent == "financial-operations-agent":
        if action == "invoice.process":
            return {"processed": True, "invoice_id": params.get("invoice_id")}
        if action == "expense.approve":
            return {"approved": True, "expense_id": params.get("expense_id")}
        if action == "budget.track":
            return {"tracked": True, "budget_variance": 5.2}
        if action == "forecast.update":
            return {"updated": True, "forecast_accuracy": 92.5}
        if action == "audit.prepare":
            return {"prepared": True, "audit_documents": ["financials.pdf", "reports.xlsx"]}

    # ---- Knowledge Management Agent (legacy stubs) ----
    if agent == "knowledge-management-agent":
        if action == "document.index":
            return {"indexed": True, "documents_processed": 25}
        if action == "search.optimize":
            return {"optimized": True, "search_accuracy": 94.2}
        if action == "content.curate":
            return {"curated": True, "articles_added": 12}
        if action == "training.recommend":
            return {"recommended": True, "courses": ["AI Ethics", "Data Governance"]}
        if action == "expert.connect":
            return {"connected": True, "expert_id": params.get("expert_id")}

    # ---- UCP / M365 Administrator (admin config surface) ----
    if agent in ("ucp-administrator", "m365-administrator"):
        if action == "admin.list_tiers":
            return await admin_list_tiers(params, correlation_id)
        if action == "admin.get_tier":
            return await admin_get_tier(params, correlation_id)
        if action == "admin.list_users":
            return await admin_list_users(params, correlation_id)
        if action == "admin.get_user_tier":
            return await admin_get_user_tier(params, correlation_id)
        if action == "admin.set_user_tier":
            return await admin_set_user_tier(params, correlation_id)
        if action == "admin.remove_user_tier":
            return await admin_remove_user_tier(params, correlation_id)
        if action == "admin.get_tenant_config":
            return await admin_get_tenant_config(params, correlation_id)
        if action == "admin.reload_config":
            return await admin_reload_config(params, correlation_id)
        if action == "admin.audit_log":
            return await admin_audit_log(params, correlation_id)

    raise ValueError(f"Unsupported action: {agent}/{action}")
