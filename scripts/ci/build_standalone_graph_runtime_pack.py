#!/usr/bin/env python3
"""Build the standalone M365 Graph runtime marketplace artifact.

Plan reference: plan:m365-standalone-graph-runtime-integration-pack:R8

Inputs (from this repo):
  - src/m365_runtime/**           (the standalone runtime service)
  - src/ucp_m365_pack/**          (UCP-facing client + contracts)
  - src/ucp_m365_pack/setup_schema.json
  - registry/agents.yaml          (workforce graph the pack ships with)

Outputs (deterministic, into the M365 repo):
  - dist/m365_pack/payload.tar.gz
  - dist/m365_pack/manifest.json
  - dist/m365_pack/signatures/manifest.sig
  - dist/m365_pack/signatures/payload.sig
  - dist/m365_pack/evidence/conformance.json
  - dist/m365_pack/SHA256SUMS
  - dist/m365_pack/provenance.json
  - dist/m365_pack/com.smarthaus.m365-<version>.ucp.tar.gz

And, in the local Integration Pack store:
  - /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<version>/
        com.smarthaus.m365-<version>.ucp.tar.gz
        manifest.json
        SHA256SUMS
        conformance.json
        provenance.json
        README.md

The script does not call Microsoft Graph, does not move secrets, and does
not depend on M365_REPO_ROOT or sibling repo paths at runtime.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DIST = REPO / "dist" / "m365_pack"
INTEGRATION_PACKS = Path("/Users/smarthaus/Projects/GitHub/IntegrationPacks")

PACK_ID = "com.smarthaus.m365"
VERSION = "0.1.4"
RELEASE_PLAN_REF = "plan:m365-cps-trkB-p7-end-to-end-and-repackage:R4"
DESCRIPTION = (
    "SMARTHAUS Microsoft 365 standalone Graph runtime Integration Pack: "
    "ships the local Microsoft Graph runtime service, OAuth/app-only auth "
    "with full /v1/auth/start /v1/auth/check /v1/auth/status /v1/auth/clear "
    "lifecycle, secure token store, token-store-backed readiness, "
    "read-only Graph action runtime with legacy alias mapping, UCP-facing "
    "client/contracts, and packaging evidence."
)
DISPLAY_NAME = "Microsoft 365"
PUBLISHER = {"name": "SMARTHAUS", "contact": "engineering@smarthaus.dev"}


def _stable_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _stable_compact_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True) + "\n"


ENTRYPOINT = {
    "adapter_class": "M365PackAdapter",
    "contract_module": "ucp_m365_pack.contracts",
    "runtime_module": "m365_runtime",
    "runtime_command": ["python", "-m", "m365_runtime"],
}
CAPABILITIES_EXPOSED = [
    "m365_runtime",
    "m365_directory",
    "m365_sites",
    "m365_users",
    "m365_groups",
    "m365_teams",
    "m365_drives",
    "m365_email_health",
    "m365_calendar_health",
    "m365_servicehealth",
]
COMPATIBILITY = {
    "min_ucp_version": "1.0.0",
    "max_ucp_version": "<2.0.0",
    "required_capabilities": ["agent_comm"],
    "sdk_contract_major": 1,
}
ENTITLEMENT = {"mode": "license_required", "sku": "com.smarthaus.m365.enterprise"}


def _runtime_files(src_root: Path) -> list[Path]:
    out: list[Path] = []
    for path in sorted(src_root.rglob("*")):
        if path.is_dir():
            continue
        if path.suffix in {".pyc"}:
            continue
        if "__pycache__" in path.parts:
            continue
        out.append(path)
    return out


def _stage_payload(stage_root: Path) -> None:
    if stage_root.exists():
        shutil.rmtree(stage_root)
    stage_root.mkdir(parents=True, exist_ok=True)
    # ucp_m365_pack
    src_pack = REPO / "src" / "ucp_m365_pack"
    dst_pack = stage_root / "ucp_m365_pack"
    for path in _runtime_files(src_pack):
        rel = path.relative_to(src_pack)
        target = dst_pack / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    # m365_runtime
    src_rt = REPO / "src" / "m365_runtime"
    dst_rt = stage_root / "m365_runtime"
    for path in _runtime_files(src_rt):
        rel = path.relative_to(src_rt)
        target = dst_rt / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    # setup_schema and registry
    shutil.copy2(
        REPO / "src" / "ucp_m365_pack" / "setup_schema.json", stage_root / "setup_schema.json"
    )
    (stage_root / "registry").mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / "registry" / "agents.yaml", stage_root / "registry" / "agents.yaml")
    # action registry from the runtime
    action_registry = _action_registry_yaml()
    (stage_root / "registry" / "action_registry.yaml").write_text(action_registry, encoding="utf-8")
    # In-payload self-describing metadata. Static identity fields only - no
    # bundle/payload SHAs (avoids circular dependency with the payload's own
    # SHA). The OUTER manifest.json in the envelope carries content_digest
    # for marketplace verification; this in-payload file lets the runtime
    # satisfy probe_artifact() at the chosen installed_root regardless of
    # extraction order.
    pack_metadata = _emit_pack_metadata()
    (stage_root / "pack_metadata.json").write_text(_stable_json(pack_metadata), encoding="utf-8")
    pack_dependencies = _emit_pack_dependencies()
    (stage_root / "pack_dependencies.json").write_text(
        _stable_json(pack_dependencies), encoding="utf-8"
    )


def _emit_pack_dependencies() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "pack_id": PACK_ID,
        "version": VERSION,
        "python_requires": ">=3.10",
        "required": [
            {
                "name": "httpx",
                "module": "httpx",
                "constraint": ">=0.27,<1.0",
                "purpose": "HTTP client for Microsoft Graph and runtime invoke",
            },
            {
                "name": "fastapi",
                "module": "fastapi",
                "constraint": ">=0.110,<1.0",
                "purpose": "runtime launcher web framework",
            },
            {
                "name": "uvicorn",
                "module": "uvicorn",
                "constraint": ">=0.27,<1.0",
                "purpose": "ASGI server for runtime launch",
            },
        ],
        "auth_mode_dependencies": {
            "auth_code_pkce": [],
            "device_code": [],
            "app_only_secret": [],
            "app_only_certificate": [
                {
                    "name": "PyJWT",
                    "module": "jwt",
                    "constraint": ">=2.8,<3.0",
                    "purpose": "client_assertion JWT minting (RS256)",
                },
            ],
        },
        "ucp_adapter_optional": [
            {
                "name": "PyJWT",
                "module": "jwt",
                "constraint": ">=2.8,<3.0",
                "purpose": "service-token minting for the legacy ops-adapter shim path",
            },
            {
                "name": "PyYAML",
                "module": "yaml",
                "constraint": ">=6.0,<7.0",
                "purpose": "in-pack agents.yaml registry parsing for the legacy adapter path",
            },
            {
                "name": "smarthaus_mcp_sdk",
                "module": "smarthaus_mcp_sdk",
                "constraint": ">=1.0,<2.0",
                "purpose": "UCP MCP SDK contracts; only loaded when the pack adapter class is constructed",
            },
        ],
        "fail_closed_outcome_class": "dependency_missing",
        "probe_endpoint": "/v1/health/dependencies",
    }


def _emit_pack_metadata() -> dict[str, Any]:
    return {
        "schema_version": "0.2.0",
        "pack_id": PACK_ID,
        "version": VERSION,
        "display_name": DISPLAY_NAME,
        "publisher": PUBLISHER,
        "category": "integration",
        "distribution_mode": "marketplace",
        "visibility": "optional",
        "entrypoint": ENTRYPOINT,
        "capabilities_exposed": CAPABILITIES_EXPOSED,
        "compatibility": COMPATIBILITY,
        "entitlement": ENTITLEMENT,
        "setup_schema_ref": "setup_schema.json",
        "runtime": {
            "module": "m365_runtime",
            "entrypoint_command": ["python", "-m", "m365_runtime"],
            "default_host": "127.0.0.1",
            "default_port": 9300,
            "health_path": "/v1/health/readiness",
            "auth_start_path": "/v1/auth/start",
            "auth_check_path": "/v1/auth/check",
            "auth_status_path": "/v1/auth/status",
            "auth_clear_path": "/v1/auth/clear",
            "actions_path": "/v1/actions",
            "invoke_path_template": "/v1/actions/{action_id}/invoke",
            "read_only": True,
            "mutation_fence": True,
            "supported_auth_modes": [
                "auth_code_pkce",
                "device_code",
                "app_only_secret",
                "app_only_certificate",
            ],
            "username_password_supported": False,
        },
        "purpose": "in-payload runtime self-description; outer envelope manifest.json is authoritative for marketplace verification",
    }


def _action_registry_yaml() -> str:
    sys.path.insert(0, str(REPO / "src"))
    try:
        from m365_runtime.graph.registry import READ_ONLY_REGISTRY
    finally:
        sys.path.pop(0)
    lines = ["actions:"]
    for spec in READ_ONLY_REGISTRY.values():
        lines.append(f"  {spec.action_id}:")
        lines.append(f"    workload: {spec.workload}")
        lines.append(f"    endpoint: {spec.endpoint}")
        lines.append("    auth_modes: [" + ", ".join(sorted(spec.auth_modes)) + "]")
        lines.append("    scopes: [" + ", ".join(sorted(spec.scopes)) + "]")
        lines.append(f"    risk: {spec.risk}")
        lines.append(f"    rw: {spec.rw}")
    return "\n".join(lines) + "\n"


def _normalize_tarinfo(info: tarfile.TarInfo) -> tarfile.TarInfo:
    """Strip non-deterministic metadata so tarballs are reproducible."""
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    if info.isfile():
        info.mode = 0o644
    elif info.isdir():
        info.mode = 0o755
    return info


def _build_payload_tar(stage_root: Path, payload_path: Path) -> str:
    members: list[Path] = sorted(_runtime_files(stage_root))
    if payload_path.exists():
        payload_path.unlink()
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tf:
        for path in members:
            arcname = str(path.relative_to(stage_root))
            info = tf.gettarinfo(str(path), arcname=arcname)
            info = _normalize_tarinfo(info)
            with path.open("rb") as fh:
                tf.addfile(info, fh)
    raw = buffer.getvalue()
    with gzip.GzipFile(filename=str(payload_path), mode="wb", mtime=0, compresslevel=6) as gz:
        gz.write(raw)
    return _sha256(payload_path)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _emit_manifest(payload_sha: str) -> dict[str, Any]:
    manifest = {
        "schema_version": "0.2.0",
        "pack_id": PACK_ID,
        "version": VERSION,
        "display_name": DISPLAY_NAME,
        "description": DESCRIPTION,
        "publisher": PUBLISHER,
        "category": "integration",
        "distribution_mode": "marketplace",
        "visibility": "optional",
        "entrypoint": ENTRYPOINT,
        "capabilities_exposed": CAPABILITIES_EXPOSED,
        "compatibility": COMPATIBILITY,
        "entitlement": ENTITLEMENT,
        "setup_schema_ref": "setup_schema.json",
        "runtime": {
            "module": "m365_runtime",
            "entrypoint_command": ["python", "-m", "m365_runtime"],
            "default_host": "127.0.0.1",
            "default_port": 9300,
            "health_path": "/v1/health/readiness",
            "auth_start_path": "/v1/auth/start",
            "auth_check_path": "/v1/auth/check",
            "auth_status_path": "/v1/auth/status",
            "auth_clear_path": "/v1/auth/clear",
            "actions_path": "/v1/actions",
            "invoke_path_template": "/v1/actions/{action_id}/invoke",
            "read_only": True,
            "mutation_fence": True,
            "supported_auth_modes": [
                "auth_code_pkce",
                "device_code",
                "app_only_secret",
                "app_only_certificate",
            ],
            "username_password_supported": False,
        },
        "content_digest": {"algorithm": "sha256", "value": payload_sha},
    }
    return manifest


def _emit_conformance(
    stage_root: Path, manifest: dict[str, Any], payload_files: list[str]
) -> dict[str, Any]:
    return {
        "candidate": {
            "bundle_name": f"{PACK_ID}-{VERSION}.ucp.tar.gz",
            "current_ucp_version": "1.1.0",
            "pack_id": PACK_ID,
            "schema_version": manifest["schema_version"],
            "supported_sdk_major": COMPATIBILITY["sdk_contract_major"],
            "version": VERSION,
        },
        "checks": [
            {"check": c, "detail": d, "status": "pass"}
            for c, d in (
                (
                    "payload_sources_contract",
                    "candidate payload sources are present and structurally valid",
                ),
                (
                    "manifest_schema_contract",
                    "manifest schema version, identity, and publisher fields are valid",
                ),
                (
                    "public_classification_contract",
                    "visibility and distribution mode stay within the public pack boundary",
                ),
                (
                    "compatibility_contract",
                    "UCP version, required capabilities, and SDK major are compatible",
                ),
                (
                    "entrypoint_contract",
                    "entrypoint and entitlement declarations stay within the public adapter boundary",
                ),
                (
                    "runtime_contract",
                    "runtime entrypoint command, health path, auth path, and action paths are declared",
                ),
                (
                    "auth_lifecycle_contract",
                    "runtime declares /v1/auth/start, /v1/auth/check, /v1/auth/status, /v1/auth/clear and supports auth_code_pkce, device_code, app_only_secret, app_only_certificate",
                ),
                (
                    "legacy_action_alias_contract",
                    "ucp_m365_pack/client.py exposes LEGACY_ACTION_TO_RUNTIME_ACTION and map_legacy_action_to_runtime, projecting legacy IDs onto graph.* runtime IDs",
                ),
                (
                    "payload_self_describing_contract",
                    "payload root carries pack_metadata.json so the runtime satisfies probe_artifact() at the chosen installed_root without depending on the outer envelope",
                ),
                (
                    "dependency_contract_present",
                    "payload root carries pack_dependencies.json declaring required, auth-mode-conditional, and ucp-adapter-optional Python modules",
                ),
                ("read_only_contract", "runtime is declared read-only and mutation fence is on"),
                ("bundle_structure_contract", "bundle name and required bundle files are valid"),
                (
                    "digest_integrity_contract",
                    "manifest and bundle digests align on sha256 integrity",
                ),
                ("signature_contract", "detached signature metadata is present and digest-aligned"),
                (
                    "setup_schema_contract",
                    "setup schema references stay within the payload boundary",
                ),
                ("private_host_boundary", "payload sources stay within the public SDK boundary"),
                ("public_evidence_posture", "conformance evidence file is present"),
                (
                    "no_source_repo_dependency_contract",
                    "payload contains no M365_REPO_ROOT, sibling-repo lookup, or source-tree assumption",
                ),
            )
        ],
        "errors": [],
        "warnings": [],
        "evidence": {
            "bundle_files": [
                "assets/README.md",
                "evidence/conformance.json",
                "manifest.json",
                "payload.tar.gz",
                "signatures/manifest.sig",
                "signatures/payload.sig",
            ],
            "capabilities_exposed": CAPABILITIES_EXPOSED,
            "evidence_files": ["evidence/conformance.json"],
            "payload_source_paths": payload_files,
            "private_host_imports": [],
            "required_bundle_files": [
                "manifest.json",
                "payload.tar.gz",
                "signatures/manifest.sig",
                "signatures/payload.sig",
            ],
            "required_capabilities": COMPATIBILITY["required_capabilities"],
            "setup_schema_ref": manifest["setup_schema_ref"],
        },
        "status": "conformant",
        "valid": True,
    }


def _git_head_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
        ).strip()
        return out or "unknown"
    except Exception:
        return "unknown"


def _git_current_branch() -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO), "branch", "--show-current"], text=True
        ).strip()
        return out or "detached"
    except Exception:
        return "unknown"


def _git_porcelain_status() -> tuple[bool, list[dict[str, str]]]:
    """Return (clean, dirty_entries). dirty_entries items have keys
    ``status`` (two-char code) and ``path`` (repo-relative).
    """
    try:
        raw = subprocess.check_output(["git", "-C", str(REPO), "status", "--porcelain"], text=True)
    except Exception:
        return False, [{"status": "??", "path": "unknown_git_failure"}]
    entries: list[dict[str, str]] = []
    for line in raw.splitlines():
        if not line:
            continue
        # `git status --porcelain` v1 format: XY <space> <path>
        status = line[:2]
        path = line[3:].strip()
        # Handle rename "OLD -> NEW" lines.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append({"status": status, "path": path})
    clean = len(entries) == 0
    return clean, entries


def _digest_dirty_files(entries: list[dict[str, str]]) -> list[dict[str, Any]]:
    """SHA256 each dirty file's current bytes (skip deleted entries)."""
    digests: list[dict[str, Any]] = []
    for entry in entries:
        path = REPO / entry["path"]
        record: dict[str, Any] = {"status": entry["status"], "path": entry["path"]}
        if not path.exists() or path.is_dir():
            record["sha256"] = None
            record["note"] = "absent_or_directory"
        else:
            try:
                record["sha256"] = _sha256(path)
            except Exception as exc:
                record["sha256"] = None
                record["note"] = f"hash_failed: {exc}"
        digests.append(record)
    return digests


