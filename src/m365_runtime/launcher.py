"""Standalone runtime service launcher.

The launcher resolves its installed root from the file location of this
module. The forbidden source-repo and sibling-repo env names live once in
``_forbidden_tokens.py``; the runtime never reads them. The launcher
exposes the auth/health/action/lifecycle contracts on a local FastAPI
socket. Phases covered:

- Launch + readiness + setup-status + auth-status + action list (P4).
- Read-only Graph action surface (P5).
- UCP contract layer (P6).
- Full auth lifecycle (start/check) and token-store-backed readiness (fix R3).
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import RUNTIME_VERSION
from .audit import build_envelope
from .auth.token_store import TokenStore, TokenStoreError
from .graph.registry import READ_ONLY_REGISTRY
from .setup import SetupConfig, SetupConfigError, load_setup_from_env

# Submodules that transitively import third-party deps (httpx, fastapi,
# uvicorn) are NOT imported at module load. They are imported lazily inside
# the functions that use them - either inside `build_app`, which is only
# reached after `plan_launch` confirms the dependency probe is clean, or
# inside the run() helper which is only invoked by the CLI entry point.
# This guarantees `import m365_runtime.launcher` succeeds even when httpx
# / fastapi / uvicorn are absent, so `plan_launch()` can return a
# structured `outcome=dependency_missing` instead of crashing at import.


LAUNCH_OUTCOMES = (
    "started",
    "port_conflict",
    "config_invalid",
    "dependency_missing",
    "launch_unknown",
)
TOKEN_ACCOUNT_ACCESS = "access_token"
TOKEN_ACCOUNT_REFRESH = "refresh_token"

RUNTIME_REQUIRED_MODULES = ("httpx", "fastapi", "uvicorn")
RUNTIME_CONDITIONAL_MODULES = {
    "app_only_certificate": ("jwt",),
}


def _probe_required_dependencies(*, auth_mode: str | None = None) -> tuple[list[str], list[str]]:
    """Return (present, missing) for the modules this runtime needs at launch.

    Always probes the unconditionally-required runtime modules. If
    ``auth_mode`` is provided, also probes the auth-mode conditional set.
    """
    import importlib

    present: list[str] = []
    missing: list[str] = []
    targets: list[str] = list(RUNTIME_REQUIRED_MODULES)
    if auth_mode and auth_mode in RUNTIME_CONDITIONAL_MODULES:
        targets.extend(RUNTIME_CONDITIONAL_MODULES[auth_mode])
    for name in targets:
        try:
            importlib.import_module(name)
            present.append(name)
        except ImportError:
            missing.append(name)
    return present, missing


class LaunchError(RuntimeError):
    def __init__(self, outcome: str, message: str) -> None:
        super().__init__(f"LaunchError {outcome}: {message}")
        self.outcome = outcome
        self.message = message


@dataclass
class LaunchPlan:
    outcome: str
    installed_root: Path
    setup: SetupConfig | None
    listen_host: str
    listen_port: int
    detail: dict[str, Any]


def installed_root_from_module() -> Path:
    return Path(__file__).resolve().parent.parent


def plan_launch(
    *, host: str | None = None, port: int | None = None, env: dict[str, str] | None = None
) -> LaunchPlan:
    started_at = time.monotonic()
    try:
        installed_root = installed_root_from_module()
    except Exception as exc:
        return LaunchPlan(
            outcome="dependency_missing",
            installed_root=Path("."),
            setup=None,
            listen_host=host or "127.0.0.1",
            listen_port=port or 9300,
            detail={"reason": "installed_root_unresolved", "exception": str(exc)},
        )
    if not installed_root.is_dir():
        return LaunchPlan(
            outcome="dependency_missing",
            installed_root=installed_root,
            setup=None,
            listen_host=host or "127.0.0.1",
            listen_port=port or 9300,
            detail={"reason": "installed_root_not_dir"},
        )
    present, missing = _probe_required_dependencies()
    if missing:
        return LaunchPlan(
            outcome="dependency_missing",
            installed_root=installed_root,
            setup=None,
            listen_host=host or "127.0.0.1",
            listen_port=port or 9300,
            detail={
                "reason": "required_modules_missing",
                "missing_modules": missing,
                "present_modules": present,
                "remediation": "install the missing modules in the pack runtime environment",
            },
        )
    listen_host = host if host is not None else (os.getenv("M365_RUNTIME_HOST") or "127.0.0.1")
    try:
        port_value: int | str = (
            port if port is not None else (os.getenv("M365_RUNTIME_PORT") or "9300")
        )
        listen_port = int(port_value)
    except ValueError:
        return LaunchPlan(
            outcome="config_invalid",
            installed_root=installed_root,
            setup=None,
            listen_host=listen_host,
            listen_port=0,
            detail={"reason": "invalid_port"},
        )
    setup_obj: SetupConfig | None = None
    setup_detail: dict[str, Any] = {"loaded": False}
    if env is not None:
        try:
            setup_obj = load_setup_from_env_dict(env)
            setup_detail = {"loaded": True, "auth_mode": setup_obj.auth_mode}
        except SetupConfigError as exc:
            setup_detail = {"loaded": False, "reason": str(exc)}
    else:
        try:
            setup_obj = load_setup_from_env()
            setup_detail = {"loaded": True, "auth_mode": setup_obj.auth_mode}
        except SetupConfigError as exc:
            setup_detail = {"loaded": False, "reason": str(exc)}
    elapsed = time.monotonic() - started_at
    if elapsed > 5.0:
        return LaunchPlan(
            outcome="launch_unknown",
            installed_root=installed_root,
            setup=setup_obj,
            listen_host=listen_host,
            listen_port=listen_port,
            detail={"reason": "exceeded_5s_budget", "elapsed_s": round(elapsed, 3)},
        )
    return LaunchPlan(
        outcome="started",
        installed_root=installed_root,
        setup=setup_obj,
        listen_host=listen_host,
        listen_port=listen_port,
        detail={"setup": setup_detail, "elapsed_s": round(elapsed, 3)},
    )


def load_setup_from_env_dict(env: dict[str, str]) -> SetupConfig:
    saved = dict(os.environ)
    try:
        os.environ.clear()
        os.environ.update(env)
        return load_setup_from_env()
    finally:
        os.environ.clear()
        os.environ.update(saved)


def _make_token_store(plan: LaunchPlan) -> TokenStore | None:
    if plan.setup is None:
        return None
    try:
        return TokenStore.from_setup(plan.setup, plan.installed_root)
    except TokenStoreError:
        return None


def _store_access_token(
    store: TokenStore | None, access_token: str | None, refresh_token: str | None = None
) -> bool:
    if store is None or not access_token:
        return False
    try:
        store.put(TOKEN_ACCOUNT_ACCESS, access_token)
        if refresh_token:
            store.put(TOKEN_ACCOUNT_REFRESH, refresh_token)
        return True
    except Exception:
        return False


def _clear_stored_tokens(store: TokenStore | None) -> None:
    if store is None:
        return
    for account in (TOKEN_ACCOUNT_ACCESS, TOKEN_ACCOUNT_REFRESH):
        try:
            store.clear(account)
        except Exception:
            continue


def _looked_up_secret_or_cert_ref(
    setup: SetupConfig, store: TokenStore | None, ref_kind: str
) -> str | None:
    """Resolve a configured secret/cert reference into raw material at request time.

    Production deployments place the secret value (or PEM private key) in the
    keychain item named by the ref. The runtime never holds these values
    statically and never logs them.
    """
    if store is None:
        return None
    if ref_kind == "secret":
        ref = (setup.app_only_secret_ref or "").strip()
    elif ref_kind == "certificate":
        ref = (setup.app_only_certificate_ref or "").strip()
    else:
        return None
    if not ref:
        return None
    try:
        return store.get(ref)
    except Exception:
        return None


def build_app(
    plan: LaunchPlan, *, oauth_transport: Any | None = None, graph_transport: Any | None = None
) -> Any:
    """Build the FastAPI app for this launch plan.

    `oauth_transport` and `graph_transport` are httpx mock seams used by the
    acceptance tests. They default to None (production path).

    All dependency-sensitive imports (fastapi, oauth_mod, app_only,
    graph.actions, health) happen here, AFTER `plan_launch()` has confirmed
    the dependency probe is clean. Importing the launcher module itself
    must remain safe when these third-party packages are absent.
    """
    from fastapi import FastAPI

    from .auth import oauth as oauth_mod
    from .auth.app_only import CertificateMaterial, acquire_with_certificate, acquire_with_secret
    from .graph.actions import invoke as invoke_action
    from .graph.actions import list_actions
    from .health import compose_readiness

    app = FastAPI(title=f"SMARTHAUS M365 Runtime {RUNTIME_VERSION}")

    token_store = _make_token_store(plan)
    state: dict[str, Any] = {
        "access_token": None,
        "refresh_token": None,
        "token_expires_at": None,
        "auth_mode": plan.setup.auth_mode if plan.setup else None,
        "device_code_session": None,
        "pkce_session": None,
        "auth_failure": None,
    }

    def current_setup() -> SetupConfig | None:
        return plan.setup

    def emit_audit(
        actor: str, action: str, status: str, *, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return build_envelope(
            actor=actor,
            action=action,
            status_class=status,
            extra=extra or {},
            correlation_id=str(uuid.uuid4()),
        )

    @app.get("/v1/runtime/version")
    def version() -> dict[str, Any]:
        return {
            "runtime_version": RUNTIME_VERSION,
            "installed_root": str(plan.installed_root),
            "outcome": plan.outcome,
            "auth_mode": state["auth_mode"],
            "token_store_backend": token_store.backend if token_store else None,
        }

    @app.get("/v1/health/dependencies")
    def dependencies_endpoint() -> dict[str, Any]:
        auth_mode = plan.setup.auth_mode if plan.setup else None
        present, missing = _probe_required_dependencies(auth_mode=auth_mode)
        envelope = emit_audit(
            "system",
            "health.dependencies",
            "success" if not missing else "dependency_missing",
            extra={"present": present, "missing": missing, "auth_mode": auth_mode},
        )
        return {
            "required_modules": list(RUNTIME_REQUIRED_MODULES),
            "conditional_modules": {k: list(v) for k, v in RUNTIME_CONDITIONAL_MODULES.items()},
            "auth_mode": auth_mode,
            "present_modules": present,
            "missing_modules": missing,
            "audit": envelope,
        }

    @app.get("/v1/health/readiness")
    def readiness_endpoint() -> dict[str, Any]:
        result = compose_readiness(
            plan.installed_root,
            plan.setup,
            token_store,
            state.get("access_token"),
            transport=graph_transport,
        )
        envelope = emit_audit(
            "system", "health.readiness", result.detail["state"], extra=result.detail
        )
        return {"vector": result.vector.as_dict(), "state": result.detail, "audit": envelope}

    @app.get("/v1/auth/status")
    def auth_status() -> dict[str, Any]:
        if state.get("access_token"):
            return {"state": "signed_in", "auth_mode": state["auth_mode"]}
        if plan.setup is None:
            return {"state": "unconfigured"}
        if state.get("device_code_session"):
            return {"state": "consent_required", "auth_mode": state["auth_mode"]}
        if state.get("auth_failure"):
            return {
                "state": "auth_required",
                "auth_mode": state["auth_mode"],
                "reason": state["auth_failure"],
            }
        return {"state": "auth_required", "auth_mode": state["auth_mode"]}

    @app.post("/v1/auth/clear")
    def auth_clear() -> dict[str, Any]:
        state["access_token"] = None
        state["refresh_token"] = None
        state["token_expires_at"] = None
        state["device_code_session"] = None
        state["pkce_session"] = None
        state["auth_failure"] = None
        _clear_stored_tokens(token_store)
        return {"state": "auth_required"}

    @app.post("/v1/auth/start")
    def auth_start(body: dict[str, Any] | None = None) -> dict[str, Any]:
        body = body or {}
        setup = current_setup()
        if setup is None:
            return {
                "state": "unconfigured",
                "audit": emit_audit("system", "auth.start", "not_configured"),
            }
        scopes = list(setup.granted_scopes) or ["https://graph.microsoft.com/.default"]
        actor = str(body.get("actor") or setup.actor_upn)
        if setup.auth_mode == "auth_code_pkce":
            if not setup.redirect_uri:
                return {
                    "state": "config_invalid",
                    "reason": "redirect_uri_missing",
                    "audit": emit_audit(actor, "auth.start", "not_configured"),
                }
            pkce = oauth_mod.make_pkce()
            url = oauth_mod.authorize_url(
                setup.tenant_id, setup.client_id, setup.redirect_uri, scopes, pkce
            )
            state["pkce_session"] = {
                "verifier": pkce.code_verifier,
                "state": pkce.state,
                "scopes": scopes,
            }
            state["device_code_session"] = None
            state["auth_failure"] = None
            return {
                "state": "auth_started",
                "auth_mode": "auth_code_pkce",
                "authorize_url": url,
                "expected_state": pkce.state,
                "audit": emit_audit(
                    actor, "auth.start", "auth_started", extra={"flow": "auth_code_pkce"}
                ),
            }
        if setup.auth_mode == "device_code":
            try:
                resp = oauth_mod.request_device_code(
                    setup.tenant_id, setup.client_id, scopes, transport=oauth_transport
                )
            except oauth_mod.OAuthError as exc:
                state["auth_failure"] = exc.code
                return {
                    "state": "auth_required",
                    "reason": exc.code,
                    "audit": emit_audit(
                        actor, "auth.start", "auth_required", extra={"reason": exc.code}
                    ),
                }
            state["device_code_session"] = {
                "device_code": resp["device_code"],
                "user_code": resp["user_code"],
                "verification_uri": resp["verification_uri"],
                "interval": resp.get("interval", 5),
                "expires_in": resp.get("expires_in", 900),
                "scopes": scopes,
            }
            state["pkce_session"] = None
            state["auth_failure"] = None
            return {
                "state": "device_code_pending",
                "auth_mode": "device_code",
                "user_code": resp["user_code"],
                "verification_uri": resp["verification_uri"],
                "interval": resp.get("interval", 5),
                "audit": emit_audit(
                    actor, "auth.start", "consent_required", extra={"flow": "device_code"}
                ),
            }
        if setup.auth_mode == "app_only_secret":
            secret = _looked_up_secret_or_cert_ref(setup, token_store, "secret")
            if not secret:
                return {
                    "state": "config_invalid",
                    "reason": "client_secret_unresolved",
                    "audit": emit_audit(actor, "auth.start", "not_configured"),
                }
            try:
                token = acquire_with_secret(
                    setup.tenant_id, setup.client_id, secret, scopes, transport=oauth_transport
                )
            except oauth_mod.OAuthError as exc:
                state["auth_failure"] = exc.code
                return {
                    "state": "auth_required",
                    "reason": exc.code,
                    "audit": emit_audit(
                        actor, "auth.start", "auth_required", extra={"reason": exc.code}
                    ),
                }
            _ingest_token_response(state, token_store, token)
            return {
                "state": "signed_in",
                "auth_mode": "app_only_secret",
                "audit": emit_audit(
                    actor, "auth.start", "success", extra={"flow": "app_only_secret"}
                ),
            }
        if setup.auth_mode == "app_only_certificate":
            pem = _looked_up_secret_or_cert_ref(setup, token_store, "certificate")
            thumbprint = ""
            if token_store is not None and setup.app_only_certificate_ref:
                try:
                    thumbprint = (
                        token_store.get(f"{setup.app_only_certificate_ref}::thumbprint") or ""
                    ).strip()
                except Exception:
                    thumbprint = ""
            if not pem or not thumbprint:
                return {
                    "state": "config_invalid",
                    "reason": "certificate_material_unresolved",
                    "audit": emit_audit(actor, "auth.start", "not_configured"),
                }
            cert = CertificateMaterial(pem_private_key=pem, thumbprint_sha1_hex=thumbprint)
            try:
                token = acquire_with_certificate(
                    setup.tenant_id, setup.client_id, cert, scopes, transport=oauth_transport
                )
            except oauth_mod.OAuthError as exc:
                state["auth_failure"] = exc.code
                return {
                    "state": "auth_required",
                    "reason": exc.code,
                    "audit": emit_audit(
                        actor, "auth.start", "auth_required", extra={"reason": exc.code}
                    ),
                }
            _ingest_token_response(state, token_store, token)
            return {
                "state": "signed_in",
                "auth_mode": "app_only_certificate",
                "audit": emit_audit(
                    actor, "auth.start", "success", extra={"flow": "app_only_certificate"}
                ),
            }
        return {"state": "auth_required", "reason": "auth_mode_unsupported"}

    @app.post("/v1/auth/check")
    def auth_check(body: dict[str, Any] | None = None) -> dict[str, Any]:
        body = body or {}
        setup = current_setup()
        if setup is None:
            return {
                "state": "unconfigured",
                "audit": emit_audit("system", "auth.check", "not_configured"),
            }
        actor = str(body.get("actor") or setup.actor_upn)
        if setup.auth_mode == "auth_code_pkce":
            session = state.get("pkce_session")
            if session is None:
                return {
                    "state": "auth_required",
                    "reason": "no_pkce_session",
                    "audit": emit_audit(actor, "auth.check", "auth_required"),
                }
            received_state = str(body.get("state") or "")
            code = str(body.get("code") or "")
            if not code or received_state != session["state"]:
                state["auth_failure"] = "pkce_state_mismatch"
                return {
                    "state": "auth_required",
                    "reason": "pkce_state_mismatch",
                    "audit": emit_audit(actor, "auth.check", "auth_required"),
                }
            try:
                token = oauth_mod.exchange_authorization_code(
                    setup.tenant_id,
                    setup.client_id,
                    code,
                    setup.redirect_uri or "",
                    session["verifier"],
                    session["scopes"],
                    transport=oauth_transport,
                )
            except oauth_mod.OAuthError as exc:
                state["auth_failure"] = exc.code
                return {
                    "state": "auth_required",
                    "reason": exc.code,
                    "audit": emit_audit(
                        actor, "auth.check", "auth_required", extra={"reason": exc.code}
                    ),
                }
            _ingest_token_response(state, token_store, token)
            state["pkce_session"] = None
            return {
                "state": "signed_in",
                "auth_mode": "auth_code_pkce",
                "audit": emit_audit(actor, "auth.check", "success"),
            }
        if setup.auth_mode == "device_code":
            session = state.get("device_code_session")
            if session is None:
                return {
                    "state": "auth_required",
                    "reason": "no_device_code_session",
                    "audit": emit_audit(actor, "auth.check", "auth_required"),
                }
            try:
                token = oauth_mod.poll_device_code(
                    setup.tenant_id,
                    setup.client_id,
                    session["device_code"],
                    transport=oauth_transport,
                )
            except oauth_mod.OAuthError as exc:
                state["auth_failure"] = exc.code
                return {
                    "state": "auth_required",
                    "reason": exc.code,
                    "audit": emit_audit(
                        actor, "auth.check", "auth_required", extra={"reason": exc.code}
                    ),
                }
            if token.get("pending"):
                return {
                    "state": "device_code_pending",
                    "auth_mode": "device_code",
                    "audit": emit_audit(actor, "auth.check", "consent_required"),
                }
            _ingest_token_response(state, token_store, token)
            state["device_code_session"] = None
            return {
                "state": "signed_in",
                "auth_mode": "device_code",
                "audit": emit_audit(actor, "auth.check", "success"),
            }
        # App-only modes complete on auth.start, so check just reports current state.
        return {
            "state": "signed_in" if state.get("access_token") else "auth_required",
            "auth_mode": setup.auth_mode,
        }

    @app.get("/v1/actions")
    def actions() -> dict[str, Any]:
        return {"count": len(READ_ONLY_REGISTRY), "actions": list_actions()}

    @app.post("/v1/actions/{action_id}/invoke")
    def invoke_endpoint(action_id: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        body = body or {}
        actor = str(body.get("actor") or (plan.setup.actor_upn if plan.setup else "unknown"))
        params = dict(body.get("params") or {})
        if action_id not in READ_ONLY_REGISTRY:
            return {
                "status_class": "mutation_fence",
                "reason": "action_not_in_read_only_registry",
                "audit": build_envelope(
                    actor=actor,
                    action=action_id,
                    status_class="mutation_fence",
                    extra={"params": params},
                ),
            }
        if plan.setup is None:
            return {
                "status_class": "not_configured",
                "audit": build_envelope(
                    actor=actor,
                    action=action_id,
                    status_class="not_configured",
                    extra={"params": params},
                ),
            }
        result = invoke_action(
            action_id=action_id,
            actor=actor,
            granted_scopes=plan.setup.granted_scopes,
            current_auth_mode=plan.setup.auth_mode,
            access_token=state.get("access_token"),
            params=params,
            transport=graph_transport,
        )
        return {
            "status_class": result.status_class,
            "payload": result.payload,
            "audit": result.audit,
            "correlation_id": result.correlation_id,
        }

    return app


def _ingest_token_response(
    state: dict[str, Any], token_store: TokenStore | None, token: dict[str, Any]
) -> None:
    state["access_token"] = token.get("access_token")
    state["refresh_token"] = token.get("refresh_token")
    state["token_expires_at"] = token.get("expires_at") or 0
    state["auth_failure"] = None
    _store_access_token(token_store, state["access_token"], state.get("refresh_token"))


def run(host: str = "127.0.0.1", port: int = 9300) -> int:
    plan = plan_launch(host=host, port=port)
    if plan.outcome != "started":
        sys.stderr.write(f"M365 runtime launch failed: {plan.outcome} {plan.detail}\n")
        return 1
    try:
        import uvicorn
    except ImportError:
        sys.stderr.write("uvicorn missing; cannot run server\n")
        return 1
    app = build_app(plan)
    uvicorn.run(
        app,
        host=plan.listen_host,
        port=plan.listen_port,
        log_level=os.getenv("M365_RUNTIME_LOG_LEVEL", "info").lower(),
    )
    return 0
