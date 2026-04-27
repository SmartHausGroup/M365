from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest
from ucp_m365_pack.client import (
    LEGACY_ACTION_TO_RUNTIME_ACTION,
    M365ExecutionError,
    _installed_pack_root,
    _stub_execute,
    execute_m365_action,
    get_agent_config,
    map_legacy_action_to_runtime,
    routing_snapshot,
    validate_agent_action,
)


@pytest.fixture
def _bundle_with_repo_registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Stage a bundle root that contains a copy of the repo registry."""
    import shutil

    import ucp_m365_pack.client as client_mod

    repo_registry = Path(__file__).resolve().parent.parent / "registry" / "agents.yaml"
    bundle_root = tmp_path / "installed-pack"
    (bundle_root / "ucp_m365_pack").mkdir(parents=True)
    (bundle_root / "registry").mkdir(parents=True)
    shutil.copyfile(repo_registry, bundle_root / "registry" / "agents.yaml")
    for var in (
        "M365_REPO_ROOT",
        "SMARTHAUS_M365_REPO_ROOT",
        "M365_REGISTRY_PATH",
        "UCP_ROOT",
        "REPOS_ROOT",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(client_mod, "_MODULE_DIR", str(bundle_root / "ucp_m365_pack"))
    monkeypatch.setattr(client_mod, "_REGISTRY", None)
    return bundle_root


def test_validate_known_agent_action(_bundle_with_repo_registry: Path) -> None:
    ok, reason = validate_agent_action("m365-administrator", "users.read")
    assert ok is True
    assert reason == ""


def test_validate_unknown_agent(_bundle_with_repo_registry: Path) -> None:
    ok, reason = validate_agent_action("totally-fake-agent", "anything")
    assert ok is False
    assert "unknown_agent" in reason


def test_get_agent_config_exists(_bundle_with_repo_registry: Path) -> None:
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

    def _http_execute(*_args: object, **_kwargs: object) -> None:
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


def test_missing_service_fails_closed_without_runtime_or_legacy_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("M365_RUNTIME_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_RUNTIME_URL", raising=False)
    monkeypatch.delenv("M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("GRAPH_STUB_MODE", raising=False)

    with pytest.raises(
        M365ExecutionError,
        match="No configured M365 runtime or service URL",
    ):
        execute_m365_action("m365-administrator", "users.read", {"top": 1})


def test_installed_pack_root_resolves_from_module_location(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ucp_m365_pack.client as client_mod

    bundle_root = tmp_path / "installed-pack"
    (bundle_root / "ucp_m365_pack").mkdir(parents=True)
    (bundle_root / "registry").mkdir(parents=True)
    (bundle_root / "registry" / "agents.yaml").write_text("agents: {}\n", encoding="utf-8")

    for var in (
        "M365_REPO_ROOT",
        "SMARTHAUS_M365_REPO_ROOT",
        "M365_REGISTRY_PATH",
        "UCP_ROOT",
        "REPOS_ROOT",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(client_mod, "_MODULE_DIR", str(bundle_root / "ucp_m365_pack"))

    assert _installed_pack_root() == bundle_root.resolve()


def test_get_agent_config_reads_only_installed_registry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ucp_m365_pack.client as client_mod

    bundle_root = tmp_path / "installed-pack"
    (bundle_root / "ucp_m365_pack").mkdir(parents=True)
    (bundle_root / "registry").mkdir(parents=True)
    (bundle_root / "registry" / "agents.yaml").write_text(
        "agents:\n  m365-administrator:\n    allowed_actions:\n      - directory.org\n",
        encoding="utf-8",
    )

    for var in (
        "M365_REPO_ROOT",
        "SMARTHAUS_M365_REPO_ROOT",
        "M365_REGISTRY_PATH",
        "UCP_ROOT",
        "REPOS_ROOT",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(client_mod, "_MODULE_DIR", str(bundle_root / "ucp_m365_pack"))
    monkeypatch.setattr(client_mod, "_REGISTRY", None)

    cfg = get_agent_config("m365-administrator")
    assert cfg is not None
    assert cfg["allowed_actions"] == ["directory.org"]


def test_get_agent_config_does_not_honor_repo_root_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """F1 regression: source-repo env vars are no longer consulted."""
    import ucp_m365_pack.client as client_mod

    fake_repo_root = tmp_path / "fake-source-repo"
    (fake_repo_root / "registry").mkdir(parents=True)
    (fake_repo_root / "registry" / "agents.yaml").write_text(
        "agents:\n  m365-administrator:\n    allowed_actions:\n      - directory.org\n",
        encoding="utf-8",
    )

    bundle_root = tmp_path / "installed-pack"
    (bundle_root / "ucp_m365_pack").mkdir(parents=True)
    # No registry inside the installed pack.

    monkeypatch.setenv("M365_REPO_ROOT", str(fake_repo_root))
    monkeypatch.setenv("SMARTHAUS_M365_REPO_ROOT", str(fake_repo_root))
    monkeypatch.setenv("M365_REGISTRY_PATH", str(fake_repo_root / "registry" / "agents.yaml"))
    monkeypatch.setattr(client_mod, "_MODULE_DIR", str(bundle_root / "ucp_m365_pack"))
    monkeypatch.setattr(client_mod, "_REGISTRY", None)

    cfg = get_agent_config("m365-administrator")
    assert cfg is None  # registry not present inside installed pack -> nothing loaded


def test_map_legacy_action_routes_known_aliases() -> None:
    expected_pairs = (
        ("directory.org", "graph.org_profile"),
        ("users.read", "graph.users.list"),
        ("users.list", "graph.users.list"),
        ("me.read", "graph.me"),
        ("groups.read", "graph.groups.list"),
        ("sites.root", "graph.sites.root"),
        ("sites.search", "graph.sites.search"),
        ("teams.read", "graph.teams.list"),
        ("drives.list", "graph.drives.list"),
        ("mail.health", "graph.mail.health"),
        ("calendar.health", "graph.calendar.health"),
        ("servicehealth.read", "graph.servicehealth"),
    )
    for legacy, expected in expected_pairs:
        assert legacy in LEGACY_ACTION_TO_RUNTIME_ACTION
        assert map_legacy_action_to_runtime(legacy) == expected


def test_map_legacy_action_passes_runtime_ids_through() -> None:
    assert map_legacy_action_to_runtime("graph.org_profile") == "graph.org_profile"
    assert map_legacy_action_to_runtime("graph.users.list") == "graph.users.list"


def test_map_legacy_action_passes_unknown_actions_through_for_runtime_to_fence() -> None:
    assert map_legacy_action_to_runtime("totally.unknown") == "totally.unknown"
    assert map_legacy_action_to_runtime("users.create") == "users.create"


def test_runtime_url_path_invokes_mapped_action(monkeypatch: pytest.MonkeyPatch) -> None:
    import ucp_m365_pack.client as client_mod

    monkeypatch.setenv("SMARTHAUS_M365_RUNTIME_URL", "http://127.0.0.1:9300")
    monkeypatch.delenv("M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.setenv("M365_SERVICE_ACTOR_UPN", "ops@example.com")

    captured: dict[str, object] = {}

    def fake_invoke(
        runtime_url: str,
        action_id: str,
        params: dict[str, object],
        correlation_id: str,
        actor_identity: str | None = None,
    ) -> dict[str, object]:
        captured.update({"runtime_url": runtime_url, "action_id": action_id, "params": params})
        return {"status_class": "success", "echo": action_id}

    monkeypatch.setattr(client_mod, "_http_runtime_invoke", fake_invoke)
    result = client_mod.execute_m365_action("m365-administrator", "users.read", {"top": 1})
    assert result["status_class"] == "success"
    assert captured["action_id"] == "graph.users.list"
    assert captured["runtime_url"] == "http://127.0.0.1:9300"