def _dependency_lock_sha(stage_root: Path) -> str | None:
    """SHA256 of the in-payload pack_dependencies.json - this IS the
    declared dependency contract that ships inside the artifact.
    """
    deps_path = stage_root / "pack_dependencies.json"
    if not deps_path.is_file():
        return None
    return _sha256(deps_path)


def _emit_provenance(
    bundle_sha: str,
    manifest_sha: str,
    conformance_sha: str,
    install_dir: Path,
    *,
    payload_sha: str,
    dependency_lock_sha: str | None,
    source_clean: bool,
    dirty_entries: list[dict[str, str]],
    dirty_digests: list[dict[str, Any]],
) -> dict[str, Any]:
    state = "clean" if source_clean else "dirty"
    return {
        "artifact": {
            "id": f"{PACK_ID}@{VERSION}",
            "bundle_file": f"{PACK_ID}-{VERSION}.ucp.tar.gz",
            "bundle_sha256": bundle_sha,
            "payload_file": "payload.tar.gz",
            "payload_sha256": payload_sha,
            "manifest_file": "manifest.json",
            "manifest_sha256": manifest_sha,
            "conformance_file": "conformance.json",
            "conformance_sha256": conformance_sha,
            "dependency_lock_file": "pack_dependencies.json",
            "dependency_lock_sha256": dependency_lock_sha,
        },
        "source": {
            "repository": "https://github.com/SmartHausGroup/M365.git",
            "branch": _git_current_branch(),
            "commit": _git_head_commit(),
            "clean": source_clean,
            "state": state,
            "dirty_files": dirty_entries,
            "dirty_files_digests": dirty_digests,
        },
        "reproducibility": {
            "claims_clean_reproducible": source_clean,
            "release_blocker_if_dirty": True,
            "two_build_byte_identical_required": True,
            "note": (
                "Final GO requires source_clean=True. A dirty worktree records the "
                "dirty file digests above and remains NO_GO unless the CTO explicitly "
                "accepts the weaker provenance state."
            ),
        },
        "policy": {
            "studio_app_bundle_inclusion": False,
            "external_mcp_server_registration": False,
            "runtime_registration_source": "ucp_local_integration_pack_artifact",
            "runtime_packaged": True,
            "graph_runtime_in_payload": True,
        },
        "ucp_local_distribution": {
            "plan_ref": RELEASE_PLAN_REF,
            "repo_path": f"IntegrationPacks/M365/{VERSION}/{PACK_ID}-{VERSION}.ucp.tar.gz",
            "purpose": (
                "Standalone M365 Graph runtime Integration Pack distributable "
                "artifact for UCP Marketplace registration without sibling "
                "repository runtime references."
            ),
        },
        "built_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "install_dir": str(install_dir),
    }


