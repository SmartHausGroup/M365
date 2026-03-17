from __future__ import annotations

import httpx
import respx
from smarthaus_common.config import AppConfig
from smarthaus_graph.client import GraphClient, GraphTokenProvider


class DummyTP(GraphTokenProvider):
    def __init__(self):
        self._token = None

    def get_token(self) -> str:  # type: ignore[override]
        return "dummy-token"


def test_graph_client_get_org(monkeypatch):
    cfg = AppConfig()
    client = GraphClient(cfg)
    # Inject dummy token provider
    client._token_provider = DummyTP()  # type: ignore[attr-defined]

    with respx.mock(base_url="https://graph.microsoft.com") as mock:
        route = mock.get("/v1.0/organization").mock(
            return_value=httpx.Response(200, json={"value": [{"displayName": "SmartHaus"}]})
        )
        data = client.get_organization()
        assert "value" in data
        assert route.called
