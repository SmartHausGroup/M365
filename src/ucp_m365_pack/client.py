"""Standalone UCP-facing M365 executor owned by the M365 repo."""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

import jwt
import yaml

try:
    _MODULE_DIR = os.path.dirname(__file__)
except NameError:
    _MODULE_DIR = os.getcwd()

ENV_M365_OPS_ADAPTER_URL = "M365_OPS_ADAPTER_URL"
ENV_M365_OPS_ADAPTER_URL_SMARTHAUS = "SMARTHAUS_M365_OPS_ADAPTER_URL"
ENV_M365_REPO_ROOT = "M365_REPO_ROOT"
ENV_M365_REPO_ROOT_SMARTHAUS = "SMARTHAUS_M365_REPO_ROOT"
ENV_M365_SERVICE_JWT_HS256_KEY_VAR = "M365_SERVICE_JWT_HS256_SECRET"
ENV_M365_SERVICE_JWT_HS256_KEY_VAR_SMARTHAUS = "SMARTHAUS_M365_SERVICE_JWT_HS256_SECRET"
ENV_M365_SERVICE_JWT_ISSUER = "M365_SERVICE_JWT_ISSUER"
ENV_M365_SERVICE_JWT_ISSUER_SMARTHAUS = "SMARTHAUS_M365_SERVICE_JWT_ISSUER"
ENV_M365_SERVICE_JWT_AUDIENCE = "M365_SERVICE_JWT_AUDIENCE"
ENV_M365_SERVICE_JWT_AUDIENCE_SMARTHAUS = "SMARTHAUS_M365_SERVICE_JWT_AUDIENCE"
ENV_M365_SERVICE_JWT_TTL_SECONDS = "M365_SERVICE_JWT_TTL_SECONDS"
ENV_M365_SERVICE_JWT_TTL_SECONDS_SMARTHAUS = "SMARTHAUS_M365_SERVICE_JWT_TTL_SECONDS"
ENV_M365_SERVICE_ACTOR_UPN = "M365_SERVICE_ACTOR_UPN"
ENV_M365_SERVICE_ACTOR_UPN_SMARTHAUS = "SMARTHAUS_M365_SERVICE_ACTOR_UPN"
ENV_M365_SERVICE_ACTOR_EMAIL = "M365_SERVICE_ACTOR_EMAIL"
ENV_M365_SERVICE_ACTOR_EMAIL_SMARTHAUS = "SMARTHAUS_M365_SERVICE_ACTOR_EMAIL"
ENV_M365_SERVICE_ACTOR_SUB = "M365_SERVICE_ACTOR_SUB"
ENV_M365_SERVICE_ACTOR_SUB_SMARTHAUS = "SMARTHAUS_M365_SERVICE_ACTOR_SUB"
ENV_M365_SERVICE_ACTOR_OID = "M365_SERVICE_ACTOR_OID"
ENV_M365_SERVICE_ACTOR_OID_SMARTHAUS = "SMARTHAUS_M365_SERVICE_ACTOR_OID"
ENV_M365_SERVICE_ACTOR_GROUPS = "M365_SERVICE_ACTOR_GROUPS"
ENV_M365_SERVICE_ACTOR_GROUPS_SMARTHAUS = "SMARTHAUS_M365_SERVICE_ACTOR_GROUPS"

_REGISTRY: dict[str, Any] | None = None
_DEFAULT_SERVICE_JWT_TTL_SECONDS = 300


