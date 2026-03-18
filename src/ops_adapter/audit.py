from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

SENSITIVE_KEYS = {"password", "temporaryPassword", "Authorization", "token", "secret"}


def _log_dir(log_dir: str | None = None) -> Path:
    resolved_log_dir = log_dir if log_dir is not None else os.getenv("LOG_DIR", "./logs")
    path = Path(resolved_log_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _log_file(log_dir: str | None = None) -> Path:
    return _log_dir(log_dir) / "ops_audit.log"


def _sanitize(obj: Any) -> Any:
    try:
        if isinstance(obj, dict):
            return {k: ("***" if k in SENSITIVE_KEYS else _sanitize(v)) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_sanitize(v) for v in obj]
        return obj
    except Exception:
        return obj


def _write_entry(entry: dict[str, Any], log_dir: str | None = None) -> None:
    with _log_file(log_dir).open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _base_entry(
    *,
    status: str,
    agent: str,
    action: str,
    correlation_id: str,
    details: Any,
    surface: str,
    event_class: str | None = None,
    actor: str | None = None,
    actor_tier: dict[str, Any] | None = None,
    actor_groups: list[str] | None = None,
    executor: dict[str, Any] | None = None,
    tenant: str | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "correlation_id": correlation_id,
        "surface": surface,
        "agent": agent,
        "action": action,
        "status": status,
        "details": _sanitize(details),
    }
    if event_class:
        entry["event_class"] = event_class
    if actor:
        entry["actor"] = actor
    if actor_tier:
        entry["actor_tier"] = _sanitize(actor_tier)
    if actor_groups:
        entry["actor_groups"] = _sanitize(actor_groups)
    if executor:
        entry["executor"] = _sanitize(executor)
    if tenant:
        entry["tenant"] = tenant
    if before is not None:
        entry["before"] = _sanitize(before)
    if after is not None:
        entry["after"] = _sanitize(after)
    return entry


class Auditor:
    def __init__(self, log_dir: str | None = None):
        resolved_log_dir = log_dir if log_dir is not None else os.getenv("LOG_DIR", "./logs")
        self.log_dir = _log_dir(resolved_log_dir)
        self.log_file = _log_file(log_dir)
        self.la_workspace = os.getenv("LA_WORKSPACE_ID")
        self.la_shared_key = os.getenv("LA_SHARED_KEY")
        self.enterprise_audit = os.getenv("AUDIT_SERVICE_URL")

    def _sanitize(self, obj: Any) -> Any:
        return _sanitize(obj)

    async def log(
        self, status: str, agent: str, action: str, details: Any, correlation_id: str
    ) -> None:
        detail_map = details if isinstance(details, dict) else {}
        entry = _base_entry(
            status=status,
            agent=agent,
            action=action,
            correlation_id=correlation_id,
            details=self._sanitize(details),
            surface="ops_adapter",
            actor=detail_map.get("actor"),
            actor_tier=detail_map.get("actor_tier"),
            actor_groups=detail_map.get("actor_groups"),
            executor=detail_map.get("executor"),
            tenant=detail_map.get("tenant"),
        )
        _write_entry(entry, str(self.log_dir))

        # Optional: Log Analytics ingestion
        if self.la_workspace and self.la_shared_key:
            try:
                await self._send_to_log_analytics(entry)
            except Exception:
                # Avoid raising audit failures
                pass

        # Forward to Enterprise audit-service if configured
        if self.enterprise_audit:
            try:
                await self._send_to_enterprise(entry)
            except Exception:
                pass

    async def _send_to_log_analytics(self, entry: dict[str, Any]) -> None:
        # Minimal placeholder for the HTTP Data Collector API
        # In production, sign requests with the shared key
        # https://learn.microsoft.com/azure/azure-monitor/logs/data-collector-api
        _ = entry
        return

    async def _send_to_enterprise(self, entry: dict[str, Any]) -> None:
        enterprise_audit = self.enterprise_audit
        if not enterprise_audit:
            return
        payload = {
            "correlation_id": entry.get("correlation_id"),
            "service": "ops-adapter",
            "action": entry.get("action"),
            "agent": entry.get("agent"),
            "status": entry.get("status"),
            "details": entry.get("details") or {},
            "actor": entry.get("actor"),
            "actor_tier": entry.get("actor_tier"),
            "actor_groups": entry.get("actor_groups"),
            "executor": entry.get("executor"),
            "tenant": entry.get("tenant"),
            "timestamp": entry.get("timestamp"),
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(f"{enterprise_audit.rstrip('/')}/audit/ingest", json=payload)


def record_admin_event(
    *,
    event_class: str,
    action: str,
    correlation_id: str,
    actor: str | None,
    actor_tier: dict[str, Any] | None,
    actor_groups: list[str] | None,
    executor: dict[str, Any] | None,
    tenant: str,
    status: str,
    details: dict[str, Any] | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = _base_entry(
        status=status,
        agent="m365-administrator",
        action=action,
        correlation_id=correlation_id,
        details=details or {},
        surface="ops_adapter_admin",
        event_class=event_class,
        actor=actor or "system",
        actor_tier=actor_tier,
        actor_groups=actor_groups,
        executor=executor,
        tenant=tenant,
        before=before,
        after=after,
    )
    _write_entry(entry)
    return entry


def recent_admin_events(
    *,
    tenant: str | None = None,
    action: str | None = None,
    event_class: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    log_file = _log_file()
    if not log_file.exists():
        return []

    try:
        lines = log_file.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    events: list[dict[str, Any]] = []
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("surface") != "ops_adapter_admin":
            continue
        if tenant and entry.get("tenant") != tenant:
            continue
        if action and entry.get("action") != action:
            continue
        if event_class and entry.get("event_class") != event_class:
            continue
        events.append(entry)
        if len(events) >= max(1, min(limit, 200)):
            break
    return events


# Backward-compatible sync logger used by ops_adapter.app
def audit_log(status: str, *, agent: str, action: str, correlation_id: str, **kwargs: Any) -> None:
    try:
        entry = _base_entry(
            status=status,
            agent=agent,
            action=action,
            correlation_id=correlation_id,
            details=kwargs,
            surface="ops_adapter_sync",
            actor=kwargs.get("actor"),
            actor_tier=kwargs.get("actor_tier"),
            actor_groups=kwargs.get("actor_groups"),
            executor=kwargs.get("executor"),
            tenant=kwargs.get("tenant"),
        )
        _write_entry(entry)
    except Exception:
        # Never fail caller due to audit issues
        pass
