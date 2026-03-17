from __future__ import annotations

from fastapi.testclient import TestClient

from provisioning_api.main import app


def test_agent_task_and_instruction_flow(tmp_path, monkeypatch):
    # Isolate data dir
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    client = TestClient(app)

    agent_id = "m365-administrator"

    # Status (empty)
    r = client.get(f"/api/agents/{agent_id}/status")
    assert r.status_code == 200
    data = r.json()
    assert data["agent"] == agent_id
    assert data["tasks"]["total"] == 0

    # Create a task
    r = client.post(
        f"/api/agents/{agent_id}/tasks",
        json={"title": "Onboard user", "priority": "high"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "accepted"
    task_id = body["id"]

    # List tasks
    r = client.get(f"/api/agents/{agent_id}/tasks")
    assert r.status_code == 200
    tasks = r.json()
    assert any(t["id"] == task_id for t in tasks)

    # Update task
    r = client.put(
        f"/api/agents/{agent_id}/tasks/{task_id}",
        json={"status": "in_progress", "percent": 20},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    # Instruction
    r = client.post(
        f"/api/agents/{agent_id}/instructions",
        json={"instruction": "Create user jdoe@example.com"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "accepted"

    # Performance
    r = client.get(f"/api/agents/{agent_id}/performance")
    assert r.status_code == 200
    perf = r.json()["metrics"]
    assert "total" in perf

    # Dry-run execute (no mutations)
    r = client.post(
        f"/api/agents/{agent_id}/execute",
        json={"action": "users.read", "params": {"userPrincipalName": "test@example.com"}},
    )
    assert r.status_code == 200
    exec_body = r.json()
    # default dry-run without OPS_ADAPTER_URL
    assert exec_body["status"] in ("queued", "ok")

