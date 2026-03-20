from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field
from smarthaus_common.config import AppConfig, has_selected_tenant
from smarthaus_common.errors import SmarthausError
from smarthaus_common.executor_routing import executor_route_for_action
from smarthaus_common.tenant_config import get_tenant_config
from smarthaus_graph.client import GraphClient

from provisioning_api import auth as authn
from provisioning_api.audit import log_event
from provisioning_api.m365_provision import provision_group_site, provision_teams_workspace
from provisioning_api.metrics import inc_sites_created, inc_teams_created
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/m365", tags=["m365"])
_SESSION_DEPENDENCY = Depends(authn.verify_microsoft_token)

_IDEMPOTENCY_COLLECTION = "m365_instruction_idempotency"
_SUPPORTED_ACTIONS = {
    "create_site",
    "create_team",
    "add_channel",
    "provision_service",
    "list_users",
    "list_teams",
    "list_sites",
    "get_user",
    "reset_user_password",
}
_MUTATING_ACTIONS = {
    "create_site",
    "create_team",
    "add_channel",
    "provision_service",
    "reset_user_password",
}


class M365InstructionRequest(BaseModel):
    action: str = Field(..., min_length=1)
    params: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None


class M365InstructionResponse(BaseModel):
    ok: bool
    result: dict[str, Any] | None = None
    error: str | None = None
    trace_id: str | None = None


def _allow_mutations() -> bool:
    return os.getenv("ALLOW_M365_MUTATIONS", "false").lower() in ("1", "true", "yes")


def _validate_caio_api_key(request: Request) -> bool:
    expected = os.getenv("CAIO_API_KEY")
    if not expected:
        return True
    provided = request.headers.get("X-CAIO-API-Key") or request.headers.get("X-CAIO-Token")
    return bool(provided and provided == expected)


def _request_hash(action: str, params: dict[str, Any]) -> str:
    payload = {"action": action, "params": params}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _get_idempotency_record(key: str) -> dict[str, Any] | None:
    store = JsonStore()
    for rec in store.list(_IDEMPOTENCY_COLLECTION):
        if rec.get("key") == key:
            return rec
    return None


def _store_idempotency_record(
    key: str, request_hash: str, response_payload: dict[str, Any]
) -> None:
    JsonStore().append(
        _IDEMPOTENCY_COLLECTION,
        {"key": key, "request_hash": request_hash, "response": response_payload},
    )


def _require_str(params: dict[str, Any], key: str) -> str:
    value = params.get(key)
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(status_code=400, detail=f"Missing or invalid '{key}'")
    return value.strip()


def _optional_str(params: dict[str, Any], key: str) -> str | None:
    value = params.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail=f"Invalid '{key}'")
    return value.strip()


def _normalize_str_list(params: dict[str, Any], key: str, default: list[str]) -> list[str]:
    value = params.get(key, default)
    if not isinstance(value, list):
        raise HTTPException(status_code=400, detail=f"'{key}' must be a list of strings")
    cleaned = [str(x).strip() for x in value if str(x).strip()]
    if not cleaned:
        return list(default)
    return cleaned


def _slugify_mail_nickname(value: str) -> str:
    cleaned = value.strip().lower()
    slug = re.sub(r"[^a-z0-9-]+", "-", cleaned)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if not slug:
        raise HTTPException(status_code=400, detail="Missing or invalid 'mail_nickname'")
    return slug


