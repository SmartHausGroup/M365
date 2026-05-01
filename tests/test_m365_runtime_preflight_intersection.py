"""Tests for compute_intersection and the /v1/auth/preflight endpoint.

plan:m365-cps-trkA-p3-preflight-intersection / L102
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from m365_runtime import launcher
from m365_runtime.graph.preflight import compute_intersection
from m365_runtime.graph.registry import READ_ONLY_REGISTRY


def test_compute_intersection_partition_complete() -> None:
    """L102.L_PARTITION_COMPLETE — invokable + blocked_auth + blocked_scopes == REGISTRY."""
    result = compute_intersection("device_code", ["User.Read", "Mail.Read", "Calendars.Read"])
    total = (
        len(result["invokable"])
        + len(result["blocked_by_auth_mode"])
        + len(result["blocked_by_scopes"])
    )
    assert total == len(READ_ONLY_REGISTRY)
    assert result["registry_size"] == len(READ_ONLY_REGISTRY)


def test_compute_intersection_disjoint_sets() -> None:
    """L102.L_BLOCKED_BY_AUTH_MODE_DISJOINT and L_BLOCKED_BY_SCOPES_DISJOINT."""
    result = compute_intersection("device_code", ["User.Read"])
    invokable = set(result["invokable"])
    blocked_auth = set(result["blocked_by_auth_mode"])
    blocked_scopes = set(result["blocked_by_scopes"])
    assert invokable.isdisjoint(blocked_auth)
    assert invokable.isdisjoint(blocked_scopes)
    assert blocked_auth.isdisjoint(blocked_scopes)


def test_compute_intersection_invokable_inclusion() -> None:
    """L102.L_INVOKABLE_INCLUSION — every invokable action's auth_mode includes session mode."""
    result = compute_intersection("device_code", ["User.Read", "Mail.Read", "Calendars.Read"])
    for action_id in result["invokable"]:
        spec = READ_ONLY_REGISTRY[action_id]
        assert "device_code" in spec.auth_modes
        assert spec.scopes.issubset({"User.Read", "Mail.Read", "Calendars.Read"})


def test_compute_intersection_blocked_by_auth_mode() -> None:
    """Actions whose auth_modes exclude device_code go to blocked_by_auth_mode."""
    result = compute_intersection("device_code", ["User.Read", "Sites.Read.All"])
    # graph.org_profile requires app_only auth and is not device_code-compatible
    assert "graph.org_profile" in result["blocked_by_auth_mode"]


def test_compute_intersection_no_auth_mode() -> None:
    """When auth_mode is None, every action is in blocked_by_auth_mode."""
    result = compute_intersection(None, [])
    assert len(result["blocked_by_auth_mode"]) == len(READ_ONLY_REGISTRY)
    assert result["invokable"] == []
    assert result["blocked_by_scopes"] == []


def test_compute_intersection_pure_no_mutation() -> None:
    """L102.L_NO_MUTATION — function is pure; calling twice returns same result."""
    a = compute_intersection("device_code", ["User.Read"])
    b = compute_intersection("device_code", ["User.Read"])
    assert a == b


@pytest.fixture()
def preflight_client(tmp_path: Path) -> TestClient:
    env = {
        "M365_TENANT_ID": "11111111-1111-1111-1111-111111111111",
        "M365_CLIENT_ID": "22222222-2222-2222-2222-222222222222",
        "M365_AUTH_MODE": "device_code",
        "M365_SERVICE_ACTOR_UPN": "ops@example.com",
        "M365_GRANTED_SCOPES": "User.Read,Mail.Read",
        "M365_TOKEN_STORE": "memory",
    }
    plan = launcher.plan_launch(env=env)
    app = launcher.build_app(plan)
    return TestClient(app)


def test_preflight_endpoint_returns_partition(preflight_client: TestClient) -> None:
    """/v1/auth/preflight returns the intersection contract."""
    response = preflight_client.post(
        "/v1/auth/preflight",
        json={"auth_mode": "device_code", "granted_scopes": ["User.Read", "Mail.Read"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert {
        "invokable",
        "blocked_by_auth_mode",
        "blocked_by_scopes",
        "session",
        "registry_size",
    } <= set(body.keys())
    total = (
        len(body["invokable"]) + len(body["blocked_by_auth_mode"]) + len(body["blocked_by_scopes"])
    )
    assert total == body["registry_size"]


def test_preflight_endpoint_handles_empty_body(preflight_client: TestClient) -> None:
    """Empty body returns a valid partition (auth_mode may be None when setup is unloaded)."""
    response = preflight_client.post("/v1/auth/preflight", json={})
    assert response.status_code == 200
    body = response.json()
    # Partition must still be complete regardless of auth_mode value
    total = (
        len(body["invokable"]) + len(body["blocked_by_auth_mode"]) + len(body["blocked_by_scopes"])
    )
    assert total == body["registry_size"]
    # auth_mode in session echo is either a real mode or None
    assert body["session"]["auth_mode"] in (
        None,
        "auth_code_pkce",
        "device_code",
        "app_only_secret",
        "app_only_certificate",
    )
