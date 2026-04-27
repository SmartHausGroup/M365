"""App-only Microsoft Graph auth: client_credentials with secret or certificate.

The runtime never reads or persists the secret/private-key bytes itself; it
asks the TokenStore (or the operating-system keychain via the supplied ref)
for the secret material at the moment of token acquisition.
"""

from __future__ import annotations

import base64
import time
import uuid
from dataclasses import dataclass
from typing import Any

import httpx

from .oauth import GRAPH_DEFAULT_TIMEOUT_SECONDS, OAuthError, _normalize_token_response, _safe_error


@dataclass(frozen=True)
class CertificateMaterial:
    pem_private_key: str
    thumbprint_sha1_hex: str


def acquire_with_secret(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    scopes: list[str],
    *,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    if not client_secret:
        raise OAuthError("400", "client_secret_missing", "client secret is empty")
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": " ".join(scopes) if scopes else "https://graph.microsoft.com/.default",
    }
    with httpx.Client(transport=transport, timeout=GRAPH_DEFAULT_TIMEOUT_SECONDS) as client:
        response = client.post(url, data=data)
    if response.status_code != 200:
        raise OAuthError(
            str(response.status_code), "client_credentials_failed", _safe_error(response)
        )
    return _normalize_token_response(response.json())


def acquire_with_certificate(
    tenant_id: str,
    client_id: str,
    cert: CertificateMaterial,
    scopes: list[str],
    *,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    if not cert.pem_private_key or not cert.thumbprint_sha1_hex:
        raise OAuthError("400", "certificate_material_missing", "certificate material missing")
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    assertion = _build_client_assertion(tenant_id, client_id, cert)
    data = {
        "client_id": client_id,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": assertion,
        "grant_type": "client_credentials",
        "scope": " ".join(scopes) if scopes else "https://graph.microsoft.com/.default",
    }
    with httpx.Client(transport=transport, timeout=GRAPH_DEFAULT_TIMEOUT_SECONDS) as client:
        response = client.post(url, data=data)
    if response.status_code != 200:
        raise OAuthError(
            str(response.status_code), "client_credentials_failed", _safe_error(response)
        )
    return _normalize_token_response(response.json())


def _build_client_assertion(tenant_id: str, client_id: str, cert: CertificateMaterial) -> str:
    try:
        import jwt  # PyJWT is only needed for app_only_certificate auth.
    except ImportError as exc:
        raise OAuthError(
            "500",
            "dependency_missing",
            "PyJWT is required for app_only_certificate auth: install PyJWT",
        ) from exc
    now = int(time.time())
    headers = {
        "alg": "RS256",
        "typ": "JWT",
        "x5t": _b64url(bytes.fromhex(cert.thumbprint_sha1_hex)),
    }
    claims = {
        "aud": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        "iss": client_id,
        "sub": client_id,
        "jti": str(uuid.uuid4()),
        "nbf": now,
        "iat": now,
        "exp": now + 600,
    }
    return jwt.encode(claims, cert.pem_private_key, algorithm="RS256", headers=headers)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")
