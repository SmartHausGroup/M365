from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from ops_adapter import actions
from smarthaus_common.auth_model import reload_auth_model_registry, resolve_action_auth
from smarthaus_common.tenant_config import reload_tenant_config


@pytest.fixture(autouse=True)
def _reset_auth_registry() -> None:
    reload_auth_model_registry()
    reload_tenant_config()
    yield
    reload_auth_model_registry()
    reload_tenant_config()


def test_auth_model_v2_defaults_directory_actions_to_app_only() -> None:
    resolution = resolve_action_auth("m365-administrator", "list_users", {})

    assert resolution.auth_class == "app_only"
    assert resolution.prefer_delegated is False
    assert resolution.executor_domain == "directory"


def test_auth_model_v2_prefers_delegated_for_implicit_mail_self_context() -> None:
    resolution = resolve_action_auth("email-processing-agent", "mail.send", {})

    assert resolution.auth_class == "hybrid"
    assert resolution.prefer_delegated is True
    assert resolution.executor_domain == "messaging"


def test_auth_model_v2_uses_app_only_for_explicit_mail_sender() -> None:
    resolution = resolve_action_auth(
        "outreach-coordinator",
        "mail.send",
        {"from": "sender@smarthausgroup.com"},
    )

    assert resolution.auth_class == "hybrid"
    assert resolution.prefer_delegated is False


def test_auth_model_v2_prefers_delegated_for_files_without_context() -> None:
    resolution = resolve_action_auth("m365-administrator", "files.list", {})

    assert resolution.auth_class == "hybrid"
    assert resolution.prefer_delegated is True
    assert resolution.executor_domain == "sharepoint"


def test_auth_model_v2_uses_app_only_for_files_with_site_context() -> None:
    resolution = resolve_action_auth(
        "m365-administrator",
        "files.list",
        {"siteId": "site-123"},
    )

    assert resolution.auth_class == "hybrid"
    assert resolution.prefer_delegated is False


def test_mail_list_uses_me_endpoint_when_hybrid_self_context_is_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_graph_request(
        method: str,
        url: str,
        correlation_id: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        prefer_delegated: bool | None = None,
    ) -> dict[str, Any]:
        captured.update(
            {
                "method": method,
                "url": url,
                "correlation_id": correlation_id,
                "json_body": json_body,
                "params": params,
                "prefer_delegated": prefer_delegated,
            }
        )
        return {"value": []}

    monkeypatch.setattr(actions, "_stub_mode", lambda: False)
    monkeypatch.setattr(actions, "_can_use_me_endpoint", lambda: True)
    monkeypatch.setattr(actions, "_graph_request", fake_graph_request)

    result = asyncio.run(actions.mail_list({}, "corr-mail-list"))

    assert result == {"messages": [], "count": 0}
    assert captured["url"] == f"{actions.GRAPH_BASE}/me/messages"
    assert captured["prefer_delegated"] is True


def test_mail_list_uses_user_endpoint_when_explicit_context_is_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_graph_request(
        method: str,
        url: str,
        correlation_id: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        prefer_delegated: bool | None = None,
    ) -> dict[str, Any]:
        captured.update(
            {
                "method": method,
                "url": url,
                "correlation_id": correlation_id,
                "json_body": json_body,
                "params": params,
                "prefer_delegated": prefer_delegated,
            }
        )
        return {"value": []}

    monkeypatch.setattr(actions, "_stub_mode", lambda: False)
    monkeypatch.setattr(actions, "_can_use_me_endpoint", lambda: True)
    monkeypatch.setattr(actions, "_graph_request", fake_graph_request)

    result = asyncio.run(
        actions.mail_list({"userId": "operator@smarthausgroup.com"}, "corr-mail-user")
    )

    assert result == {"messages": [], "count": 0}
    assert captured["url"] == f"{actions.GRAPH_BASE}/users/operator@smarthausgroup.com/messages"
    assert captured["prefer_delegated"] is False


def test_files_list_uses_me_drive_when_hybrid_self_context_is_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_graph_request(
        method: str,
        url: str,
        correlation_id: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        prefer_delegated: bool | None = None,
    ) -> dict[str, Any]:
        captured.update(
            {
                "method": method,
                "url": url,
                "correlation_id": correlation_id,
                "json_body": json_body,
                "params": params,
                "prefer_delegated": prefer_delegated,
            }
        )
        return {"value": []}

    monkeypatch.setattr(actions, "_stub_mode", lambda: False)
    monkeypatch.setattr(actions, "_can_use_me_endpoint", lambda: True)
    monkeypatch.setattr(actions, "_graph_request", fake_graph_request)

    result = asyncio.run(actions.files_list({}, "corr-files-list"))

    assert result == {"files": [], "count": 0}
    assert captured["url"] == f"{actions.GRAPH_BASE}/me/drive/root/children"
    assert captured["prefer_delegated"] is True


def test_drives_list_uses_primary_site_when_self_context_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-alpha.yaml").write_text(
        """
tenant:
  id: tenant-alpha
org:
  primary_site_id: tenant-primary-site
auth:
  mode: app_only
""".strip()
        + "\n",
        encoding="utf-8",
    )

    captured: dict[str, Any] = {}

    async def fake_graph_request(
        method: str,
        url: str,
        correlation_id: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        prefer_delegated: bool | None = None,
    ) -> dict[str, Any]:
        captured.update(
            {
                "method": method,
                "url": url,
                "correlation_id": correlation_id,
                "json_body": json_body,
                "params": params,
                "prefer_delegated": prefer_delegated,
            }
        )
        return {"value": []}

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "tenant-alpha")
    monkeypatch.setattr(actions, "_stub_mode", lambda: False)
    monkeypatch.setattr(actions, "_can_use_me_endpoint", lambda: False)
    monkeypatch.setattr(actions, "_graph_request", fake_graph_request)

    result = asyncio.run(actions.drives_list({}, "corr-drives-list"))

    assert result == {"drives": [], "count": 0}
    assert captured["url"] == f"{actions.GRAPH_BASE}/sites/tenant-primary-site/drives"
    assert captured["prefer_delegated"] is False
