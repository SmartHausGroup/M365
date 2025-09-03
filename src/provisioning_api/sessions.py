from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

_sessions: dict[str, dict[str, Any]] = {}


def _timeout_seconds() -> int:
    try:
        return int(os.getenv("SESSION_TIMEOUT", "86400"))
    except Exception:
        return 86400


def create_session_token(user_info: dict) -> str:
    token = secrets.token_urlsafe(32)
    _sessions[token] = {
        "user_info": user_info,
        "created_at": datetime.now(tz=UTC),
        "expires_at": datetime.now(tz=UTC) + timedelta(seconds=_timeout_seconds()),
    }
    return token


def verify_session_token(token: str) -> dict[str, Any]:
    if token not in _sessions:
        raise ValueError("Invalid session token")
    session = _sessions[token]
    if datetime.now(tz=UTC) > session["expires_at"]:
        del _sessions[token]
        raise ValueError("Session expired")
    return session
