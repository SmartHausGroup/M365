from __future__ import annotations

import os
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Annotated, Any

import httpx as _httpx
import jwt
import yaml
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPBearer
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from smarthaus_common.approval_risk import resolve_action_approval_risk
from smarthaus_common.config import has_selected_tenant
from smarthaus_common.permission_enforcer import (
    check_user_permission,
    get_confirmation_override,
    get_user_tier_info,
)
from smarthaus_common.persona_task_queue import (
    build_persona_state,
    create_persona_task,
    list_persona_tasks,
    update_persona_task,
)
from smarthaus_common.tenant_config import get_tenant_config
from starlette.responses import Response

from .actions import (
    GraphAPIError,
    build_executor_identity,
    execute,
    resolve_executor_name_for_action,
)
from .approvals import ApprovalsStore, GraphApprovalsStore
from .audit import Auditor
from .models import ActionRequest, ActionResponse
from .personas import (
    load_persona_registry,
    resolve_humanized_delegation_request,
    resolve_persona_target,
)
from .policies import OPAClient
from .rate_limit import RateLimiter

app = FastAPI(title="SMARTHAUS Ops Adapter", version="0.1.0")
security = HTTPBearer(auto_error=False)
SecurityDependency = Annotated[Any | None, Depends(security)]

# Prometheus metrics
REQ_COUNT = Counter("ops_requests_total", "Total requests", ["agent", "action", "outcome"])
REQ_LATENCY = Histogram("ops_request_latency_seconds", "Request latency", ["agent", "action"])


