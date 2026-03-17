from __future__ import annotations

import os
import uuid
from typing import Any, Callable, Dict

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .audit import audit_log
from .policies import OPAClient
from .rate_limit import RateLimiter
from .approvals import ApprovalsStore
from .models import ActionRequest, ActionResponse
from .actions import execute as execute_action
from smarthaus_common.config import has_selected_tenant
from smarthaus_common.permission_enforcer import check_user_permission, get_confirmation_override
from smarthaus_common.tenant_config import get_tenant_config


def create_app() -> FastAPI:
    app = FastAPI(title="Ops Adapter", version=os.getenv("OPS_ADAPTER_VERSION", "0.1.0"))

    opa_url = os.getenv("OPA_URL", "http://opa:8181")
    opa = OPAClient(base_url=opa_url)
    approvals = ApprovalsStore()
    limiter = RateLimiter(
        default_rps=float(os.getenv("OPS_RATE_DEFAULT_RPS", "5")),
        burst=int(os.getenv("OPS_RATE_BURST", "10")),
    )

    @app.middleware("http")
    async def add_correlation_id(request: Request, call_next: Callable):
        corr = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.correlation_id = corr
        response = await call_next(request)
        response.headers["X-Request-ID"] = corr
        return response

    @app.get("/health")
    async def health() -> Dict[str, Any]:
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
        user_email = (request.headers.get("X-User-Email") or "").strip().lower()

        if not user_email:
            audit_log(
                "policy_denied",
                agent=agent,
                action=action,
                correlation_id=correlation_id,
                reason="user_identity_missing",
            )
            raise HTTPException(status_code=403, detail="user_identity_missing")

        if not has_selected_tenant():
            audit_log(
                "policy_denied",
                agent=agent,
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
                agent=agent,
                action=action,
                correlation_id=correlation_id,
                reason=reason,
            )
            raise HTTPException(status_code=403, detail=reason)

        allowed, reason = check_user_permission(
            user_email=user_email,
            action=action,
            tenant_config=tenant_config,
        )
        if not allowed:
            audit_log(
                "policy_denied",
                agent=agent,
                action=action,
                correlation_id=correlation_id,
                reason=reason,
            )
            raise HTTPException(status_code=403, detail=reason)

        # Rate limit per agent
        if not limiter.allow(agent):
            raise HTTPException(status_code=429, detail="rate_limit_exceeded")

        # Policy check via OPA (fail-open behavior is handled by OPA client)
        # Pass rate_allowed=True since limiter already enforced
        params = payload.model_dump().get("params", {})
        params.setdefault("requestor", user_email)
        decision = await opa.check(agent=agent, action=action, data=params, rate_allowed=True, correlation_id=correlation_id)
        if not decision.get("allowed", False):
            audit_log(
                "policy_denied",
                agent=agent,
                action=action,
                correlation_id=correlation_id,
                reason=decision.get("reason") or "denied",
            )
            raise HTTPException(status_code=403, detail="policy_denied")

        # Handle approval requirements
        approval_required = bool(decision.get("approval_required"))
        if get_confirmation_override(user_email, action, tenant_config) == "always":
            approval_required = True

        if approval_required:
            registry = getattr(approvals, "registry", {}) or {}
            approvers: list[str] = []
            for rule in registry.get("agents", {}).get(agent, {}).get("approval_rules", []) or []:
                if rule.get("action") == action:
                    approvers = rule.get("approvers", []) or []
                    break
            if not approvers:
                audit_log(
                    "policy_denied",
                    agent=agent,
                    action=action,
                    correlation_id=correlation_id,
                    reason="approval_configuration_missing",
                )
                raise HTTPException(status_code=500, detail="approval_configuration_missing")
            approval_id = approvals.create(agent=agent, action=action, params=params)
            audit_log(
                "approval_pending",
                agent=agent,
                action=action,
                correlation_id=correlation_id,
                approval_id=approval_id,
            )
            return ActionResponse(
                status="pending_approval",
                approval_id=approval_id,
                reason="approval_required",
            )

        # Execute action (may be dry-run)
        # Map known aliases for compatibility
        if agent == "m365-administrator" and action == "user.provision":
            mapped_action = "users.create"
        else:
            mapped_action = action

        try:
            result = await execute_action(agent=agent, action=mapped_action, params=params, correlation_id=correlation_id)
            audit_log("action_executed", agent=agent, action=action, correlation_id=correlation_id, result=result)
            return ActionResponse(status="ok", result=result)
        except Exception as e:
            raise

    @app.get("/approvals/{approval_id}")
    async def get_approval(approval_id: str):
        item = approvals.get(approval_id)
        if not item:
            raise HTTPException(status_code=404, detail="not_found")
        return item

    @app.post("/approvals/{approval_id}")
    async def update_approval(approval_id: str, body: Dict[str, Any]):
        decision = body.get("decision")
        if decision not in ("approved", "rejected"):
            raise HTTPException(status_code=400, detail="invalid_decision")
        updated = approvals.set_status(approval_id, decision)
        if not updated:
            raise HTTPException(status_code=404, detail="not_found")
        return updated

    return app
