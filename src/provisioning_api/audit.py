from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from smarthaus_common.audit_schema import build_audit_record_v2
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
    detail_map = details or {}
    user_map = user_info or {}
    blocked = bool(detail_map.get("blocked"))
    ok = detail_map.get("ok")
    if blocked:
        status = "blocked"
    elif ok is True:
        status = "success"
    elif ok is False:
        status = "error"
    else:
        status = "recorded"

    result_context: dict[str, Any] = {"outcome": status}
    if "ok" in detail_map:
        result_context["ok"] = bool(ok)
    if "result" in detail_map:
        result_context["payload"] = detail_map.get("result")
    if detail_map.get("error") is not None:
        result_context["error"] = detail_map.get("error")
    if detail_map.get("trace_id") is not None:
        result_context["trace_id"] = detail_map.get("trace_id")
    if detail_map.get("blocked") is not None:
        result_context["blocked"] = blocked
    if detail_map.get("idempotent_replay") is not None:
        result_context["idempotent_replay"] = bool(detail_map.get("idempotent_replay"))

    record = build_audit_record_v2(
        surface="instruction_api",
        action=action,
        status=status,
        correlation_id=str(detail_map.get("trace_id") or detail_map.get("correlation_id") or ""),
        agent="m365-instruction-router",
        actor=(
            user_map.get("userPrincipalName")
            or user_map.get("preferred_username")
            or user_map.get("mail")
            or user_map.get("email")
        ),
        details=detail_map,
        result=result_context,
        legacy_user=user_map,
        timestamp=ts,
    )
    jpath, lpath = _paths()
    try:
        with jpath.open("a", encoding="utf-8") as jf:
            jf.write(json.dumps(record) + "\n")
        with lpath.open("a", encoding="utf-8") as lf:
            lf.write(f"{ts} {status} {action} {json.dumps(detail_map)}\n")
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
