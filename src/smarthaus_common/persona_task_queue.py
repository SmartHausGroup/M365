from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from smarthaus_common.json_store import JsonStore


def _default_persona_task_queue_file() -> Path:
    registry_file = Path(os.getenv("REGISTRY_FILE", "./registry/agents.yaml")).resolve()
    return registry_file.with_name("persona_task_queue_state_v1.yaml")


def load_persona_task_queue_authority(path: Path | None = None) -> dict[str, Any]:
    source = path or Path(
        os.getenv("PERSONA_TASK_QUEUE_FILE") or _default_persona_task_queue_file()
    )
    if not source.exists():
        raise ValueError(f"persona_task_queue_authority_missing:{source}")
    with source.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("persona_task_queue_authority_invalid")
    validate_persona_task_queue_authority(payload)
    return payload


def validate_persona_task_queue_authority(payload: dict[str, Any]) -> None:
    required_root = {"version", "authority", "task_statuses", "persona_states", "transitions"}
    missing = sorted(required_root - set(payload))
    if missing:
        raise ValueError(f"persona_task_queue_authority_missing_keys:{','.join(missing)}")

    task_statuses = payload.get("task_statuses")
    if not isinstance(task_statuses, dict) or not task_statuses:
        raise ValueError("persona_task_queue_authority_invalid_task_statuses")

    persona_states = payload.get("persona_states")
    if not isinstance(persona_states, dict) or not persona_states:
        raise ValueError("persona_task_queue_authority_invalid_persona_states")

    transitions = payload.get("transitions")
    if not isinstance(transitions, dict) or not transitions:
        raise ValueError("persona_task_queue_authority_invalid_transitions")

    for status, allowed in transitions.items():
        if status not in task_statuses:
            raise ValueError(f"persona_task_queue_unknown_transition_status:{status}")
        if not isinstance(allowed, list):
            raise ValueError(f"persona_task_queue_invalid_transition_list:{status}")
        unknown = [candidate for candidate in allowed if candidate not in task_statuses]
        if unknown:
            raise ValueError(
                f"persona_task_queue_unknown_transition_target:{status}:{','.join(unknown)}"
            )


def _task_collection(canonical_agent: str) -> str:
    return f"agent_tasks_{canonical_agent}"


def _instruction_collection(canonical_agent: str) -> str:
    return f"agent_instructions_{canonical_agent}"


def _log_collection(canonical_agent: str) -> str:
    return f"agent_logs_{canonical_agent}"


def _status_definition(
    authority: dict[str, Any], status: str, key: str, default: bool = False
) -> bool:
    status_payload = authority.get("task_statuses", {}).get(status) or {}
    return bool(status_payload.get(key, default))


def _normalize_priority(raw_priority: Any) -> str:
    priority = str(raw_priority or "medium").strip().lower()
    if priority == "normal":
        priority = "medium"
    if priority not in {"critical", "high", "medium", "low"}:
        raise ValueError(f"invalid_task_priority:{priority}")
    return priority


def _normalize_task_status(authority: dict[str, Any], raw_status: Any) -> str:
    status = str(raw_status or "queued").strip().lower()
    if status not in authority.get("task_statuses", {}):
        raise ValueError(f"invalid_task_status:{status}")
    return status


def _normalize_instruction_status(raw_status: Any) -> str:
    status = str(raw_status or "queued").strip().lower()
    if status not in {"queued", "acknowledged", "cancelled"}:
        raise ValueError(f"invalid_instruction_status:{status}")
    return status


def _priority_rank(priority: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}[priority]


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


def _sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = list(enumerate(records))
    indexed.sort(key=lambda item: (int(item[1].get("ts", 0)), item[0]))
    return [record for _, record in indexed]


def _allowed_transition(authority: dict[str, Any], current_status: str, next_status: str) -> bool:
    if current_status == next_status:
        return True
    return next_status in set(authority.get("transitions", {}).get(current_status) or [])


