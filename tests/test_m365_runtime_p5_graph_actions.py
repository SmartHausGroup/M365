"""P5 regressions for the read-only Graph action runtime.

Plan: plan:m365-standalone-graph-runtime-integration-pack:R6
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from m365_runtime.graph.actions import ActionInvocation, invoke, list_actions
from m365_runtime.graph.registry import READ_ONLY_REGISTRY


def _transport(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def _ok_handler(payload: dict[str, Any]) -> Callable[[httpx.Request], httpx.Response]:
    def h(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    return h


def test_list_actions_is_sorted_and_complete() -> None:
    out = list_actions()
    assert len(out) == len(READ_ONLY_REGISTRY)
    ids = [a["action_id"] for a in out]
    assert ids == sorted(ids)
    for entry in out:
        assert entry["rw"] == "read"
        assert entry["scopes"]
        assert entry["auth_modes"]


def test_invoke_admit_path_calls_graph_and_emits_audit() -> None:
    payload = {"id": "tenant", "displayName": "Acme"}
    result = invoke(
        action_id="graph.org_profile",
        actor="ops@acme.com",
        granted_scopes=frozenset({"Organization.Read.All"}),
        current_auth_mode="app_only_secret",
        access_token="AT",
        params={},
        transport=_transport(_ok_handler(payload)),
    )
    assert result.status_class == "success"
    assert result.payload == payload
    assert result.audit["actor"] == "ops@acme.com"
    assert result.audit["action"] == "graph.org_profile"
    assert result.audit["status_class"] == "success"


def test_invoke_denies_unknown_action_with_mutation_fence() -> None:
    result = invoke(
        action_id="graph.unknown",
        actor="ops@acme.com",
        granted_scopes=frozenset({"X"}),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
    )
    assert result.status_class == "mutation_fence"
    assert result.audit["status_class"] == "mutation_fence"


def test_invoke_denies_when_scopes_missing() -> None:
    result = invoke(
        action_id="graph.users.list",
        actor="ops@acme.com",
        granted_scopes=frozenset(),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
    )
    assert result.status_class == "permission_missing"


def test_invoke_denies_when_auth_mode_mismatch() -> None:
    result = invoke(
        action_id="graph.servicehealth",
        actor="ops@acme.com",
        granted_scopes=frozenset({"ServiceHealth.Read.All"}),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
    )
    assert result.status_class == "auth_required"


def test_invoke_returns_auth_required_when_no_token() -> None:
    result = invoke(
        action_id="graph.me",
        actor="user@acme.com",
        granted_scopes=frozenset({"User.Read"}),
        current_auth_mode="auth_code_pkce",
        access_token=None,
    )
    assert result.status_class == "auth_required"


def test_invoke_normalizes_403_consent_required() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403, json={"error": {"code": "ConsentRequired", "message": "Consent needed"}}
        )

    result = invoke(
        action_id="graph.users.list",
        actor="ops@acme.com",
        granted_scopes=frozenset({"User.Read.All"}),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
        transport=_transport(handler),
    )
    assert result.status_class == "consent_required"


def test_invoke_normalizes_403_forbidden_to_policy_denied() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error": {"code": "Forbidden", "message": "no access"}})

    result = invoke(
        action_id="graph.users.list",
        actor="ops@acme.com",
        granted_scopes=frozenset({"User.Read.All"}),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
        transport=_transport(handler),
    )
    assert result.status_class == "policy_denied"


def test_invoke_throttled_then_success() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(
                429, headers={"Retry-After": "1"}, json={"error": {"code": "Throttled"}}
            )
        return httpx.Response(200, json={"value": []})

    sleeps: list[float] = []
    result = invoke(
        action_id="graph.users.list",
        actor="ops@acme.com",
        granted_scopes=frozenset({"User.Read.All"}),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
        transport=_transport(handler),
        sleep=lambda s: sleeps.append(s),
    )
    assert result.status_class == "success"
    assert sleeps == [1]


def test_invoke_5xx_then_5xx_then_5xx_returns_graph_unreachable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": {"code": "Internal"}})

    result = invoke(
        action_id="graph.users.list",
        actor="ops@acme.com",
        granted_scopes=frozenset({"User.Read.All"}),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
        transport=_transport(handler),
        sleep=lambda s: None,
    )
    assert result.status_class == "graph_unreachable"


def test_invoke_emits_redacted_audit_envelope() -> None:
    payload: dict[str, Any] = {"value": []}
    result = invoke(
        action_id="graph.org_profile",
        actor="ops@acme.com",
        granted_scopes=frozenset({"Organization.Read.All"}),
        current_auth_mode="app_only_secret",
        access_token="AT",
        params={"client_secret": "should_be_redacted", "ok": "fine"},
        transport=_transport(_ok_handler(payload)),
    )
    assert result.audit["extra_redacted"]["params"]["client_secret"] == "[redacted]"
    assert result.audit["extra_redacted"]["params"]["ok"] == "fine"


def test_invoke_action_invocation_struct_shape() -> None:
    result = invoke(
        action_id="graph.unknown",
        actor="ops@acme.com",
        granted_scopes=frozenset(),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
    )
    assert isinstance(result, ActionInvocation)
    assert result.correlation_id
    assert result.audit["correlation_id"] == result.correlation_id
    assert result.status_class == "mutation_fence"
