"""P7 packaging acceptance tests.

Plan: plan:m365-standalone-graph-runtime-integration-pack:R8
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
INTEGRATION_PACKS = Path("/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _active_version() -> str:
    spec = importlib.util.spec_from_file_location(
        "build_pack_m365", REPO / "scripts" / "ci" / "build_standalone_graph_runtime_pack.py"
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.VERSION


def _active_install_dir() -> Path:
    return INTEGRATION_PACKS / _active_version()


def _current_git_branch() -> str:
    out = subprocess.check_output(
        ["git", "-C", str(REPO), "branch", "--show-current"], text=True
    ).strip()
    return out or "detached"


@pytest.fixture(scope="module")
def built_pack(tmp_path_factory: pytest.TempPathFactory) -> str:
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts/ci/build_standalone_graph_runtime_pack.py")],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert out.returncode == 0, out.stderr or out.stdout
    return out.stdout


def test_dist_layout_contains_runtime_bundle(built_pack: str) -> None:
    dist = REPO / "dist" / "m365_pack"
    assert (dist / "manifest.json").exists()
    assert (dist / "payload.tar.gz").exists()
    assert (dist / "signatures" / "manifest.sig").exists()
    assert (dist / "signatures" / "payload.sig").exists()
    assert (dist / "evidence" / "conformance.json").exists()
    bundles = sorted(dist.glob("com.smarthaus.m365-*.ucp.tar.gz"))
    assert bundles


def test_payload_includes_m365_runtime(built_pack: str) -> None:
    payload = REPO / "dist" / "m365_pack" / "payload.tar.gz"
    with tarfile.open(payload) as tf:
        names = {m.name for m in tf.getmembers() if m.isfile()}
    assert "m365_runtime/__init__.py" in names
    assert "m365_runtime/__main__.py" in names
    assert "m365_runtime/launcher.py" in names
    assert "m365_runtime/auth/oauth.py" in names
    assert "m365_runtime/auth/app_only.py" in names
    assert "m365_runtime/auth/token_store.py" in names
    assert "m365_runtime/graph/client.py" in names
    assert "m365_runtime/graph/errors.py" in names
    assert "m365_runtime/graph/registry.py" in names
    assert "m365_runtime/graph/actions.py" in names
    assert "m365_runtime/health.py" in names
    assert "m365_runtime/audit.py" in names
    assert "m365_runtime/_forbidden_tokens.py" in names
    assert "ucp_m365_pack/__init__.py" in names
    assert "ucp_m365_pack/client.py" in names
    assert "ucp_m365_pack/contracts.py" in names
    assert "setup_schema.json" in names
    assert "registry/agents.yaml" in names
    assert "registry/action_registry.yaml" in names
    assert "pack_metadata.json" in names


def test_manifest_declares_runtime(built_pack: str) -> None:
    manifest = json.loads((REPO / "dist" / "m365_pack" / "manifest.json").read_text())
    assert manifest["pack_id"] == "com.smarthaus.m365"
    assert manifest["schema_version"] == "0.2.0"
    runtime = manifest["runtime"]
    assert runtime["module"] == "m365_runtime"
    assert runtime["entrypoint_command"] == ["python", "-m", "m365_runtime"]
    assert runtime["read_only"] is True
    assert runtime["mutation_fence"] is True
    assert runtime["health_path"] == "/v1/health/readiness"
    assert runtime["actions_path"] == "/v1/actions"
    assert runtime["invoke_path_template"] == "/v1/actions/{action_id}/invoke"


def test_sha256sums_match_files(built_pack: str) -> None:
    dist = REPO / "dist" / "m365_pack"
    sums_path = dist / "SHA256SUMS"
    expected = {}
    for line in sums_path.read_text().splitlines():
        if not line.strip():
            continue
        sha, name = line.split(maxsplit=1)
        expected[name.strip()] = sha
    for name, sha in expected.items():
        path = dist / name
        assert path.exists(), name
        assert _sha(path) == sha, name


def test_install_dir_contains_runtime_pack(built_pack: str) -> None:
    latest = _active_version()
    install = _active_install_dir()
    bundle = install / f"com.smarthaus.m365-{latest}.ucp.tar.gz"
    manifest = install / "manifest.json"
    conformance = install / "conformance.json"
    sums = install / "SHA256SUMS"
    provenance = install / "provenance.json"
    readme = install / "README.md"
    for required in (bundle, manifest, conformance, sums, provenance, readme):
        assert required.exists(), str(required)


def test_installed_pack_contains_runtime_when_extracted(tmp_path: Path) -> None:
    install_dir = _active_install_dir()
    bundle = next(install_dir.glob("com.smarthaus.m365-*.ucp.tar.gz"))
    extract = tmp_path / "extract"
    extract.mkdir()
    with tarfile.open(bundle) as tf:
        tf.extractall(extract)
    payload = extract / "payload.tar.gz"
    assert payload.exists()
    with tarfile.open(payload) as tf:
        tf.extractall(extract)
    assert (extract / "m365_runtime" / "__init__.py").exists()
    assert (extract / "m365_runtime" / "launcher.py").exists()
    assert (extract / "m365_runtime" / "graph" / "actions.py").exists()


def test_installed_pack_runtime_runs_without_repo_root(tmp_path: Path) -> None:
    install_dir = _active_install_dir()
    bundle = next(install_dir.glob("com.smarthaus.m365-*.ucp.tar.gz"))
    extract = tmp_path / "extract"
    extract.mkdir()
    with tarfile.open(bundle) as tf:
        tf.extractall(extract)
    with tarfile.open(extract / "payload.tar.gz") as tf:
        tf.extractall(extract)
    env = {"PATH": "/Users/smarthaus/Projects/GitHub/M365/.venv/bin:/usr/bin:/bin"}
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import m365_runtime; from m365_runtime.launcher import plan_launch; from m365_runtime.graph.registry import READ_ONLY_REGISTRY; print(m365_runtime.RUNTIME_VERSION); print(len(READ_ONLY_REGISTRY)); print(plan_launch().outcome)",
        ],
        env={**env, "PYTHONPATH": str(extract)},
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.strip().splitlines()
    assert out[0] == _active_version()
    assert out[1] == "11"
    assert out[2] == "started"


def test_installed_provenance_records_graph_runtime_in_payload() -> None:
    install_dir = _active_install_dir()
    provenance = json.loads((install_dir / "provenance.json").read_text())
    assert provenance["policy"]["runtime_packaged"] is True
    assert provenance["policy"]["graph_runtime_in_payload"] is True


def test_installed_provenance_records_current_release_source() -> None:
    install_dir = _active_install_dir()
    provenance = json.loads((install_dir / "provenance.json").read_text())
    assert provenance["source"]["branch"] == _current_git_branch()
    assert provenance["ucp_local_distribution"]["plan_ref"] == (
        "plan:m365-0-1-3-github-release-and-ucp-handoff-closure:R6"
    )
