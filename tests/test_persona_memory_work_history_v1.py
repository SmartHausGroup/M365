from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ops_adapter.app import create_app
from provisioning_api.routers.agent_dashboard import router as agent_dashboard_router
from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_memory import (
    build_persona_work_history,
    create_persona_memory,
    list_persona_memory,
)
from smarthaus_common.persona_task_queue import (
    create_persona_instruction,
    create_persona_task,
    update_persona_task,
)


def test_e5e_creates_and_lists_bounded_memory_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    create_persona_memory(
        "website-manager",
        {"memory_type": "note", "content": "Homepage refresh started", "created_by": "owner"},
        store,
    )
    create_persona_memory(
        "website-manager",
        {"memory_type": "decision", "content": "Ship the blue hero variant", "created_by": "owner"},
        store,
    )

    memory = list_persona_memory("website-manager", store=store)

    assert len(memory) == 2
    assert memory[0]["memory_type"] == "decision"
    assert memory[1]["memory_type"] == "note"


def test_e5e_builds_work_history_from_tasks_instructions_and_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    task = create_persona_task("website-manager", {"title": "Draft homepage refresh"}, store)
    update_persona_task(
        "website-manager",
        task["id"],
        {"status": "in_progress", "updated_by": "owner@smarthausgroup.com"},
        store,
    )
    create_persona_instruction(
        "website-manager",
        {
            "instruction": "Keep the investor page unchanged",
            "created_by": "owner@smarthausgroup.com",
        },
        store,
    )
    create_persona_memory(
        "website-manager",
        {
            "memory_type": "summary",
            "content": "Leadership wants the launch this week",
            "created_by": "owner",
        },
        store,
    )

    history = build_persona_work_history("website-manager", store=store)
    event_types = {event["event_type"] for event in history["history"]}

    assert history["memory_count"] == 1
    assert history["task_count"] == 1
    assert history["instruction_count"] == 1
    assert {"task_created", "task_update", "instruction", "memory"} <= event_types


def test_e5e_memory_route_requires_actor_header(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    monkeypatch.delenv("M365_ACTOR_HEADER_FALLBACK", raising=False)
    client = TestClient(create_app())

    denied = client.post(
        "/personas/Elena Rodriguez/memory",
        json={"memory_type": "note", "content": "Blocked by brand review"},
    )
    assert denied.status_code == 403

    monkeypatch.setenv("M365_ACTOR_HEADER_FALLBACK", "1")
    client = TestClient(create_app())
    accepted = client.post(
        "/personas/Elena Rodriguez/memory",
        headers={"X-User-Email": "owner@smarthausgroup.com"},
        json={"memory_type": "note", "content": "Blocked by brand review"},
    )

    assert accepted.status_code == 200
    assert accepted.json()["memory"]["created_by"] == "owner@smarthausgroup.com"


def test_e5e_dashboard_projects_memory_and_history_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    app = FastAPI()
    app.include_router(agent_dashboard_router)
    client = TestClient(app)

    client.post("/api/agents/m365-administrator/tasks", json={"title": "Review guest access"})
    client.post(
        "/api/agents/m365-administrator/memory",
        json={"memory_type": "fact", "content": "Guest access review is due Friday"},
    )

    status_response = client.get("/api/agents/m365-administrator/status")
    history_response = client.get("/api/agents/m365-administrator/history")

    assert status_response.status_code == 200
    assert history_response.status_code == 200
    assert status_response.json()["memory_count"] == 1
    assert history_response.json()["history"]["event_count"] >= 2
