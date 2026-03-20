"""Verify bootstrap env loading and tenant-first config authority."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from smarthaus_common.config import AppConfig, load_bootstrap_env, resolve_sharepoint_hostname
from smarthaus_common.tenant_config import load_tenant_config, reload_tenant_config


def test_load_bootstrap_env_loads_existing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("B1_BOOTSTRAP_TOKEN=from_file\n", encoding="utf-8")

    monkeypatch.delenv("B1_BOOTSTRAP_TOKEN", raising=False)
    loaded = load_bootstrap_env(env_path)

    assert loaded == str(env_path.resolve())
    assert os.getenv("B1_BOOTSTRAP_TOKEN") == "from_file"


def test_load_bootstrap_env_does_not_override_existing_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("B1_BOOTSTRAP_TOKEN=from_file\n", encoding="utf-8")

    monkeypatch.setenv("B1_BOOTSTRAP_TOKEN", "from_env")
    load_bootstrap_env(env_path)

    assert os.getenv("B1_BOOTSTRAP_TOKEN") == "from_env"


def test_env_fallbacks_after_load() -> None:
    """After loading .env, key fallbacks work (no secrets asserted)."""
    repo_root = Path(__file__).resolve().parents[1]
    load_bootstrap_env(repo_root / ".env")

    # Defaults used when var not set (doc'd in ENV.md)
    port = os.getenv("M365_SERVER_PORT", "9000")
    assert port.isdigit() and int(port) > 0

    mutations = os.getenv("ALLOW_M365_MUTATIONS", "false").lower()
    assert mutations in ("true", "false", "1", "0", "yes", "no")

    # Graph vars: we only check they are strings (empty or set)
    for name in ("GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "AZURE_TENANT_ID"):
        val = os.getenv(name, "")
        assert isinstance(val, str)


def test_config_resolves_graph_fallbacks() -> None:
    """smarthaus_common.config GraphAuthConfig reads Graph/Azure fallbacks."""
    repo_root = Path(__file__).resolve().parents[1]
    load_bootstrap_env(repo_root / ".env")

    cfg = AppConfig().graph
    # Should not raise; tenant_id/client_id/client_secret are str (possibly empty)
    assert isinstance(cfg.tenant_id, str)
    assert isinstance(cfg.client_id, str)
    assert isinstance(cfg.client_secret, str)


@pytest.fixture(autouse=True)
def _reset_tenant_cache() -> Iterator[None]:
    reload_tenant_config()
    yield
    reload_tenant_config()


def test_app_config_prefers_selected_tenant_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-alpha.yaml").write_text(
        """
tenant:
  id: tenant-alpha
azure:
  tenant_id: tenant-from-yaml
  client_id: client-from-yaml
auth:
  mode: app_only
  app_only:
    scope: https://graph.microsoft.com/.default
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_TENANT", "tenant-alpha")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("AZURE_TENANT_ID", "tenant-from-env")
    monkeypatch.setenv("AZURE_CLIENT_ID", "client-from-env")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "secret-from-env")

    cfg = AppConfig().graph

    assert cfg.tenant_id == "tenant-from-yaml"
    assert cfg.client_id == "client-from-yaml"
    assert cfg.client_secret == "secret-from-env"