def _project_task(
    authority: dict[str, Any],
    task: dict[str, Any],
    updates: list[dict[str, Any]],
) -> dict[str, Any]:
    projected = dict(task)
    status = _normalize_task_status(authority, projected.get("status"))
    last_activity_ts = int(projected.get("ts", 0))
    history: list[dict[str, Any]] = []
    for update in _sort_records(updates):
        next_status = _normalize_task_status(
            authority, update.get("to_status") or update.get("status") or status
        )
        if not _allowed_transition(authority, status, next_status):
            raise ValueError(f"invalid_task_transition:{status}->{next_status}")
        status = next_status
        last_activity_ts = max(last_activity_ts, int(update.get("ts", 0)))
        history.append(
            {
                "event_id": str(update.get("id") or ""),
                "ts": int(update.get("ts", 0)),
                "from_status": str(update.get("from_status") or projected.get("status") or ""),
                "to_status": status,
                "percent": update.get("percent"),
                "message": update.get("message"),
            }
        )
    projected["status"] = status
    projected["priority"] = _normalize_priority(projected.get("priority"))
    projected["is_open"] = _status_definition(authority, status, "open")
    projected["is_terminal"] = _status_definition(authority, status, "terminal")
    projected["last_activity_ts"] = last_activity_ts
    projected["history"] = history
    projected["history_count"] = len(history)
    return projected


def list_persona_tasks(
    canonical_agent: str, store: JsonStore | None = None
) -> list[dict[str, Any]]:
    authority = load_persona_task_queue_authority()
    runtime_store = store or JsonStore()
    tasks = _sort_records(runtime_store.list(_task_collection(canonical_agent)))
    logs = _sort_records(runtime_store.list(_log_collection(canonical_agent)))
    updates_by_task: dict[str, list[dict[str, Any]]] = {}
    for log in logs:
        if log.get("type") != "task_update":
            continue
        task_id = str(log.get("task_id") or "")
        if not task_id:
            continue
        updates_by_task.setdefault(task_id, []).append(log)

    projected = [
        _project_task(authority, task, updates_by_task.get(str(task.get("id") or ""), []))
        for task in tasks
    ]
    return sorted(
        projected,
        key=lambda item: (
            0 if item.get("is_open") else 1,
            _priority_rank(str(item.get("priority"))),
            -int(item.get("last_activity_ts", 0)),
            str(item.get("id") or ""),
        ),
    )


def list_persona_instructions(
    canonical_agent: str, store: JsonStore | None = None
) -> list[dict[str, Any]]:
    runtime_store = store or JsonStore()
    instructions = _sort_records(runtime_store.list(_instruction_collection(canonical_agent)))
    normalized = []
    for record in instructions:
        projected = dict(record)
        projected["status"] = _normalize_instruction_status(projected.get("status"))
        normalized.append(projected)
    return normalized


def build_persona_state(canonical_agent: str, store: JsonStore | None = None) -> dict[str, Any]:
    authority = load_persona_task_queue_authority()
    runtime_store = store or JsonStore()
    tasks = list_persona_tasks(canonical_agent, store=runtime_store)
    instructions = list_persona_instructions(canonical_agent, store=runtime_store)

    task_counts = {status: 0 for status in authority.get("task_statuses", {})}
    for task in tasks:
        task_counts[str(task.get("status"))] += 1
    task_counts["total"] = len(tasks)

    instruction_counts = {
        "queued": 0,
        "acknowledged": 0,
        "cancelled": 0,
        "total": len(instructions),
    }
    for instruction in instructions:
        status = str(instruction.get("status") or "queued")
        instruction_counts[status] += 1

    open_tasks = [task for task in tasks if bool(task.get("is_open"))]
    active_task_id = next(
        (str(task.get("id")) for task in tasks if str(task.get("status")) == "in_progress"),
        None,
    )

    if task_counts.get("in_progress", 0) > 0:
        persona_state = "active"
    elif task_counts.get("blocked", 0) > 0:
        persona_state = "blocked"
    elif task_counts.get("failed", 0) > 0:
        persona_state = "attention_required"
    elif task_counts.get("queued", 0) > 0 or instruction_counts.get("queued", 0) > 0:
        persona_state = "queued"
    else:
        persona_state = "idle"

    last_activity_ts = max(
        [int(task.get("last_activity_ts", 0)) for task in tasks]
        + [int(instruction.get("ts", 0)) for instruction in instructions]
        + [0]
    )
    return {
        "canonical_agent": canonical_agent,
        "persona_state": persona_state,
        "open_task_count": len(open_tasks),
        "active_task_id": active_task_id,
        "task_counts": task_counts,
        "instruction_counts": instruction_counts,
        "queue_depth": len(open_tasks) + int(instruction_counts.get("queued", 0)),
        "last_activity_ts": last_activity_ts or None,
    }


