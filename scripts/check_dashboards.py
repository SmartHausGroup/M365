from fastapi.testclient import TestClient
from provisioning_api.main import app

if __name__ == "__main__":
    c = TestClient(app)
    paths = ["/api/agents/dashboard", "/api/email/dashboard"]
    for path in paths:
        r = c.get(path, headers={"accept": "text/html"})
        print(path, r.status_code, len(r.text))
