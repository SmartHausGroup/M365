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
from dataclasses import dataclass
from typing import Any

import httpx

from ..audit import build_envelope
from .client import GraphResult, graph_get
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
    sleep: callable = time.sleep,
) -> ActionInvocation:
    correlation_id = str(uuid.uuid4())
    params = params or {}
    decision, reason = admit(action_id, granted_scopes, current_auth_mode)
    if decision == "denied":
        envelope = build_envelope(
            actor=actor,
            action=action_id,
            status_class=_denial_to_status(reason),
            extra={"reason": reason, "params": params},
            correlation_id=correlation_id,
        )
        return ActionInvocation(status_class=_denial_to_status(reason), payload=None, audit=envelope, correlation_id=correlation_id)
    if not access_token:
        envelope = build_envelope(actor=actor, action=action_id, status_class="auth_required", extra={"params": params}, correlation_id=correlation_id)
        return ActionInvocation("auth_required", None, envelope, correlation_id)
    spec = get_action(action_id)
    endpoint = spec.endpoint
    if "?search=" in endpoint and "search" in params:
        endpoint = f"{endpoint}{httpx.QueryParams({'search': str(params['search'])})}"[:1024]
    elif endpoint.endswith("?search="):
        envelope = build_envelope(actor=actor, action=action_id, status_class="internal_error", extra={"reason": "search_param_missing"}, correlation_id=correlation_id)
        return ActionInvocation("internal_error", None, envelope, correlation_id)
    result = graph_get(access_token, endpoint, params=params if "?search=" not in spec.endpoint else None, transport=transport, sleep=sleep)
    envelope = build_envelope(
        actor=actor,
        action=action_id,
        status_class=result.status_class,
        after={"http_status": result.http_status, "correlation_id_graph": result.correlation_id, "retry_after_seconds": result.retry_after_seconds},
        extra={"params": params},
        correlation_id=correlation_id,
    )
    return ActionInvocation(result.status_class, result.body, envelope, correlation_id)


def list_actions() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for spec in READ_ONLY_REGISTRY.values():
        out.append({
            "action_id": spec.action_id,
            "workload": spec.workload,
            "endpoint": spec.endpoint,
            "auth_modes": sorted(spec.auth_modes),
            "scopes": sorted(spec.scopes),
            "risk": spec.risk,
            "rw": spec.rw,
        })
    return sorted(out, key=lambda x: x["action_id"])


def _denial_to_status(reason: str) -> str:
    if reason == "permission_missing":
        return "permission_missing"
    if reason == "auth_mode_mismatch":
        return "auth_required"
    if reason == "unknown_action":
        return "mutation_fence"
    if reason == "mutation_fence":
        return "mutation_fence"
    return "policy_denied"
