"""Bounded Microsoft Graph client with retry/throttle/normalized errors."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from .errors import NormalizedGraphError, normalize_response

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
DEFAULT_TIMEOUT = 30.0
MAX_TIMEOUT = 60.0
GRAPH_5XX_RETRY_BUDGET = 2
THROTTLE_RETRY_BUDGET = 2
RETRY_AFTER_MAX_SECONDS = 30


class GraphInvocationError(RuntimeError):
    def __init__(self, normalized: NormalizedGraphError) -> None:
        super().__init__(f"GraphInvocationError {normalized.status_class}/{normalized.http_status}/{normalized.code}")
        self.normalized = normalized


@dataclass
class GraphResult:
    status_class: str
    http_status: int
    body: dict[str, Any] | None
    correlation_id: str | None
    retry_after_seconds: int | None


def graph_get(
    access_token: str,
    endpoint: str,
    *,
    params: dict[str, Any] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    transport: httpx.BaseTransport | None = None,
    sleep: callable = time.sleep,
) -> GraphResult:
    timeout = min(timeout, MAX_TIMEOUT)
    url = endpoint if endpoint.startswith("https://") else f"{GRAPH_BASE}{endpoint}"
    if params:
        url = f"{url}{'&' if '?' in url else '?'}{urlencode(params)}"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    five_xx_attempts = 0
    throttle_attempts = 0
    backoff = 1.0
    last_normalized: NormalizedGraphError | None = None
    while True:
        with httpx.Client(transport=transport, timeout=timeout) as client:
            try:
                response = client.get(url, headers=headers)
            except httpx.HTTPError as exc:
                last_normalized = NormalizedGraphError("graph_unreachable", 0, "transport_error", str(exc), None, None)
                break
        body: dict[str, Any] | None = None
        try:
            body = response.json()
        except Exception:
            body = None
        normalized = normalize_response(response.status_code, body, dict(response.headers))
        if normalized.status_class == "success":
            return GraphResult(normalized.status_class, response.status_code, body, normalized.correlation_id, normalized.retry_after_seconds)
        if normalized.status_class == "throttled" and throttle_attempts < THROTTLE_RETRY_BUDGET:
            throttle_attempts += 1
            sleep(min(normalized.retry_after_seconds or 1, RETRY_AFTER_MAX_SECONDS))
            continue
        if normalized.status_class == "graph_unreachable" and 500 <= response.status_code < 600 and five_xx_attempts < GRAPH_5XX_RETRY_BUDGET:
            five_xx_attempts += 1
            sleep(backoff)
            backoff *= 4
            continue
        last_normalized = normalized
        break
    if last_normalized is None:
        last_normalized = NormalizedGraphError("internal_error", 0, "unknown", "no response", None, None)
    return GraphResult(last_normalized.status_class, last_normalized.http_status, None, last_normalized.correlation_id, last_normalized.retry_after_seconds)
