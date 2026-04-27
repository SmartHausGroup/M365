"""Normalized Microsoft Graph error classes.

Maps an HTTP status + body to one node of the failure lattice
(success, auth_required, consent_required, permission_missing, throttled,
graph_unreachable, policy_denied, internal_error).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedGraphError:
    status_class: str
    http_status: int
    code: str | None
    message: str
    retry_after_seconds: int | None
    correlation_id: str | None


def normalize_response(
    http_status: int, body: dict[str, Any] | None, headers: dict[str, str] | None = None
) -> NormalizedGraphError:
    body = body or {}
    headers = headers or {}
    correlation_id = headers.get("client-request-id") or headers.get("request-id")
    retry_after = headers.get("Retry-After") or headers.get("retry-after")
    retry_after_seconds = None
    if retry_after:
        try:
            retry_after_seconds = int(retry_after)
        except ValueError:
            retry_after_seconds = None

    err = (body.get("error") or {}) if isinstance(body.get("error"), dict) else {}
    code = err.get("code") if isinstance(err, dict) else None
    message = (
        (err.get("message") if isinstance(err, dict) else None)
        or body.get("error_description")
        or ""
    )

    if 200 <= http_status < 300:
        return NormalizedGraphError(
            "success", http_status, code, message, retry_after_seconds, correlation_id
        )

    if http_status == 401:
        return NormalizedGraphError(
            "auth_required", http_status, code, message, retry_after_seconds, correlation_id
        )
    if http_status == 403:
        scope_hint = isinstance(message, str) and any(
            t in message.lower() for t in ("scope", "permission", "insufficient")
        )
        if scope_hint or (code and "permission" in code.lower()):
            return NormalizedGraphError(
                "permission_missing",
                http_status,
                code,
                message,
                retry_after_seconds,
                correlation_id,
            )
        if code and "consent" in code.lower():
            return NormalizedGraphError(
                "consent_required", http_status, code, message, retry_after_seconds, correlation_id
            )
        return NormalizedGraphError(
            "policy_denied", http_status, code, message, retry_after_seconds, correlation_id
        )
    if http_status == 429 or (code and code.lower() == "throttled"):
        return NormalizedGraphError(
            "throttled", http_status, code, message, retry_after_seconds, correlation_id
        )
    if 500 <= http_status < 600:
        return NormalizedGraphError(
            "graph_unreachable", http_status, code, message, retry_after_seconds, correlation_id
        )
    if 400 <= http_status < 500:
        return NormalizedGraphError(
            "internal_error", http_status, code, message, retry_after_seconds, correlation_id
        )
    return NormalizedGraphError(
        "internal_error", http_status, code, message, retry_after_seconds, correlation_id
    )
