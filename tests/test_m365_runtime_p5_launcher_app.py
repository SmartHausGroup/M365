"""P5 FastAPI launcher app smoke tests.

Plan: plan:m365-standalone-graph-runtime-integration-pack:R6
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from m365_runtime.launcher import build_app, plan_launch


def _build_setup_env() -> dict[str, str]:
    return {
        "M365_TENANT_ID": "t",
        "M365_CLIENT_ID": "c",
        "M365_AUTH_MODE": "device_code",
        "M365_SERVICE_ACTOR_UPN": "ops@acme.com",
        "M365_GRANTED_SCOPES": "User.Read,Sites.Read.All,Organization.Read.All",
    }


def test_runtime_app_exposes_version_and_actions():
    plan = plan_launch(env=_build_setup_env())
    assert plan.outcome == "started"
    app = build_app(plan)
    client = TestClient(app)
    version = client.get("/v1/runtime/version").json()
    assert version["runtime_version"]
    assert version["outcome"] == "started"
    actions = client.get("/v1/actions").json()
    assert actions["count"] == 11
    assert any(a["action_id"] == "graph.org_profile" for a in actions["actions"])


def test_runtime_app_readiness_returns_lattice_state():
    plan = plan_launch(env=_build_setup_env())
    app = build_app(plan)
    client = TestClient(app)
    ready = client.get("/v1/health/readiness").json()
    assert "vector" in ready
    assert ready["state"]["state"] in ("ready", "not_ready")
    assert ready["state"]["label"]


def test_runtime_app_invoke_unknown_action_is_mutation_fenced():
    plan = plan_launch(env=_build_setup_env())
    app = build_app(plan)
    client = TestClient(app)
    response = client.post("/v1/actions/graph.write_something/invoke", json={})
    body = response.json()
    assert body["status_class"] == "mutation_fence"


def test_runtime_app_invoke_known_action_without_token_is_auth_required():
    plan = plan_launch(env=_build_setup_env())
    app = build_app(plan)
    client = TestClient(app)
    response = client.post("/v1/actions/graph.org_profile/invoke", json={"actor": "ops@acme.com"})
    body = response.json()
    assert body["status_class"] in ("auth_required", "permission_missing")


def test_runtime_app_auth_status_reports_unconfigured_when_no_setup():
    plan = plan_launch(env={"M365_TENANT_ID": "", "M365_CLIENT_ID": "", "M365_AUTH_MODE": "", "M365_SERVICE_ACTOR_UPN": ""})
    app = build_app(plan)
    client = TestClient(app)
    response = client.get("/v1/auth/status").json()
    assert response["state"] == "unconfigured"
