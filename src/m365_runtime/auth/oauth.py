"""Delegated OAuth: Authorization Code + PKCE and device-code fallback.

Microsoft Graph endpoints used:
  - {tenant}/oauth2/v2.0/devicecode
  - {tenant}/oauth2/v2.0/token
  - {tenant}/oauth2/v2.0/authorize

Tokens are returned to the caller for storage in TokenStore. They are never
written to disk by this module and never logged.
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx


GRAPH_DEFAULT_TIMEOUT_SECONDS = 30.0
TOKEN_REFRESH_TIMEOUT_SECONDS = 15.0


class OAuthError(RuntimeError):
    def __init__(self, status: str, code: str, message: str) -> None:
        super().__init__(f"OAuthError {status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


@dataclass(frozen=True)
class PkceMaterial:
    code_verifier: str
    code_challenge: str
    state: str
    nonce: str


def make_pkce() -> PkceMaterial:
    verifier_bytes = os.urandom(32)
    code_verifier = base64.urlsafe_b64encode(verifier_bytes).rstrip(b"=").decode("ascii")
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)
    return PkceMaterial(code_verifier=code_verifier, code_challenge=code_challenge, state=state, nonce=nonce)


def authorize_url(tenant_id: str, client_id: str, redirect_uri: str, scopes: list[str], pkce: PkceMaterial) -> str:
    base = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "response_mode": "query",
        "scope": " ".join(scopes),
        "state": pkce.state,
        "nonce": pkce.nonce,
        "code_challenge": pkce.code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{base}?{urlencode(params)}"


def exchange_authorization_code(
    tenant_id: str,
    client_id: str,
    code: str,
    redirect_uri: str,
    code_verifier: str,
    scopes: list[str],
    *,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
        "scope": " ".join(scopes),
    }
    return _post_token(url, data, transport=transport)


def request_device_code(tenant_id: str, client_id: str, scopes: list[str], *, transport: httpx.BaseTransport | None = None) -> dict[str, Any]:
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode"
    data = {
        "client_id": client_id,
        "scope": " ".join(scopes),
    }
    with httpx.Client(transport=transport, timeout=GRAPH_DEFAULT_TIMEOUT_SECONDS) as client:
        response = client.post(url, data=data)
    if response.status_code != 200:
        raise OAuthError(str(response.status_code), "device_code_request_failed", _safe_error(response))
    body = response.json()
    return {
        "device_code": body["device_code"],
        "user_code": body["user_code"],
        "verification_uri": body["verification_uri"],
        "expires_in": body.get("expires_in", 900),
        "interval": body.get("interval", 5),
        "message": body.get("message"),
    }


def poll_device_code(
    tenant_id: str,
    client_id: str,
    device_code: str,
    *,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
    }
    return _post_token(url, data, transport=transport, allow_pending=True)


def refresh_access_token(
    tenant_id: str,
    client_id: str,
    refresh_token: str,
    scopes: list[str],
    *,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": " ".join(scopes),
    }
    with httpx.Client(transport=transport, timeout=TOKEN_REFRESH_TIMEOUT_SECONDS) as client:
        response = client.post(url, data=data)
    if response.status_code != 200:
        raise OAuthError(str(response.status_code), "refresh_failed", _safe_error(response))
    return _normalize_token_response(response.json())


def _post_token(url: str, data: dict[str, str], *, transport: httpx.BaseTransport | None, allow_pending: bool = False) -> dict[str, Any]:
    with httpx.Client(transport=transport, timeout=GRAPH_DEFAULT_TIMEOUT_SECONDS) as client:
        response = client.post(url, data=data)
    if response.status_code == 200:
        return _normalize_token_response(response.json())
    if allow_pending and response.status_code in (400, 401):
        body: dict[str, Any] = {}
        try:
            body = response.json()
        except Exception:
            pass
        err = str(body.get("error") or "")
        if err in {"authorization_pending", "slow_down", "expired_token", "access_denied"}:
            return {"pending": True, "error": err, "error_description": body.get("error_description")}
    raise OAuthError(str(response.status_code), "token_request_failed", _safe_error(response))


def _safe_error(response: httpx.Response) -> str:
    try:
        body = response.json()
    except Exception:
        return f"http_{response.status_code}"
    err = body.get("error") or "unknown"
    return f"{err}"


def _normalize_token_response(body: dict[str, Any]) -> dict[str, Any]:
    expires_in = int(body.get("expires_in") or 0)
    issued_at = int(time.time())
    return {
        "pending": False,
        "access_token": body.get("access_token"),
        "refresh_token": body.get("refresh_token"),
        "id_token": body.get("id_token"),
        "scope": body.get("scope"),
        "token_type": body.get("token_type", "Bearer"),
        "expires_in": expires_in,
        "issued_at": issued_at,
        "expires_at": issued_at + expires_in if expires_in else 0,
    }
