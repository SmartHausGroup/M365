from fastapi.testclient import TestClient
from provisioning_api.main import app

if __name__ == "__main__":
    c = TestClient(app)
    r = c.get("/api/agents/status")
    print("/api/agents/status", r.status_code)
    data = r.json()
    agents = data.get("agents", {})
    print("total_agents:", data.get("total_agents"), "departments:", data.get("departments"))
    # Show a few samples
    shown = 0
    for aid, info in agents.items():
        print(aid, "->", info.get("department"))
        shown += 1
        if shown >= 5:
            break
    # Flag any unknown departments
    unknown = [aid for aid, info in agents.items() if (info.get("department") == "unknown")]
    print("unknown_department_count:", len(unknown))

