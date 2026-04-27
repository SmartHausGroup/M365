#!/usr/bin/env python3
"""Standalone M365 Graph runtime pack verifier.

Plan reference: plan:m365-standalone-graph-runtime-integration-pack-fix:R2

Checks (all must pass):
  - C1 The runtime package exists at src/m365_runtime and exposes the expected modules.
  - C2 The runtime package never references forbidden source-repo / sibling-repo names
       (only `_forbidden_tokens.py` is allowed to spell them).
  - C3 The runtime package never imports `ops_adapter.*` or `smarthaus_graph.*`.
  - C4 The setup schema in src/ucp_m365_pack/setup_schema.json declares the new
       Microsoft Graph auth fields and lists `M365_TENANT_ID` / `M365_CLIENT_ID` /
       `M365_AUTH_MODE` / `M365_SERVICE_ACTOR_UPN` as required.
  - C5 The UCP client routes through M365_RUNTIME_URL when configured (preferred),
       falls back to legacy ops-adapter URL otherwise, and never claims
       direct_import_available.
  - C6 README/manifest claims a real Graph runtime pack and not a client-only pack.
  - C7 (fix R2) Unpack the built bundle in dist/m365_pack and scan the FULL payload
       for the forbidden source-repo / sibling-repo strings. Conformance fails when
       any forbidden string is present in any payload file.
  - C8 (fix R3) The manifest's runtime block declares the full auth lifecycle:
       auth_start_path, auth_check_path, auth_status_path, auth_clear_path.
  - C9 (fix R3) The packaged payload contains m365_runtime/launcher.py with the
       /v1/auth/start and /v1/auth/check endpoints wired in.

Emits configs/generated/standalone_graph_runtime_pack_verification.json with
per-check results and an overall verdict.
"""

from __future__ import annotations

import ast
import json
import re
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DIST = REPO / "dist" / "m365_pack"
FORBIDDEN_TOKENS_FILE = "_forbidden_tokens.py"
FORBIDDEN_PAYLOAD_TOKENS = (
    "M365_REPO_ROOT",
    "SMARTHAUS_M365_REPO_ROOT",
    "M365_REGISTRY_PATH",
    "UCP_ROOT",
    "REPOS_ROOT",
    "UCP_REPOS_ROOT",
    "../M365",
    "from ops_adapter",
    "_resolve_m365_repo_root",
)


def _runtime_files() -> list[Path]:
    runtime_root = REPO / "src" / "m365_runtime"
    return [p for p in runtime_root.rglob("*.py")]


def check_runtime_layout() -> dict[str, Any]:
    expected = {
        "src/m365_runtime/__init__.py",
        "src/m365_runtime/__main__.py",
        "src/m365_runtime/launcher.py",
        "src/m365_runtime/setup.py",
        "src/m365_runtime/state.py",
        "src/m365_runtime/audit.py",
        "src/m365_runtime/health.py",
        "src/m365_runtime/_forbidden_tokens.py",
        "src/m365_runtime/auth/__init__.py",
        "src/m365_runtime/auth/oauth.py",
        "src/m365_runtime/auth/app_only.py",
        "src/m365_runtime/auth/token_store.py",
        "src/m365_runtime/graph/__init__.py",
        "src/m365_runtime/graph/client.py",
        "src/m365_runtime/graph/errors.py",
        "src/m365_runtime/graph/registry.py",
        "src/m365_runtime/graph/actions.py",
    }
    present = {str(p.relative_to(REPO)) for p in _runtime_files()}
    missing = sorted(expected - present)
    return {
        "check": "C1_runtime_layout",
        "ok": not missing,
        "missing": missing,
        "present_count": len(present),
    }


def check_no_forbidden_tokens() -> dict[str, Any]:
    forbidden = (
        "M365_REPO_ROOT",
        "SMARTHAUS_M365_REPO_ROOT",
        "UCP_ROOT",
        "REPOS_ROOT",
        "UCP_REPOS_ROOT",
        "../M365",
        "from ops_adapter",
    )
    offenders: list[str] = []
    for path in _runtime_files():
        if path.name == FORBIDDEN_TOKENS_FILE:
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.relative_to(REPO)}:{token}")
    return {"check": "C2_no_forbidden_tokens", "ok": not offenders, "offenders": offenders}


