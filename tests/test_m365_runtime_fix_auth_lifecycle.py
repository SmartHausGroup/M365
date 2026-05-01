"""Fix R3: full auth lifecycle + token-store-backed readiness.

Plan: plan:m365-standalone-graph-runtime-integration-pack-fix:R3
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402
from m365_runtime.launcher import build_app, plan_launch  # noqa: E402


# ---------------------------------------------------------------------------
# In-memory token store backend so the launcher can run on CI without macOS
# Keychain. The real production backend remains Keychain.
# ---------------------------------------------------------------------------
class _MemoryTokenStore:
    backend = "memory"
    keychain_service = "ai.smarthaus.m365.test"
    encrypted_pack_local_allowed = False
    pack_local_path = None

    def __init__(self) -> None:
        self._values: dict[str, str] = {}

    def put(self, key: str, value: str) -> None:
        self._values[key] = value

    def get(self, key: str) -> str | None:
        return self._values.get(key)

    def clear(self, key: str) -> None:
        self._values.pop(key, None)


@pytest.fixture
def installed_pack_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Stage an installed-pack layout the launcher can resolve from."""
    repo_root = Path(__file__).resolve().parent.parent
    pack = tmp_path / "pack"
    (pack / "registry").mkdir(parents=True)
    (pack / "m365_runtime").mkdir()
    shutil.copyfile(repo_root / "registry" / "agents.yaml", pack / "registry" / "agents.yaml")
    shutil.copyfile(
        repo_root / "src" / "ucp_m365_pack" / "setup_schema.json", pack / "setup_schema.json"
    )
    (pack / "manifest.json").write_text("{}", encoding="utf-8")
    (pack / "m365_runtime" / "marker").write_text("ok", encoding="utf-8")
    return pack


@pytest.fixture
def memory_store(monkeypatch: pytest.MonkeyPatch) -> _MemoryTokenStore:
    store = _MemoryTokenStore()

    monkeypatch.setattr(
        "m365_runtime.auth.token_store.TokenStore.from_setup", classmethod(lambda cls, s, r: store)
    )
    return store


def _setup_env_pkce() -> dict[str, str]:
    return {
        "M365_TENANT_ID": "11111111-1111-1111-1111-111111111111",
        "M365_CLIENT_ID": "22222222-2222-2222-2222-222222222222",
        "M365_AUTH_MODE": "auth_code_pkce",
        "M365_SERVICE_ACTOR_UPN": "ops@example.com",
        "M365_REDIRECT_URI": "http://127.0.0.1:9301/callback",
        "M365_GRANTED_SCOPES": "User.Read,Sites.Read.All,Organization.Read.All",
        "M365_TOKEN_STORE": "keychain",
    }


def _setup_env_device() -> dict[str, str]:
    env = _setup_env_pkce()
    env["M365_AUTH_MODE"] = "device_code"
    env.pop("M365_REDIRECT_URI", None)
    return env


def _setup_env_app_only() -> dict[str, str]:
    env = _setup_env_pkce()
    env["M365_AUTH_MODE"] = "app_only_secret"
    env["M365_APP_ONLY_CLIENT_SECRET_REF"] = "kc::ai.smarthaus.m365::client_secret"
    env.pop("M365_REDIRECT_URI", None)
    return env


def _make_client(
    installed_pack_root: Path,
    env: dict[str, str],
    oauth_handler: Callable[[httpx.Request], httpx.Response],
    graph_handler: Callable[[httpx.Request], httpx.Response],
) -> tuple[TestClient, Any]:
    plan = plan_launch(env=env)
    plan = plan.__class__(
        outcome=plan.outcome,
        installed_root=installed_pack_root,
        setup=plan.setup,
        listen_host=plan.listen_host,
        listen_port=plan.listen_port,
        detail=plan.detail,
    )
    app = build_app(
        plan,
        oauth_transport=httpx.MockTransport(oauth_handler),
        graph_transport=httpx.MockTransport(graph_handler),
    )
    return TestClient(app), plan


def _form(request: httpx.Request) -> dict[str, str]:
    parsed = parse_qs(request.content.decode("utf-8"))
    return {key: values[-1] for key, values in parsed.items()}