def load_registry() -> dict[str, Any]:
    path = os.getenv("REGISTRY_FILE", "./registry/agents.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


REGISTRY = load_registry()
PERSONAS = load_persona_registry(REGISTRY)
OPA = OPAClient(base_url=os.getenv("OPA_URL"))
AUDITOR = Auditor(log_dir=os.getenv("LOG_DIR", "./logs"))
APPROVALS = ApprovalsStore(REGISTRY, PERSONAS)
RATE = RateLimiter(default_rps=5.0, burst=10)

_JWKS_CACHE: dict[str, Any] = {}
_JWKS_BY_URL: dict[str, Any] = {}
RequestHandler = Callable[[Request], Awaitable[Response]]


def _truthy_env(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


def _actor_header_fallback_enabled() -> bool:
    """Non-enterprise override for legacy header-only actor identity."""
    return _truthy_env("M365_ACTOR_HEADER_FALLBACK", "0")


def _jwt_required_for_actions() -> bool:
    """Require JWT-backed actor identity on governed action paths by default."""
    raw = os.getenv("JWT_REQUIRED")
    if raw is None:
        return not _actor_header_fallback_enabled()
    return _truthy_env("JWT_REQUIRED", "0")


def _auth_error_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def _get_jwks(tenant_id: str) -> dict[str, Any]:
    if tenant_id in _JWKS_CACHE:
        return _JWKS_CACHE[tenant_id]
    # Fetch OpenID config then JWKS
    oidc = f"https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration"
    async with _httpx.AsyncClient(timeout=10.0) as client:
        cfg = (await client.get(oidc)).json()
        jwks_uri = cfg.get("jwks_uri")
        jwks = (await client.get(jwks_uri)).json()
        _JWKS_CACHE[tenant_id] = jwks
        return jwks


async def _get_jwks_from_url(jwks_url: str) -> dict[str, Any]:
    if jwks_url in _JWKS_BY_URL:
        return _JWKS_BY_URL[jwks_url]
    async with _httpx.AsyncClient(timeout=10.0) as client:
        jwks = (await client.get(jwks_url)).json()
        _JWKS_BY_URL[jwks_url] = jwks
        return jwks


async def _discover_jwks() -> dict | None:
    # Priority: explicit JWKS_URL, then JWT_ISSUER discovery, then Azure tenant
    jwks_url = os.getenv("JWKS_URL")
    if jwks_url:
        try:
            return await _get_jwks_from_url(jwks_url)
        except Exception:
            return None
    issuer = os.getenv("JWT_ISSUER")
    if issuer:
        try:
            well_known = issuer.rstrip("/") + "/.well-known/openid-configuration"
            async with _httpx.AsyncClient(timeout=10.0) as client:
                cfg = (await client.get(well_known)).json()
                return await _get_jwks_from_url(cfg.get("jwks_uri"))
        except Exception:
            return None
    tenant = os.getenv("AZURE_TENANT_ID")
    if tenant:
        try:
            return await _get_jwks(tenant)
        except Exception:
            return None
    return None


@app.middleware("http")
async def add_correlation_id(request: Request, call_next: RequestHandler) -> Response:
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.middleware("http")
async def jwt_validation_middleware(request: Request, call_next: RequestHandler) -> Response:
    # Governed action execution requires JWT-backed actor identity by default.
    require = _jwt_required_for_actions()
    path = request.url.path or ""
    if not (require and path.startswith("/actions/")):
        return await call_next(request)

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return _auth_error_response(401, "missing_bearer_token")
    token = auth.split(" ", 1)[1].strip()

    # Accept HS256 with shared secret in dev, or RS* via JWKS in prod
    hs_secret = os.getenv("JWT_HS256_SECRET")
    audience = os.getenv("JWT_AUDIENCE")
    issuer = os.getenv("JWT_ISSUER")

    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError:
        return _auth_error_response(401, "invalid_token_header")

    alg = header.get("alg", "RS256")
    options = {"verify_exp": True}
    if audience:
        options["verify_aud"] = True
    else:
        options["verify_aud"] = False

    try:
        if alg.startswith("HS") and hs_secret:
            claims = jwt.decode(
                token,
                key=hs_secret,
                algorithms=[alg],
                audience=audience if audience else None,
                issuer=issuer if issuer else None,
                options=options,
            )
        else:
            jwks = await _discover_jwks()
            if not jwks:
                return _auth_error_response(500, "jwks_unavailable")
            kid = header.get("kid")
            key = next((k for k in jwks.get("keys", []) if (not kid or k.get("kid") == kid)), None)
            if not key:
                return _auth_error_response(401, "jwks_key_not_found")
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            claims = jwt.decode(
                token,
                key=public_key,
                algorithms=[alg],
                audience=audience if audience else None,
                issuer=issuer if issuer else None,
                options=options,
            )
    except jwt.ExpiredSignatureError:
        return _auth_error_response(401, "token_expired")
    except jwt.PyJWTError as e:
        return _auth_error_response(401, f"invalid_token:{e}")

    # Stash identity for auditing
    request.state.principal = {
        "sub": claims.get("sub"),
        "oid": claims.get("oid"),
        "upn": claims.get("preferred_username") or claims.get("upn") or claims.get("email"),
        "iss": claims.get("iss"),
        "aud": claims.get("aud"),
        "scp": claims.get("scp") or claims.get("scope"),
        "groups": claims.get("groups") if isinstance(claims.get("groups"), list) else [],
    }
    return await call_next(request)


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": app.version,
    }


@app.get("/personas/resolve")
async def resolve_persona(query: str = Query(..., min_length=1)) -> dict[str, Any]:
    try:
        return resolve_humanized_delegation_request(query, PERSONAS)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _resolve_task_queue_target(agent_target: str) -> tuple[str, dict[str, Any]]:
    canonical_agent, persona = _resolve_persona_agent(agent_target)
    if str(persona.get("status") or "") == "inactive":
        raise HTTPException(status_code=403, detail=f"persona_inactive:{canonical_agent}")
    return canonical_agent, persona


@app.get("/personas/{agent_target}/state")
async def get_persona_state(agent_target: str) -> dict[str, Any]:
    canonical_agent, persona = _resolve_task_queue_target(agent_target)
    state = build_persona_state(canonical_agent)
    state["persona"] = persona
    return state


@app.get("/personas/{agent_target}/tasks")
async def get_persona_tasks(agent_target: str) -> dict[str, Any]:
    canonical_agent, persona = _resolve_task_queue_target(agent_target)
    return {
        "canonical_agent": canonical_agent,
        "persona": persona,
        "tasks": list_persona_tasks(canonical_agent),
    }


@app.post("/personas/{agent_target}/tasks")
async def queue_persona_task(
    agent_target: str, body: dict[str, Any], request: Request
) -> dict[str, Any]:
    canonical_agent, persona = _resolve_task_queue_target(agent_target)
    payload = dict(body)
    payload.setdefault("created_by", _resolve_user_identity(request))
    try:
        task = create_persona_task(canonical_agent, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "status": "accepted",
        "canonical_agent": canonical_agent,
        "persona": persona,
        "task": task,
    }


@app.put("/personas/{agent_target}/tasks/{task_id}")
async def set_persona_task_state(
    agent_target: str, task_id: str, body: dict[str, Any], request: Request
) -> dict[str, Any]:
    canonical_agent, persona = _resolve_task_queue_target(agent_target)
    payload = dict(body)
    payload.setdefault("updated_by", _resolve_user_identity(request))
    try:
        task = update_persona_task(canonical_agent, task_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok", "canonical_agent": canonical_agent, "persona": persona, "task": task}


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _validate_agent_action(agent: str, action: str) -> bool:
    agents = REGISTRY.get("agents", {})
    if agent not in agents:
        return False
    allowed = set(agents[agent].get("allowed_actions", []) or [])
    return action in allowed


def _resolve_persona_agent(agent_target: str) -> tuple[str, dict[str, Any]]:
    return resolve_persona_target(agent_target, PERSONAS)


def _resolve_user_identity(request: Request) -> str:
    principal = getattr(request.state, "principal", {}) or {}
    for candidate in (principal.get("upn"),):
        if candidate:
            return str(candidate).strip().lower()
    if _actor_header_fallback_enabled():
        for candidate in (
            request.headers.get("X-User-Email"),
            request.headers.get("X-Principal-Email"),
        ):
            if candidate:
                return str(candidate).strip().lower()
    raise HTTPException(403, "entra_actor_identity_required")


def _resolve_actor_groups(request: Request) -> list[str]:
    principal = getattr(request.state, "principal", {}) or {}
    groups = principal.get("groups") or []
    if isinstance(groups, list):
        return [str(group) for group in groups if group]
    if groups:
        return [str(groups)]
    return []


def _require_tenant_context() -> Any:
    if not has_selected_tenant():
        raise HTTPException(403, "tenant_selection_missing")
    try:
        return get_tenant_config()
    except Exception as exc:
        raise HTTPException(403, f"tenant_config_unavailable:{type(exc).__name__}") from exc


def _approval_rule(agent: str, action: str) -> dict[str, Any] | None:
    for rule in REGISTRY.get("agents", {}).get(agent, {}).get("approval_rules", []) or []:
        if rule.get("action") == action:
            return rule
    return None


@app.get("/approvals/{approval_id}")
async def get_approval(approval_id: str) -> dict[str, Any]:
    rec = APPROVALS.get(approval_id)
    if not rec:
        raise HTTPException(404, "approval_not_found")
    return rec


class ApprovalUpdateBody(ActionRequest):
    pass


@app.post("/approvals/{approval_id}/approve")
async def approve(
    approval_id: str,
    request: Request,
    body: ApprovalUpdateBody | None = None,
    ts: str | None = Query(default=None),
    sig: str | None = Query(default=None),
) -> dict[str, str]:
    # Verify Teams HMAC if configured
    if hasattr(APPROVALS, "verify_signature") and not APPROVALS.verify_signature(
        approval_id, "approve", ts, sig
    ):
        raise HTTPException(401, "invalid_signature")
    ok = APPROVALS.set_status(
        approval_id, "approved", (body.params.get("reason") if body else None)
    )
    if not ok:
        raise HTTPException(404, "approval_not_found")
    approver = request.headers.get("X-Teams-User", None)
    await AUDITOR.log(
        "approved",
        "-",
        "-",
        {"approval_id": approval_id, "approver": approver},
        request.state.correlation_id,
    )
    return {"status": "approved", "id": approval_id}


@app.post("/approvals/{approval_id}/deny")
async def deny(
    approval_id: str,
    request: Request,
    body: ApprovalUpdateBody | None = None,
    ts: str | None = Query(default=None),
    sig: str | None = Query(default=None),
) -> dict[str, str]:
    if hasattr(APPROVALS, "verify_signature") and not APPROVALS.verify_signature(
        approval_id, "deny", ts, sig
    ):
        raise HTTPException(401, "invalid_signature")
    ok = APPROVALS.set_status(approval_id, "denied", (body.params.get("reason") if body else None))
    if not ok:
        raise HTTPException(404, "approval_not_found")
    approver = request.headers.get("X-Teams-User", None)
    await AUDITOR.log(
        "denied",
        "-",
        "-",
        {
            "approval_id": approval_id,
            "reason": (body.params.get("reason") if body else None),
            "approver": approver,
        },
        request.state.correlation_id,
    )
    return {"status": "denied", "id": approval_id}


class BulkApprovalBody(ActionRequest):
    pass


@app.post("/approvals/bulk")
async def approvals_bulk(request: Request, body: BulkApprovalBody) -> dict[str, Any]:
    action = body.params.get("action")
    ids = body.params.get("ids") or []
    reason = body.params.get("reason")
    if action not in ("approve", "deny"):
        raise HTTPException(400, "invalid_action")
    status = "approved" if action == "approve" else "denied"
    res = APPROVALS.bulk_set_status(ids, status, reason)
    await AUDITOR.log(
        "approvals_bulk", "-", action, {"ids": ids, "result": res}, request.state.correlation_id
    )
    return res


@app.get("/approvals/query")
async def approvals_query(
    agent: str | None = None,
    action: str | None = None,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    if not isinstance(APPROVALS, GraphApprovalsStore):
        # Fallback: list all from memory if available
        if hasattr(APPROVALS, "db"):
            values = list(APPROVALS.db.values())[:limit]
            return {"items": values}
        raise HTTPException(400, "approvals_backend_not_configured")
    items = APPROVALS.query(
        agent=agent,
        action=action,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return {"items": items}


# Minimal Teams bot/webhook endpoint for authenticated approvals
class TeamsWebhookBody(ActionRequest):
    pass


@app.post("/teams/webhook")
async def teams_webhook(request: Request, body: TeamsWebhookBody) -> dict[str, str]:
    # Simple shared-secret validation
    expected = os.getenv("TEAMS_BOT_TOKEN")
    auth = request.headers.get("Authorization", "")
    if expected and auth != f"Bearer {expected}":
        raise HTTPException(401, "unauthorized")

    # Expected payload shape: { params: { approvalId, action: approve|deny, reason?, user?: { upn|id|name } } }
    params = body.params or {}
    approval_id = params.get("approvalId")
    action = params.get("action")
    reason = params.get("reason")
    user = params.get("user") or {}

    if not approval_id or action not in ("approve", "deny"):
        raise HTTPException(400, "invalid_payload")

    status = "approved" if action == "approve" else "denied"
    ok = APPROVALS.set_status(approval_id, status, reason)
    if not ok:
        raise HTTPException(404, "approval_not_found")

    await AUDITOR.log(
        status,
        "-",
        "-",
        {"approval_id": approval_id, "approver": user},
        request.state.correlation_id,
    )
    return {"status": status, "id": approval_id}


class TeamsOAuthBody(ActionRequest):
    pass


@app.post("/teams/oauth/callback")
async def teams_oauth_callback(request: Request, body: TeamsOAuthBody) -> dict[str, Any]:
    # Body: { params: { approvalId, action: approve|deny, id_token } }
    p = body.params or {}
    approval_id = p.get("approvalId")
    action = p.get("action")
    id_token = p.get("id_token")
    if not approval_id or action not in ("approve", "deny") or not id_token:
        raise HTTPException(400, "invalid_payload")

    tenant_id = os.getenv("AZURE_TENANT_ID") or os.getenv("GRAPH_TENANT_ID")
    client_id = (
        os.getenv("TEAMS_OAUTH_CLIENT_ID")
        or os.getenv("AZURE_CLIENT_ID")
        or os.getenv("AZURE_APP_CLIENT_ID_TAI")
        or os.getenv("MICROSOFT_CLIENT_ID")
        or os.getenv("GRAPH_CLIENT_ID")
    )
    if not tenant_id or not client_id:
        raise HTTPException(500, "oauth_not_configured")

    # Verify ID token against tenant JWKS
    jwks = await _get_jwks(tenant_id)
    try:
        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise HTTPException(401, "jwks_key_not_found")
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        claims = jwt.decode(
            id_token,
            key=public_key,
            algorithms=[unverified_header.get("alg", "RS256")],
            audience=client_id,
            options={"verify_exp": True, "verify_aud": True},
        )
    except jwt.PyJWTError as e:
        raise HTTPException(401, f"invalid_id_token: {e}") from e

    approver = (
        claims.get("preferred_username")
        or claims.get("upn")
        or claims.get("email")
        or claims.get("oid")
    )
    if not approver:
        raise HTTPException(401, "approver_identity_missing")

    # Validate approver against approval item or registry rules
    item = APPROVALS.get(approval_id)
    if not item:
        raise HTTPException(404, "approval_not_found")
    allowed = False
    approvers = item.get("approvers") or []
    if approvers:
        allowed = any(approver.lower() == a.lower() for a in approvers)
    else:
        # fallback to registry rules
        ag = item.get("agent")
        ac = item.get("action")
        for r in REGISTRY.get("agents", {}).get(ag, {}).get("approval_rules", []) or []:
            if r.get("action") == ac:
                allowed = approver.lower() in [a.lower() for a in (r.get("approvers") or [])]
                if allowed:
                    break
    if os.getenv("ENFORCE_APPROVER_LIST", "true").lower() in ("1", "true", "yes") and not allowed:
        raise HTTPException(403, "approver_not_allowed")

    status = "approved" if action == "approve" else "denied"
    ok = APPROVALS.set_status(approval_id, status)
    if not ok:
        raise HTTPException(404, "approval_not_found")
    await AUDITOR.log(
        status,
        "-",
        "-",
        {"approval_id": approval_id, "approver": approver, "method": "oauth"},
        request.state.correlation_id,
    )
    return {"status": status, "id": approval_id, "approver": approver}


@app.post("/actions/{agent}/{action}")
async def actions(
    agent: str,
    action: str,
    req: ActionRequest,
    request: Request,
    token: SecurityDependency = None,
) -> ActionResponse:
    corr = request.state.correlation_id
    try:
        canonical_agent, persona = _resolve_persona_agent(agent)
    except ValueError as exc:
        await AUDITOR.log(
            "denied",
            agent,
            action,
            {"reason": str(exc), "persona_target": agent},
            corr,
        )
        raise HTTPException(400, str(exc)) from exc

    if persona.get("status") != "active":
        await AUDITOR.log(
            "denied",
            canonical_agent,
            action,
            {"reason": f"persona_inactive:{canonical_agent}", "persona": persona},
            corr,
        )
        raise HTTPException(403, f"persona_inactive:{canonical_agent}")

    if not _validate_agent_action(canonical_agent, action):
        await AUDITOR.log(
            "denied",
            canonical_agent,
            action,
            {"reason": "invalid_agent_or_action", "persona": persona},
            corr,
        )
        raise HTTPException(400, "invalid_agent_or_action")

    # Per-agent/action rate limiting
    rk = f"{canonical_agent}:{action}"
    rate_allowed = RATE.allow(rk)

    user_email = _resolve_user_identity(request)
    request.state.actor = user_email
    request.state.persona = persona
    actor_groups = _resolve_actor_groups(request)
    tenant_config = _require_tenant_context()
    actor_tier = get_user_tier_info(user_email, tenant_config, actor_groups)
    try:
        executor_name = resolve_executor_name_for_action(canonical_agent, action, tenant_config)
    except ValueError as exc:
        REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="failed").inc()
        await AUDITOR.log(
            "failed",
            canonical_agent,
            action,
            {
                "reason": str(exc),
                "actor": user_email,
                "actor_tier": actor_tier,
                "actor_groups": actor_groups,
                "persona": persona,
                "tenant": tenant_config.tenant.id,
            },
            corr,
        )
        raise HTTPException(500, str(exc)) from exc
    executor_identity = build_executor_identity(tenant_config, executor_name)
    executor_domain = str(executor_identity.get("domain") or "")
    allowed_domains = [str(domain) for domain in (persona.get("allowed_domains") or []) if domain]
    if (
        len(getattr(tenant_config, "executors", {}) or {}) > 1
        and executor_domain
        and executor_domain != "default"
        and allowed_domains
        and executor_domain not in allowed_domains
    ):
        deny_reason = f"persona_domain_mismatch:{canonical_agent}:{executor_domain}"
        REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="denied").inc()
        await AUDITOR.log(
            "denied",
            canonical_agent,
            action,
            {
                "reason": deny_reason,
                "actor": user_email,
                "actor_tier": actor_tier,
                "actor_groups": actor_groups,
                "persona": persona,
                "executor": executor_identity,
                "tenant": tenant_config.tenant.id,
            },
            corr,
        )
        raise HTTPException(403, deny_reason)

    allowed, deny_reason = check_user_permission(
        user_email=user_email,
        action=action,
        tenant_config=tenant_config,
        actor_groups=actor_groups,
    )
    if not allowed:
        REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="denied").inc()
        await AUDITOR.log(
            "denied",
            canonical_agent,
            action,
            {
                "reason": deny_reason,
                "actor": user_email,
                "actor_tier": actor_tier,
                "actor_groups": actor_groups,
                "persona": persona,
                "executor": executor_identity,
                "tenant": tenant_config.tenant.id,
            },
            corr,
        )
        raise HTTPException(403, deny_reason)

    params = dict(req.params or {})
    params.setdefault("requestor", user_email)
    params.setdefault("requestor_tier", actor_tier.get("tier_name"))
    params.setdefault("requestor_tier_info", actor_tier)
    params.setdefault("requestor_groups", actor_groups)
    params.setdefault("persona", persona)
    params.setdefault("persona_target", agent)
    params.setdefault("executor_name", executor_name)
    params.setdefault("executor_domain", executor_identity.get("domain"))
    params.setdefault("executor_identity", executor_identity)
    params.setdefault("tenant", tenant_config.tenant.id)
    governance_resolution = resolve_action_approval_risk(canonical_agent, action, params)
    params.setdefault("risk_class", governance_resolution.risk_class)
    params.setdefault("approval_profile", governance_resolution.approval_profile)
    params.setdefault("approval_required_by_matrix", governance_resolution.approval_required)
    params.setdefault("approval_rule_source", governance_resolution.rule_source)

    # Policy check via OPA
    policy = await OPA.check(canonical_agent, action, params, rate_allowed, corr)
    if not policy.get("allowed", False):
        REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="denied").inc()
        await AUDITOR.log(
            "denied",
            canonical_agent,
            action,
            {
                "reason": policy.get("reason"),
                "actor": user_email,
                "actor_tier": actor_tier,
                "actor_groups": actor_groups,
                "persona": persona,
                "executor": executor_identity,
                "tenant": tenant_config.tenant.id,
                "risk_class": governance_resolution.risk_class,
                "approval_profile": governance_resolution.approval_profile,
                "approval_rule_source": governance_resolution.rule_source,
            },
            corr,
        )
        status_code = 429 if policy.get("reason") == "rate_limited" else 403
        raise HTTPException(status_code, policy.get("reason", "policy_denied"))

    # Approvals
    approval_required = (
        bool(policy.get("approval_required")) or governance_resolution.approval_required
    )
    if get_confirmation_override(user_email, action, tenant_config, actor_groups) == "always":
        approval_required = True

    if approval_required:
        rule = _approval_rule(canonical_agent, action)
        if rule is None and governance_resolution.approvers:
            rule = {"action": action, "approvers": list(governance_resolution.approvers)}
        approvers = (rule or {}).get("approvers", [])
        params.setdefault("approvers", approvers)
        if not approvers:
            REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="denied").inc()
            await AUDITOR.log(
                "denied",
                canonical_agent,
                action,
                {
                    "reason": "approval_configuration_missing",
                    "actor": user_email,
                    "actor_tier": actor_tier,
                    "actor_groups": actor_groups,
                    "persona": persona,
                    "executor": executor_identity,
                    "tenant": tenant_config.tenant.id,
                    "risk_class": governance_resolution.risk_class,
                    "approval_profile": governance_resolution.approval_profile,
                    "approval_rule_source": governance_resolution.rule_source,
                },
                corr,
            )
            raise HTTPException(500, "approval_configuration_missing")
        approval_id = APPROVALS.create(canonical_agent, action, params)
        REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="pending").inc()
        await AUDITOR.log(
            "pending_approval",
            canonical_agent,
            action,
            {
                "approval_id": approval_id,
                "actor": user_email,
                "actor_tier": actor_tier,
                "actor_groups": actor_groups,
                "persona": persona,
                "executor": executor_identity,
                "tenant": tenant_config.tenant.id,
                "approvers": approvers,
                "risk_class": governance_resolution.risk_class,
                "approval_profile": governance_resolution.approval_profile,
                "approval_rule_source": governance_resolution.rule_source,
            },
            corr,
        )
        return ActionResponse(status="pending_approval", approval_id=approval_id)

    # Execute
    with REQ_LATENCY.labels(agent=canonical_agent, action=action).time():
        try:
            result = await execute(
                canonical_agent, action, params, corr, executor_name=executor_name
            )
            REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="success").inc()
            audit_payload = dict(result or {})
            audit_payload["actor"] = user_email
            audit_payload["actor_tier"] = actor_tier
            audit_payload["actor_groups"] = actor_groups
            audit_payload["persona"] = persona
            audit_payload["executor"] = executor_identity
            audit_payload["tenant"] = tenant_config.tenant.id
            audit_payload["risk_class"] = governance_resolution.risk_class
            audit_payload["approval_profile"] = governance_resolution.approval_profile
            audit_payload["approval_rule_source"] = governance_resolution.rule_source
            await AUDITOR.log("success", canonical_agent, action, audit_payload, corr)
            return ActionResponse(status="success", result=result)
        except GraphAPIError as ge:
            REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="failed").inc()
            await AUDITOR.log(
                "failed",
                canonical_agent,
                action,
                {
                    "error": ge.message,
                    "code": ge.code,
                    "status": ge.status,
                    "actor": user_email,
                    "actor_tier": actor_tier,
                    "actor_groups": actor_groups,
                    "persona": persona,
                    "executor": executor_identity,
                    "tenant": tenant_config.tenant.id,
                    "risk_class": governance_resolution.risk_class,
                    "approval_profile": governance_resolution.approval_profile,
                    "approval_rule_source": governance_resolution.rule_source,
                },
                corr,
            )
            raise HTTPException(ge.status, f"graph_error:{ge.code}: {ge.message}") from ge
        except Exception as e:
            REQ_COUNT.labels(agent=canonical_agent, action=action, outcome="failed").inc()
            await AUDITOR.log(
                "failed",
                canonical_agent,
                action,
                {
                    "error": str(e),
                    "actor": user_email,
                    "actor_tier": actor_tier,
                    "actor_groups": actor_groups,
                    "persona": persona,
                    "executor": executor_identity,
                    "tenant": tenant_config.tenant.id,
                    "risk_class": governance_resolution.risk_class,
                    "approval_profile": governance_resolution.approval_profile,
                    "approval_rule_source": governance_resolution.rule_source,
                },
                corr,
            )
            raise HTTPException(500, f"action_failed: {e}") from e
