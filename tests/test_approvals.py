from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import ops_adapter.approvals as approvals_module
import pytest
from ops_adapter.personas import build_persona_registry
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
        tenant_cfg = approvals_module._selected_tenant_config()
        assert tenant_cfg is not None
        captured["tenant_id"] = tenant_cfg.tenant.id
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


def test_approvals_store_uses_projected_default_executor_from_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-beta.yaml").write_text(
        """
tenant:
  id: tenant-beta
  display_name: SMARTHAUS
azure:
  tenant_id: root-tenant
  client_id: root-client
auth:
  mode: app_only
executors:
  collaboration:
    display_name: SMARTHAUS Collaboration Executor
    domain: collaboration
    azure:
      tenant_id: collab-tenant
      client_id: collab-client
      client_secret: collab-secret
  sharepoint:
    display_name: SMARTHAUS SharePoint Executor
    domain: sharepoint
    capabilities:
      - approvals
      - sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
      client_secret: sharepoint-secret
executor_registry:
  default_executor: collaboration
  routes:
    approvals: sharepoint
    sharepoint: sharepoint
    collaboration: collaboration
governance:
  approvals_site_id: site-123
  approvals_list_id: list-456
  approvals_list_name: Approvals
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "tenant-beta")
    reload_tenant_config()

    captured: dict[str, Any] = {}

    class _DummyProvider:
        def get_app_token(self) -> str:
            return "token-beta"

    def _provider_factory() -> _DummyProvider:
        tenant_cfg = approvals_module._selected_tenant_config()
        approval_cfg = approvals_module._approval_tenant_config()
        assert tenant_cfg is not None
        assert approval_cfg is not None
        captured["default_executor"] = tenant_cfg.default_executor_name
        captured["client_id"] = approval_cfg.azure.client_id
        return _DummyProvider()

    monkeypatch.setattr(approvals_module, "_build_graph_token_provider", _provider_factory)

    store = approvals_module.GraphApprovalsStore()
    client = store._graph()
    client.close()

    assert store.site_id == "site-123"
    assert store.list_id == "list-456"
    assert captured["default_executor"] == "collaboration"
    assert captured["client_id"] == "sharepoint-client"


def test_memory_approvals_store_preserves_persona_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPROVAL_SERVICE_URL", raising=False)
    monkeypatch.delenv("APPROVALS_SERVICE_URL", raising=False)
    monkeypatch.delenv("APPROVALS_SITE_URL", raising=False)
    monkeypatch.delenv("APPROVALS_SITE_ID", raising=False)
    monkeypatch.delenv("APPROVALS_LIST_ID", raising=False)
    monkeypatch.setattr(approvals_module, "_selected_tenant_config", lambda: None)

    registry = {
        "agents": {
            "website-manager": {
                "allowed_actions": ["sites.get"],
                "approval_rules": [{"action": "sites.get", "approvers": ["global_admin"]}],
            }
        }
    }
    personas = build_persona_registry(
        registry,
        {
            "departments": {
                "operations": [
                    {
                        "agent": "website-manager",
                        "name": "Elena Rodriguez",
                        "role": "Website Manager",
                    }
                ]
            }
        },
    )
    store = approvals_module.ApprovalsStore(registry, personas)

    approval_id = store.create(
        "website-manager",
        "sites.get",
        {
            "requestor": "admin@example.com",
            "persona": personas["website-manager"],
            "persona_target": "Elena Rodriguez",
            "executor_identity": {"domain": "sharepoint", "client_id": "sharepoint-client"},
            "tenant": "tenant-alpha",
        },
    )

    approval = store.get(approval_id)

    assert approval is not None
    assert approval["persona"]["display_name"] == "Elena Rodriguez"
    assert approval["persona"]["canonical_agent"] == "website-manager"
    assert approval["persona_target"] == "Elena Rodriguez"
