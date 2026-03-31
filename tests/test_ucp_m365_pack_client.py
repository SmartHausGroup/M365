from __future__ import annotations

import os
from unittest import mock

import pytest

from ucp_m365_pack.client import (
    M365ExecutionError,
    _stub_execute,
    execute_m365_action,
    get_agent_config,
    routing_snapshot,
    validate_agent_action,
)


def test_validate_known_agent_action() -> None:
    ok, reason = validate_agent_action("m365-administrator", "users.read")
    assert ok is True
    assert reason == ""


def test_validate_unknown_agent() -> None:
    ok, reason = validate_agent_action("totally-fake-agent", "anything")
    assert ok is False
    assert "unknown_agent" in reason


def test_get_agent_config_exists() -> None:
    cfg = get_agent_config("m365-administrator")
    assert cfg is not None
    assert "users.read" in cfg.get("allowed_actions", [])


def test_stub_executor_shape() -> None:
    result = _stub_execute("test-agent", "test.action", {"key": "value"}, "corr-1")
    assert result["stub"] is True
    assert result["agent"] == "test-agent"
    assert result["action"] == "test.action"


def test_service_mode_prefers_http(monkeypatch: pytest.MonkeyPatch) -> None:
    import ucp_m365_pack.client as client_mod

    monkeypatch.setenv("SMARTHAUS_M365_OPS_ADAPTER_URL", "http://127.0.0.1:9000")

    http_calls: list[tuple[str, str, str]] = []

    def _http_execute(
        base_url: str, agent: str, action: str, _params: dict, _corr: str, _actor: dict | None
    ) -> dict:
        http_calls.append((base_url, agent, action))
        return {"path": "http", "agent": agent, "action": action}

    monkeypatch.setattr(client_mod, "_http_execute", _http_execute)

    result = client_mod.execute_m365_action("m365-administrator", "users.read", {"top": 1})
    snapshot = client_mod.routing_snapshot()

    assert result["path"] == "http"
    assert http_calls == [("http://127.0.0.1:9000", "m365-administrator", "users.read")]
    assert snapshot["selected_live_path"] == "http_service"
    assert snapshot["direct_import_available"] is False
    assert snapshot["direct_import_authority"] == "removed"


def test_configured_service_mode_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    import ucp_m365_pack.client as client_mod

    monkeypatch.setenv("SMARTHAUS_M365_OPS_ADAPTER_URL", "http://127.0.0.1:9000")

    def _http_execute(*_args, **_kwargs):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(client_mod, "_http_execute", _http_execute)

    with pytest.raises(M365ExecutionError, match="Configured M365 service mode failed"):
        client_mod.execute_m365_action("m365-administrator", "users.read", {"top": 1})


@mock.patch.dict(os.environ, {"GRAPH_STUB_MODE": "1"}, clear=False)
def test_stub_mode_returns_stub_without_service_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_OPS_ADAPTER_URL", raising=False)

    result = execute_m365_action(
        "m365-administrator",
        "users.read",
        {"userPrincipalName": "test@smarthaus.ai"},
    )
    snapshot = routing_snapshot()

    assert result["stub"] is True
    assert snapshot["selected_live_path"] == "stub"


def test_missing_service_fails_closed_without_direct_import_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("GRAPH_STUB_MODE", raising=False)

    with pytest.raises(
        M365ExecutionError,
        match="Direct import fallback has been removed",
    ):
        execute_m365_action("m365-administrator", "users.read", {"top": 1})
