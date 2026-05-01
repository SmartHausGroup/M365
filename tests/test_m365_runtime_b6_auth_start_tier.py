"""Tests for B6 T2/T3 auth-start tier integration. plan:m365-cps-trkB-p6-auth-mode-tiers / L113"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from m365_runtime import launcher
from m365_runtime.graph.actions import invoke
from m365_runtime.graph.registry import ALLOWED_TIERS, READ_ONLY_REGISTRY


@pytest.fixture()
def tier_client(tmp_path: Path) -> TestClient:
    env = {
        "M365_TENANT_ID": "11111111-1111-1111-1111-111111111111",
        "M365_CLIENT_ID": "22222222-2222-2222-2222-222222222222",
        "M365_AUTH_MODE": "auth_code_pkce",
        "M365_SERVICE_ACTOR_UPN": "ops@example.com",
        "M365_REDIRECT_URI": "http://127.0.0.1:9301/callback",
        "M365_GRANTED_SCOPES": "User.Read",
        "M365_TOKEN_STORE": "memory",
    }
    plan = launcher.plan_launch(env=env)
    app = launcher.build_app(plan)
    return TestClient(app)


def test_b6_invoke_accepts_current_tier_kwarg() -> None:
    """L113.L_INVOKE_FORWARDS_TIER — invoke() takes current_tier and forwards to admit."""
    result = invoke(
        action_id="graph.me",
        actor="ops@acme.com",
        granted_scopes=frozenset({"User.Read"}),
        current_auth_mode="device_code",
        access_token="AT",
        current_tier="read-only",
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"id": "u"})),
    )
    assert result.status_class == "success", result.audit


def test_b6_invoke_default_tier_is_read_only() -> None:
    """L113.L_DEFAULT_PRESERVED — invoke() default tier is read-only."""
    # Same call without current_tier: default keeps existing read-only behavior
    result = invoke(
        action_id="graph.me",
        actor="ops@acme.com",
        granted_scopes=frozenset({"User.Read"}),
        current_auth_mode="device_code",
        access_token="AT",
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"id": "u"})),
    )
    assert result.status_class == "success"


def test_b6_auth_start_accepts_valid_tier(tier_client: TestClient) -> None:
    """L113.L_AUTH_START_ACCEPTS_TIER — body.tier is accepted and stored."""
    response = tier_client.post("/v1/auth/start", json={"tier": "standard"})
    assert response.status_code == 200
    body = response.json()
    # Should NOT be config_invalid; should proceed with auth flow
    assert body.get("state") != "config_invalid"


def test_b6_auth_start_rejects_invalid_tier(tier_client: TestClient) -> None:
    """L113.L_TIER_VALIDATED — invalid tier returns config_invalid."""
    response = tier_client.post("/v1/auth/start", json={"tier": "superuser"})
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "config_invalid"
    assert body["reason"] == "invalid_tier"
    assert "allowed_tiers" in body
    assert set(body["allowed_tiers"]) == set(ALLOWED_TIERS)


def test_b6_auth_start_default_tier_when_omitted(tier_client: TestClient) -> None:
    """L113.L_DEFAULT_PRESERVED — omitting tier proceeds with read-only default."""
    response = tier_client.post("/v1/auth/start", json={})
    assert response.status_code == 200
    body = response.json()
    assert body.get("state") != "config_invalid"


def test_b6_token_account_session_tier_constant() -> None:
    """L113 — TOKEN_ACCOUNT_SESSION_TIER and DEFAULT_SESSION_TIER are exposed."""
    assert launcher.TOKEN_ACCOUNT_SESSION_TIER == "session_tier"
    assert launcher.DEFAULT_SESSION_TIER == "read-only"
    assert launcher.DEFAULT_SESSION_TIER in ALLOWED_TIERS


def test_b6_invoke_admit_rejects_when_tier_below_min() -> None:
    """L113.L_INVOKE_FORWARDS_TIER — invoke at read-only tier rejects an admin-tier action.

    Synthesize an admin-tier ActionSpec on the fly to test the gate without
    introducing a permanent admin action to the registry.
    """
    from m365_runtime.graph.registry import ActionSpec

    spec = ActionSpec(
        "graph.fake.admin",
        "test",
        "/me",
        frozenset({"device_code"}),
        frozenset({"User.Read"}),
        "low",
        "read",
        min_tier="admin",
    )
    READ_ONLY_REGISTRY[spec.action_id] = spec
    try:
        result = invoke(
            action_id="graph.fake.admin",
            actor="ops@acme.com",
            granted_scopes=frozenset({"User.Read"}),
            current_auth_mode="device_code",
            access_token="AT",
            current_tier="read-only",
        )
        # admit returns ("denied", "tier_insufficient"); _denial_to_status maps unknown
        # reasons to policy_denied (since trkB doesn't have the C1 not_yet_implemented
        # mapping yet). We assert the call was denied (not success).
        assert result.status_class != "success"
    finally:
        del READ_ONLY_REGISTRY[spec.action_id]
