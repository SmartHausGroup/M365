"""Regression tests for the 0.1.2 readiness fix invariants.

Plan reference: plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix
Lemma backing: L99_m365_standalone_graph_runtime_pack_0_1_2_readiness_fix_v1
Notebook: notebooks/m365/INV-M365-DO-standalone-graph-runtime-pack-0-1-2-readiness-fix-v1.ipynb

Each test maps to a single L99 invariant clause:

- test_runtime_version_constant_is_0_1_2 -> L_VERSION_CORRECT
- test_pack_metadata_in_staged_payload   -> L_ARTIFACT_SELFDESC
- test_probe_artifact_succeeds_on_payload_root -> L_ARTIFACT_SELFDESC
- test_probe_artifact_succeeds_on_overlay_layout -> L_ARTIFACT_SELFDESC
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
BUILD_SCRIPT = REPO / "scripts" / "ci" / "build_standalone_graph_runtime_pack.py"


def _import_build_script() -> ModuleType:
    sys.path.insert(0, str(SRC))
    spec = importlib.util.spec_from_file_location("build_pack_m365", BUILD_SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _import_health() -> ModuleType:
    sys.path.insert(0, str(SRC))
    import importlib

    if "m365_runtime.health" in sys.modules:
        return importlib.reload(sys.modules["m365_runtime.health"])
    return importlib.import_module("m365_runtime.health")


def test_runtime_version_constant_matches_pack_builder_version() -> None:
    sys.path.insert(0, str(SRC))
    import importlib

    if "m365_runtime" in sys.modules:
        m365_runtime = importlib.reload(sys.modules["m365_runtime"])
    else:
        m365_runtime = importlib.import_module("m365_runtime")
    build_pack = _import_build_script()
    assert m365_runtime.RUNTIME_VERSION == build_pack.VERSION


def test_pack_metadata_in_staged_payload(tmp_path: Path) -> None:
    build_pack = _import_build_script()
    stage_root = tmp_path / "stage"
    build_pack._stage_payload(stage_root)
    metadata_path = stage_root / "pack_metadata.json"
    assert (
        metadata_path.is_file()
    ), f"pack_metadata.json missing from staged payload at {stage_root}"
    metadata = json.loads(metadata_path.read_text())
    assert metadata["pack_id"] == "com.smarthaus.m365"
    assert metadata["version"] == build_pack.VERSION
    assert metadata["runtime"]["module"] == "m365_runtime"
    assert metadata["runtime"]["read_only"] is True
    assert metadata["runtime"]["mutation_fence"] is True
    assert metadata["runtime"]["username_password_supported"] is False
    assert "device_code" in metadata["runtime"]["supported_auth_modes"]


def test_probe_artifact_succeeds_on_payload_root(tmp_path: Path) -> None:
    build_pack = _import_build_script()
    health = _import_health()
    stage_root = tmp_path / "payload_only"
    build_pack._stage_payload(stage_root)
    assert (stage_root / "pack_metadata.json").is_file()
    assert (stage_root / "setup_schema.json").is_file()
    assert (stage_root / "registry" / "agents.yaml").is_file()
    assert health.probe_artifact(stage_root) is True


def test_probe_artifact_succeeds_on_overlay_layout(tmp_path: Path) -> None:
    """Outer envelope + inner payload extracted into the same directory.

    This mirrors the live-installed-pack flow: the user (or _copy_to_integration_packs)
    extracts the outer .ucp.tar.gz into install_dir and then extracts the inner
    payload.tar.gz into the same install_dir. probe_artifact() must succeed
    against that overlay layout.
    """
    build_pack = _import_build_script()
    health = _import_health()
    overlay = tmp_path / "overlay"
    # _stage_payload wipes the directory first, so stage the inner payload
    # before adding the outer envelope's manifest.json on top.
    build_pack._stage_payload(overlay)
    payload_sha_placeholder = "0" * 64
    outer_manifest = build_pack._emit_manifest(payload_sha_placeholder)
    (overlay / "manifest.json").write_text(
        json.dumps(outer_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    # All four self-describing files now sit at the install root.
    assert (overlay / "manifest.json").is_file()
    assert (overlay / "pack_metadata.json").is_file()
    assert (overlay / "setup_schema.json").is_file()
    assert (overlay / "registry" / "agents.yaml").is_file()
    assert health.probe_artifact(overlay) is True


def test_probe_artifact_fails_when_payload_missing(tmp_path: Path) -> None:
    health = _import_health()
    bare = tmp_path / "bare"
    bare.mkdir()
    # Only manifest.json present (current 1.1.1 install_dir layout). probe_artifact
    # must fail because setup_schema.json and registry/agents.yaml are absent.
    (bare / "manifest.json").write_text("{}", encoding="utf-8")
    assert health.probe_artifact(bare) is False


# --- L_DEPENDENCY_CLOSED ---------------------------------------------------


def test_pack_dependencies_in_staged_payload(tmp_path: Path) -> None:
    build_pack = _import_build_script()
    stage_root = tmp_path / "stage"
    build_pack._stage_payload(stage_root)
    deps_path = stage_root / "pack_dependencies.json"
    assert deps_path.is_file(), "pack_dependencies.json missing from staged payload"
    deps = json.loads(deps_path.read_text())
    assert deps["pack_id"] == "com.smarthaus.m365"
    assert deps["version"] == build_pack.VERSION
    required_names = {entry["module"] for entry in deps["required"]}
    assert {"httpx", "fastapi", "uvicorn"}.issubset(required_names)
    cert_modules = {
        entry["module"] for entry in deps["auth_mode_dependencies"]["app_only_certificate"]
    }
    assert "jwt" in cert_modules
    assert deps["fail_closed_outcome_class"] == "dependency_missing"


def test_jwt_not_imported_at_module_load_for_app_only() -> None:
    """L_DEPENDENCY_CLOSED: PyJWT must not be a module-load-time dependency
    of m365_runtime.auth.app_only. Verified statically by reading the source
    so the test does not need to manipulate sys.modules (which would risk
    polluting other tests in the suite).
    """
    source = (SRC / "m365_runtime" / "auth" / "app_only.py").read_text()
    # Module-level lines that look like `import jwt` or `from jwt ...`.
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("import jwt") or stripped.startswith("from jwt"):
            # Allowed only if indented (i.e., inside a function body).
            assert line.startswith((" ", "\t")), (
                f"app_only.py imports jwt at module load: {line!r}; "
                "PyJWT must be lazy-imported inside the function that uses it."
            )


def test_launcher_returns_dependency_missing_when_required_module_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L_DEPENDENCY_CLOSED: missing required module surfaces as
    structured dependency_missing outcome, not raw ModuleNotFoundError.

    In-process variant: blocks httpx after the launcher is already loaded.
    The harder F1 invariant - that the launcher MODULE itself imports
    cleanly even when httpx is genuinely absent at import time - is
    proven by the subprocess tests below.
    """
    sys.path.insert(0, str(SRC))
    import importlib

    if "m365_runtime.launcher" in sys.modules:
        del sys.modules["m365_runtime.launcher"]
    launcher = importlib.import_module("m365_runtime.launcher")
    # Simulate httpx missing.
    monkeypatch.setitem(sys.modules, "httpx", None)
    plan = launcher.plan_launch()
    assert plan.outcome == "dependency_missing"
    assert plan.detail.get("reason") == "required_modules_missing"
    assert "httpx" in plan.detail.get("missing_modules", [])