def test_pkce_auth_lifecycle_completes_through_http_endpoints(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    def oauth_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth2/v2.0/token"):
            return httpx.Response(
                200, json={"access_token": "AT", "refresh_token": "RT", "expires_in": 3600}
            )
        return httpx.Response(404, json={"error": "unexpected"})

    def graph_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1.0/organization":
            return httpx.Response(200, json={"value": [{"id": "tenant"}]})
        return httpx.Response(404, json={"error": "unhandled"})

    client, _ = _make_client(installed_pack_root, _setup_env_pkce(), oauth_handler, graph_handler)

    status_before = client.get("/v1/auth/status").json()
    assert status_before["state"] == "auth_required"

    start = client.post("/v1/auth/start", json={}).json()
    assert start["state"] == "auth_started"
    assert "code_challenge" in start["authorize_url"]
    pkce_state = start["expected_state"]

    check = client.post("/v1/auth/check", json={"code": "AUTH_CODE", "state": pkce_state}).json()
    assert check["state"] == "signed_in"
    assert "access_token" not in str(check.get("audit", {}))  # redacted
    assert memory_store.get("token_expires_at") is not None

    status_after = client.get("/v1/auth/status").json()
    assert status_after["state"] == "signed_in"

    readiness = client.get("/v1/health/readiness").json()
    assert readiness["state"]["state"] == "ready"
    assert readiness["state"]["label"] == "success"
    assert readiness["vector"]["auth"] is True
    assert readiness["vector"]["tok"] is True
    assert readiness["vector"]["graph"] is True


def test_pkce_check_rejects_state_mismatch(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    def oauth_handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access_token": "AT", "expires_in": 3600})

    def graph_handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"value": []})

    client, _ = _make_client(installed_pack_root, _setup_env_pkce(), oauth_handler, graph_handler)
    client.post("/v1/auth/start", json={})
    response = client.post("/v1/auth/check", json={"code": "x", "state": "wrong_state"}).json()
    assert response["state"] == "auth_required"
    assert response["reason"] == "pkce_state_mismatch"


def test_device_code_lifecycle_pending_then_signed_in(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    poll_calls = {"n": 0}

    def oauth_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/devicecode"):
            return httpx.Response(
                200,
                json={
                    "device_code": "DC",
                    "user_code": "ABC-DEF",
                    "verification_uri": "https://microsoft.com/devicelogin",
                    "expires_in": 900,
                    "interval": 5,
                },
            )
        if request.url.path.endswith("/oauth2/v2.0/token"):
            poll_calls["n"] += 1
            if poll_calls["n"] == 1:
                return httpx.Response(400, json={"error": "authorization_pending"})
            return httpx.Response(200, json={"access_token": "AT", "expires_in": 3600})
        return httpx.Response(404)

    def graph_handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"value": []})

    client, _ = _make_client(installed_pack_root, _setup_env_device(), oauth_handler, graph_handler)
    start = client.post("/v1/auth/start", json={}).json()
    assert start["state"] == "device_code_pending"
    assert start["user_code"] == "ABC-DEF"

    pending = client.post("/v1/auth/check", json={}).json()
    assert pending["state"] == "device_code_pending"

    final = client.post("/v1/auth/check", json={}).json()
    assert final["state"] == "signed_in"

    readiness = client.get("/v1/health/readiness").json()
    assert readiness["state"]["state"] == "ready"


def test_app_only_secret_resolves_secret_from_token_store(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    memory_store.put("kc::ai.smarthaus.m365::client_secret", "REAL_CLIENT_SECRET")

    def oauth_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth2/v2.0/token"):
            return httpx.Response(200, json={"access_token": "AT", "expires_in": 3600})
        return httpx.Response(404)

    def graph_handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"value": []})

    client, _ = _make_client(
        installed_pack_root, _setup_env_app_only(), oauth_handler, graph_handler
    )
    start = client.post("/v1/auth/start", json={}).json()
    assert start["state"] == "signed_in"
    readiness = client.get("/v1/health/readiness").json()
    assert readiness["state"]["state"] == "ready"


def test_auth_clear_returns_to_auth_required_and_clears_store(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    def oauth_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"access_token": "AT", "refresh_token": "RT", "expires_in": 3600}
        )

    def graph_handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"value": []})

    client, _ = _make_client(installed_pack_root, _setup_env_pkce(), oauth_handler, graph_handler)
    start = client.post("/v1/auth/start", json={}).json()
    client.post("/v1/auth/check", json={"code": "x", "state": start["expected_state"]})

    cleared = client.post("/v1/auth/clear").json()
    assert cleared["state"] == "auth_required"
    assert client.get("/v1/auth/status").json()["state"] == "auth_required"
    assert memory_store.get("access_token") is None
    assert memory_store.get("refresh_token") is None


def test_auth_audit_does_not_leak_tokens(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    def oauth_handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"access_token": "VERY_SECRET", "refresh_token": "RT", "expires_in": 3600}
        )

    def graph_handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"value": []})

    client, _ = _make_client(installed_pack_root, _setup_env_pkce(), oauth_handler, graph_handler)
    start = client.post("/v1/auth/start", json={}).json()
    check = client.post(
        "/v1/auth/check", json={"code": "x", "state": start["expected_state"]}
    ).json()
    audit_blob = str(check.get("audit", {}))
    assert "VERY_SECRET" not in audit_blob


