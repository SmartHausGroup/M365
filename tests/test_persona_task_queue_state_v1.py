from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ops_adapter.app import create_app
from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_task_queue import (
    build_persona_state,
    create_persona_instruction,
    create_persona_task,
    update_persona_task,
)


def test_e5c_projects_queue_state_and_instruction_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    task = create_persona_task("website-manager", {"title": "Draft homepage", "priority": "high"}, store)
    create_persona_instruction("website-manager", {"instruction": "Review the draft"}, store)

    state = build_persona_state("website-manager", store)

    assert task["status"] == "queued"
    assert state["persona_state"] == "queued"
    assert state["task_counts"]["queued"] == 1
    assert state["instruction_counts"]["queued"] == 1
    assert state["queue_depth"] == 2


def test_e5c_enforces_transition_matrix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)
    task = create_persona_task("website-manager", {"title": "Publish site"}, store)

    with pytest.raises(ValueError, match=r"invalid_task_transition:queued->completed"):
        update_persona_task("website-manager", task["id"], {"status": "completed"}, store)


def test_e5c_projects_active_and_attention_required_states(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)
    task = create_persona_task("website-manager", {"title": "Launch banner"}, store)

    updated = update_persona_task("website-manager", task["id"], {"status": "in_progress"}, store)
    assert updated["status"] == "in_progress"
    assert build_persona_state("website-manager", store)["persona_state"] == "active"

    update_persona_task("website-manager", task["id"], {"status": "failed"}, store)
    state = build_persona_state("website-manager", store)
    assert state["persona_state"] == "attention_required"
    assert state["task_counts"]["failed"] == 1


def test_e5c_app_routes_task_queue_with_humanized_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    monkeypatch.setenv("M365_ACTOR_HEADER_FALLBACK", "1")
    client = TestClient(create_app())

    create_response = client.post(
        "/personas/Elena Rodriguez/tasks",
        headers={"X-User-Email": "owner@smarthausgroup.com"},
        json={"title": "Prepare homepage refresh", "priority": "high"},
    )
    assert create_response.status_code == 200
    task = create_response.json()["task"]

    update_response = client.put(
        f"/personas/Elena Rodriguez/tasks/{task['id']}",
        headers={"X-User-Email": "owner@smarthausgroup.com"},
        json={"status": "in_progress", "percent": 40},
    )
    assert update_response.status_code == 200
    assert update_response.json()["task"]["status"] == "in_progress"

    state_response = client.get("/personas/Elena Rodriguez/state")
    assert state_response.status_code == 200
    payload = state_response.json()
    assert payload["canonical_agent"] == "website-manager"
    assert payload["persona"]["display_name"] == "Elena Rodriguez"
    assert payload["persona_state"] == "active"


def test_e5c_planned_persona_can_hold_queued_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    monkeypatch.setenv("M365_ACTOR_HEADER_FALLBACK", "1")
    client = TestClient(create_app())

    response = client.post(
        "/personas/analytics-reporter/tasks",
        headers={"X-User-Email": "owner@smarthausgroup.com"},
        json={"title": "Prepare weekly dashboard"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["persona"]["status"] == "planned"
    assert payload["task"]["status"] == "queued"
