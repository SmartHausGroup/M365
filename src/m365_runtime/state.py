"""Runtime state classes (auth, health vector, action result)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HealthVector:
    svc: bool | None = None
    auth: bool | None = None
    tok: bool | None = None
    graph: bool | None = None
    perm: bool | None = None
    ctr: bool | None = None
    art: bool | None = None
    src: bool | None = None
    aud: bool | None = None

    def as_dict(self) -> dict[str, bool | None]:
        return {
            "svc": self.svc,
            "auth": self.auth,
            "tok": self.tok,
            "graph": self.graph,
            "perm": self.perm,
            "ctr": self.ctr,
            "art": self.art,
            "src": self.src,
            "aud": self.aud,
        }


def readiness(h: HealthVector) -> tuple[str, str]:
    vals = h.as_dict()
    if any(v is None for v in vals.values()):
        return ("not_ready", "unknown_clause")
    if all(v is True for v in vals.values()):
        return ("ready", "success")
    failing = [name for name, v in vals.items() if v is False]
    return ("not_ready", failing[0])


@dataclass
class ActionResult:
    status_class: str
    payload: Any | None = None
    correlation_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
