"""Health probes feeding the readiness predicate (L_READINESS)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._forbidden_tokens import FORBIDDEN_TOKENS
from .auth.token_store import TokenStore
from .graph.client import graph_get
from .graph.registry import READ_ONLY_REGISTRY
from .setup import SetupConfig
from .state import HealthVector, readiness

REQUIRED_PAYLOAD_FILES = (
    "setup_schema.json",
    "registry/agents.yaml",
)
ACCEPTED_METADATA_FILES = (
    "pack_metadata.json",
    "manifest.json",
)
REQUIRED_INSTALLED_FILES = ACCEPTED_METADATA_FILES[:1] + REQUIRED_PAYLOAD_FILES


@dataclass
class HealthProbeResult:
    vector: HealthVector
    detail: dict[str, Any]


def probe_service(installed_root: Path) -> bool:
    return installed_root.is_dir()


def probe_artifact(installed_root: Path) -> bool:
    has_metadata = any((installed_root / f).exists() for f in ACCEPTED_METADATA_FILES)
    has_payload = all((installed_root / f).exists() for f in REQUIRED_PAYLOAD_FILES)
    return has_metadata and has_payload


def probe_no_source_repo_dependency(installed_root: Path) -> bool:
    runtime_root = installed_root / "m365_runtime"
    if not runtime_root.is_dir():
        return False
    for path in runtime_root.rglob("*.py"):
        if path.name == "_forbidden_tokens.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if any(token in text for token in FORBIDDEN_TOKENS):
            return False
    return True


def probe_token(setup: SetupConfig, store: TokenStore) -> bool:
    if not setup.token_store_safe():
        return False
    try:
        store.put("__health_probe__", "ok")
        value = store.get("__health_probe__")
        store.clear("__health_probe__")
        return value == "ok"
    except Exception:
        return False


def probe_auth(access_token: str | None) -> bool:
    return bool(access_token)


def probe_graph(access_token: str | None, *, transport: Any | None = None) -> bool:
    if not access_token:
        return False
    result = graph_get(access_token, "/organization", transport=transport)
    return result.status_class == "success"


def probe_permissions(setup: SetupConfig) -> bool:
    if not setup.granted_scopes:
        return False
    for spec in READ_ONLY_REGISTRY.values():
        if setup.auth_mode in spec.auth_modes and spec.scopes.issubset(setup.granted_scopes):
            return True
    return False


def probe_contracts(installed_root: Path) -> bool:
    schema = installed_root / "setup_schema.json"
    return schema.is_file()


def compose_readiness(
    installed_root: Path,
    setup: SetupConfig | None,
    store: TokenStore | None,
    access_token: str | None,
    *,
    transport: Any | None = None,
) -> HealthProbeResult:
    vec = HealthVector()
    vec.svc = probe_service(installed_root)
    vec.art = probe_artifact(installed_root)
    vec.src = probe_no_source_repo_dependency(installed_root)
    vec.ctr = probe_contracts(installed_root)
    if setup is None:
        vec.auth = False
        vec.tok = False
        vec.perm = False
        vec.graph = False
        vec.aud = True
    else:
        vec.auth = probe_auth(access_token)
        vec.tok = probe_token(setup, store) if store is not None else False
        vec.graph = probe_graph(access_token, transport=transport)
        vec.perm = probe_permissions(setup)
        vec.aud = True
    state, label = readiness(vec)
    return HealthProbeResult(vector=vec, detail={"state": state, "label": label})
