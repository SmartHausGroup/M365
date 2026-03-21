from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_task_queue import build_persona_state


def _default_persona_accountability_file() -> Path:
    registry_file = Path(os.getenv("REGISTRY_FILE", "./registry/agents.yaml")).resolve()
    return registry_file.with_name("persona_accountability_v1.yaml")


def _default_persona_registry_file() -> Path:
    registry_file = Path(os.getenv("REGISTRY_FILE", "./registry/agents.yaml")).resolve()
    return registry_file.with_name("persona_registry_v2.yaml")


def load_persona_accountability_authority(path: Path | None = None) -> dict[str, Any]:
    source = path or Path(
        os.getenv("PERSONA_ACCOUNTABILITY_FILE") or _default_persona_accountability_file()
    )
    if not source.exists():
        raise ValueError(f"persona_accountability_authority_missing:{source}")
    with source.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("persona_accountability_authority_invalid")
    validate_persona_accountability_authority(payload)
    return payload


def validate_persona_accountability_authority(payload: dict[str, Any]) -> None:
    required_root = {"version", "authority", "profiles", "accountability_states", "rules"}
    missing = sorted(required_root - set(payload))
    if missing:
        raise ValueError(f"persona_accountability_authority_missing_keys:{','.join(missing)}")

    profiles = payload.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("persona_accountability_authority_invalid_profiles")
    for risk_tier, profile in profiles.items():
        if not isinstance(profile, dict):
            raise ValueError(f"persona_accountability_authority_invalid_profile:{risk_tier}")
        required_profile_keys = {
            "target_queue_depth",
            "max_queue_depth",
            "max_open_tasks",
            "blocked_task_threshold",
            "failed_task_threshold",
        }
        missing_profile = sorted(required_profile_keys - set(profile))
        if missing_profile:
            raise ValueError(
                "persona_accountability_authority_missing_profile_keys:"
                f"{risk_tier}:{','.join(missing_profile)}"
            )

    states = payload.get("accountability_states")
    if not isinstance(states, dict) or sorted(states) != ["escalated", "on_track", "warning"]:
        raise ValueError("persona_accountability_authority_invalid_states")

    rules = payload.get("rules")
    if not isinstance(rules, dict):
        raise ValueError("persona_accountability_authority_invalid_rules")
    target_order = rules.get("escalation_target_order")
    if not isinstance(target_order, list) or not target_order:
        raise ValueError("persona_accountability_authority_invalid_target_order")


def load_persona_registry_snapshot(path: Path | None = None) -> dict[str, Any]:
    source = path or Path(os.getenv("PERSONA_REGISTRY_FILE") or _default_persona_registry_file())
    if not source.exists():
        raise ValueError(f"persona_registry_snapshot_missing:{source}")
    with source.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("personas"), dict):
        raise ValueError("persona_registry_snapshot_invalid")
    return payload


def _risk_profile(authority: dict[str, Any], risk_tier: str) -> dict[str, int]:
    profiles = authority.get("profiles", {})
    profile = profiles.get(risk_tier) or profiles.get("medium")
    if not isinstance(profile, dict):
        raise ValueError(f"persona_accountability_profile_missing:{risk_tier}")
    return {key: int(value) for key, value in profile.items()}


def _escalation_target(
    authority: dict[str, Any], persona: dict[str, Any]
) -> tuple[str | None, str | None]:
    order = authority.get("rules", {}).get("escalation_target_order", [])
    for field in order:
        value = str(persona.get(field) or "").strip()
        if value:
            return field, value
    return None, None


def build_persona_accountability(
    canonical_agent: str,
    store: JsonStore | None = None,
    persona_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    authority = load_persona_accountability_authority()
    registry_snapshot = persona_registry or load_persona_registry_snapshot()
    personas = registry_snapshot.get("personas", {})
    persona = personas.get(canonical_agent)
    if not isinstance(persona, dict):
        raise ValueError(f"persona_accountability_unknown_persona:{canonical_agent}")

    queue_state = build_persona_state(canonical_agent, store=store)
    task_counts = dict(queue_state.get("task_counts") or {})
    instruction_counts = dict(queue_state.get("instruction_counts") or {})
    risk_tier = str(persona.get("risk_tier") or "medium").strip().lower()
    thresholds = _risk_profile(authority, risk_tier)

    total_tasks = int(task_counts.get("total", 0))
    completed_tasks = int(task_counts.get("completed", 0))
    blocked_tasks = int(task_counts.get("blocked", 0))
    failed_tasks = int(task_counts.get("failed", 0))
    open_task_count = int(queue_state.get("open_task_count", 0))
    queue_depth = int(queue_state.get("queue_depth", 0))
    queued_instructions = int(instruction_counts.get("queued", 0))
    completion_ratio = round((completed_tasks / total_tasks), 3) if total_tasks else 0.0

    escalation_reasons: list[str] = []
    if queue_depth > thresholds["max_queue_depth"]:
        escalation_reasons.append("queue_depth_exceeded")
    if open_task_count > thresholds["max_open_tasks"]:
        escalation_reasons.append("open_task_limit_exceeded")
    if authority.get("rules", {}).get("escalate_on_blocked_tasks", False) and blocked_tasks >= int(
        thresholds["blocked_task_threshold"]
    ):
        escalation_reasons.append("blocked_work_present")
    if authority.get("rules", {}).get("escalate_on_failed_tasks", False) and failed_tasks >= int(
        thresholds["failed_task_threshold"]
    ):
        escalation_reasons.append("failed_work_present")

    if escalation_reasons:
        accountability_state = "escalated"
    elif authority.get("rules", {}).get("warning_when_queue_depth_reaches_target", False) and (
        queue_depth >= thresholds["target_queue_depth"]
    ):
        accountability_state = "warning"
    else:
        accountability_state = "on_track"

    escalation_field, escalation_target = _escalation_target(authority, persona)
    return {
        "canonical_agent": canonical_agent,
        "display_name": persona.get("display_name"),
        "accountability_state": accountability_state,
        "risk_tier": risk_tier,
        "approval_profile": persona.get("approval_profile"),
        "ownership": {
            "department": persona.get("department"),
            "title": persona.get("title"),
            "manager": persona.get("manager"),
            "escalation_owner": persona.get("escalation_owner"),
            "approval_owner": persona.get("approval_owner"),
            "status": persona.get("status"),
            "coverage_status": persona.get("coverage_status"),
        },
        "thresholds": thresholds,
        "metrics": {
            "queue_depth": queue_depth,
            "open_task_count": open_task_count,
            "queued_tasks": int(task_counts.get("queued", 0)),
            "in_progress_tasks": int(task_counts.get("in_progress", 0)),
            "blocked_tasks": blocked_tasks,
            "failed_tasks": failed_tasks,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "queued_instructions": queued_instructions,
            "completion_ratio": completion_ratio,
            "last_activity_ts": queue_state.get("last_activity_ts"),
            "persona_state": queue_state.get("persona_state"),
        },
        "escalation": {
            "required": accountability_state == "escalated",
            "target_role": escalation_field,
            "target": escalation_target,
            "reasons": escalation_reasons,
        },
    }
