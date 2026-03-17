"""Verify bootstrap env loading and tenant-first config authority."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from smarthaus_common.config import AppConfig, load_bootstrap_env, resolve_sharepoint_hostname
from smarthaus_common.tenant_config import reload_tenant_config


def test_load_bootstrap_env_loads_existing_file(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("B1_BOOTSTRAP_TOKEN=from_file\n", encoding="utf-8")

    monkeypatch.delenv("B1_BOOTSTRAP_TOKEN", raising=False)
    loaded = load_bootstrap_env(env_path)

    assert loaded == str(env_path.resolve())
    assert os.getenv("B1_BOOTSTRAP_TOKEN") == "from_file"


def test_load_bootstrap_env_does_not_override_existing_env(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("B1_BOOTSTRAP_TOKEN=from_file\n", encoding="utf-8")

    monkeypatch.setenv("B1_BOOTSTRAP_TOKEN", "from_env")
    load_bootstrap_env(env_path)

    assert os.getenv("B1_BOOTSTRAP_TOKEN") == "from_env"


def test_env_fallbacks_after_load():
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


def test_config_resolves_graph_fallbacks():
    """smarthaus_common.config GraphAuthConfig reads Graph/Azure fallbacks."""
    repo_root = Path(__file__).resolve().parents[1]
    load_bootstrap_env(repo_root / ".env")

    cfg = AppConfig().graph
    # Should not raise; tenant_id/client_id/client_secret are str (possibly empty)
    assert isinstance(cfg.tenant_id, str)
    assert isinstance(cfg.client_id, str)
    assert isinstance(cfg.client_secret, str)


@pytest.fixture(autouse=True)
def _reset_tenant_cache():
    reload_tenant_config()
    yield
    reload_tenant_config()


def test_app_config_prefers_selected_tenant_yaml(tmp_path, monkeypatch):
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


def test_sharepoint_hostname_prefers_selected_tenant_org_mapping(tmp_path, monkeypatch):
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
