from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import httpx


class Auditor:
    def __init__(self, log_dir: str | None = None):
        self.log_dir = Path(log_dir or os.getenv("LOG_DIR", "./logs"))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "ops_audit.log"
        self.la_workspace = os.getenv("LA_WORKSPACE_ID")
        self.la_shared_key = os.getenv("LA_SHARED_KEY")
        self.enterprise_audit = os.getenv("AUDIT_SERVICE_URL")

    def _sanitize(self, obj: Any) -> Any:
        SENSITIVE_KEYS = {"password", "temporaryPassword", "Authorization", "token", "secret"}
        try:
            if isinstance(obj, dict):
                return {k: ("***" if k in SENSITIVE_KEYS else self._sanitize(v)) for k, v in obj.items()}
            if isinstance(obj, list):
                return [self._sanitize(v) for v in obj]
            return obj
        except Exception:
            return obj

    async def log(self, status: str, agent: str, action: str, details: Any, correlation_id: str):
        safe_details = self._sanitize(details)
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "agent": agent,
            "action": action,
            "status": status,
            "details": safe_details,
        }
        # Write JSONL
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

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

    async def _send_to_log_analytics(self, entry: Dict[str, Any]):
        # Minimal placeholder for the HTTP Data Collector API
        # In production, sign requests with the shared key
        # https://learn.microsoft.com/azure/azure-monitor/logs/data-collector-api
        _ = entry
        return

    async def _send_to_enterprise(self, entry: Dict[str, Any]):
        payload = {
            "correlation_id": entry.get("correlation_id"),
            "service": "ops-adapter",
            "action": entry.get("action"),
            "agent": entry.get("agent"),
            "status": entry.get("status"),
            "details": entry.get("details") or {},
            "timestamp": entry.get("timestamp"),
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(f"{self.enterprise_audit.rstrip('/')}/audit/ingest", json=payload)


# Backward-compatible sync logger used by ops_adapter.app
def audit_log(status: str, *, agent: str, action: str, correlation_id: str, **kwargs: Any) -> None:  # type: ignore[no-redef]
    try:
        log_dir = Path(os.getenv("LOG_DIR", "./logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "ops_audit.log"
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "agent": agent,
            "action": action,
            "status": status,
            "details": kwargs,
        }
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        # Never fail caller due to audit issues
        pass