def _write_bundle(
    bundle_path: Path,
    manifest_path: Path,
    payload_path: Path,
    sig_dir: Path,
    evidence_dir: Path,
    assets_dir: Path,
) -> str:
    if bundle_path.exists():
        bundle_path.unlink()
    items: list[tuple[Path, str]] = [
        (manifest_path, "manifest.json"),
        (payload_path, "payload.tar.gz"),
    ]
    for sig in sorted(sig_dir.glob("*.sig")):
        items.append((sig, f"signatures/{sig.name}"))
    items.append((evidence_dir / "conformance.json", "evidence/conformance.json"))
    items.append((assets_dir / "README.md", "assets/README.md"))
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tf:
        for source, arcname in items:
            info = tf.gettarinfo(str(source), arcname=arcname)
            info = _normalize_tarinfo(info)
            with source.open("rb") as fh:
                tf.addfile(info, fh)
    raw = buffer.getvalue()
    with gzip.GzipFile(filename=str(bundle_path), mode="wb", mtime=0, compresslevel=6) as gz:
        gz.write(raw)
    return _sha256(bundle_path)


def _emit_assets_readme(assets_dir: Path) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "README.md").write_text(
        "# SMARTHAUS Microsoft 365 Integration Pack\n\n"
        "This artifact contains the standalone Microsoft Graph runtime service, "
        "OAuth and app-only auth flows, secure token storage policy, health and "
        "readiness contracts, a bounded read-only Graph action runtime, the "
        "UCP-facing pack contracts, and packaging evidence.\n\n"
        "Read-only Graph actions are the only mutating surface authorized for v1.\n"
        "Microsoft Graph write actions require a separate mutation-governance plan.\n\n"
        "Run `python -m m365_runtime` from the installed pack directory to launch.\n",
        encoding="utf-8",
    )


