from __future__ import annotations

import json
from pathlib import Path

from provisioning_api.audit import log_event, recent_events
from smarthaus_common.audit_schema import build_audit_record_v2, reload_unified_audit_schema_registry


def test_build_audit_record_v2_projects_canonical_contexts() -> None:
    reload_unified_audit_schema_registry()
    record = build_audit_record_v2(
        surface="ops_adapter",
        action="users.disable",
        status="approval_pending",
        correlation_id="corr-123",
        agent="m365-administrator",
        actor="admin@example.com",
        actor_tier={"tier_name": "global_admin"},
        actor_groups=["entra-global-admins"],
        persona="Marcus Chen",
        persona_target="m365-administrator",
        executor={"mode": "app_only", "domain": "directory"},
        tenant="tenant-alpha",
        approval={
            "approval_id": "appr-123",
            "approval_profile": "high-impact",
            "risk_class": "high",
            "required": True,
        },
        result={"outcome": "approval_pending"},
        details={"reason": "approval_required"},
    )

    assert record["schema_version"] == "2.0"
    assert record["surface"] == "ops_adapter"
    assert record["actor"] == "admin@example.com"
    assert record["persona"] == "Marcus Chen"
    assert record["approval"]["approval_id"] == "appr-123"
    assert record["result"]["outcome"] == "approval_pending"
    assert record["ts"] == record["timestamp"]


def test_provisioning_api_log_event_writes_unified_schema(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("ENABLE_AUDIT_LOGGING", "1")
    monkeypatch.setenv("APP_DATA", str(tmp_path / "data"))

    log_event(
        "m365_instruction",
        {
            "action": "list_users",
            "params": {},
            "ok": True,
            "result": {"users": [], "count": 0},
            "trace_id": "trace-123",
        },
        user_info={"userPrincipalName": "tester@example.com"},
    )

    events = recent_events(10)
    assert events
    entry = events[-1]
    assert entry["schema_version"] == "2.0"
    assert entry["surface"] == "instruction_api"
    assert entry["correlation_id"] == "trace-123"
    assert entry["actor"] == "tester@example.com"
    assert entry["result"]["outcome"] == "success"
    assert entry["result"]["trace_id"] == "trace-123"
    assert entry["user"]["userPrincipalName"] == "tester@example.com"

    audit_path = (tmp_path / "data" / "audit.jsonl").resolve()
    raw = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert raw[-1]["status"] == "success"
