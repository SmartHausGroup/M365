import json

from fastapi.testclient import TestClient
from provisioning_api.main import app

if __name__ == "__main__":
    client = TestClient(app)
    r = client.get("/status")
    print(r.status_code)
    print(json.dumps(r.json(), indent=2))
