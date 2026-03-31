from __future__ import annotations

import os
from pathlib import Path

from m365_server.__main__ import _discover_bootstrap_tenant, _load_env


def test_discover_bootstrap_tenant_prefers_smarthaus(tmp_path: Path, monkeypatch) -> None:
    app_root = tmp_path / "M365"
    app_root.mkdir()
    tenants_dir = tmp_path / "UCP" / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-alpha.yaml").write_text("tenant:\n  id: tenant-alpha\n", encoding="utf-8")
    (tenants_dir / "smarthaus.yaml").write_text("tenant:\n  id: smarthaus\n", encoding="utf-8")

    monkeypatch.delenv("M365_DEFAULT_TENANT", raising=False)

    assert _discover_bootstrap_tenant(app_root) == "smarthaus"


def test_load_env_sets_ucp_tenant_when_single_local_tenant_exists(
    tmp_path: Path,
    monkeypatch,
) -> None:
    app_root = tmp_path / "M365"
    app_root.mkdir()
    (app_root / ".env").write_text("M365_SERVER_PORT=9000\n", encoding="utf-8")
    tenants_dir = tmp_path / "UCP" / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-alpha.yaml").write_text("tenant:\n  id: tenant-alpha\n", encoding="utf-8")

    monkeypatch.delenv("UCP_TENANT", raising=False)
    monkeypatch.delenv("M365_DEFAULT_TENANT", raising=False)

    _load_env(app_root)

    assert os.getenv("UCP_TENANT") == "tenant-alpha"