def _env_value(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
    return None


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [item for item in (_normalize_text(entry) for entry in value) if item]
    text = _normalize_text(value)
    if not text:
        return []
    return [part for part in (_normalize_text(piece) for piece in text.split(",")) if part]


def _positive_int(raw: Any, default: int) -> int:
    text = _normalize_text(raw)
    if not text:
        return default
    try:
        parsed = int(text)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _resolve_service_jwt_settings() -> dict[str, Any]:
    return {
        "hs256_secret": _normalize_text(
            _env_value(
                ENV_M365_SERVICE_JWT_HS256_KEY_VAR,
                ENV_M365_SERVICE_JWT_HS256_KEY_VAR_SMARTHAUS,
                "JWT_HS256_SECRET",
            )
        ),
        "issuer": _normalize_text(
            _env_value(
                ENV_M365_SERVICE_JWT_ISSUER,
                ENV_M365_SERVICE_JWT_ISSUER_SMARTHAUS,
                "JWT_ISSUER",
            )
        ),
        "audience": _normalize_text(
            _env_value(
                ENV_M365_SERVICE_JWT_AUDIENCE,
                ENV_M365_SERVICE_JWT_AUDIENCE_SMARTHAUS,
                "JWT_AUDIENCE",
            )
        ),
        "ttl_seconds": _positive_int(
            _env_value(
                ENV_M365_SERVICE_JWT_TTL_SECONDS,
                ENV_M365_SERVICE_JWT_TTL_SECONDS_SMARTHAUS,
            ),
            _DEFAULT_SERVICE_JWT_TTL_SECONDS,
        ),
    }


class M365ExecutionError(Exception):
    def __init__(self, status: int, code: str | None, message: str):
        super().__init__(f"M365ExecutionError {status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


def _resolve_service_actor_identity(actor_identity: dict[str, Any] | None) -> dict[str, Any]:
    payload = actor_identity or {}
    upn = _normalize_text(
        payload.get("preferred_username")
        or payload.get("upn")
        or payload.get("email")
        or payload.get("requestor")
        or _env_value(
            ENV_M365_SERVICE_ACTOR_UPN,
            ENV_M365_SERVICE_ACTOR_UPN_SMARTHAUS,
            ENV_M365_SERVICE_ACTOR_EMAIL,
            ENV_M365_SERVICE_ACTOR_EMAIL_SMARTHAUS,
        )
    ).lower()
    if not upn:
        raise M365ExecutionError(
            500,
            "caller_actor_identity_missing",
            "M365 service caller actor identity is missing. Set M365_SERVICE_ACTOR_UPN or pass actor_identity.",
        )
    client_id = _normalize_text(payload.get("client_id") or payload.get("client"))
    subject = _normalize_text(
        payload.get("sub")
        or _env_value(
            ENV_M365_SERVICE_ACTOR_SUB,
            ENV_M365_SERVICE_ACTOR_SUB_SMARTHAUS,
        )
    )
    if not subject:
        subject = f"ucp-client:{client_id}" if client_id else upn
    oid = _normalize_text(
        payload.get("oid")
        or _env_value(
            ENV_M365_SERVICE_ACTOR_OID,
            ENV_M365_SERVICE_ACTOR_OID_SMARTHAUS,
        )
    )
    groups = _normalize_string_list(payload.get("groups")) or _normalize_string_list(
        _env_value(
            ENV_M365_SERVICE_ACTOR_GROUPS,
            ENV_M365_SERVICE_ACTOR_GROUPS_SMARTHAUS,
        )
    )
    return {
        "upn": upn,
        "sub": subject,
        "oid": oid or None,
        "groups": groups,
        "client_id": client_id or None,
    }


def _build_service_bearer_token(
    actor_identity: dict[str, Any] | None,
    correlation_id: str,
) -> str:
    settings = _resolve_service_jwt_settings()
    if not settings["hs256_secret"]:
        raise M365ExecutionError(
            500,
            "caller_auth_config_missing",
            "M365 service caller JWT secret is missing. Set M365_SERVICE_JWT_HS256_SECRET or JWT_HS256_SECRET.",
        )

    actor = _resolve_service_actor_identity(actor_identity)
    now = int(time.time())
    claims: dict[str, Any] = {
        "sub": actor["sub"],
        "preferred_username": actor["upn"],
        "upn": actor["upn"],
        "email": actor["upn"],
        "iat": now,
        "exp": now + int(settings["ttl_seconds"]),
        "jti": correlation_id,
    }
    if settings["issuer"]:
        claims["iss"] = settings["issuer"]
    if settings["audience"]:
        claims["aud"] = settings["audience"]
    if actor["oid"]:
        claims["oid"] = actor["oid"]
    if actor["groups"]:
        claims["groups"] = actor["groups"]
    if actor["client_id"]:
        claims["azp"] = actor["client_id"]

    token = jwt.encode(claims, settings["hs256_secret"], algorithm="HS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def _resolve_m365_repo_root() -> str:
    configured_root = _env_value(ENV_M365_REPO_ROOT, ENV_M365_REPO_ROOT_SMARTHAUS)
    if configured_root:
        return configured_root
    candidate = os.path.normpath(os.path.join(_MODULE_DIR, "..", ".."))
    if os.path.isdir(os.path.join(candidate, "src", "ops_adapter")):
        return candidate
    return ""


def _configured_service_url() -> str | None:
    configured_url = _env_value(ENV_M365_OPS_ADAPTER_URL, ENV_M365_OPS_ADAPTER_URL_SMARTHAUS)
    if configured_url is None:
        return None
    stripped = configured_url.strip()
    return stripped or None


def _load_registry() -> dict[str, Any]:
    global _REGISTRY
    if _REGISTRY is not None:
        return _REGISTRY

    search_paths = [
        os.getenv("M365_REGISTRY_PATH", ""),
        os.path.join(_resolve_m365_repo_root(), "registry", "agents.yaml"),
    ]

    for path in search_paths:
        expanded = os.path.expanduser(path.strip())
        if expanded and os.path.isfile(expanded):
            with open(expanded, encoding="utf-8") as handle:
                _REGISTRY = yaml.safe_load(handle)
                return _REGISTRY

    _REGISTRY = {"agents": {}}
    return _REGISTRY


def get_agent_config(agent: str) -> dict[str, Any] | None:
    registry = _load_registry()
    return registry.get("agents", {}).get(agent)


def validate_agent_action(agent: str, action: str) -> tuple[bool, str]:
    cfg = get_agent_config(agent)
    if cfg is None:
        return False, f"unknown_agent:{agent}"
    allowed = set(cfg.get("allowed_actions") or [])
    if not allowed:
        return False, f"agent_has_no_actions:{agent}"
    if action not in allowed:
        return False, f"action_not_allowed:{agent}/{action}"
    return True, ""


def _http_execute(
    base_url: str,
    agent: str,
    action: str,
    params: dict[str, Any],
    correlation_id: str,
    actor_identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    import httpx

    normalized_base_url = base_url.rstrip("/")
    url = f"{normalized_base_url}/actions/{agent}/{action}"
    actor = _resolve_service_actor_identity(actor_identity)
    token = _build_service_bearer_token(actor, correlation_id)
    headers = {
        "Content-Type": "application/json",
        "X-Correlation-ID": correlation_id,
        "Authorization": f"Bearer {token}",
        "X-User-Email": actor["upn"],
        "X-Principal-Email": actor["upn"],
    }

    with httpx.Client(timeout=30.0) as client:
        try:
            response = client.post(url, json={"params": params}, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = ""
            try:
                payload = exc.response.json()
                detail = _normalize_text(payload.get("detail") or payload.get("error"))
            except Exception:
                detail = _normalize_text(exc.response.text)
            message = detail or f"HTTP {exc.response.status_code}"
            raise M365ExecutionError(
                exc.response.status_code,
                detail or f"http_{exc.response.status_code}",
                f"M365 service rejected {agent}/{action}: {message}",
            ) from exc
        except httpx.HTTPError as exc:
            raise M365ExecutionError(
                502,
                "service_http_error",
                f"M365 service HTTP call failed: {exc}",
            ) from exc
        return response.json()


def _stub_execute(
    agent: str,
    action: str,
    params: dict[str, Any],
    correlation_id: str,
) -> dict[str, Any]:
    return {
        "stub": True,
        "agent": agent,
        "action": action,
        "params": params,
        "correlation_id": correlation_id,
        "message": "Stub mode — action accepted but not executed against Graph API",
    }


def _is_stub_mode() -> bool:
    return os.getenv("GRAPH_STUB_MODE", "0").lower() in ("1", "true", "yes", "on")


def routing_snapshot() -> dict[str, Any]:
    service_url = _configured_service_url()
    return {
        "service_mode_configured": service_url is not None,
        "service_url": service_url,
        "selected_live_path": "http_service"
        if service_url is not None
        else ("stub" if _is_stub_mode() else "unavailable"),
        "direct_import_available": False,
        "direct_import_authority": "removed",
        "fail_closed_when_service_mode_configured": True,
    }


def execute_m365_action(
    agent: str,
    action: str,
    params: dict[str, Any] | None = None,
    correlation_id: str | None = None,
    actor_identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    params = params or {}
    correlation_id = correlation_id or str(uuid.uuid4())
    service_url = _configured_service_url()

    if service_url is not None:
        try:
            return _http_execute(
                service_url,
                agent,
                action,
                params,
                correlation_id,
                actor_identity,
            )
        except M365ExecutionError:
            raise
        except Exception as exc:
            raise M365ExecutionError(
                502,
                "service_mode_unavailable",
                f"Configured M365 service mode failed: {exc}",
            ) from exc

    if _is_stub_mode():
        return _stub_execute(agent, action, params, correlation_id)

    raise M365ExecutionError(
        503,
        "m365_executor_unavailable",
        "No configured M365 service URL. Direct import fallback has been removed.",
    )