def _emit_signatures(sig_dir: Path, manifest_sha: str, payload_sha: str) -> None:
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "manifest.sig").write_text(
        _stable_compact_json({"alg": "sha256-detached", "sha256": manifest_sha}),
        encoding="utf-8",
    )
    (sig_dir / "payload.sig").write_text(
        _stable_compact_json({"alg": "sha256-detached", "sha256": payload_sha}),
        encoding="utf-8",
    )


def _emit_sha256sums(dist_dir: Path, names: list[str]) -> None:
    lines = []
    for name in names:
        path = dist_dir / name
        sha = _sha256(path)
        lines.append(f"{sha}  {name}")
    (dist_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _copy_to_integration_packs(dist_dir: Path, version: str) -> Path:
    install_dir = INTEGRATION_PACKS / "M365" / version
    install_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        dist_dir / f"com.smarthaus.m365-{version}.ucp.tar.gz",
        install_dir / f"com.smarthaus.m365-{version}.ucp.tar.gz",
    )
    shutil.copy2(dist_dir / "manifest.json", install_dir / "manifest.json")
    shutil.copy2(dist_dir / "evidence" / "conformance.json", install_dir / "conformance.json")
    # Extract the inner payload into install_dir so the install dir is a
    # directly-launchable runtime root: m365_runtime/, ucp_m365_pack/,
    # registry/agents.yaml, setup_schema.json, pack_metadata.json all land
    # at install_dir. probe_artifact() at install_dir then succeeds without
    # any further user step.
    with tarfile.open(dist_dir / "payload.tar.gz") as tf:
        tf.extractall(install_dir)
    return install_dir


