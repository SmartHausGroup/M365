#!/usr/bin/env python3
"""C5 acceptance: real local socket UCP-client acceptance for `0.1.2`.

Plan reference: plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix:C5
Lemma backing: L99_m365_standalone_graph_runtime_pack_0_1_2_readiness_fix_v1
Invariant: L_SOCKET_REAL

Flow:
  1. Locate the install dir for the active VERSION (from build script).
  2. Verify SHA256SUMS integrity.
  3. Extract outer .ucp.tar.gz + inner payload.tar.gz into a temp dir.
  4. Spawn a subprocess that builds the runtime app with MockTransport for
     OAuth + Graph (so Microsoft is mocked, but the runtime listens on a
     real local socket via uvicorn).
  5. Wait for the runtime to bind a dynamic loopback port.
  6. Set M365_RUNTIME_URL to the bound port.
  7. Drive auth_start + auth_check + readiness over real `httpx` to the
     local socket.
  8. Call `ucp_m365_pack.client.execute_m365_action()` WITHOUT patching
     `_http_runtime_invoke`. The guard `_assert_unpatched_http_runtime_invoke`
     fails the run if monkeypatching is detected.
  9. Prove a representative legacy alias mapping over real HTTP
     (users.read -> graph.users.list).
  10. Capture findings + release decision.
  11. Tear down subprocess.

Mocked unit-test variants (FastAPI TestClient against build_app) live in
`tests/test_m365_runtime_p4_runtime_and_auth.py`,
`tests/test_m365_runtime_p5_launcher_app.py`, and
`tests/test_m365_runtime_fix_auth_lifecycle.py` and are intentionally NOT
the release acceptance gate.

Live UCP through-the-installed-pack acceptance is intentionally out of
scope for this M365-side plan and is the responsibility of the sibling
UCP plan.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PACKS = Path("/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365")


def _active_version() -> str:
    spec = importlib.util.spec_from_file_location(
        "build_pack_m365", REPO / "scripts" / "ci" / "build_standalone_graph_runtime_pack.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.VERSION


def _active_install_dir() -> Path:
    return PACKS / _active_version()


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_integrity(install_dir: Path) -> dict:
    sums_path = install_dir / "SHA256SUMS"
    if not sums_path.exists():
        return {"ok": False, "reason": "sha256sums_missing"}
    expected = {}
    for line in sums_path.read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        expected[parts[1].strip()] = parts[0]
    actual = {name: _sha(install_dir / name) for name in expected.keys()}
    ok = all(expected[name] == actual[name] for name in expected.keys())
    return {"ok": ok, "expected": expected, "actual": actual}


def _extract_bundle(install_dir: Path, dst: Path) -> Path:
    bundle = next(install_dir.glob("com.smarthaus.m365-*.ucp.tar.gz"))
    with tarfile.open(bundle) as tf:
        tf.extractall(dst)
    with tarfile.open(dst / "payload.tar.gz") as tf:
        tf.extractall(dst)
    return dst


def _pick_free_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


_RUNTIME_SUBPROCESS_SCRIPT = '''
import json, os, sys, threading
sys.path.insert(0, os.environ["PACK_ROOT"])
from pathlib import Path

import httpx, uvicorn

import m365_runtime
from m365_runtime.launcher import build_app, plan_launch, LaunchPlan

# In-memory token store backend so acceptance does not need macOS Keychain.
class _MemoryTokenStore:
    backend = "memory"
    keychain_service = "ai.smarthaus.m365.acceptance"
    encrypted_pack_local_allowed = False
    pack_local_path = None
    def __init__(self):
        self._values = {}
    def put(self, key, value):
        self._values[key] = value
    def get(self, key):
        return self._values.get(key)
    def clear(self, key):
        self._values.pop(key, None)

import m365_runtime.auth.token_store as ts_mod
_acceptance_store = _MemoryTokenStore()
ts_mod.TokenStore.from_setup = classmethod(lambda cls, s, r: _acceptance_store)

def oauth_handler(request):
    if request.url.path.endswith("/oauth2/v2.0/token"):
        return httpx.Response(200, json={"access_token": "ACCEPT_AT", "refresh_token": "ACCEPT_RT", "expires_in": 3600})
    if request.url.path.endswith("/devicecode"):
        return httpx.Response(200, json={
            "device_code": "DC", "user_code": "ABC-DEF", "verification_uri": "https://microsoft.com/devicelogin",
            "expires_in": 900, "interval": 5,
        })
    return httpx.Response(404, json={"error": "unhandled_oauth"})

def graph_handler(request):
    path = request.url.path
    if path == "/v1.0/organization":
        return httpx.Response(200, json={"value": [{"id": "tenant-acceptance", "displayName": "Acceptance Tenant"}]})
    if path == "/v1.0/me":
        return httpx.Response(200, json={"id": "me-1", "displayName": "Acceptance Me", "userPrincipalName": "acceptance@example.com"})
    if path == "/v1.0/users":
        return httpx.Response(200, json={"value": [{"id": "u1", "displayName": "User One"}]})
    return httpx.Response(404, json={"error": {"code": "Unhandled", "message": path}})

env = {
    "M365_TENANT_ID": "11111111-1111-1111-1111-111111111111",
    "M365_CLIENT_ID": "22222222-2222-2222-2222-222222222222",
    "M365_AUTH_MODE": "auth_code_pkce",
    "M365_SERVICE_ACTOR_UPN": "acceptance@example.com",
    "M365_REDIRECT_URI": "http://127.0.0.1:9301/callback",
    "M365_GRANTED_SCOPES": "User.Read,User.Read.All,Sites.Read.All,Organization.Read.All",
    "M365_TOKEN_STORE": "keychain",
}

plan = plan_launch(env=env)
plan = LaunchPlan(
    outcome=plan.outcome,
    installed_root=Path(os.environ["PACK_ROOT"]),
    setup=plan.setup,
    listen_host=plan.listen_host,
    listen_port=plan.listen_port,
    detail=plan.detail,
)
app = build_app(
    plan,
    oauth_transport=httpx.MockTransport(oauth_handler),
    graph_transport=httpx.MockTransport(graph_handler),
)

port = int(os.environ["RUNTIME_PORT"])
config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
server = uvicorn.Server(config)
# Signal readiness via a marker file once the server is up.
def _signal_ready():
    import time as _t
    while not server.started:
        _t.sleep(0.05)
    Path(os.environ["READY_FILE"]).write_text(str(port))

threading.Thread(target=_signal_ready, daemon=True).start()
server.run()
'''


def _launch_runtime_subprocess(extract_dir: Path, port: int, ready_file: Path) -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, "-c", _RUNTIME_SUBPROCESS_SCRIPT],
        env={
            "PATH": "/Users/smarthaus/Projects/GitHub/M365/.venv/bin:/usr/bin:/bin",
            "PACK_ROOT": str(extract_dir),
            "PYTHONPATH": str(extract_dir),
            "RUNTIME_PORT": str(port),
            "READY_FILE": str(ready_file),
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 15.0
    while time.monotonic() < deadline:
        if ready_file.exists():
            return proc
        if proc.poll() is not None:
            stdout, stderr = proc.communicate(timeout=2)
            raise RuntimeError(
                f"runtime subprocess exited before binding port: rc={proc.returncode}\nstdout={stdout}\nstderr={stderr}"
            )
        time.sleep(0.1)
    proc.terminate()
    proc.wait(timeout=5)
    raise RuntimeError("runtime subprocess did not bind port within 15s")


def _stop_runtime_subprocess(proc: subprocess.Popen) -> tuple[int, str, str]:
    try:
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate(timeout=5)
        return proc.returncode if proc.returncode is not None else -1, stdout or "", stderr or ""
    except Exception as exc:
        return -1, "", f"stop_error: {exc}"


def _assert_unpatched_http_runtime_invoke(extract_dir: Path) -> None:
    """Hard guard: refuse to run release acceptance if `_http_runtime_invoke`
    has been monkey-patched. C5 invariant: the function MUST be the original
    real-httpx implementation defined in the packaged client module.

    The guard inspects the live ucp_m365_pack.client module in sys.modules
    (importing it for the first time if necessary) without resetting prior
    patches - the whole point is to detect a patch that is currently in
    effect.
    """
    sys.path.insert(0, str(extract_dir))
    import ucp_m365_pack.client as ucp_client  # use the live module if loaded
    func = ucp_client._http_runtime_invoke
    func_module = getattr(func, "__module__", None)
    func_qualname = getattr(func, "__qualname__", "")
    if func_module != "ucp_m365_pack.client" or func_qualname != "_http_runtime_invoke":
        raise RuntimeError(
            f"_http_runtime_invoke has been monkey-patched "
            f"(module={func_module}, qualname={func_qualname}); "
            "release acceptance MUST use the unpatched real-httpx implementation."
        )


def _real_socket_acceptance(extract_dir: Path) -> dict[str, Any]:
    import httpx

    port = _pick_free_port()
    with tempfile.TemporaryDirectory(prefix="m365-acceptance-ready-") as ready_dir:
        ready_file = Path(ready_dir) / "ready"
        proc = _launch_runtime_subprocess(extract_dir, port, ready_file)
        runtime_url = f"http://127.0.0.1:{port}"
        findings: dict[str, Any] = {}
        try:
            with httpx.Client(timeout=10.0) as client:
                # Static: runtime version + actions count.
                version_resp = client.get(f"{runtime_url}/v1/runtime/version")
                version_resp.raise_for_status()
                findings["runtime_version"] = version_resp.json()["runtime_version"]
                actions_resp = client.get(f"{runtime_url}/v1/actions")
                actions_resp.raise_for_status()
                findings["actions_count"] = actions_resp.json()["count"]

                # Pre-auth state.
                findings["status_before"] = client.get(f"{runtime_url}/v1/auth/status").json()["state"]
                readiness_before = client.get(f"{runtime_url}/v1/health/readiness").json()
                findings["readiness_before_state"] = readiness_before["state"]["state"]
                findings["readiness_before_label"] = readiness_before["state"]["label"]
                vec_before = readiness_before.get("vector", {})
                findings["art_before"] = vec_before.get("art")

                # Dependency probe over real HTTP.
                deps_resp = client.get(f"{runtime_url}/v1/health/dependencies")
                deps_resp.raise_for_status()
                deps_payload = deps_resp.json()
                findings["dependency_missing_modules"] = deps_payload["missing_modules"]
                findings["dependency_present_modules"] = deps_payload["present_modules"]

                # Drive auth_code_pkce start + check.
                start = client.post(f"{runtime_url}/v1/auth/start", json={}).json()
                findings["start_state"] = start["state"]
                expected_state = start.get("expected_state")
                check = client.post(
                    f"{runtime_url}/v1/auth/check",
                    json={"code": "AUTH_CODE", "state": expected_state},
                ).json()
                findings["check_state"] = check["state"]
                findings["status_after"] = client.get(f"{runtime_url}/v1/auth/status").json()["state"]
                readiness_after = client.get(f"{runtime_url}/v1/health/readiness").json()
                findings["readiness_after_state"] = readiness_after["state"]["state"]
                findings["readiness_after_label"] = readiness_after["state"]["label"]
                vec_after = readiness_after.get("vector", {})
                findings["art_after"] = vec_after.get("art")

                # Audit must not contain the access token bytes.
                findings["audit_no_access_token"] = "ACCEPT_AT" not in json.dumps(check)

                # Mutation fence.
                mutation = client.post(
                    f"{runtime_url}/v1/actions/graph.users.create/invoke",
                    json={"actor": "acceptance@example.com"},
                ).json()
                findings["mutation_status_class"] = mutation["status_class"]

                # Direct read-only invoke over real HTTP.
                direct = client.post(
                    f"{runtime_url}/v1/actions/graph.me/invoke",
                    json={"actor": "acceptance@example.com"},
                ).json()
                findings["direct_invoke_status_class"] = direct["status_class"]

                # Audit redaction proof.
                redact_check = client.post(
                    f"{runtime_url}/v1/actions/graph.org_profile/invoke",
                    json={"actor": "acceptance@example.com", "params": {"client_secret": "MUST_BE_REDACTED"}},
                ).json()
                findings["audit_redacts_secrets"] = "MUST_BE_REDACTED" not in json.dumps(redact_check)

            # UCP-facing client over real HTTP socket. NO _http_runtime_invoke
            # monkeypatching: execute_m365_action() must call the real httpx
            # function inside the packaged client module.
            _assert_unpatched_http_runtime_invoke(extract_dir)
            findings["http_runtime_invoke_unpatched_guard"] = True

            sys.path.insert(0, str(extract_dir))
            if "ucp_m365_pack.client" in sys.modules:
                del sys.modules["ucp_m365_pack.client"]
            import ucp_m365_pack.client as ucp_client

            os.environ["M365_RUNTIME_URL"] = runtime_url
            os.environ["M365_SERVICE_ACTOR_UPN"] = "acceptance@example.com"
            os.environ["M365_SERVICE_JWT_HS256_SECRET"] = "test-hs256-secret-not-a-real-key"

            ucp_result = ucp_client.execute_m365_action(
                "m365-administrator", "users.read", {"top": 1}
            )
            findings["ucp_client_status_class"] = ucp_result.get("status_class")
            findings["ucp_client_audit_action"] = ucp_result.get("audit", {}).get("action")
            # routing_snapshot() is a separate accessor, not part of the
            # execute_m365_action response. We call it explicitly to confirm
            # the configured live path is the local HTTP runtime.
            findings["ucp_client_routing_path"] = ucp_client.routing_snapshot().get(
                "selected_live_path"
            )

            ucp_org = ucp_client.execute_m365_action(
                "m365-administrator", "directory.org", {}
            )
            findings["ucp_org_status_class"] = ucp_org.get("status_class")
            findings["ucp_org_audit_action"] = ucp_org.get("audit", {}).get("action")

            # Final guard re-check after execute_m365_action: function still unpatched.
            assert ucp_client._http_runtime_invoke.__module__ == "ucp_m365_pack.client", (
                "_http_runtime_invoke was replaced during the acceptance run"
            )

        finally:
            rc, stdout, stderr = _stop_runtime_subprocess(proc)
            findings["runtime_subprocess_returncode"] = rc
            findings["runtime_subprocess_stderr_tail"] = (stderr or "")[-1024:]

    return findings


def main() -> int:
    install_dir = _active_install_dir()
    integrity = _verify_integrity(install_dir) if install_dir.exists() else {"ok": False, "reason": "install_dir_missing"}

    findings: dict[str, Any] = {}
    runtime_run_error: str | None = None
    if install_dir.exists():
        with tempfile.TemporaryDirectory(prefix="m365-acceptance-") as tmp_str:
            tmp = Path(tmp_str)
            extract_dir = tmp / "pack"
            extract_dir.mkdir()
            try:
                _extract_bundle(install_dir, extract_dir)
                findings = _real_socket_acceptance(extract_dir)
            except Exception as exc:
                runtime_run_error = f"{type(exc).__name__}: {exc}"
    else:
        runtime_run_error = "install_dir_missing"

    clauses = {
        "install_dir_present": install_dir.exists(),
        "integrity_sha256sums": integrity.get("ok") is True,
        "runtime_subprocess_no_error": runtime_run_error is None,
        "runtime_version_locked": findings.get("runtime_version") == _active_version(),
        "actions_count_locked": findings.get("actions_count") == 11,
        "art_true_after_extract": findings.get("art_after") is True,
        "readiness_after_is_ready": findings.get("readiness_after_state") == "ready",
        "readiness_after_label_is_success": findings.get("readiness_after_label") == "success",
        "auth_check_is_signed_in": findings.get("check_state") == "signed_in",
        "status_after_is_signed_in": findings.get("status_after") == "signed_in",
        "audit_does_not_leak_access_token": findings.get("audit_no_access_token") is True,
        "audit_redacts_secrets_in_params": findings.get("audit_redacts_secrets") is True,
        "mutation_action_fenced": findings.get("mutation_status_class") == "mutation_fence",
        "runtime_http_action_succeeds": findings.get("direct_invoke_status_class") == "success",
        "dependency_probe_no_missing": findings.get("dependency_missing_modules") == [],
        "http_runtime_invoke_unpatched": findings.get("http_runtime_invoke_unpatched_guard") is True,
        "ucp_client_legacy_alias_succeeds": findings.get("ucp_client_status_class") == "success",
        "ucp_client_legacy_alias_targets_runtime_action": findings.get("ucp_client_audit_action")
        == "graph.users.list",
        "ucp_client_routing_path_is_http_runtime": findings.get("ucp_client_routing_path")
        == "http_runtime",
        "ucp_client_directory_org_alias_targets_runtime_action": findings.get("ucp_org_audit_action")
        == "graph.org_profile",
        "ucp_client_directory_org_alias_fences_pkce_correctly": findings.get("ucp_org_status_class")
        == "auth_required",
    }

    decision = "GO" if all(clauses.values()) else "NO_GO"

    payload = {
        "plan_ref": "plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix:C5",
        "phase": "C5",
        "active_version": _active_version(),
        "install_dir": str(install_dir),
        "integrity": integrity,
        "runtime_run_error": runtime_run_error,
        "findings": findings,
        "clauses": clauses,
        "release_decision": decision,
        "live_ucp_through_installed_pack": "deferred_to_sibling_ucp_plan",
    }
    out = REPO / "artifacts" / "diagnostics" / "m365_standalone_graph_runtime_pack_acceptance.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    passed = sum(1 for v in clauses.values() if v)
    print(f"C5 real-socket acceptance: {decision}; clauses passed: {passed}/{len(clauses)}")
    print(f"Evidence: {out}")
    return 0 if decision == "GO" else 1


if __name__ == "__main__":
    sys.exit(main())
