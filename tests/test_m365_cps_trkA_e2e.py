"""End-to-end test of Track A surface (status semantics + inventory + preflight).

plan:m365-cps-trkA-p4-end-to-end:T1-T3

Exercises every Track A surface piece against a freshly-built M365
runtime FastAPI app via TestClient. No live tenant; the test stays
hermetic by mocking the OAuth/Graph transports where needed and
exercising only the routes Track A defines:

- A1: GET unknown action via POST /v1/actions/{action_id}/invoke returns
  status_class == "unknown_action" (not "mutation_fence").
- A2: GET /v1/inventory returns the contract shape.
- A3: POST /v1/auth/preflight returns the partition contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from m365_runtime import launcher
from m365_runtime.graph.registry import READ_ONLY_REGISTRY


@pytest.fixture()
def trkA_client(tmp_path: Path) -> TestClient:
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


def test_trkA_e2e_unknown_action_returns_unknown_action_status(trkA_client: TestClient) -> None:
    """A1 e2e: unknown action via HTTP returns honest unknown_action status."""
    response = trkA_client.post("/v1/actions/graph.does.not.exist/invoke", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["status_class"] == "unknown_action"
    assert body["status_class"] != "mutation_fence"


def test_trkA_e2e_inventory_endpoint_contract(trkA_client: TestClient) -> None:
    """A2 e2e: /v1/inventory returns the full contract shape."""
    body = trkA_client.get("/v1/inventory").json()
    required = {"implemented_actions", "alias_map", "advertised_only", "agent_summary", "runtime_version"}
    assert required <= set(body.keys())
    assert len(body["implemented_actions"]) == len(READ_ONLY_REGISTRY)
    # Coverage gap: the test repo's agents.yaml has many actions not in the registry
    assert len(body["advertised_only"]) > 0


def test_trkA_e2e_preflight_endpoint_partition(trkA_client: TestClient) -> None:
    """A3 e2e: /v1/auth/preflight returns a complete partition."""
    body = trkA_client.post(
        "/v1/auth/preflight",
        json={"auth_mode": "device_code", "granted_scopes": ["User.Read", "Mail.Read"]},
    ).json()
    total = (
        len(body["invokable"])
        + len(body["blocked_by_auth_mode"])
        + len(body["blocked_by_scopes"])
    )
    assert total == body["registry_size"]
    # device_code with User.Read + Mail.Read should at least allow graph.me + mail.health
    assert "graph.me" in body["invokable"]


def test_trkA_e2e_three_surfaces_mutually_consistent(trkA_client: TestClient) -> None:
    """A1+A2+A3: inventory implemented_actions matches registry; preflight uses same registry."""
    inventory = trkA_client.get("/v1/inventory").json()
    preflight = trkA_client.post(
        "/v1/auth/preflight",
        json={"auth_mode": "auth_code_pkce", "granted_scopes": []},
    ).json()
    assert preflight["registry_size"] == len(inventory["implemented_actions"])