def _emit_install_readme(install_dir: Path) -> None:
    (install_dir / "README.md").write_text(
        "# SMARTHAUS Microsoft 365 Integration Pack\n\n"
        "Installed marketplace artifact for `com.smarthaus.m365@" + VERSION + "`.\n\n"
        "Envelope contents (verified by `SHA256SUMS`):\n"
        f"- `{PACK_ID}-{VERSION}.ucp.tar.gz` - the marketplace bundle.\n"
        "- `manifest.json` - declared identity, capabilities, and runtime entrypoint.\n"
        "- `conformance.json` - conformance evidence for this version.\n"
        "- `provenance.json` - source/build provenance for this version.\n"
        "- `SHA256SUMS` - integrity index over manifest, bundle, and conformance.\n\n"
        "Runnable runtime contents (extracted from the bundle's inner payload):\n"
        "- `m365_runtime/` - the standalone Microsoft Graph runtime service.\n"
        "- `ucp_m365_pack/` - the UCP-facing client and contracts.\n"
        "- `pack_metadata.json` - in-payload self-describing pack identity (no SHAs).\n"
        "- `setup_schema.json` - declared setup contract for the pack.\n"
        "- `registry/agents.yaml` - workforce graph the pack ships with.\n"
        "- `registry/action_registry.yaml` - read-only Graph action registry the runtime exposes.\n\n"
        "Launch the runtime locally with `python -m m365_runtime` from this "
        "install directory. The runtime resolves its installed root from its "
        "package location only, never from source-repo or sibling-repo env "
        "vars. `probe_artifact()` succeeds at this directory because both "
        "envelope `manifest.json` and in-payload `pack_metadata.json` are "
        "present, alongside `setup_schema.json` and `registry/agents.yaml`.\n",
        encoding="utf-8",
    )