def create_persona_task(
    canonical_agent: str, body: dict[str, Any], store: JsonStore | None = None
) -> dict[str, Any]:
    runtime_store = store or JsonStore()
    task = {
        "agent": canonical_agent,
        "title": body.get("title") or body.get("description") or "Task",
        "description": body.get("description"),
        "priority": _normalize_priority(body.get("priority")),
        "due": body.get("due"),
        "status": "queued",
        "created_by": body.get("created_by", "system"),
        "source": body.get("source", "persona-runtime"),
        "created_at": _iso_now(),
    }
    record = runtime_store.append(_task_collection(canonical_agent), task)
    runtime_store.append(
        _log_collection(canonical_agent),
        {
            "type": "task_created",
            "task_id": record["id"],
            "from_status": None,
            "to_status": "queued",
            "message": task["title"],
        },
    )
    return next(
        task
        for task in list_persona_tasks(canonical_agent, store=runtime_store)
        if task["id"] == record["id"]
    )


def update_persona_task(
    canonical_agent: str,
    task_id: str,
    body: dict[str, Any],
    store: JsonStore | None = None,
) -> dict[str, Any]:
    authority = load_persona_task_queue_authority()
    runtime_store = store or JsonStore()
    tasks = {
        str(task.get("id")): task
        for task in list_persona_tasks(canonical_agent, store=runtime_store)
    }
    if task_id not in tasks:
        raise ValueError(f"persona_task_not_found:{task_id}")
    current = tasks[task_id]
    next_status = _normalize_task_status(authority, body.get("status") or current.get("status"))
    current_status = str(current.get("status") or "queued")
    if not _allowed_transition(authority, current_status, next_status):
        raise ValueError(f"invalid_task_transition:{current_status}->{next_status}")
    runtime_store.append(
        _log_collection(canonical_agent),
        {
            "type": "task_update",
            "task_id": task_id,
            "from_status": current_status,
            "to_status": next_status,
            "percent": body.get("percent"),
            "message": body.get("message"),
            "updated_by": body.get("updated_by", "system"),
        },
    )
    return next(
        task
        for task in list_persona_tasks(canonical_agent, store=runtime_store)
        if task["id"] == task_id
    )


def create_persona_instruction(
    canonical_agent: str, body: dict[str, Any], store: JsonStore | None = None
) -> dict[str, Any]:
    runtime_store = store or JsonStore()
    instruction_text = body.get("instruction") or body.get("command")
    if not instruction_text:
        raise ValueError("instruction_required")
    instruction = {
        "instruction": instruction_text,
        "mode": body.get("mode") or "immediate",
        "priority": _normalize_priority(body.get("priority") or "medium"),
        "scheduled_at": body.get("scheduled_at"),
        "status": _normalize_instruction_status(body.get("status") or "queued"),
        "created_by": body.get("created_by", "system"),
    }
    record = runtime_store.append(_instruction_collection(canonical_agent), instruction)
    runtime_store.append(
        _log_collection(canonical_agent),
        {"type": "instruction", "instruction_id": record["id"], "status": instruction["status"]},
    )
    return dict(record)
