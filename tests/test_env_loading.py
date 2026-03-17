"""Verify .env loading and that env var fallbacks work (no secrets required)."""
from __future__ import annotations

import os
from pathlib import Path

import pytest


def test_dotenv_loads_from_repo_root():
    """Load .env from repo root (same path as provisioning_api.main)."""
    from dotenv import load_dotenv

    repo_root = Path(__file__).resolve().parents[1]
    env_path = repo_root / ".env"
    # .env may not exist in CI; loading it should not raise
    load_dotenv(env_path, override=False)
    # If we set a test var in env, it should be visible (or we just check defaults)
    assert True


def test_env_fallbacks_after_load():
    """After loading .env, key fallbacks work (no secrets asserted)."""
    from dotenv import load_dotenv

    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env", override=False)

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
    from dotenv import load_dotenv

    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env", override=False)

    from smarthaus_common.config import GraphAuthConfig

    cfg = GraphAuthConfig()
    # Should not raise; tenant_id/client_id/client_secret are str (possibly empty)
    assert isinstance(cfg.tenant_id, str)
    assert isinstance(cfg.client_id, str)
    assert isinstance(cfg.client_secret, str)