def _subprocess_probe(blocked_module: str) -> dict[str, Any]:
    """Spawn a Python subprocess where ``blocked_module`` is poisoned in
    ``sys.modules`` BEFORE ``m365_runtime.launcher`` is imported, then
    import the launcher and call ``plan_launch()``. Returns the parsed
    JSON the subprocess emits on stdout (or an error envelope).
    """
    script = f"""
import json, sys
# Block the target module BEFORE m365_runtime.launcher is imported.
sys.modules[{blocked_module!r}] = None
import_outcome = {{"importable": False}}
try:
    import m365_runtime.launcher as launcher
    import_outcome["importable"] = True
    plan = launcher.plan_launch()
    out = {{
        "blocked": {blocked_module!r},
        "module_import_succeeded": True,
        "plan_outcome": plan.outcome,
        "plan_detail_reason": plan.detail.get("reason"),
        "missing_modules": plan.detail.get("missing_modules", []),
        "present_modules": plan.detail.get("present_modules", []),
    }}
except Exception as exc:
    out = {{
        "blocked": {blocked_module!r},
        "module_import_succeeded": False,
        "exception_class": type(exc).__name__,
        "exception_message": str(exc)[:200],
    }}
print(json.dumps(out))
"""
    proc = subprocess.run(
        [sys.executable, "-c", script],
        env={
            "PATH": "/Users/smarthaus/Projects/GitHub/M365/.venv/bin:/usr/bin:/bin",
            "PYTHONPATH": str(SRC),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        capture_output=True,
        text=True,
        timeout=20,
    )
    out = proc.stdout.strip().splitlines()
    if not out:
        return {"_subprocess_failed": True, "returncode": proc.returncode, "stderr": proc.stderr}
    try:
        return json.loads(out[-1])
    except json.JSONDecodeError:
        return {"_parse_error": out[-1], "stderr": proc.stderr}


def test_launcher_imports_when_httpx_absent_at_import_time() -> None:
    """F1 hard invariant: importing m365_runtime.launcher must succeed
    even when httpx is genuinely absent at import time, and plan_launch()
    must return outcome=dependency_missing with httpx listed as missing.
    """
    result = _subprocess_probe("httpx")
    assert result.get("module_import_succeeded") is True, result
    assert result.get("plan_outcome") == "dependency_missing", result
    assert result.get("plan_detail_reason") == "required_modules_missing", result
    assert "httpx" in result.get("missing_modules", []), result


def test_launcher_imports_when_fastapi_absent_at_import_time() -> None:
    """F1 hard invariant: same proof, but with fastapi blocked."""
    result = _subprocess_probe("fastapi")
    assert result.get("module_import_succeeded") is True, result
    assert result.get("plan_outcome") == "dependency_missing", result
    assert "fastapi" in result.get("missing_modules", []), result


def test_launcher_imports_when_uvicorn_absent_at_import_time() -> None:
    """F1 hard invariant: same proof, but with uvicorn blocked."""
    result = _subprocess_probe("uvicorn")
    assert result.get("module_import_succeeded") is True, result
    assert result.get("plan_outcome") == "dependency_missing", result
    assert "uvicorn" in result.get("missing_modules", []), result


def test_launcher_top_level_does_not_import_dependency_sensitive_submodules() -> None:
    """F1 static guard: the launcher source must not import the
    dependency-sensitive submodules at module load. The dangerous imports
    must be inside function bodies (indented).
    """
    source = (SRC / "m365_runtime" / "launcher.py").read_text()
    forbidden_top_level = (
        "from .auth import oauth",
        "from .auth.app_only import",
        "from .graph.actions import",
        "from .graph.client import",
        "from .health import",
    )
    for line in source.splitlines():
        for forbidden in forbidden_top_level:
            if line.startswith(forbidden):
                pytest.fail(
                    f"launcher.py top-level imports dependency-sensitive submodule: {line!r}; "
                    "move this import inside the function that uses it."
                )


def test_dependency_probe_endpoint_reports_present_modules() -> None:
    """L_DEPENDENCY_CLOSED: /v1/health/dependencies surfaces present and
    missing module names so operators can diagnose without reading raw
    Python tracebacks.
    """
    sys.path.insert(0, str(SRC))
    import importlib

    if "m365_runtime.launcher" in sys.modules:
        del sys.modules["m365_runtime.launcher"]
    launcher = importlib.import_module("m365_runtime.launcher")
    present, missing = launcher._probe_required_dependencies()
    # In the dev .venv, all required modules are present.
    assert "httpx" in present
    assert "fastapi" in present
    assert "uvicorn" in present
    assert missing == []


# --- L_SOCKET_REAL ---------------------------------------------------------


def _import_acceptance_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "acceptance_pack_m365",
        REPO / "scripts" / "ci" / "acceptance_standalone_graph_runtime_pack.py",
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_acceptance_script_does_not_monkeypatch_http_runtime_invoke() -> None:
    """L_SOCKET_REAL: the C5 acceptance script must not contain the legacy
    `ucp_client._http_runtime_invoke = ...` monkey-patch line.
    """
    text = (REPO / "scripts" / "ci" / "acceptance_standalone_graph_runtime_pack.py").read_text()
    assert "_http_runtime_invoke = fake_runtime_invoke" not in text
    assert "ucp_client._http_runtime_invoke =" not in text
    assert "_assert_unpatched_http_runtime_invoke" in text


def test_acceptance_unpatched_guard_passes_for_real_function() -> None:
    """The guard must accept the unpatched real implementation defined in
    ucp_m365_pack.client.
    """
    acceptance = _import_acceptance_script()
    sys.path.insert(0, str(SRC))
    # Use the live ucp_m365_pack.client module (do NOT delete from sys.modules:
    # other tests in the suite import functions from this module at collection
    # time, and replacing the module would leave their references stale).
    acceptance._assert_unpatched_http_runtime_invoke(SRC)


def test_acceptance_unpatched_guard_fails_when_patched(monkeypatch: pytest.MonkeyPatch) -> None:
    """L_SOCKET_REAL: monkey-patching `_http_runtime_invoke` must trip the
    guard so release acceptance fails closed.
    """
    acceptance = _import_acceptance_script()
    sys.path.insert(0, str(SRC))
    import ucp_m365_pack.client as ucp_client

    def _fake(*a: Any, **kw: Any) -> dict[str, str]:  # different __module__ than the real function
        return {"status_class": "fake"}

    # Use monkeypatch.setattr so the live module is restored after the test
    # rather than left in a patched state (preserving suite test isolation).
    monkeypatch.setattr(ucp_client, "_http_runtime_invoke", _fake)
    with pytest.raises(RuntimeError, match="monkey-patched"):
        acceptance._assert_unpatched_http_runtime_invoke(SRC)


def test_acceptance_uses_subprocess_and_uvicorn() -> None:
    """L_SOCKET_REAL: the acceptance script must spawn a runtime subprocess
    bound to a real loopback port via uvicorn, not an in-process TestClient
    or in-process transport.
    """
    text = (REPO / "scripts" / "ci" / "acceptance_standalone_graph_runtime_pack.py").read_text()
    assert "uvicorn" in text
    assert "subprocess.Popen" in text
    assert "_pick_free_port" in text
    # TestClient must not be USED in the acceptance script (docstring may
    # reference where the in-process unit tests live).
    assert "TestClient(" not in text
    assert "from fastapi.testclient" not in text


# --- L_READINESS_READY (C6) ------------------------------------------------


def test_readiness_flips_to_ready_success_with_pack_metadata_layout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """C6 mocked-acceptance gate: with the new pack_metadata.json layout
    staged at installed_root and OAuth+Graph mocked at the transport
    boundary, the full readiness vector must flip to ready/success after
    auth_check stores a token through the configured token store.
    """
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    import httpx
    from fastapi.testclient import TestClient

    sys.path.insert(0, str(SRC))
    import importlib

    if "m365_runtime.launcher" in sys.modules:
        del sys.modules["m365_runtime.launcher"]
    if "m365_runtime.health" in sys.modules:
        del sys.modules["m365_runtime.health"]
    launcher = importlib.import_module("m365_runtime.launcher")

    build_pack = _import_build_script()
    pack = tmp_path / "pack"
    build_pack._stage_payload(pack)

    class _MemStore:
        backend = "memory"
        keychain_service = "ai.smarthaus.m365.c6"
        encrypted_pack_local_allowed = False
        pack_local_path = None

        def __init__(self) -> None:
            self._v: dict[str, str] = {}

        def put(self, k: str, v: str) -> None:
            self._v[k] = v

        def get(self, k: str) -> str | None:
            return self._v.get(k)

        def clear(self, k: str) -> None:
            self._v.pop(k, None)

    store = _MemStore()
    monkeypatch.setattr(
        "m365_runtime.auth.token_store.TokenStore.from_setup",
        classmethod(lambda cls, s, r: store),
    )

    env = {
        "M365_TENANT_ID": "11111111-1111-1111-1111-111111111111",
        "M365_CLIENT_ID": "22222222-2222-2222-2222-222222222222",
        "M365_AUTH_MODE": "auth_code_pkce",
        "M365_SERVICE_ACTOR_UPN": "ops@example.com",
        "M365_REDIRECT_URI": "http://127.0.0.1:9301/callback",
        "M365_GRANTED_SCOPES": "User.Read,Sites.Read.All,Organization.Read.All",
        "M365_TOKEN_STORE": "keychain",
    }

    plan = launcher.plan_launch(env=env)
    plan = launcher.LaunchPlan(
        outcome=plan.outcome,
        installed_root=pack,
        setup=plan.setup,
        listen_host=plan.listen_host,
        listen_port=plan.listen_port,
        detail=plan.detail,
    )

    def oauth_handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/oauth2/v2.0/token"):
            return httpx.Response(
                200, json={"access_token": "AT", "refresh_token": "RT", "expires_in": 3600}
            )
        return httpx.Response(404, json={"error": "unhandled"})

    def graph_handler(req: httpx.Request) -> httpx.Response:
        if req.url.path == "/v1.0/organization":
            return httpx.Response(200, json={"value": [{"id": "tenant-c6"}]})
        return httpx.Response(404, json={"error": "unhandled"})

    app = launcher.build_app(
        plan,
        oauth_transport=httpx.MockTransport(oauth_handler),
        graph_transport=httpx.MockTransport(graph_handler),
    )
    client = TestClient(app)

    readiness_before = client.get("/v1/health/readiness").json()
    assert readiness_before["state"]["state"] == "not_ready"
    assert readiness_before["vector"]["art"] is True  # C3 layout fix proven
    assert readiness_before["vector"]["auth"] is False

    start = client.post("/v1/auth/start", json={}).json()
    assert start["state"] == "auth_started"
    check = client.post(
        "/v1/auth/check", json={"code": "X", "state": start["expected_state"]}
    ).json()
    assert check["state"] == "signed_in"

    readiness_after = client.get("/v1/health/readiness").json()
    assert readiness_after["state"]["state"] == "ready", readiness_after
    assert readiness_after["state"]["label"] == "success"
    vec = readiness_after["vector"]
    assert vec["art"] is True
    assert vec["auth"] is True
    assert vec["tok"] is True
    assert vec["graph"] is True
    assert vec["perm"] is True
    assert vec["src"] is True
    assert vec["ctr"] is True
    assert vec["aud"] is True
    assert vec["svc"] is True


# --- L_PROVENANCE_REPRO (C8) -----------------------------------------------


def test_provenance_records_required_keys_for_reproducibility() -> None:
    """C8 gate: provenance.json (built into the active install dir) must
    record source commit/branch/clean state, payload SHA, bundle SHA,
    manifest SHA, conformance SHA, dependency lock SHA, and an explicit
    reproducibility claim block.
    """
    install_dir = Path("/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365") / "0.1.2"
    if not install_dir.exists():
        pytest.skip("0.1.2 install dir not built yet")
    provenance = json.loads((install_dir / "provenance.json").read_text())
    artifact = provenance["artifact"]
    for key in (
        "id",
        "bundle_file",
        "bundle_sha256",
        "payload_file",
        "payload_sha256",
        "manifest_file",
        "manifest_sha256",
        "conformance_file",
        "conformance_sha256",
        "dependency_lock_file",
        "dependency_lock_sha256",
    ):
        assert key in artifact, f"provenance.artifact missing {key}"
    source = provenance["source"]
    for key in (
        "repository",
        "branch",
        "commit",
        "clean",
        "state",
        "dirty_files",
        "dirty_files_digests",
    ):
        assert key in source, f"provenance.source missing {key}"
    repro = provenance["reproducibility"]
    for key in (
        "claims_clean_reproducible",
        "release_blocker_if_dirty",
        "two_build_byte_identical_required",
    ):
        assert key in repro
    assert repro["release_blocker_if_dirty"] is True
    # Honesty: claims_clean_reproducible must mirror source.clean.
    assert repro["claims_clean_reproducible"] is source["clean"]


def test_provenance_does_not_lie_about_clean_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """C8 invariant: `_emit_provenance` must NEVER mark
    `claims_clean_reproducible=True` while `source_clean=False`. Drives
    `_emit_provenance` directly with a forced dirty state and asserts the
    invariant.
    """
    build_pack = _import_build_script()
    prov = build_pack._emit_provenance(
        "0" * 64,
        "0" * 64,
        "0" * 64,
        tmp_path / "install_x",
        payload_sha="0" * 64,
        dependency_lock_sha="0" * 64,
        source_clean=False,
        dirty_entries=[{"status": " M", "path": "src/example.py"}],
        dirty_digests=[{"status": " M", "path": "src/example.py", "sha256": "a" * 64}],
    )
    assert prov["source"]["clean"] is False
    assert prov["source"]["state"] == "dirty"
    assert prov["reproducibility"]["claims_clean_reproducible"] is False
    assert prov["reproducibility"]["release_blocker_if_dirty"] is True
