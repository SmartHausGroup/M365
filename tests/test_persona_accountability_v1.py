from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ops_adapter.app import create_app
from provisioning_api.routers.agent_dashboard import router as agent_dashboard_router
from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_accountability import build_persona_accountability
from smarthaus_common.persona_task_queue import create_persona_task, update_persona_task


def test_e5d_builds_on_track_accountability_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    create_persona_task("website-manager", {"title": "Prepare homepage refresh"}, store)

    snapshot = build_persona_accountability("website-manager", store=store)

    assert snapshot["accountability_state"] == "on_track"
    assert snapshot["ownership"]["manager"] == "department-lead:operations"
    assert snapshot["metrics"]["queue_depth"] == 1
    assert snapshot["escalation"]["required"] is False


def test_e5d_warns_when_queue_depth_reaches_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    for index in range(3):
        create_persona_task("website-manager", {"title": f"Task {index + 1}"}, store)

    snapshot = build_persona_accountability("website-manager", store=store)

    assert snapshot["accountability_state"] == "warning"
    assert snapshot["metrics"]["queue_depth"] == 3
    assert snapshot["thresholds"]["target_queue_depth"] == 3


def test_e5d_escalates_on_blocked_work(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    task = create_persona_task("website-manager", {"title": "Publish refreshed homepage"}, store)
    update_persona_task(
        "website-manager",
        task["id"],
        {"status": "in_progress", "updated_by": "owner@smarthausgroup.com"},
        store,
    )
    update_persona_task(
        "website-manager",
        task["id"],
        {"status": "blocked", "updated_by": "owner@smarthausgroup.com"},
        store,
    )

    snapshot = build_persona_accountability("website-manager", store=store)

    assert snapshot["accountability_state"] == "escalated"
    assert snapshot["escalation"]["required"] is True
    assert snapshot["escalation"]["target"] == "department-lead:operations"
    assert "blocked_work_present" in snapshot["escalation"]["reasons"]


def test_e5d_accountability_route_exposes_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    monkeypatch.setenv("M365_ACTOR_HEADER_FALLBACK", "1")
    client = TestClient(create_app())

    create_response = client.post(
        "/personas/Elena Rodriguez/tasks",
        headers={"X-User-Email": "owner@smarthausgroup.com"},
        json={"title": "Prepare leadership update"},
    )
    assert create_response.status_code == 200

    response = client.get("/personas/Elena Rodriguez/accountability")

    assert response.status_code == 200
    payload = response.json()
    assert payload["canonical_agent"] == "website-manager"
    assert payload["accountability"]["ownership"]["department"] == "operations"
    assert payload["accountability"]["metrics"]["queue_depth"] == 1


def test_e5d_dashboard_projects_accountability_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    app = FastAPI()
    app.include_router(agent_dashboard_router)
    client = TestClient(app)

    client.post("/api/agents/m365-administrator/tasks", json={"title": "Review license posture"})

    status_response = client.get("/api/agents/m365-administrator/status")
    perf_response = client.get("/api/agents/m365-administrator/performance")

    assert status_response.status_code == 200
    assert perf_response.status_code == 200
    assert status_response.json()["accountability"]["ownership"]["department"] == "operations"
    assert perf_response.json()["metrics"]["accountability_state"] in {
        "on_track",
        "warning",
        "escalated",
    }
