from __future__ import annotations

import os
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import yaml
from fastapi import FastAPI, Header, HTTPException, Request
from smarthaus_common.config import has_selected_tenant
from smarthaus_common.permission_enforcer import (
    check_user_permission,
    get_confirmation_override,
    get_user_tier_info,
)
from smarthaus_common.tenant_config import get_tenant_config
from starlette.responses import Response

from .actions import (
    build_executor_identity,
    resolve_executor_name_for_action,
)
from .actions import (
    execute as execute_action,
)
from .approvals import ApprovalsStore
from .audit import audit_log
from .models import ActionRequest, ActionResponse
from .personas import load_persona_registry, resolve_persona_target
from .policies import OPAClient
from .rate_limit import RateLimiter


def _truthy_env(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


def _actor_header_fallback_enabled() -> bool:
    """Legacy app path is header-only and must fail closed unless explicitly enabled."""
    return _truthy_env("M365_ACTOR_HEADER_FALLBACK", "0")


def load_registry() -> dict[str, Any]:
    path = os.getenv("REGISTRY_FILE", "./registry/agents.yaml")
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def create_app() -> FastAPI:
    app = FastAPI(title="Ops Adapter", version=os.getenv("OPS_ADAPTER_VERSION", "0.1.0"))

    opa_url = os.getenv("OPA_URL", "http://opa:8181")
    opa = OPAClient(base_url=opa_url)
    registry = load_registry()
    personas = load_persona_registry(registry)
    approvals = ApprovalsStore(registry, personas)
    limiter = RateLimiter(
        default_rps=float(os.getenv("OPS_RATE_DEFAULT_RPS", "5")),
        burst=int(os.getenv("OPS_RATE_BURST", "10")),
    )

    @app.middleware("http")
    async def add_correlation_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        corr = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.correlation_id = corr
        response = await call_next(request)
        response.headers["X-Request-ID"] = corr
        return response

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "service": "ops-adapter", "version": app.version}

    @app.post("/actions/{agent}/{action}", response_model=ActionResponse)
    async def perform_action(
        agent: str,
        action: str,
        payload: ActionRequest,
        request: Request,
        x_request_id: str | None = Header(default=None),
    ) -> ActionResponse:
        correlation_id = getattr(request.state, "correlation_id", x_request_id) or str(uuid.uuid4())
        try:
            canonical_agent, persona = resolve_persona_target(agent, personas)
        except ValueError as exc:
            audit_log(
                "policy_denied",
                agent=agent,
                action=action,
                correlation_id=correlation_id,
                reason=str(exc),
            )
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        if persona.get("status") != "active":
            audit_log(
                "policy_denied",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                reason=f"persona_inactive:{canonical_agent}",
            )
            raise HTTPException(status_code=403, detail=f"persona_inactive:{canonical_agent}")

        if not _actor_header_fallback_enabled():
            audit_log(
                "policy_denied",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                actor="system",
                reason="entra_actor_identity_required",
            )
            raise HTTPException(status_code=403, detail="entra_actor_identity_required")

        user_email = (
            (request.headers.get("X-User-Email") or request.headers.get("X-Principal-Email") or "")
            .strip()
            .lower()
        )

        if not user_email:
            audit_log(
                "policy_denied",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                reason="user_identity_missing",
            )
            raise HTTPException(status_code=403, detail="user_identity_missing")

        if not has_selected_tenant():
            audit_log(
                "policy_denied",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                reason="tenant_selection_missing",
            )
            raise HTTPException(status_code=403, detail="tenant_selection_missing")
        try:
            tenant_config = get_tenant_config()
        except Exception as exc:
            reason = f"tenant_config_unavailable:{type(exc).__name__}"
            audit_log(
                "policy_denied",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                reason=reason,
            )
            raise HTTPException(status_code=403, detail=reason) from exc

        actor_groups: list[str] = []
        actor_tier = get_user_tier_info(user_email, tenant_config, actor_groups)
        try:
            executor_name = resolve_executor_name_for_action(canonical_agent, action, tenant_config)
        except ValueError as exc:
            audit_log(
                "action_failed",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                reason=str(exc),
                actor=user_email,
                actor_tier=actor_tier,
                actor_groups=actor_groups,
                persona=persona,
                tenant=tenant_config.tenant.id,
            )
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        executor_identity = build_executor_identity(tenant_config, executor_name)
        executor_domain = str(executor_identity.get("domain") or "")
        allowed_domains = [
            str(domain) for domain in (persona.get("allowed_domains") or []) if domain
        ]
        if (
            len(getattr(tenant_config, "executors", {}) or {}) > 1
            and executor_domain
            and executor_domain != "default"
            and allowed_domains
            and executor_domain not in allowed_domains
        ):
            deny_reason = f"persona_domain_mismatch:{canonical_agent}:{executor_domain}"
            audit_log(
                "policy_denied",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                reason=deny_reason,
                actor=user_email,
                actor_tier=actor_tier,
                actor_groups=actor_groups,
                persona=persona,
                executor=executor_identity,
                tenant=tenant_config.tenant.id,
            )
            raise HTTPException(status_code=403, detail=deny_reason)

        allowed, reason = check_user_permission(
            user_email=user_email,
            action=action,
            tenant_config=tenant_config,
            actor_groups=actor_groups,
        )
        if not allowed:
            audit_log(
                "policy_denied",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                reason=reason,
                actor=user_email,
                actor_tier=actor_tier,
                actor_groups=actor_groups,
                persona=persona,
                executor=executor_identity,
                tenant=tenant_config.tenant.id,
            )
            raise HTTPException(status_code=403, detail=reason)

        # Rate limit per agent
        if not limiter.allow(canonical_agent):
            raise HTTPException(status_code=429, detail="rate_limit_exceeded")

        # Policy check via OPA (fail-open behavior is handled by OPA client)
        # Pass rate_allowed=True since limiter already enforced
        params = payload.model_dump().get("params", {})
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
        decision = await opa.check(
            agent=canonical_agent,
            action=action,
            data=params,
            rate_allowed=True,
            correlation_id=correlation_id,
        )
        if not decision.get("allowed", False):
            audit_log(
                "policy_denied",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                reason=decision.get("reason") or "denied",
                actor=user_email,
                actor_tier=actor_tier,
                actor_groups=actor_groups,
                persona=persona,
                executor=executor_identity,
                tenant=tenant_config.tenant.id,
            )
            raise HTTPException(status_code=403, detail="policy_denied")

        # Handle approval requirements
        approval_required = bool(decision.get("approval_required"))
        if get_confirmation_override(user_email, action, tenant_config, actor_groups) == "always":
            approval_required = True

        if approval_required:
            registry = getattr(approvals, "registry", {}) or {}
            approvers: list[str] = []
            for rule in (
                registry.get("agents", {}).get(canonical_agent, {}).get("approval_rules", []) or []
            ):
                if rule.get("action") == action:
                    approvers = rule.get("approvers", []) or []
                    break
            if not approvers:
                audit_log(
                    "policy_denied",
                    agent=canonical_agent,
                    action=action,
                    correlation_id=correlation_id,
                    reason="approval_configuration_missing",
                    actor=user_email,
                    actor_tier=actor_tier,
                    actor_groups=actor_groups,
                    persona=persona,
                    executor=executor_identity,
                    tenant=tenant_config.tenant.id,
                )
                raise HTTPException(status_code=500, detail="approval_configuration_missing")
            approval_id = approvals.create(agent=canonical_agent, action=action, params=params)
            audit_log(
                "approval_pending",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                approval_id=approval_id,
                actor=user_email,
                actor_tier=actor_tier,
                actor_groups=actor_groups,
                persona=persona,
                executor=executor_identity,
                tenant=tenant_config.tenant.id,
            )
            return ActionResponse(
                status="pending_approval",
                approval_id=approval_id,
                reason="approval_required",
            )

        # Execute action (may be dry-run)
        # Map known aliases for compatibility
        if canonical_agent == "m365-administrator" and action == "user.provision":
            mapped_action = "users.create"
        else:
            mapped_action = action

        try:
            result = await execute_action(
                agent=canonical_agent,
                action=mapped_action,
                params=params,
                correlation_id=correlation_id,
                executor_name=executor_name,
            )
            audit_log(
                "action_executed",
                agent=canonical_agent,
                action=action,
                correlation_id=correlation_id,
                result=result,
                actor=user_email,
                actor_tier=actor_tier,
                actor_groups=actor_groups,
                persona=persona,
                executor=executor_identity,
                tenant=tenant_config.tenant.id,
            )
            return ActionResponse(status="ok", result=result)
        except Exception:
            raise

    @app.get("/approvals/{approval_id}")
    async def get_approval(approval_id: str) -> dict[str, Any]:
        item = approvals.get(approval_id)
        if not item:
            raise HTTPException(status_code=404, detail="not_found")
        return item

    @app.post("/approvals/{approval_id}")
    async def update_approval(approval_id: str, body: dict[str, Any]) -> dict[str, Any]:
        decision = body.get("decision")
        if decision not in ("approved", "rejected"):
            raise HTTPException(status_code=400, detail="invalid_decision")
        updated = approvals.set_status(approval_id, decision)
        if not updated:
            raise HTTPException(status_code=404, detail="not_found")
        return updated

    return app
