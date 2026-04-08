from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from smarthaus_common.tenant_config import load_tenant_config, reload_tenant_config


@pytest.fixture(autouse=True)
def _reset_tenant_cache() -> Iterator[None]:
    reload_tenant_config()
    yield
    reload_tenant_config()


def _write_tenant(path: Path, body: str) -> None:
    path.write_text(body.strip() + "\n", encoding="utf-8")


def test_project_powerplatform_executor_prefers_explicit_executor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    _write_tenant(
        tenants_dir / "tenant-pp.yaml",
        """
tenant:
  id: tenant-pp
auth:
  mode: app_only
executors:
  sharepoint:
    domain: sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
  powerplatform:
    domain: powerplatform
    azure:
      tenant_id: pp-tenant
      client_id: pp-client
      client_secret: pp-secret
executor_registry:
  default_executor: sharepoint
  routes:
    sharepoint: sharepoint
    powerplatform: powerplatform
""",
    )
    monkeypatch.setenv("UCP_TENANT", "tenant-pp")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))

    cfg = load_tenant_config()
    projected = cfg.project_powerplatform_executor()

    assert projected.default_executor_name == "powerplatform"
    assert projected.azure.client_id == "pp-client"
    assert projected.azure.client_secret == "pp-secret"


def test_project_powerplatform_executor_uses_explicit_env_credentials_when_executor_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    _write_tenant(
        tenants_dir / "tenant-no-pp.yaml",
        """
tenant:
  id: tenant-no-pp
auth:
  mode: app_only
executors:
  sharepoint:
    domain: sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
executor_registry:
  default_executor: sharepoint
  routes:
    sharepoint: sharepoint
""",
    )
    monkeypatch.setenv("UCP_TENANT", "tenant-no-pp")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("SMARTHAUS_PP_TENANT_ID", "pp-tenant")
    monkeypatch.setenv("SMARTHAUS_PP_CLIENT_ID", "pp-client")
    monkeypatch.setenv("SMARTHAUS_PP_CLIENT_SECRET", "pp-secret")

    cfg = load_tenant_config()
    projected = cfg.project_powerplatform_executor()

    assert projected.default_executor_name == "powerplatform"
    assert projected.azure.tenant_id == "pp-tenant"
    assert projected.azure.client_id == "pp-client"
    assert projected.azure.client_secret == "pp-secret"
    assert projected.executors["powerplatform"].domain == "powerplatform"


def test_project_powerplatform_executor_uses_legacy_bootstrap_env_as_transitional_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    _write_tenant(
        tenants_dir / "tenant-legacy-pp.yaml",
        """
tenant:
  id: tenant-legacy-pp
auth:
  mode: app_only
executors:
  sharepoint:
    domain: sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
executor_registry:
  default_executor: sharepoint
  routes:
    sharepoint: sharepoint
""",
    )
    monkeypatch.setenv("UCP_TENANT", "tenant-legacy-pp")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("AZURE_TENANT_ID", "legacy-tenant")
    monkeypatch.setenv("AZURE_APP_CLIENT_ID_TAI", "legacy-client")
    monkeypatch.setenv("AZURE_APP_CLIENT_SECRET_TAI", "legacy-secret")

    cfg = load_tenant_config()
    projected = cfg.project_powerplatform_executor()

    assert projected.azure.tenant_id == "legacy-tenant"
    assert projected.azure.client_id == "legacy-client"
    assert projected.azure.client_secret == "legacy-secret"


def test_project_powerplatform_executor_fails_closed_without_executor_or_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    _write_tenant(
        tenants_dir / "tenant-missing-pp.yaml",
        """
tenant:
  id: tenant-missing-pp
auth:
  mode: app_only
executors:
  sharepoint:
    domain: sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
executor_registry:
  default_executor: sharepoint
  routes:
    sharepoint: sharepoint
""",
    )
    monkeypatch.setenv("UCP_TENANT", "tenant-missing-pp")
    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    for key in (
        "SMARTHAUS_PP_TENANT_ID",
        "SMARTHAUS_PP_CLIENT_ID",
        "SMARTHAUS_PP_CLIENT_SECRET",
        "SMARTHAUS_POWERPLATFORM_TENANT_ID",
        "SMARTHAUS_POWERPLATFORM_CLIENT_ID",
        "SMARTHAUS_POWERPLATFORM_CLIENT_SECRET",
        "AZURE_TENANT_ID",
        "AZURE_APP_CLIENT_ID_TAI",
        "AZURE_APP_CLIENT_SECRET_TAI",
        "GRAPH_TENANT_ID",
        "GRAPH_CLIENT_ID",
        "GRAPH_CLIENT_SECRET",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
        "MICROSOFT_TENANT_ID",
        "MICROSOFT_CLIENT_ID",
        "MICROSOFT_CLIENT_SECRET",
    ):
        monkeypatch.delenv(key, raising=False)

    cfg = load_tenant_config()

    with pytest.raises(ValueError, match="powerplatform_executor_unconfigured"):
        cfg.project_powerplatform_executor()
