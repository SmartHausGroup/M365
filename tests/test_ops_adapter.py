import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi.testclient import TestClient

from ops_adapter.app import create_app

# Load environment variables for testing
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def test_health():
    app = create_app()
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_action_with_fail_open_allows():
    # Set up environment for testing
    os.environ["OPA_FAIL_OPEN"] = "true"
    os.environ["GRAPH_STUB_MODE"] = "false"  # Use real Graph API
    
    app = create_app()
    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/user.provision",
        json={"params": {"userPrincipalName": "jdoe@example.com", "displayName": "John Doe"}},
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") in ("ok", "pending")