def test_invoke_action_uses_stored_access_token(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    captured: dict[str, str] = {}

    def oauth_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access_token": "AT_STORED", "expires_in": 3600})

    def graph_handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("Authorization", "")
        return httpx.Response(200, json={"id": "tenant", "displayName": "Acme"})

    client, _ = _make_client(
        installed_pack_root, _setup_env_app_only(), oauth_handler, graph_handler
    )
    memory_store.put("kc::ai.smarthaus.m365::client_secret", "S")
    client.post("/v1/auth/start", json={})
    invoke = client.post(
        "/v1/actions/graph.org_profile/invoke", json={"actor": "ops@example.com"}
    ).json()
    assert invoke["status_class"] == "success"
    assert captured["auth"] == "Bearer AT_STORED"


def test_startup_refreshes_stored_refresh_token_without_user_reauth(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    memory_store.put("access_token", "AT_STALE")
    memory_store.put("refresh_token", "RT_STORED")
    captured: dict[str, str] = {}

    def oauth_handler(request: httpx.Request) -> httpx.Response:
        body = _form(request)
        captured["grant_type"] = body.get("grant_type", "")
        captured["refresh_token"] = body.get("refresh_token", "")
        return httpx.Response(200, json={"access_token": "AT_REFRESHED", "expires_in": 3600})

    def graph_handler(request: httpx.Request) -> httpx.Response:
        captured["graph_auth"] = request.headers.get("Authorization", "")
        return httpx.Response(200, json={"id": "tenant", "displayName": "Acme"})

    client, _ = _make_client(installed_pack_root, _setup_env_device(), oauth_handler, graph_handler)

    assert captured["grant_type"] == "refresh_token"
    assert captured["refresh_token"] == "RT_STORED"
    assert client.get("/v1/auth/status").json()["state"] == "signed_in"
    assert memory_store.get("access_token") == "AT_REFRESHED"
    assert memory_store.get("refresh_token") == "RT_STORED"
    assert memory_store.get("token_expires_at") is not None

    invoke = client.post("/v1/actions/graph.me/invoke", json={"actor": "ops@example.com"}).json()
    assert invoke["status_class"] == "success"
    assert captured["graph_auth"] == "Bearer AT_REFRESHED"


def test_startup_refresh_failure_is_auth_required_and_does_not_use_stale_token(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    memory_store.put("access_token", "AT_STALE")
    memory_store.put("refresh_token", "RT_STORED")
    graph_calls = {"count": 0}

    def oauth_handler(request: httpx.Request) -> httpx.Response:
        body = _form(request)
        assert body.get("grant_type") == "refresh_token"
        return httpx.Response(400, json={"error": "invalid_grant"})

    def graph_handler(_request: httpx.Request) -> httpx.Response:
        graph_calls["count"] += 1
        return httpx.Response(200, json={"unexpected": True})

    client, _ = _make_client(installed_pack_root, _setup_env_device(), oauth_handler, graph_handler)

    status = client.get("/v1/auth/status").json()
    assert status["state"] == "auth_required"
    assert status["reason"] == "refresh_failed"

    invoke = client.post("/v1/actions/graph.me/invoke", json={"actor": "ops@example.com"}).json()
    assert invoke["status_class"] == "auth_required"
    assert graph_calls["count"] == 0


def test_stored_access_without_expiry_or_refresh_is_not_signed_in(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    memory_store.put("access_token", "AT_UNKNOWN_EXPIRY")

    def oauth_handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("refresh must not be attempted without refresh token")

    def graph_handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("Graph must not be called with unknown-expiry access token")

    client, _ = _make_client(installed_pack_root, _setup_env_device(), oauth_handler, graph_handler)
    status = client.get("/v1/auth/status").json()
    assert status["state"] == "auth_required"
    assert status["reason"] in {
        "stored_access_token_unusable",
        "lazy_refresh:refresh_token_missing",
    }


def test_unexpired_stored_access_token_can_hydrate_without_refresh(
    installed_pack_root: Path,
    memory_store: _MemoryTokenStore,
) -> None:
    import time

    memory_store.put("access_token", "AT_UNEXPIRED")
    memory_store.put("token_expires_at", str(int(time.time()) + 3600))
    captured: dict[str, str] = {}

    def oauth_handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("fresh stored access token should not refresh")

    def graph_handler(request: httpx.Request) -> httpx.Response:
        captured["graph_auth"] = request.headers.get("Authorization", "")
        return httpx.Response(200, json={"id": "tenant"})

    client, _ = _make_client(installed_pack_root, _setup_env_device(), oauth_handler, graph_handler)
    assert client.get("/v1/auth/status").json()["state"] == "signed_in"
    invoke = client.post("/v1/actions/graph.me/invoke", json={"actor": "ops@example.com"}).json()
    assert invoke["status_class"] == "success"
    assert captured["graph_auth"] == "Bearer AT_UNEXPIRED"