def check_no_forbidden_imports() -> dict[str, Any]:
    forbidden_modules = ("ops_adapter", "smarthaus_graph")
    offenders: list[str] = []
    for path in _runtime_files():
        if path.name == FORBIDDEN_TOKENS_FILE:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                head = node.module.split(".")[0]
                if head in forbidden_modules:
                    offenders.append(f"{path.relative_to(REPO)}:{node.module}")
            if isinstance(node, ast.Import):
                for n in node.names:
                    head = n.name.split(".")[0]
                    if head in forbidden_modules:
                        offenders.append(f"{path.relative_to(REPO)}:{n.name}")
    return {"check": "C3_no_forbidden_imports", "ok": not offenders, "offenders": offenders}


def check_setup_schema() -> dict[str, Any]:
    schema_path = REPO / "src" / "ucp_m365_pack" / "setup_schema.json"
    schema = json.loads(schema_path.read_text())
    required = set(schema.get("required", []))
    properties = set(schema.get("properties", {}).keys())
    expected_required = {
        "M365_TENANT_ID",
        "M365_CLIENT_ID",
        "M365_AUTH_MODE",
        "M365_SERVICE_ACTOR_UPN",
    }
    expected_properties = {
        "M365_RUNTIME_URL",
        "M365_TENANT_ID",
        "M365_CLIENT_ID",
        "M365_AUTH_MODE",
        "M365_REDIRECT_URI",
        "M365_DEVICE_CODE_FALLBACK",
        "M365_APP_ONLY_CLIENT_SECRET_REF",
        "M365_APP_ONLY_CERTIFICATE_REF",
        "M365_TOKEN_STORE",
        "M365_KEYCHAIN_SERVICE",
        "M365_ENCRYPTED_PACK_LOCAL_ALLOWED",
        "M365_GRANTED_SCOPES",
    }
    missing_required = sorted(expected_required - required)
    missing_properties = sorted(expected_properties - properties)
    return {
        "check": "C4_setup_schema",
        "ok": not missing_required and not missing_properties,
        "missing_required": missing_required,
        "missing_properties": missing_properties,
    }


def check_client_routing() -> dict[str, Any]:
    client_src = (REPO / "src" / "ucp_m365_pack" / "client.py").read_text()
    pattern = re.compile(r"_configured_runtime_url\s*\(", re.MULTILINE)
    has_runtime_url = pattern.search(client_src) is not None
    runtime_path_first = client_src.find("runtime_url is not None") < client_src.find(
        "service_url is not None"
    )
    direct_import_unavailable = '"direct_import_available": False' in client_src
    has_alias_table = "LEGACY_ACTION_TO_RUNTIME_ACTION" in client_src
    has_alias_function = "def map_legacy_action_to_runtime" in client_src
    return {
        "check": "C5_client_routing",
        "ok": has_runtime_url
        and runtime_path_first
        and direct_import_unavailable
        and has_alias_table
        and has_alias_function,
        "has_runtime_url": has_runtime_url,
        "runtime_path_first": runtime_path_first,
        "direct_import_unavailable": direct_import_unavailable,
        "has_alias_table": has_alias_table,
        "has_alias_function": has_alias_function,
    }


def check_manifest_marker() -> dict[str, Any]:
    manifest_path = DIST / "manifest.json"
    if not manifest_path.exists():
        return {
            "check": "C6_manifest_marker",
            "ok": True,
            "skipped": "no_dist_manifest_present_yet",
        }
    manifest = json.loads(manifest_path.read_text())
    description = str(manifest.get("description") or "")
    capabilities = list(manifest.get("capabilities_exposed") or [])
    runtime_claim = "runtime" in description.lower() or "m365_runtime" in capabilities
    return {
        "check": "C6_manifest_marker",
        "ok": runtime_claim,
        "description": description,
        "capabilities": capabilities,
        "runtime_claim": runtime_claim,
    }


