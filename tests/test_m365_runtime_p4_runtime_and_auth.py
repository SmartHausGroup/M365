"""P4 focused regressions for m365_runtime: setup, auth state, audit, OAuth, app-only, registry.

Plan: plan:m365-standalone-graph-runtime-integration-pack:R5
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import httpx
import pytest
from m365_runtime import ALLOWED_AUTH_MODES, FAILURE_LATTICE
from m365_runtime.audit import REDACT_PATTERN, build_envelope, redact
from m365_runtime.auth.app_only import CertificateMaterial, acquire_with_secret
from m365_runtime.auth.oauth import (
    OAuthError,
    authorize_url,
    exchange_authorization_code,
    make_pkce,
    poll_device_code,
    refresh_access_token,
    request_device_code,
)
from m365_runtime.graph.errors import normalize_response
from m365_runtime.graph.registry import READ_ONLY_REGISTRY, admit
from m365_runtime.launcher import installed_root_from_module, plan_launch
from m365_runtime.setup import SetupConfigError, load_setup
from m365_runtime.state import HealthVector, readiness


def test_constants_match_calculus() -> None:
    assert ALLOWED_AUTH_MODES == frozenset(
        {"auth_code_pkce", "device_code", "app_only_secret", "app_only_certificate"}
    )
    assert "success" in FAILURE_LATTICE
    assert "mutation_fence" in FAILURE_LATTICE
    assert "auth_required" in FAILURE_LATTICE


def test_load_setup_rejects_password_mode() -> None:
    with pytest.raises(SetupConfigError, match="auth_mode_password_rejected"):
        load_setup(
            {
                "M365_TENANT_ID": "t",
                "M365_CLIENT_ID": "c",
                "M365_AUTH_MODE": "password",
                "M365_SERVICE_ACTOR_UPN": "u@t.com",
            }
        )


def test_load_setup_admits_pkce_with_redirect() -> None:
    cfg = load_setup(
        {
            "M365_TENANT_ID": "t",
            "M365_CLIENT_ID": "c",
            "M365_AUTH_MODE": "auth_code_pkce",
            "M365_SERVICE_ACTOR_UPN": "u@t.com",
            "M365_REDIRECT_URI": "http://localhost:9301/callback",
            "M365_GRANTED_SCOPES": "User.Read,Sites.Read.All",
        }
    )
    assert cfg.auth_mode == "auth_code_pkce"
    assert cfg.redirect_uri == "http://localhost:9301/callback"
    assert "User.Read" in cfg.granted_scopes


def test_load_setup_app_only_certificate_requires_ref() -> None:
    with pytest.raises(SetupConfigError, match="credential_refs_missing_for:app_only_certificate"):
        load_setup(
            {
                "M365_TENANT_ID": "t",
                "M365_CLIENT_ID": "c",
                "M365_AUTH_MODE": "app_only_certificate",
                "M365_SERVICE_ACTOR_UPN": "u@t.com",
            }
        )


def test_load_setup_token_store_unsafe_rejected() -> None:
    with pytest.raises(SetupConfigError, match="token_store_unsafe:plaintext_file"):
        load_setup(
            {
                "M365_TENANT_ID": "t",
                "M365_CLIENT_ID": "c",
                "M365_AUTH_MODE": "device_code",
                "M365_SERVICE_ACTOR_UPN": "u@t.com",
                "M365_TOKEN_STORE": "plaintext_file",
            }
        )


def test_audit_envelope_redacts_secrets_and_caps_size() -> None:
    env = build_envelope(
        "u",
        "auth.start",
        "auth_required",
        before={"client_secret": "abc", "ok": "fine"},
        extra={"Authorization": "Bearer xx"},
    )
    assert env["before_redacted"]["client_secret"] == "[redacted]"
    assert env["before_redacted"]["ok"] == "fine"
    assert (
        env["extra_redacted"]["Authorization"] == "[redacted]"
        or env["extra_redacted"].get("Authorization") == "[redacted]"
    )
    assert REDACT_PATTERN.search("password=zzz")
    with pytest.raises(ValueError, match="audit_envelope_oversize"):
        build_envelope("u", "auth.start", "ok", extra={"description": "x" * 16000})


def test_redact_token_only_outside_keys() -> None:
    masked = redact({"name": "alice", "access_token": "zz"})
    assert masked["access_token"] == "[redacted]"


def test_make_pkce_uses_secure_randomness_and_distinct_per_call() -> None:
    a = make_pkce()
    b = make_pkce()
    assert a.code_verifier != b.code_verifier
    assert a.state != b.state
    assert a.nonce != b.nonce
    assert len(a.code_challenge) >= 32


def test_authorize_url_includes_pkce_and_state() -> None:
    pkce = make_pkce()
    url = authorize_url("tenant", "client", "http://localhost:9301/callback", ["User.Read"], pkce)
    assert "code_challenge=" in url
    assert "code_challenge_method=S256" in url
    assert "state=" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A9301%2Fcallback" in url


def _mock_transport(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def test_request_device_code_normalizes_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/devicecode")
        return httpx.Response(
            200,
            json={
                "device_code": "DC",
                "user_code": "UC",
                "verification_uri": "https://x",
                "expires_in": 900,
                "interval": 5,
                "message": "go",
            },
        )

    body = request_device_code(
        "tenant", "client", ["User.Read"], transport=_mock_transport(handler)
    )
    assert body["device_code"] == "DC"
    assert body["user_code"] == "UC"


def test_poll_device_code_pending_state() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "authorization_pending"})

    body = poll_device_code("tenant", "client", "DC", transport=_mock_transport(handler))
    assert body["pending"] is True
    assert body["error"] == "authorization_pending"


def test_exchange_authorization_code_normalizes_token_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"access_token": "AT", "refresh_token": "RT", "expires_in": 3600}
        )

    body = exchange_authorization_code(
        "tenant",
        "client",
        "code",
        "http://localhost",
        "verifier",
        ["User.Read"],
        transport=_mock_transport(handler),
    )
    assert body["access_token"] == "AT"
    assert body["refresh_token"] == "RT"
    assert body["expires_at"] >= body["issued_at"] + 3600


def test_refresh_access_token_failure_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "invalid_grant"})

    with pytest.raises(OAuthError):
        refresh_access_token(
            "tenant", "client", "RT", ["User.Read"], transport=_mock_transport(handler)
        )


def test_acquire_with_secret_normalizes_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access_token": "AT", "expires_in": 3600})

    body = acquire_with_secret(
        "tenant",
        "client",
        "secret",
        ["https://graph.microsoft.com/.default"],
        transport=_mock_transport(handler),
    )
    assert body["access_token"] == "AT"


def test_acquire_with_secret_rejects_empty_secret() -> None:
    with pytest.raises(OAuthError, match="client_secret_missing"):
        acquire_with_secret("tenant", "client", "", ["scope"])


def test_certificate_material_struct() -> None:
    cm = CertificateMaterial(pem_private_key="X", thumbprint_sha1_hex="00")
    assert cm.thumbprint_sha1_hex == "00"


def test_action_registry_is_read_only_and_consistent() -> None:
    assert len(READ_ONLY_REGISTRY) == 11
    for spec in READ_ONLY_REGISTRY.values():
        assert spec.rw == "read"
        assert spec.scopes
        for mode in spec.auth_modes:
            assert mode in ALLOWED_AUTH_MODES


def test_admit_returns_admit_when_scopes_and_mode_match() -> None:
    assert admit("graph.me", frozenset({"User.Read"}), "auth_code_pkce") == ("admit", "ok")


def test_admit_denies_unknown_action_and_scope_and_mode_mismatch() -> None:
    assert admit("does.not.exist", frozenset({"User.Read"}), "auth_code_pkce") == (
        "denied",
        "unknown_action",
    )
    assert admit("graph.me", frozenset(), "auth_code_pkce") == ("denied", "permission_missing")
    assert admit("graph.me", frozenset({"User.Read"}), "app_only_secret") == (
        "denied",
        "auth_mode_mismatch",
    )


def test_normalize_response_maps_status_classes() -> None:
    assert normalize_response(200, {"x": 1}).status_class == "success"
    assert (
        normalize_response(
            401, {"error": {"code": "InvalidAuthenticationToken", "message": "bad"}}
        ).status_class
        == "auth_required"
    )
    assert (
        normalize_response(
            403, {"error": {"code": "AccessDenied", "message": "insufficient privileges"}}
        ).status_class
        == "permission_missing"
    )
    assert (
        normalize_response(
            403, {"error": {"code": "ConsentRequired", "message": "consent needed"}}
        ).status_class
        == "consent_required"
    )
    assert (
        normalize_response(403, {"error": {"code": "Forbidden", "message": "no"}}).status_class
        == "policy_denied"
    )
    assert (
        normalize_response(
            429, {"error": {"code": "Throttled", "message": "slow"}}, headers={"Retry-After": "10"}
        ).status_class
        == "throttled"
    )
    assert (
        normalize_response(500, {"error": {"code": "Internal"}}).status_class == "graph_unreachable"
    )
    assert (
        normalize_response(400, {"error": {"code": "BadRequest"}}).status_class == "internal_error"
    )


def test_readiness_function_classifies_clauses() -> None:
    assert readiness(
        HealthVector(
            svc=True,
            auth=True,
            tok=True,
            graph=True,
            perm=True,
            ctr=True,
            art=True,
            src=True,
            aud=True,
        )
    ) == ("ready", "success")
    assert readiness(
        HealthVector(
            svc=True,
            auth=False,
            tok=True,
            graph=True,
            perm=True,
            ctr=True,
            art=True,
            src=True,
            aud=True,
        )
    ) == ("not_ready", "auth")
    assert readiness(
        HealthVector(
            svc=True,
            auth=None,
            tok=True,
            graph=True,
            perm=True,
            ctr=True,
            art=True,
            src=True,
            aud=True,
        )
    ) == ("not_ready", "unknown_clause")


def test_plan_launch_resolves_installed_root_without_repo_root_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in (
        "M365_REPO_ROOT",
        "SMARTHAUS_M365_REPO_ROOT",
        "UCP_ROOT",
        "REPOS_ROOT",
        "UCP_REPOS_ROOT",
    ):
        monkeypatch.delenv(key, raising=False)
    plan = plan_launch(
        env={
            "M365_TENANT_ID": "t",
            "M365_CLIENT_ID": "c",
            "M365_AUTH_MODE": "device_code",
            "M365_SERVICE_ACTOR_UPN": "u@t.com",
        }
    )
    assert plan.outcome in ("started", "config_invalid", "dependency_missing")
    assert plan.installed_root == installed_root_from_module()


def test_plan_launch_preserves_lattice_outcomes_for_invalid_setup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = plan_launch(
        env={
            "M365_TENANT_ID": "",
            "M365_CLIENT_ID": "",
            "M365_AUTH_MODE": "password",
            "M365_SERVICE_ACTOR_UPN": "",
        }
    )
    assert plan.outcome == "started"
    assert plan.setup is None
    assert "reason" in plan.detail.get("setup", {})


def test_runtime_module_does_not_reference_source_repo_paths(tmp_path: Path) -> None:
    runtime_root = Path(__file__).resolve().parent.parent / "src" / "m365_runtime"
    forbidden = (
        "M365_REPO_ROOT",
        "SMARTHAUS_M365_REPO_ROOT",
        "UCP_ROOT",
        "REPOS_ROOT",
        "UCP_REPOS_ROOT",
        "../M365",
        "from ops_adapter",
    )
    for path in runtime_root.rglob("*.py"):
        if path.name == "_forbidden_tokens.py":
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{path}: forbidden token {token!r} present"
