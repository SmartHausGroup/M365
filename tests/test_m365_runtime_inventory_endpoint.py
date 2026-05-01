"""Tests for the /v1/inventory endpoint.

plan:m365-cps-trkA-p2-inventory-tool:T3 / L101_m365_cps_capability_inventory_v1
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from m365_runtime import launcher
from m365_runtime.graph.registry import READ_ONLY_REGISTRY
from ucp_m365_pack.client import LEGACY_ACTION_TO_RUNTIME_ACTION


@pytest.fixture()
def inventory_client(tmp_path: Path) -> TestClient:
    """Build a minimal m365_runtime app with a stub installed_root.

    The /v1/inventory endpoint does not require auth, graph, or live tenant.
    """
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


def test_inventory_endpoint_returns_200(inventory_client: TestClient) -> None:
    """L101.L_NO_MUTATION — endpoint is reachable, no auth, no body."""
    response = inventory_client.get("/v1/inventory")
    assert response.status_code == 200


def test_inventory_response_shape_stable(inventory_client: TestClient) -> None:
    """L101.L_RESPONSE_SHAPE_STABLE — top-level keys are present."""
    body = inventory_client.get("/v1/inventory").json()
    required_keys = {
        "implemented_actions",
        "alias_map",
        "advertised_only",
        "agent_summary",
        "runtime_version",
    }
    assert required_keys.issubset(
        set(body.keys())
    ), f"missing keys: {required_keys - set(body.keys())}"


def test_inventory_implemented_matches_registry(inventory_client: TestClient) -> None:
    """L101.L_IMPL_LIST_FROM_REGISTRY — list size matches registry."""
    body = inventory_client.get("/v1/inventory").json()
    impl = body["implemented_actions"]
    assert isinstance(impl, list)
    assert len(impl) == len(READ_ONLY_REGISTRY)
    # Every registry action_id appears
    impl_ids = {entry["action_id"] for entry in impl}
    assert impl_ids == set(READ_ONLY_REGISTRY.keys())


def test_inventory_alias_map_matches_client(inventory_client: TestClient) -> None:
    """L101.L_ALIAS_MAP_FROM_CLIENT — alias map equals the client's source-of-truth dict."""
    body = inventory_client.get("/v1/inventory").json()
    alias = body["alias_map"]
    assert alias == LEGACY_ACTION_TO_RUNTIME_ACTION


def test_inventory_advertised_only_is_set_difference(inventory_client: TestClient) -> None:
    """L101.L_ADVERTISED_ONLY_DIFF — advertised_only excludes implemented and aliased."""
    body = inventory_client.get("/v1/inventory").json()
    advertised_only = set(body["advertised_only"])
    impl_keys = set(READ_ONLY_REGISTRY.keys())
    alias_keys = set(LEGACY_ACTION_TO_RUNTIME_ACTION.keys())
    # Property: nothing in advertised_only is also in impl or alias
    assert advertised_only.isdisjoint(impl_keys)
    assert advertised_only.isdisjoint(alias_keys)


def test_inventory_agent_summary_per_agent_counts(inventory_client: TestClient) -> None:
    """Agent summary counts per-agent total / implemented / aliased / planned."""
    body = inventory_client.get("/v1/inventory").json()
    agent_summary = body["agent_summary"]
    assert isinstance(agent_summary, dict)
    for agent_id, counts in agent_summary.items():
        assert {"total", "implemented", "aliased", "planned"} <= set(counts.keys())
        assert counts["total"] == counts["implemented"] + counts["aliased"] + counts["planned"]
        assert all(v >= 0 for v in counts.values())


def test_inventory_runtime_version_present(inventory_client: TestClient) -> None:
    """L101.L_RESPONSE_SHAPE_STABLE — runtime_version key is non-empty."""
    body = inventory_client.get("/v1/inventory").json()
    assert isinstance(body["runtime_version"], str)
    assert body["runtime_version"]


def test_inventory_no_auth_required(inventory_client: TestClient) -> None:
    """L101.L_NO_MUTATION — endpoint works without any auth header."""
    response = inventory_client.get("/v1/inventory")
    assert response.status_code == 200
