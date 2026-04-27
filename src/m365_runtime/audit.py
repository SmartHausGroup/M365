"""Bounded audit envelope with strict secret redaction (L_AUDIT)."""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

REDACT_PATTERN = re.compile(
    r"(?i)token|secret|password|assertion|certificate.*key|private.*key|authorization"
)
MAX_AUDIT_BYTES = 8192
SENTINEL = "[redacted]"


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        if REDACT_PATTERN.search(value):
            return SENTINEL
        return value
    if isinstance(value, dict):
        return {k: (SENTINEL if REDACT_PATTERN.search(str(k)) else _redact_value(v)) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_redact_value(v) for v in value]
    return value


def redact(payload: Any) -> Any:
    return _redact_value(payload)


@dataclass(frozen=True)
class AuditEnvelope:
    actor: str
    action: str
    status_class: str
    correlation_id: str
    time_unix: float
    before: Any = None
    after: Any = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "actor": self.actor,
            "action": self.action,
            "status_class": self.status_class,
            "correlation_id": self.correlation_id,
            "time_unix": self.time_unix,
            "before_redacted": _redact_value(self.before),
            "after_redacted": _redact_value(self.after),
            "extra_redacted": _redact_value(self.extra),
        }
        encoded = json.dumps(d, sort_keys=True).encode("utf-8")
        if len(encoded) > MAX_AUDIT_BYTES:
            raise ValueError(f"audit_envelope_oversize:{len(encoded)}")
        return d


def build_envelope(
    actor: str,
    action: str,
    status_class: str,
    *,
    before: Any = None,
    after: Any = None,
    extra: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    return AuditEnvelope(
        actor=actor or "unknown",
        action=action or "unknown",
        status_class=status_class or "unknown",
        correlation_id=correlation_id or str(uuid.uuid4()),
        time_unix=time.time(),
        before=before,
        after=after,
        extra=extra or {},
    ).to_dict()