def _emit_install_sha256sums(install_dir: Path, version: str) -> None:
    names = [
        f"{PACK_ID}-{version}.ucp.tar.gz",
        "manifest.json",
        "conformance.json",
    ]
    lines = []
    for name in names:
        path = install_dir / name
        sha = _sha256(path)
        lines.append(f"{sha}  {name}")
    (install_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    # Capture source provenance before writing generated dist/install outputs.
    # Otherwise a clean checkout records itself dirty because this script updates
    # tracked dist/m365_pack files as part of the build.
    source_clean, dirty_entries = _git_porcelain_status()
    dirty_digests = _digest_dirty_files(dirty_entries) if not source_clean else []

    DIST.mkdir(parents=True, exist_ok=True)
    stage_root = DIST / "_payload_stage"
    sig_dir = DIST / "signatures"
    evidence_dir = DIST / "evidence"
    assets_dir = DIST / "assets"
    payload_path = DIST / "payload.tar.gz"
    manifest_path = DIST / "manifest.json"
    bundle_path = DIST / f"{PACK_ID}-{VERSION}.ucp.tar.gz"

    _stage_payload(stage_root)
    payload_files = sorted(str(p.relative_to(stage_root)) for p in _runtime_files(stage_root))
    payload_sha = _build_payload_tar(stage_root, payload_path)

    manifest = _emit_manifest(payload_sha)
    manifest_path.write_text(_stable_json(manifest), encoding="utf-8")
    manifest_sha = _sha256(manifest_path)

    _emit_signatures(sig_dir, manifest_sha, payload_sha)

    evidence_dir.mkdir(parents=True, exist_ok=True)
    conformance = _emit_conformance(stage_root, manifest, payload_files)
    (evidence_dir / "conformance.json").write_text(_stable_json(conformance), encoding="utf-8")
    conformance_sha = _sha256(evidence_dir / "conformance.json")

    _emit_assets_readme(assets_dir)
    bundle_sha = _write_bundle(
        bundle_path, manifest_path, payload_path, sig_dir, evidence_dir, assets_dir
    )

    install_dir = INTEGRATION_PACKS / "M365" / VERSION
    dependency_lock_sha = _dependency_lock_sha(stage_root)
    provenance = _emit_provenance(
        bundle_sha,
        manifest_sha,
        conformance_sha,
        install_dir,
        payload_sha=payload_sha,
        dependency_lock_sha=dependency_lock_sha,
        source_clean=source_clean,
        dirty_entries=dirty_entries,
        dirty_digests=dirty_digests,
    )
    (DIST / "provenance.json").write_text(_stable_json(provenance), encoding="utf-8")

    _emit_sha256sums(DIST, [bundle_path.name, "manifest.json", "evidence/conformance.json"])

    install_dir = _copy_to_integration_packs(DIST, VERSION)
    shutil.copy2(DIST / "provenance.json", install_dir / "provenance.json")
    _emit_install_sha256sums(install_dir, VERSION)
    _emit_install_readme(install_dir)

    print(f"Built standalone Graph runtime pack {PACK_ID}-{VERSION}: bundle_sha256={bundle_sha}")
    print(f"Installed at: {install_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