def test_sharepoint_hostname_prefers_selected_tenant_org_mapping(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-beta.yaml").write_text(
        """
tenant:
  id: tenant-beta
org:
  sharepoint_hostname: tenant.sharepoint.example.com
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_TENANT", "tenant-beta")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("SHAREPOINT_HOSTNAME", "env.sharepoint.example.com")

    assert resolve_sharepoint_hostname() == "tenant.sharepoint.example.com"


def test_tenant_config_synthesizes_default_executor_for_legacy_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-legacy.yaml").write_text(
        """
tenant:
  id: tenant-legacy
azure:
  tenant_id: legacy-tenant
  client_id: legacy-client
auth:
  mode: app_only
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_TENANT", "tenant-legacy")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))

    cfg = load_tenant_config()

    assert cfg.default_executor_name == "default"
    assert set(cfg.executors) == {"default"}
    assert cfg.default_executor is not None
    assert cfg.default_executor.azure.client_id == "legacy-client"
    assert cfg.azure.client_id == "legacy-client"
    assert cfg.auth.mode == "app_only"


def test_app_config_projects_explicit_default_executor_from_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-gamma.yaml").write_text(
        """
tenant:
  id: tenant-gamma
azure:
  tenant_id: root-tenant
  client_id: root-client
auth:
  mode: app_only
executors:
  collaboration:
    display_name: SMARTHAUS Collaboration Executor
    domain: collaboration
    capabilities:
      - teams
      - groups
    azure:
      tenant_id: collab-tenant
      client_id: collab-client
  sharepoint:
    display_name: SMARTHAUS SharePoint Executor
    domain: sharepoint
    capabilities:
      - approvals
      - sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
executor_registry:
  default_executor: sharepoint
  routes:
    approvals: sharepoint
    teams: collaboration
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_TENANT", "tenant-gamma")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "fallback-secret")

    cfg = load_tenant_config()
    graph = AppConfig().graph

    assert cfg.default_executor_name == "sharepoint"
    assert cfg.executor_registry.routes["teams"] == "collaboration"
    assert cfg.default_executor is not None
    assert cfg.default_executor.domain == "sharepoint"
    assert graph.tenant_id == "sharepoint-tenant"
    assert graph.client_id == "sharepoint-client"
    assert graph.client_secret == "fallback-secret"


def test_multi_executor_contract_fails_closed_without_default_executor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-delta.yaml").write_text(
        """
tenant:
  id: tenant-delta
auth:
  mode: app_only
executors:
  collaboration:
    domain: collaboration
  sharepoint:
    domain: sharepoint
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_TENANT", "tenant-delta")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))

    with pytest.raises(ValueError, match="default_executor"):
        load_tenant_config()


def test_m365_router_projects_directory_executor_for_user_actions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-router.yaml").write_text(
        """
tenant:
  id: tenant-router
azure:
  tenant_id: root-tenant
  client_id: root-client
auth:
  mode: app_only
executors:
  sharepoint:
    domain: sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
  collaboration:
    domain: collaboration
    azure:
      tenant_id: collaboration-tenant
      client_id: collaboration-client
  directory:
    domain: directory
    azure:
      tenant_id: directory-tenant
      client_id: directory-client
executor_registry:
  default_executor: sharepoint
  routes:
    sharepoint: sharepoint
    collaboration: collaboration
    directory: directory
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_TENANT", "tenant-router")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))

    from provisioning_api.routers import m365 as m365_router

    captured: dict[str, str] = {}

    class _DummyGraphClient:
        def __init__(self, tenant_config: Any | None = None, config: Any | None = None):
            if tenant_config is not None:
                captured["client_id"] = tenant_config.azure.client_id
                captured["tenant_id"] = tenant_config.azure.tenant_id

    monkeypatch.setattr(m365_router, "GraphClient", _DummyGraphClient)

    m365_router._graph_client("list_users")

    assert captured["client_id"] == "directory-client"
    assert captured["tenant_id"] == "directory-tenant"


def test_m365_provision_projects_bounded_executor_by_route(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-provision.yaml").write_text(
        """
tenant:
  id: tenant-provision
azure:
  tenant_id: root-tenant
  client_id: root-client
auth:
  mode: app_only
executors:
  sharepoint:
    domain: sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
  collaboration:
    domain: collaboration
    azure:
      tenant_id: collaboration-tenant
      client_id: collaboration-client
executor_registry:
  default_executor: sharepoint
  routes:
    sharepoint: sharepoint
    collaboration: collaboration
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_TENANT", "tenant-provision")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))

    from provisioning_api import m365_provision

    captured: dict[str, str] = {}

    class _DummyGraphClient:
        def __init__(self, tenant_config: Any | None = None, config: Any | None = None):
            if tenant_config is not None:
                captured["client_id"] = tenant_config.azure.client_id
                captured["tenant_id"] = tenant_config.azure.tenant_id

    monkeypatch.setattr(m365_provision, "GraphClient", _DummyGraphClient)

    m365_provision._graph_client("collaboration")

    assert captured["client_id"] == "collaboration-client"
    assert captured["tenant_id"] == "collaboration-tenant"