def _normalize_params(action: str, params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise HTTPException(status_code=400, detail="params must be an object")
    if action == "create_site":
        display_name = _optional_str(params, "display_name") or _optional_str(params, "site_name")
        if not display_name:
            raise HTTPException(status_code=400, detail="Missing or invalid 'display_name'")
        mail_nickname = _optional_str(params, "mail_nickname") or _optional_str(params, "url_slug")
        if not mail_nickname:
            mail_nickname = _slugify_mail_nickname(display_name)
        else:
            mail_nickname = _slugify_mail_nickname(mail_nickname)
        libraries = _normalize_str_list(params, "libraries", ["Documents"])
        description = _optional_str(params, "description")
        return {
            "display_name": display_name,
            "mail_nickname": mail_nickname,
            "libraries": libraries,
            "description": description,
        }
    if action == "create_team":
        mail_nickname = _optional_str(params, "mail_nickname")
        if not mail_nickname:
            team_name = _optional_str(params, "team_name")
            if team_name:
                mail_nickname = _slugify_mail_nickname(team_name)
        if not mail_nickname:
            raise HTTPException(status_code=400, detail="Missing or invalid 'mail_nickname'")
        mail_nickname = _slugify_mail_nickname(mail_nickname)
        channels = _normalize_str_list(params, "channels", ["General"])
        return {"mail_nickname": mail_nickname, "channels": channels}
    if action == "add_channel":
        mail_nickname = _optional_str(params, "mail_nickname")
        if not mail_nickname:
            team_name = _optional_str(params, "team_name")
            if team_name:
                mail_nickname = _slugify_mail_nickname(team_name)
        if not mail_nickname:
            raise HTTPException(status_code=400, detail="Missing or invalid 'mail_nickname'")
        mail_nickname = _slugify_mail_nickname(mail_nickname)
        channel_name = _require_str(params, "channel_name")
        description = _optional_str(params, "description")
        return {
            "mail_nickname": mail_nickname,
            "channel_name": channel_name,
            "description": description,
        }
    if action == "provision_service":
        key = _optional_str(params, "key") or _optional_str(params, "service_name")
        if not key:
            raise HTTPException(status_code=400, detail="Missing or invalid 'key'")
        return {"key": key}
    if action == "list_users":
        top = params.get("top")
        if top is not None:
            try:
                top = int(top)
                top = min(max(1, top), 999)
            except (TypeError, ValueError):
                top = 100
        else:
            top = 100
        select = (
            _optional_str(params, "select")
            or "id,displayName,userPrincipalName,mail,jobTitle,accountEnabled"
        )
        return {"top": top, "select": select}
    if action == "list_teams":
        top = params.get("top")
        if top is not None:
            try:
                top = min(max(1, int(top)), 999)
            except (TypeError, ValueError):
                top = 100
        else:
            top = 100
        return {"top": top}
    if action == "list_sites":
        top = params.get("top")
        if top is not None:
            try:
                top = min(max(1, int(top)), 999)
            except (TypeError, ValueError):
                top = 100
        else:
            top = 100
        return {"top": top}
    if action == "get_user":
        upn = (
            _optional_str(params, "userPrincipalName")
            or _optional_str(params, "user_id")
            or _optional_str(params, "id")
        )
        if not upn:
            raise HTTPException(
                status_code=400, detail="Missing 'userPrincipalName', 'user_id', or 'id'"
            )
        return {"user_id_or_upn": upn}
    if action == "reset_user_password":
        upn = (
            _optional_str(params, "userPrincipalName")
            or _optional_str(params, "user_id")
            or _optional_str(params, "id")
        )
        if not upn:
            raise HTTPException(
                status_code=400, detail="Missing 'userPrincipalName', 'user_id', or 'id'"
            )
        pwd = _optional_str(params, "temporary_password") or _optional_str(params, "password")
        if not pwd:
            raise HTTPException(
                status_code=400, detail="Missing 'temporary_password' or 'password'"
            )
        return {
            "user_id_or_upn": upn,
            "temporary_password": pwd,
            "force_change_next_sign_in": params.get("force_change_next_sign_in", True),
        }
    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


def _graph_client(action: str | None = None) -> GraphClient:
    if has_selected_tenant():
        tenant_cfg = get_tenant_config()
        if action:
            route_key = executor_route_for_action(None, action)
            if route_key and len(getattr(tenant_cfg, "executors", {}) or {}) > 1:
                executor_name = tenant_cfg.resolve_executor_name(
                    route_key,
                    fallback_keys=[route_key],
                )
                tenant_cfg = tenant_cfg.project_executor(executor_name)
        has_identity = bool(tenant_cfg.azure.tenant_id and tenant_cfg.azure.client_id)
        has_credential = bool(
            tenant_cfg.azure.client_secret or tenant_cfg.azure.client_certificate_path
        )
        if not has_identity:
            raise SmarthausError(
                "Graph not configured: set UCP_TENANT to a tenant with azure.tenant_id "
                "and azure.client_id"
            )
        if tenant_cfg.auth.mode != "delegated" and not has_credential:
            raise SmarthausError(
                "Graph not configured: selected tenant is missing app-only credentials "
                "(azure.client_secret or azure.client_certificate_path)"
            )
        return GraphClient(tenant_config=tenant_cfg)

    config = AppConfig()
    if not (config.graph.tenant_id and config.graph.client_id and config.graph.client_secret):
        raise SmarthausError(
            "Graph not configured: either select UCP_TENANT or set "
            "GRAPH_TENANT_ID, GRAPH_CLIENT_ID, and GRAPH_CLIENT_SECRET"
        )
    return GraphClient(config=config)


def _execute_action(action: str, params: dict[str, Any]) -> dict[str, Any]:
    if action == "create_site":
        result = provision_group_site(
            display_name=params["display_name"],
            mail_nickname=params["mail_nickname"],
            libraries=params["libraries"],
            description=params.get("description"),
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        return result
    if action == "create_team":
        result = provision_teams_workspace(params["mail_nickname"], params["channels"])
        inc_teams_created()
        return result
    if action == "add_channel":
        result = provision_teams_workspace(params["mail_nickname"], [params["channel_name"]])
        if params.get("description"):
            result["description"] = params["description"]
        return {"team": result, "channel": params["channel_name"]}
    if action == "provision_service":
        return provision_service(params["key"])
    if action == "list_users":
        client = _graph_client(action)
        data = client.list_users(top=params["top"], select=params.get("select"))
        return {"users": data.get("value", []), "count": len(data.get("value", []))}
    if action == "list_teams":
        client = _graph_client(action)
        data = client.list_teams()
        value = data.get("value", [])[: params.get("top", 100)]
        return {"teams": value, "count": len(value)}
    if action == "list_sites":
        client = _graph_client(action)
        data = client.list_sites(top=params["top"])
        value = data.get("value", [])
        return {"sites": value, "count": len(value)}
    if action == "get_user":
        client = _graph_client(action)
        user = client.get_user(params["user_id_or_upn"])
        return {"user": user}
    if action == "reset_user_password":
        client = _graph_client(action)
        return client.reset_user_password(
            params["user_id_or_upn"],
            params["temporary_password"],
            force_change_next_sign_in=params.get("force_change_next_sign_in", True),
        )
    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


def _audit_instruction(
    action: str,
    params: dict[str, Any],
    response_payload: dict[str, Any],
    user_info: dict[str, Any] | None,
    *,
    blocked: bool = False,
    idempotent_replay: bool = False,
) -> None:
    log_event(
        "m365_instruction",
        {
            "action": action,
            "params": params,
            "ok": response_payload.get("ok"),
            "result": response_payload.get("result"),
            "error": response_payload.get("error"),
            "trace_id": response_payload.get("trace_id"),
            "blocked": blocked,
            "idempotent_replay": idempotent_replay,
        },
        user_info=user_info or {},
    )


def execute_instruction_contract(
    *,
    action: str,
    params_payload: dict[str, Any],
    trace_id: str,
    user_info: dict[str, Any] | None = None,
    idempotency_key: str | None = None,
    require_user_context: bool = False,
) -> dict[str, Any]:
    """Execute an M365 instruction with the canonical action/params contract."""
    normalized_action = action.strip().lower()
    raw_params = params_payload if isinstance(params_payload, dict) else {}

    if require_user_context and not user_info:
        payload = M365InstructionResponse(
            ok=False,
            error="auth_required",
            trace_id=trace_id,
        ).model_dump()
        _audit_instruction(
            normalized_action or "unknown", raw_params, payload, user_info, blocked=True
        )
        return payload

    if normalized_action not in _SUPPORTED_ACTIONS:
        payload = M365InstructionResponse(
            ok=False,
            error=f"Unknown action: {normalized_action}",
            trace_id=trace_id,
        ).model_dump()
        _audit_instruction(normalized_action or "unknown", raw_params, payload, user_info)
        return payload

    try:
        params = _normalize_params(normalized_action, raw_params)
    except HTTPException as exc:
        payload = M365InstructionResponse(
            ok=False,
            error=str(exc.detail),
            trace_id=trace_id,
        ).model_dump()
        _audit_instruction(normalized_action, raw_params, payload, user_info)
        return payload

    idem_key = (idempotency_key or "").strip() or None
    request_hash = _request_hash(normalized_action, params)
    if idem_key:
        record = _get_idempotency_record(idem_key)
        if record:
            if record.get("request_hash") != request_hash:
                payload = M365InstructionResponse(
                    ok=False,
                    error="idempotency_key_conflict",
                    trace_id=trace_id,
                ).model_dump()
                _audit_instruction(normalized_action, params, payload, user_info)
                return payload
            stored = record.get("response") or {}
            _audit_instruction(normalized_action, params, stored, user_info, idempotent_replay=True)
            return stored

    if normalized_action in _MUTATING_ACTIONS and not _allow_mutations():
        blocked = M365InstructionResponse(
            ok=False,
            error="m365_mutations_disabled",
            trace_id=trace_id,
        ).model_dump()
        _audit_instruction(normalized_action, params, blocked, user_info, blocked=True)
        if idem_key:
            _store_idempotency_record(idem_key, request_hash, blocked)
        return blocked

    try:
        result = _execute_action(normalized_action, params)
        payload = M365InstructionResponse(ok=True, result=result, trace_id=trace_id).model_dump()
    except HTTPException as exc:
        payload = M365InstructionResponse(
            ok=False, error=str(exc.detail), trace_id=trace_id
        ).model_dump()
    except SmarthausError as exc:
        payload = M365InstructionResponse(ok=False, error=str(exc), trace_id=trace_id).model_dump()
    except Exception as exc:  # noqa: BLE001
        payload = M365InstructionResponse(ok=False, error=str(exc), trace_id=trace_id).model_dump()

    _audit_instruction(normalized_action, params, payload, user_info)
    if idem_key:
        _store_idempotency_record(idem_key, request_hash, payload)
    return payload


@router.post("/instruction", response_model=M365InstructionResponse)
async def handle_instruction(
    body: M365InstructionRequest,
    request: Request,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    session: dict[str, Any] = _SESSION_DEPENDENCY,
) -> M365InstructionResponse:
    trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response.headers["X-Request-ID"] = trace_id

    action = body.action.strip().lower()
    user_info = session.get("user_info") if isinstance(session, dict) else None
    if not _validate_caio_api_key(request):
        payload = M365InstructionResponse(
            ok=False,
            error="invalid_caio_api_key",
            trace_id=trace_id,
        ).model_dump()
        response.status_code = 401
        _audit_instruction(action or "unknown", body.params or {}, payload, user_info, blocked=True)
        return payload

    payload = execute_instruction_contract(
        action=action,
        params_payload=body.params or {},
        trace_id=trace_id,
        user_info=user_info,
        idempotency_key=idempotency_key or body.idempotency_key,
    )
    trace = payload.get("trace_id")
    if isinstance(trace, str) and trace:
        response.headers["X-Request-ID"] = trace
    return payload


# ---------- Instruction schema and agents (for dashboard and CAIO) ----------

INSTRUCTION_ACTIONS_SCHEMA = [
    {
        "action": "create_site",
        "description": "Create a SharePoint site with group",
        "params": ["display_name", "mail_nickname?", "libraries?", "description?"],
        "mutating": True,
    },
    {
        "action": "create_team",
        "description": "Create a Teams workspace",
        "params": ["mail_nickname", "channels?"],
        "mutating": True,
    },
    {
        "action": "add_channel",
        "description": "Add a channel to a team",
        "params": ["mail_nickname", "channel_name", "description?"],
        "mutating": True,
    },
    {
        "action": "provision_service",
        "description": "Provision a service from config",
        "params": ["key"],
        "mutating": True,
    },
    {
        "action": "list_users",
        "description": "List M365 users",
        "params": ["top?", "select?"],
        "mutating": False,
    },
    {
        "action": "list_teams",
        "description": "List Teams workspaces",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "list_sites",
        "description": "List SharePoint site collections",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "get_user",
        "description": "Get a single user by id or UPN",
        "params": ["userPrincipalName|user_id|id"],
        "mutating": False,
    },
    {
        "action": "reset_user_password",
        "description": "Reset user password (temporary); force change at next sign-in",
        "params": [
            "userPrincipalName|user_id",
            "temporary_password|password",
            "force_change_next_sign_in?",
        ],
        "mutating": True,
    },
]


@router.get("/actions", response_model=list)
def list_instruction_actions() -> list[dict[str, Any]]:
    """Return supported instruction actions for dashboard and CAIO."""
    return INSTRUCTION_ACTIONS_SCHEMA


@router.get("/agents", response_model=dict)
def list_agents() -> dict[str, Any]:
    """Return agent registry (agents.yaml) for dashboard."""
    import yaml

    registry_path = Path(os.getenv("REGISTRY_FILE", "registry/agents.yaml"))
    if not registry_path.is_absolute():
        registry_path = Path.cwd() / registry_path
    if not registry_path.exists():
        return {"agents": {}, "error": "registry_not_found"}
    with open(registry_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {
        "agents": data.get("agents", {}),
        "version": data.get("version"),
        "metadata": data.get("metadata"),
    }


def _m365_graph_status() -> str:
    try:
        client = _graph_client()
        client.get_organization()
        return "ok"
    except (SmarthausError, HTTPException, Exception):
        return "not_configured_or_unreachable"


@router.get("/status", response_model=dict)
def m365_status() -> dict[str, Any]:
    """Status for dashboard: Graph connectivity and instruction capabilities."""
    return {
        "graph": _m365_graph_status(),
        "instruction_actions_count": len(_SUPPORTED_ACTIONS),
        "mutations_allowed": _allow_mutations(),
    }


@router.post("/provision/tai")
def provision_tai() -> dict:
    try:
        result = provision_group_site(
            display_name="TAI Research Hub",
            mail_nickname="tai-research",
            description="TAI research collaboration site",
            libraries=[
                "Research Papers",
                "Holographic Memory",
                "AI Orchestration",
                "Performance Metrics",
                "Project Management",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_tai", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/lattice")
def provision_lattice() -> dict:
    try:
        result = provision_group_site(
            display_name="LATTICE Research Hub",
            mail_nickname="lattice-research",
            description="LATTICE research collaboration site",
            libraries=[
                "Architecture Documentation",
                "AIOS Development",
                "LQL Language",
                "LEF Execution",
                "Mathematical Proofs",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_lattice", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/business")
def provision_business() -> dict:
    try:
        result = provision_group_site(
            display_name="SmartHaus Group Business Hub",
            mail_nickname="business-hub",
            description="Business operations hub",
            libraries=[
                "Website Updates",
                "Business Development",
                "Client Projects",
                "Strategic Planning",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_business", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/teams/tai")
def create_tai_team() -> dict:
    try:
        channels = [
            "General",
            "Holographic Memory",
            "AI Orchestration",
            "Performance Metrics",
            "Research Updates",
        ]
        result = provision_teams_workspace("tai-research", channels)
        inc_teams_created()
        log_event("provision_team_tai", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/teams/lattice")
def create_lattice_team() -> dict:
    try:
        channels = [
            "General",
            "AIOS Development",
            "LQL Language",
            "LEF Execution",
            "Architecture Updates",
        ]
        result = provision_teams_workspace("lattice-research", channels)
        inc_teams_created()
        log_event("provision_team_lattice", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/teams/business")
def create_business_team() -> dict:
    try:
        channels = [
            "General",
            "Website Development",
            "Business Development",
            "Client Projects",
            "Strategic Planning",
        ]
        result = provision_teams_workspace("business-hub", channels)
        inc_teams_created()
        log_event("provision_team_business", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/teams/advisory-services")
def create_advisory_services_team() -> dict:
    try:
        channels = [
            "General",
            "advisory-services",  # All advisory service notifications
            "risk-management",  # Risk assessment alerts
            "aidf-certification",  # Certification requests
            "project-management",  # Project status updates
            "client-intake",  # New client intake tracking
            "governance-updates",  # AIDF governance updates
        ]
        result = provision_teams_workspace("advisory-services", channels)
        inc_teams_created()
        log_event("provision_team_advisory_services", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/service/{key}")
def provision_service(key: str) -> dict:
    cfg_path = Path("config/services.json")
    if not cfg_path.exists():
        raise HTTPException(status_code=500, detail="Missing config/services.json")
    try:
        cfg = json.loads(cfg_path.read_text())
        svc = next((s for s in cfg.get("services", []) if s.get("key") == key), None)
        if not svc:
            raise HTTPException(status_code=404, detail=f"Unknown service: {key}")
        site = provision_group_site(
            display_name=svc.get("display_name"),
            mail_nickname=svc.get("mail_nickname"),
            libraries=["Documents"],
            description=f"Service workspace for {svc.get('display_name')}",
        )
        inc_sites_created(1 if site.get("group_created") else 0)
        team = provision_teams_workspace(svc.get("mail_nickname"), svc.get("channels", []))
        inc_teams_created()
        res = {"status": "ok", "site": site, "team": team}
        log_event(f"provision_service_{key}", res)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
