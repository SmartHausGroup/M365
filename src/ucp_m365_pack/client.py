"""UCP-facing M365 pack client.

This module is bundled into the marketplace artifact under
`ucp_m365_pack/` and runs from the installed pack root. It must not read
M365 source-repo or sibling-repo paths at runtime: the registry lives next
to this file inside the installed pack, and the live path is the local
standalone Microsoft Graph runtime spawned by UCP from the same artifact.

Plan reference: plan:m365-standalone-graph-runtime-integration-pack-fix:R2
"""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any

# jwt and yaml are imported lazily inside the functions that use them so the
# UCP-facing client (and the HTTP runtime invoke path) can import without
# requiring PyJWT or PyYAML at module load. The dependency contract for the
# pack is declared in pack_dependencies.json.

try:
    _MODULE_DIR = os.path.dirname(__file__)
except NameError:
    _MODULE_DIR = os.getcwd()

ENV_M365_RUNTIME_URL = "M365_RUNTIME_URL"
ENV_M365_RUNTIME_URL_SMARTHAUS = "SMARTHAUS_M365_RUNTIME_URL"
ENV_M365_OPS_ADAPTER_URL = "M365_OPS_ADAPTER_URL"
ENV_M365_OPS_ADAPTER_URL_SMARTHAUS = "SMARTHAUS_M365_OPS_ADAPTER_URL"
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


# ---------------------------------------------------------------------------
# Legacy-action -> standalone-runtime action ID alias table.
#
# F4 fix: existing M365 agents in registry/agents.yaml advertise allowed
# actions named like ``users.read``, ``sites.root``, ``directory.org``,
# ``groups.read``, ``teams.read``, ``mail.health``, ``calendar.health``, and
# ``servicehealth.read``. The new standalone Graph runtime registry uses
# ``graph.*`` IDs. UCP must be able to call legacy IDs and have them
# dispatched onto the runtime registry deterministically. Anything not in
# this map is forwarded as-is (and the runtime fences unknown IDs with
# mutation_fence).
# ---------------------------------------------------------------------------
LEGACY_ACTION_TO_RUNTIME_ACTION: dict[str, str] = {
    "directory.org": "graph.org_profile",
    "directory.org_profile": "graph.org_profile",
    "users.read": "graph.users.list",
    "users.list": "graph.users.list",
    "users.read_self": "graph.me",
    "me.read": "graph.me",
    "me": "graph.me",
    "groups.read": "graph.groups.list",
    "groups.list": "graph.groups.list",
    "sites.root": "graph.sites.root",
    "sites.search": "graph.sites.search",
    "sites.read": "graph.sites.root",
    "drives.list": "graph.drives.list",
    "drives.read": "graph.drives.list",
    "teams.read": "graph.teams.list",
    "teams.list": "graph.teams.list",
    "mail.health": "graph.mail.health",
    "mail.read_health": "graph.mail.health",
    "calendar.health": "graph.calendar.health",
    "calendar.read_health": "graph.calendar.health",
    "servicehealth.read": "graph.servicehealth",
    "service_health.read": "graph.servicehealth",
    # plan:m365-cps-trkB-p1-sharepoint-reads:T2 / L103.L_ALIASES_RESOLVE
    "sites.list": "graph.sites.search",
    "sites.get": "graph.sites.get",
    "lists.list": "graph.lists.list",
    "lists.get": "graph.lists.get",
    "lists.items": "graph.lists.items",
    "files.list": "graph.drives.children",
    # plan:m365-cps-trkB-p2-calendar-reads:T2 / L104.L_ALIASES_RESOLVE
    "calendar.list": "graph.calendar.list",
    "calendar.get": "graph.calendar.get",
    "events.list": "graph.events.list",
    "availability.check": "graph.calendar.availability",
    # plan:m365-cps-trkB-p3-mail-reads:T2 / L105.L_ALIASES_RESOLVE
    "mail.list": "graph.mail.list",
    "mail.read": "graph.mail.message_get",
    "mail.attachments": "graph.mail.attachments",
    "mail.folders": "graph.mail.health",
    # plan:m365-cps-trkB-p4-health-and-reports:T2 / L106.L_ALIASES_RESOLVE
    "health.overview": "graph.health.overview",
    "health.issues": "graph.health.issues",
    "health.messages": "graph.health.messages",
    "reports.users_active": "graph.reports.users_active",
    "reports.email_activity": "graph.reports.email_activity",
    "reports.teams_activity": "graph.reports.teams_activity",
    "reports.sharepoint_usage": "graph.reports.sharepoint_usage",
    "reports.onedrive_usage": "graph.reports.onedrive_usage",
    # plan:m365-cps-trkB-p5-directory-and-teams:T2 / L107.L_ALIASES_RESOLVE
    "directory.domains": "graph.directory.domains",
    "directory.roles": "graph.directory.roles",
    "teams.get": "graph.teams.get",
    "channels.list": "graph.channels.list",
    "channels.get": "graph.channels.get",
}


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
    if isinstance(value, list | tuple | set):
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
    try:
        import jwt  # PyJWT only required for the legacy ops-adapter shim path.
    except ImportError as exc:
        raise M365ExecutionError(
            500,
            "dependency_missing",
            "PyJWT is required for the legacy ops-adapter service-token path: install PyJWT.",
        ) from exc
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


