"""Installed-artifact setup config validation (L_AUTH + AuthConfigured)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import ALLOWED_AUTH_MODES


class SetupConfigError(ValueError):
    pass


@dataclass(frozen=True)
class SetupConfig:
    tenant_id: str
    client_id: str
    auth_mode: str
    actor_upn: str
    redirect_uri: str | None = None
    device_code_fallback: bool = False
    app_only_secret_ref: str | None = None
    app_only_certificate_ref: str | None = None
    token_store: str = "keychain"
    keychain_service: str = "ai.smarthaus.m365"
    granted_scopes: frozenset[str] = field(default_factory=frozenset)
    encrypted_pack_local_allowed: bool = False

    def required_credential_refs_present(self) -> bool:
        if self.auth_mode == "auth_code_pkce":
            return bool(self.client_id and self.redirect_uri)
        if self.auth_mode == "device_code":
            return bool(self.client_id)
        if self.auth_mode == "app_only_secret":
            return bool(self.client_id and self.app_only_secret_ref)
        if self.auth_mode == "app_only_certificate":
            return bool(self.client_id and self.app_only_certificate_ref)
        return False

    def token_store_safe(self) -> bool:
        if self.token_store == "keychain":
            return True
        if self.token_store == "encrypted_pack_local" and self.encrypted_pack_local_allowed:
            return True
        return False


def load_setup(values: dict[str, Any]) -> SetupConfig:
    auth_mode = str(values.get("M365_AUTH_MODE") or "").strip().lower()
    if auth_mode in {"", "password", "username_password", "basic"}:
        if auth_mode in {"password", "username_password", "basic"}:
            raise SetupConfigError("auth_mode_password_rejected")
        raise SetupConfigError("auth_mode_missing")
    if auth_mode not in ALLOWED_AUTH_MODES:
        raise SetupConfigError(f"auth_mode_unsupported:{auth_mode}")
    tenant_id = str(values.get("M365_TENANT_ID") or "").strip()
    client_id = str(values.get("M365_CLIENT_ID") or "").strip()
    actor_upn = str(values.get("M365_SERVICE_ACTOR_UPN") or "").strip()
    if not tenant_id:
        raise SetupConfigError("tenant_id_missing")
    if not client_id:
        raise SetupConfigError("client_id_missing")
    if not actor_upn:
        raise SetupConfigError("actor_upn_missing")
    redirect_uri = str(values.get("M365_REDIRECT_URI") or "").strip() or None
    device_code_fallback = str(values.get("M365_DEVICE_CODE_FALLBACK") or "").strip().lower() in {"1","true","yes","on"}
    app_only_secret_ref = str(values.get("M365_APP_ONLY_CLIENT_SECRET_REF") or "").strip() or None
    app_only_certificate_ref = str(values.get("M365_APP_ONLY_CERTIFICATE_REF") or "").strip() or None
    token_store = str(values.get("M365_TOKEN_STORE") or "keychain").strip().lower()
    keychain_service = str(values.get("M365_KEYCHAIN_SERVICE") or "ai.smarthaus.m365").strip()
    encrypted_pack_local_allowed = str(values.get("M365_ENCRYPTED_PACK_LOCAL_ALLOWED") or "").strip().lower() in {"1","true","yes","on"}
    granted_raw = str(values.get("M365_GRANTED_SCOPES") or "").strip()
    granted = frozenset({s.strip() for s in granted_raw.split(",") if s.strip()}) if granted_raw else frozenset()
    cfg = SetupConfig(
        tenant_id=tenant_id,
        client_id=client_id,
        auth_mode=auth_mode,
        actor_upn=actor_upn,
        redirect_uri=redirect_uri,
        device_code_fallback=device_code_fallback,
        app_only_secret_ref=app_only_secret_ref,
        app_only_certificate_ref=app_only_certificate_ref,
        token_store=token_store,
        keychain_service=keychain_service,
        granted_scopes=granted,
        encrypted_pack_local_allowed=encrypted_pack_local_allowed,
    )
    if not cfg.required_credential_refs_present():
        raise SetupConfigError(f"credential_refs_missing_for:{auth_mode}")
    if not cfg.token_store_safe():
        raise SetupConfigError(f"token_store_unsafe:{token_store}")
    return cfg


def load_setup_from_env(prefix: str = "") -> SetupConfig:
    env = {k: v for k, v in os.environ.items() if (not prefix or k.startswith(prefix))}
    return load_setup(env)


def setup_schema_path(installed_root: Path) -> Path:
    return installed_root / "setup_schema.json"


def write_default_schema(installed_root: Path) -> Path:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "SMARTHAUS M365 Standalone Graph Runtime Pack Setup",
        "type": "object",
        "properties": {
            "M365_TENANT_ID": {"type": "string", "minLength": 1, "description": "Microsoft Entra tenant ID."},
            "M365_CLIENT_ID": {"type": "string", "minLength": 1, "description": "Microsoft Entra application (client) ID."},
            "M365_AUTH_MODE": {"type": "string", "enum": sorted(ALLOWED_AUTH_MODES), "description": "Auth flow. Username/password is forbidden."},
            "M365_SERVICE_ACTOR_UPN": {"type": "string", "minLength": 1, "description": "Operator or service principal UPN bound to delegated requests."},
            "M365_REDIRECT_URI": {"type": "string", "description": "Local loopback redirect URI (auth_code_pkce only)."},
            "M365_DEVICE_CODE_FALLBACK": {"type": "string", "description": "true/false to allow device-code fallback."},
            "M365_APP_ONLY_CLIENT_SECRET_REF": {"type": "string", "description": "Reference (e.g. keychain item name) for the app-only client secret. Never the secret itself."},
            "M365_APP_ONLY_CERTIFICATE_REF": {"type": "string", "description": "Reference for the app-only certificate. Never the private key bytes."},
            "M365_TOKEN_STORE": {"type": "string", "enum": ["keychain","encrypted_pack_local"], "default": "keychain"},
            "M365_KEYCHAIN_SERVICE": {"type": "string", "default": "ai.smarthaus.m365"},
            "M365_ENCRYPTED_PACK_LOCAL_ALLOWED": {"type": "string", "description": "true/false; only true if approved policy allows pack-local encrypted storage."},
            "M365_GRANTED_SCOPES": {"type": "string", "description": "Comma-separated list of granted Microsoft Graph permission names."},
        },
        "required": ["M365_TENANT_ID","M365_CLIENT_ID","M365_AUTH_MODE","M365_SERVICE_ACTOR_UPN"],
        "additionalProperties": True,
    }
    path = setup_schema_path(installed_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(schema, indent=2, sort_keys=True))
    return path
