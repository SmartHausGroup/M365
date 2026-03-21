from __future__ import annotations

import os
from typing import Any

from fastapi.testclient import TestClient
from provisioning_api.main import app

client = TestClient(app)


def _post(url: str, payload: dict[str, Any]) -> None:
    r = client.post(url, json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "accepted"
    assert data["id"]


def test_tai_and_lattice_endpoints() -> None:
    _post("/api/tai/research", {"title": "TAI Note", "description": "desc", "tags": ["a"]})
    _post("/api/tai/performance", {"benchmark": "b1", "value": 1.23, "unit": "ms"})
    _post("/api/lattice/research", {"title": "LATTICE", "description": "d", "tags": []})
    _post("/api/lattice/aios", {"feature": "planning", "status": "wip"})


def test_website_and_research_endpoints() -> None:
    _post(
        "/api/website/updates",
        {"change": "home page", "repo": "https://github.com/smarthaus/site"},
    )
    _post("/api/research/collaboration", {"topic": "TAI+LATTICE", "summary": "sync"})


def test_sigma_and_c2_endpoints() -> None:
    _post("/api/sigma/performance", {"strategy": "S1", "sharpe": 1.0, "pnl": 10.0, "period": "1d"})
    _post("/api/c2/security", {"status": "green", "details": "ok"})


def test_marketing_patents_infra_clients() -> None:
    _post("/api/marketing/leads", {"source": "web", "contact": "lead@example.com"})
    _post(
        "/api/patents/applications",
        {"title": "TAI Memory", "jurisdiction": "US", "status": "draft"},
    )
    _post("/api/infrastructure/cicd", {"pipeline": "api", "status": "pass", "change": "#42"})
    _post("/api/clients/projects", {"client": "Acme", "project": "AI", "description": "demo"})


def test_m365_instruction_gated_idempotent() -> None:
    os.environ["ALLOW_M365_MUTATIONS"] = "false"
    payload = {
        "action": "create_site",
        "params": {"display_name": "Test Site", "mail_nickname": "test-site"},
    }
    headers = {"Idempotency-Key": "test-m365-instruction"}
    r1 = client.post("/api/m365/instruction", json=payload, headers=headers)
    assert r1.status_code == 200
    data1 = r1.json()
    assert data1["ok"] is False
    assert data1["error"] == "m365_mutations_disabled"
    r2 = client.post("/api/m365/instruction", json=payload, headers=headers)
    assert r2.status_code == 200
    assert r2.json() == data1