def _installed_pack_root() -> Path:
    """Resolve the installed pack root.

    Inside the marketplace artifact the layout is::

        <pack-root>/ucp_m365_pack/client.py
        <pack-root>/registry/agents.yaml
        <pack-root>/setup_schema.json
        <pack-root>/m365_runtime/...

    This function returns ``<pack-root>`` from the live module location.
    Forbidden source-repo and sibling-repo env names are listed in
    ``m365_runtime/_forbidden_tokens.py`` and are never read from here.
    """
    return Path(_MODULE_DIR).resolve().parent


def _installed_registry_path() -> Path:
    return _installed_pack_root() / "registry" / "agents.yaml"


def _configured_service_url() -> str | None:
    configured_url = _env_value(ENV_M365_OPS_ADAPTER_URL, ENV_M365_OPS_ADAPTER_URL_SMARTHAUS)
    if configured_url is None:
        return None
    stripped = configured_url.strip()
    return stripped or None


def _configured_runtime_url() -> str | None:
    """Standalone Graph runtime URL.

    When set, the pack calls the locally-installed `m365_runtime` service
    bundled in the installed artifact. This is the truthful path for the
    real Integration Pack and the only path that does not require any
    legacy ops-adapter service.
    """
    configured_url = _env_value(ENV_M365_RUNTIME_URL, ENV_M365_RUNTIME_URL_SMARTHAUS)
    if configured_url is None:
        return None
    stripped = configured_url.strip()
    return stripped or None


def _load_registry() -> dict[str, Any]:
    """Load the agent registry from the installed pack root only.

    F1 fix: this used to honor a registry-path env override and walk
    parent directories looking for the source repo's registry. The
    installed pack must not depend on the source repo, so we now read only
    from the artifact's own ``registry/agents.yaml`` next to this file.
    """
    global _REGISTRY
    if _REGISTRY is not None:
        return _REGISTRY

    registry_path = _installed_registry_path()
    if registry_path.is_file():
        try:
            import yaml  # PyYAML only required when the in-pack agents registry is read.
        except ImportError as exc:
            raise M365ExecutionError(
                500,
                "dependency_missing",
                "PyYAML is required for in-pack registry parsing: install PyYAML.",
            ) from exc
        with registry_path.open(encoding="utf-8") as handle:
            _REGISTRY = yaml.safe_load(handle) or {"agents": {}}
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


def map_legacy_action_to_runtime(action: str) -> str:
    """F4: Project a legacy action name onto the runtime ``graph.*`` ID space.

    Already-runtime IDs (``graph.*``) pass through. Unknown legacy IDs
    pass through unchanged so the runtime can fence them with
    ``mutation_fence`` rather than the client silently rewriting them.
    """
    text = (action or "").strip()
    if not text:
        return text
    if text.startswith("graph."):
        return text
    return LEGACY_ACTION_TO_RUNTIME_ACTION.get(text, text)


def _http_runtime_invoke(
    runtime_url: str,
    action_id: str,
    params: dict[str, Any],
    correlation_id: str,
    actor_identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call the standalone M365 runtime at /v1/actions/{action_id}/invoke."""
    import httpx

    actor = _resolve_service_actor_identity(actor_identity)
    base = runtime_url.rstrip("/")
    url = f"{base}/v1/actions/{action_id}/invoke"
    headers = {
        "Content-Type": "application/json",
        "X-Correlation-ID": correlation_id,
        "X-Principal-Email": actor["upn"],
    }
    body = {"actor": actor["upn"], "params": params}
    with httpx.Client(timeout=30.0) as client:
        try:
            response = client.post(url, json=body, headers=headers)
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
                f"M365 runtime rejected {action_id}: {message}",
            ) from exc
        except httpx.HTTPError as exc:
            raise M365ExecutionError(
                502,
                "runtime_http_error",
                f"M365 runtime HTTP call failed: {exc}",
            ) from exc
        return response.json()


def _http_execute(
    base_url: str,
    agent: str,
    action: str,
    params: dict[str, Any],
    correlation_id: str,
    actor_identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Legacy ops-adapter call. Kept for backwards compatibility only."""
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
        "message": "Stub mode - action accepted but not executed against Graph API",
    }


def _is_stub_mode() -> bool:
    return os.getenv("GRAPH_STUB_MODE", "0").lower() in ("1", "true", "yes", "on")


def routing_snapshot() -> dict[str, Any]:
    service_url = _configured_service_url()
    runtime_url = _configured_runtime_url()
    if runtime_url is not None:
        selected = "http_runtime"
    elif service_url is not None:
        selected = "http_service"
    elif _is_stub_mode():
        selected = "stub"
    else:
        selected = "unavailable"
    return {
        "runtime_mode_configured": runtime_url is not None,
        "runtime_url": runtime_url,
        "service_mode_configured": service_url is not None,
        "service_url": service_url,
        "selected_live_path": selected,
        "direct_import_available": False,
        "direct_import_authority": "removed",
        "fail_closed_when_no_path_configured": True,
        "installed_pack_root": str(_installed_pack_root()),
        "registry_path": str(_installed_registry_path()),
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

    runtime_url = _configured_runtime_url()
    if runtime_url is not None:
        runtime_action = map_legacy_action_to_runtime(
            action if "." in action else f"{agent}.{action}"
        )
        try:
            return _http_runtime_invoke(
                runtime_url, runtime_action, params, correlation_id, actor_identity
            )
        except M365ExecutionError:
            raise
        except Exception as exc:
            raise M365ExecutionError(
                502,
                "runtime_mode_unavailable",
                f"Configured M365 runtime mode failed: {exc}",
            ) from exc

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
        "No configured M365 runtime or service URL. Set M365_RUNTIME_URL to call the standalone Graph runtime bundled in the installed pack.",
    )
