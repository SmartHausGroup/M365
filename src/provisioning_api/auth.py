from __future__ import annotations

import base64
import os
import urllib.parse
from typing import Any

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from msal import ConfidentialClientApplication

from provisioning_api.sessions import create_session_token, verify_session_token

MICROSOFT_CLIENT_ID = (
    os.getenv("MICROSOFT_CLIENT_ID")
    or os.getenv("AZURE_APP_CLIENT_ID_TAI")
    or os.getenv("GRAPH_CLIENT_ID")
    or os.getenv("AZURE_CLIENT_ID")
)
MICROSOFT_CLIENT_SECRET = (
    os.getenv("MICROSOFT_CLIENT_SECRET")
    or os.getenv("AZURE_APP_CLIENT_SECRET_TAI")
    or os.getenv("GRAPH_CLIENT_SECRET")
    or os.getenv("AZURE_CLIENT_SECRET")
)
MICROSOFT_TENANT_ID = (
    os.getenv("MICROSOFT_TENANT_ID") or os.getenv("GRAPH_TENANT_ID") or os.getenv("AZURE_TENANT_ID")
)
MICROSOFT_REDIRECT_URI = os.getenv(
    "MICROSOFT_REDIRECT_URI",
    os.getenv("API_BASE_URL", "http://localhost:9000") + "/api/auth/callback",
)

SCOPES = [
    "User.Read",
    "Group.Read.All",
    "Sites.ReadWrite.All",
]


def auth_enabled() -> bool:
    disabled = os.getenv("AUTH_DISABLED", "true").lower() in ("1", "true", "yes")
    return not disabled


def _cca() -> ConfidentialClientApplication:
    if not (MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET and MICROSOFT_TENANT_ID):
        raise HTTPException(status_code=500, detail="Microsoft OAuth not configured")
    authority = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}"
    return ConfidentialClientApplication(
        client_id=MICROSOFT_CLIENT_ID,
        client_credential=MICROSOFT_CLIENT_SECRET,
        authority=authority,
    )


def _encode_state(redirect_url: str | None) -> str:
    raw = (redirect_url or "").encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def _decode_state(state: str | None) -> str | None:
    if not state:
        return None
    try:
        return base64.urlsafe_b64decode(state.encode("ascii")).decode("utf-8")
    except Exception:
        return None


def generate_microsoft_auth_url(redirect_after: str | None = None) -> str:
    auth_base = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
    params = {
        "client_id": MICROSOFT_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": MICROSOFT_REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "response_mode": "query",
        "state": _encode_state(redirect_after),
    }
    return f"{auth_base}?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(code: str) -> dict[str, Any]:
    app = _cca()
    result = app.acquire_token_by_authorization_code(
        code=code,
        scopes=SCOPES,
        redirect_uri=MICROSOFT_REDIRECT_URI,
    )
    if "access_token" not in result:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to acquire access token: {result.get('error_description')}",
        )
    return result


def get_user_info(access_token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    with httpx.Client(timeout=10) as client:
        r = client.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user information")
        return r.json()


def microsoft_login(r: str | None = None) -> RedirectResponse:
    url = generate_microsoft_auth_url(r)
    return RedirectResponse(url=url)


def microsoft_callback(code: str, state: str | None = None) -> object:
    tokens = exchange_code_for_token(code)
    user = get_user_info(tokens["access_token"])
    session_token = create_session_token(user)
    # If state contains redirect, send user back with token in fragment
    redirect_after = _decode_state(state)
    if redirect_after:
        sep = "#" if "#" not in redirect_after else "&"
        return RedirectResponse(url=f"{redirect_after}{sep}token={session_token}")
    return {"access_token": session_token, "user": user}


def verify_microsoft_token(request: Request) -> dict[str, Any]:
    if not auth_enabled():
        # Disabled auth for dev/test: return stub user
        return {"user_info": {"displayName": "Dev User", "userPrincipalName": "dev@local"}}

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = auth_header.split(" ", 1)[1]
    try:
        session = verify_session_token(token)
        # RBAC check (optional)
        if os.getenv("ENABLE_ROLE_BASED_ACCESS", "false").lower() in ("1", "true", "yes"):
            user = session.get("user_info", {})
            upn = (user.get("userPrincipalName") or user.get("mail") or "").lower()
            allowed_upns = [
                x.strip().lower() for x in os.getenv("ALLOWED_UPNS", "").split(",") if x.strip()
            ]
            allowed_domains = [
                x.strip().lower() for x in os.getenv("ALLOWED_DOMAINS", "").split(",") if x.strip()
            ]
            if allowed_upns and upn not in allowed_upns:
                raise HTTPException(status_code=403, detail="Access denied")
            if (
                allowed_domains
                and (not any(upn.endswith("@" + d) for d in allowed_domains))
                and allowed_domains
            ):
                raise HTTPException(status_code=403, detail="Access denied")
        return session
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from None
