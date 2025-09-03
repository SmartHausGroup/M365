from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from smarthaus_common.logging import get_logger

log = get_logger(__name__)


def _enabled() -> bool:
    return os.getenv("ENABLE_AUDIT_LOGGING", "false").lower() in ("1", "true", "yes")


def _paths() -> tuple[Path, Path]:
    base = Path(os.getenv("APP_DATA", "data")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    logs = Path("logs").resolve()
    logs.mkdir(parents=True, exist_ok=True)
    return base / "audit.jsonl", logs / "audit.log"


def log_event(
    action: str, details: dict[str, Any] | None = None, user_info: dict[str, Any] | None = None
) -> None:
    if not _enabled():
        return
    ts = datetime.now(tz=UTC).isoformat()
    record = {
        "ts": ts,
        "action": action,
        "user": user_info or {},
        "details": details or {},
    }
    jpath, lpath = _paths()
    try:
        with jpath.open("a", encoding="utf-8") as jf:
            jf.write(json.dumps(record) + "\n")
        with lpath.open("a", encoding="utf-8") as lf:
            lf.write(f"{ts} {action} {json.dumps(details or {})}\n")
    except Exception as e:
        log.warning("Failed to write audit log: %s", e)


def recent_events(limit: int = 100) -> list[dict[str, Any]]:
    jpath, _ = _paths()
    if not jpath.exists():
        return []
    try:
        lines = jpath.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(x) for x in lines if x.strip()]
    except Exception:
        return []