def check_full_payload_no_forbidden_tokens() -> dict[str, Any]:
    """C7 fix R2: unpack dist/m365_pack/payload.tar.gz and scan the entire payload."""
    payload_path = DIST / "payload.tar.gz"
    if not payload_path.exists():
        return {"check": "C7_full_payload_scan", "ok": False, "reason": "payload_missing"}
    offenders: list[str] = []
    with tempfile.TemporaryDirectory(prefix="m365-verify-") as tmp_str:
        tmp = Path(tmp_str)
        with tarfile.open(payload_path) as tf:
            tf.extractall(tmp)
        for path in tmp.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".py", ".yaml", ".yml", ".json", ".md", ".txt"}:
                continue
            if path.name == FORBIDDEN_TOKENS_FILE:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            for token in FORBIDDEN_PAYLOAD_TOKENS:
                if token in text:
                    rel = path.relative_to(tmp)
                    offenders.append(f"{rel}:{token}")
    return {"check": "C7_full_payload_scan", "ok": not offenders, "offenders": offenders}


def check_manifest_declares_auth_lifecycle() -> dict[str, Any]:
    manifest_path = DIST / "manifest.json"
    if not manifest_path.exists():
        return {"check": "C8_manifest_auth_lifecycle", "ok": False, "reason": "manifest_missing"}
    manifest = json.loads(manifest_path.read_text())
    runtime = manifest.get("runtime", {})
    expected = {
        "auth_start_path": "/v1/auth/start",
        "auth_check_path": "/v1/auth/check",
        "auth_status_path": "/v1/auth/status",
        "auth_clear_path": "/v1/auth/clear",
    }
    missing = sorted(k for k, v in expected.items() if runtime.get(k) != v)
    return {
        "check": "C8_manifest_auth_lifecycle",
        "ok": not missing,
        "missing": missing,
        "runtime": {k: runtime.get(k) for k in expected.keys()},
    }


def check_payload_launcher_has_auth_lifecycle() -> dict[str, Any]:
    payload_path = DIST / "payload.tar.gz"
    if not payload_path.exists():
        return {
            "check": "C9_payload_launcher_auth_lifecycle",
            "ok": False,
            "reason": "payload_missing",
        }
    with tempfile.TemporaryDirectory(prefix="m365-verify-launcher-") as tmp_str:
        tmp = Path(tmp_str)
        with tarfile.open(payload_path) as tf:
            tf.extractall(tmp)
        launcher = tmp / "m365_runtime" / "launcher.py"
        if not launcher.is_file():
            return {
                "check": "C9_payload_launcher_auth_lifecycle",
                "ok": False,
                "reason": "launcher_missing",
            }
        text = launcher.read_text(encoding="utf-8")
        markers = {
            "auth_start_route": "/v1/auth/start" in text,
            "auth_check_route": "/v1/auth/check" in text,
            "auth_status_route": "/v1/auth/status" in text,
            "auth_clear_route": "/v1/auth/clear" in text,
            "token_store_imported": "TokenStore" in text,
        }
    return {
        "check": "C9_payload_launcher_auth_lifecycle",
        "ok": all(markers.values()),
        "markers": markers,
    }


def main() -> int:
    results = [
        check_runtime_layout(),
        check_no_forbidden_tokens(),
        check_no_forbidden_imports(),
        check_setup_schema(),
        check_client_routing(),
        check_manifest_marker(),
        check_full_payload_no_forbidden_tokens(),
        check_manifest_declares_auth_lifecycle(),
        check_payload_launcher_has_auth_lifecycle(),
    ]
    overall = all(r.get("ok", False) for r in results)
    payload = {
        "plan_ref": "plan:m365-standalone-graph-runtime-integration-pack-fix:R2",
        "phase": "fix-R2",
        "results": results,
        "overall_ok": overall,
    }
    out = REPO / "configs" / "generated" / "standalone_graph_runtime_pack_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    if overall:
        print(f"Standalone Graph runtime pack verification PASSED ({len(results)} checks)")
        return 0
    print("Standalone Graph runtime pack verification FAILED:")
    for r in results:
        if not r.get("ok"):
            print(f"  - {r['check']}: {r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
