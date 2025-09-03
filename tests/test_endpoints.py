from __future__ import annotations

from fastapi.testclient import TestClient

from provisioning_api.main import app

client = TestClient(app)


def _post(url: str, payload: dict) -> None:
    r = client.post(url, json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "accepted"
    assert data["id"]


def test_tai_and_lattice_endpoints():
    _post("/api/tai/research", {"title": "TAI Note", "description": "desc", "tags": ["a"]})
    _post("/api/tai/performance", {"benchmark": "b1", "value": 1.23, "unit": "ms"})
    _post("/api/lattice/research", {"title": "LATTICE", "description": "d", "tags": []})
    _post("/api/lattice/aios", {"feature": "planning", "status": "wip"})


def test_website_and_research_endpoints():
    _post(
        "/api/website/updates",
        {"change": "home page", "repo": "https://github.com/smarthaus/site"},
    )
    _post("/api/research/collaboration", {"topic": "TAI+LATTICE", "summary": "sync"})


def test_sigma_and_c2_endpoints():
    _post("/api/sigma/performance", {"strategy": "S1", "sharpe": 1.0, "pnl": 10.0, "period": "1d"})
    _post("/api/c2/security", {"status": "green", "details": "ok"})


def test_marketing_patents_infra_clients():
    _post("/api/marketing/leads", {"source": "web", "contact": "lead@example.com"})
    _post(
        "/api/patents/applications",
        {"title": "TAI Memory", "jurisdiction": "US", "status": "draft"},
    )
    _post("/api/infrastructure/cicd", {"pipeline": "api", "status": "pass", "change": "#42"})
    _post("/api/clients/projects", {"client": "Acme", "project": "AI", "description": "demo"})
