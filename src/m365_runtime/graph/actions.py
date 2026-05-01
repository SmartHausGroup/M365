"""Read-only Graph action invocation with permission matrix + audit envelope.

`invoke(action_id, granted_scopes, current_auth_mode, access_token, params)`
is the single bounded entry point. It:

  1. Looks up the action in `READ_ONLY_REGISTRY`.
  2. Returns `mutation_fence` if the action is not `rw=read`.
  3. Returns `permission_missing` / `auth_mode_mismatch` / `unknown_action`
     deterministically when admit() denies.
  4. Calls `graph_get` with bounded retry/throttle.
  5. Builds a redacted audit envelope and returns it alongside the result.

The runtime never mutates Graph state in P5. Mutation actions remain fenced
until a separate mutation-governance plan is approved.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from ..audit import build_envelope
from .client import graph_get
from .registry import READ_ONLY_REGISTRY, admit, get_action


@dataclass
class ActionInvocation:
    status_class: str
    payload: dict[str, Any] | None
    audit: dict[str, Any]
    correlation_id: str


def invoke(
    *,
    action_id: str,
    actor: str,
    granted_scopes: frozenset[str],
    current_auth_mode: str,
    access_token: str | None,
    params: dict[str, Any] | None = None,
    transport: httpx.BaseTransport | None = None,
    sleep: Callable[[float], None] = time.sleep,
    current_tier: str = "read-only",
) -> ActionInvocation:
    correlation_id = str(uuid.uuid4())
    params = params or {}
    # plan:m365-cps-trkB-p6-auth-mode-tiers:T2 / L113.L_INVOKE_FORWARDS_TIER
    decision, reason = admit(action_id, granted_scopes, current_auth_mode, current_tier)
    if decision == "denied":
        envelope = build_envelope(
            actor=actor,
            action=action_id,
            status_class=_denial_to_status(reason),
            extra={"reason": reason, "params": params},
            correlation_id=correlation_id,
        )
        return ActionInvocation(
            status_class=_denial_to_status(reason),
            payload=None,
            audit=envelope,
            correlation_id=correlation_id,
        )
    if not access_token:
        envelope = build_envelope(
            actor=actor,
            action=action_id,
            status_class="auth_required",
            extra={"params": params},
            correlation_id=correlation_id,
        )
        return ActionInvocation("auth_required", None, envelope, correlation_id)
    spec = get_action(action_id)
    endpoint = spec.endpoint
    # plan:m365-cps-trkB-p1-sharepoint-reads:T2 / L103.L_PATH_SUBST_CORRECT
    # Substitute {name} placeholders in the endpoint from params before
    # any further query-string handling.
    endpoint, missing_path_params = _substitute_path_params(endpoint, params)
    if missing_path_params:
        envelope = build_envelope(
            actor=actor,
            action=action_id,
            status_class="internal_error",
            extra={"reason": "endpoint_param_missing", "missing": missing_path_params},
            correlation_id=correlation_id,
        )
        return ActionInvocation("internal_error", None, envelope, correlation_id)
    if "?search=" in endpoint and "search" in params:
        endpoint = f"{endpoint}{httpx.QueryParams({'search': str(params['search'])})}"[:1024]
    elif endpoint.endswith("?search="):
        envelope = build_envelope(
            actor=actor,
            action=action_id,
            status_class="internal_error",
            extra={"reason": "search_param_missing"},
            correlation_id=correlation_id,
        )
        return ActionInvocation("internal_error", None, envelope, correlation_id)
    result = graph_get(
        access_token,
        endpoint,
        params=params if "?search=" not in spec.endpoint else None,
        transport=transport,
        sleep=sleep,
    )
    envelope = build_envelope(
        actor=actor,
        action=action_id,
        status_class=result.status_class,
        after={
            "http_status": result.http_status,
            "correlation_id_graph": result.correlation_id,
            "retry_after_seconds": result.retry_after_seconds,
        },
        extra={"params": params},
        correlation_id=correlation_id,
    )
    return ActionInvocation(result.status_class, result.body, envelope, correlation_id)


def list_actions() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for spec in READ_ONLY_REGISTRY.values():
        out.append(
            {
                "action_id": spec.action_id,
                "workload": spec.workload,
                "endpoint": spec.endpoint,
                "auth_modes": sorted(spec.auth_modes),
                "scopes": sorted(spec.scopes),
                "risk": spec.risk,
                "rw": spec.rw,
            }
        )
    return sorted(out, key=lambda x: x["action_id"])


_PATH_PARAM_RE = __import__("re").compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _substitute_path_params(
    endpoint: str, params: dict[str, Any]
) -> tuple[str, list[str]]:
    """Substitute {name} placeholders in an endpoint from params.

    plan:m365-cps-trkB-p1-sharepoint-reads:T2 / L103.L_PATH_SUBST_CORRECT

    Returns (endpoint_with_substitutions, missing_param_names).
    Path-param names consumed from `params` so they do not also become
    query-string args.
    """
    placeholders = _PATH_PARAM_RE.findall(endpoint)
    missing: list[str] = []
    if not placeholders:
        return endpoint, missing
    for name in placeholders:
        if name not in params:
            missing.append(name)
    if missing:
        return endpoint, missing
    rendered = endpoint
    for name in placeholders:
        rendered = rendered.replace("{" + name + "}", str(params[name]))
    # Consume path params from the dict so callers won't also pass them as query args.
    for name in placeholders:
        params.pop(name, None)
    return rendered, missing


def _denial_to_status(reason: str) -> str:
    if reason == "permission_missing":
        return "permission_missing"
    if reason == "auth_mode_mismatch":
        return "auth_required"
    if reason == "unknown_action":
        return "unknown_action"
    if reason == "mutation_fence":
        return "mutation_fence"
    return "policy_denied"
