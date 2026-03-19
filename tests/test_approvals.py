from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

import ops_adapter.approvals as approvals_module
from smarthaus_common.tenant_config import reload_tenant_config


@pytest.fixture
def tenant_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-alpha.yaml").write_text(
        """
tenant:
  id: tenant-alpha
  display_name: SMARTHAUS
  domain: smarthausgroup.com
azure:
  tenant_id: tenant-guid-alpha
  client_id: client-alpha
  client_secret: secret-alpha
auth:
  mode: app_only
governance:
  approvals_site_url: https://smarthausgroup.sharepoint.com/sites/operations
  approvals_list_name: Approvals
permission_tiers:
  default_tier: standard_user
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "tenant-alpha")
    monkeypatch.delenv("APPROVALS_SITE_URL", raising=False)
    monkeypatch.delenv("APPROVALS_SITE_ID", raising=False)
    monkeypatch.delenv("APPROVALS_LIST_ID", raising=False)
    monkeypatch.delenv("APPROVALS_LIST_NAME", raising=False)
    reload_tenant_config()
    yield
    reload_tenant_config()


def test_graph_approvals_store_uses_tenant_contract_target(
    tenant_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        approvals_module.GraphApprovalsStore,
        "_resolve_site_id",
        lambda self, site_url: "site-123",
    )
    monkeypatch.setattr(
        approvals_module.GraphApprovalsStore,
        "_resolve_list_id",
        lambda self, site_id, list_name: "list-456",
    )

    store = approvals_module.GraphApprovalsStore()

    assert store.site_url == "https://smarthausgroup.sharepoint.com/sites/operations"
    assert store.site_id == "site-123"
    assert store.list_name == "Approvals"
    assert store.list_id == "list-456"


def test_graph_approvals_store_uses_graph_token_provider(
    tenant_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        approvals_module.GraphApprovalsStore,
        "_resolve_site_id",
        lambda self, site_url: "site-123",
    )
    monkeypatch.setattr(
        approvals_module.GraphApprovalsStore,
        "_resolve_list_id",
        lambda self, site_id, list_name: "list-456",
    )

    captured: dict[str, Any] = {}

    class _DummyProvider:
        def get_app_token(self) -> str:
            return "token-alpha"

    def _provider_factory() -> _DummyProvider:
        captured["tenant_id"] = approvals_module._selected_tenant_config().tenant.id
        return _DummyProvider()

    monkeypatch.setattr(approvals_module, "_build_graph_token_provider", _provider_factory)

    store = approvals_module.GraphApprovalsStore()
    client = store._graph()
    try:
        assert client.headers["Authorization"] == "Bearer token-alpha"
    finally:
        client.close()

    assert captured["tenant_id"] == "tenant-alpha"


def test_approvals_store_promotes_tenant_contract_target(
    tenant_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        approvals_module.GraphApprovalsStore,
        "_resolve_site_id",
        lambda self, site_url: "site-123",
    )
    monkeypatch.setattr(
        approvals_module.GraphApprovalsStore,
        "_resolve_list_id",
        lambda self, site_id, list_name: "list-456",
    )

    store = approvals_module.ApprovalsStore({})

    assert isinstance(store, approvals_module.GraphApprovalsStore)
