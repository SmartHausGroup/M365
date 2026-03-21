from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_accountability import build_persona_accountability
from smarthaus_common.persona_task_queue import (
    list_persona_instructions,
    list_persona_tasks,
)


def _default_persona_memory_file() -> Path:
    registry_file = Path(os.getenv("REGISTRY_FILE", "./registry/agents.yaml")).resolve()
    return registry_file.with_name("persona_memory_work_history_v1.yaml")


def load_persona_memory_authority(path: Path | None = None) -> dict[str, Any]:
    source = path or Path(os.getenv("PERSONA_MEMORY_FILE") or _default_persona_memory_file())
    if not source.exists():
        raise ValueError(f"persona_memory_authority_missing:{source}")
    with source.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("persona_memory_authority_invalid")
    validate_persona_memory_authority(payload)
    return payload


def validate_persona_memory_authority(payload: dict[str, Any]) -> None:
    required_root = {
        "version",
        "authority",
        "memory_types",
        "visibility_levels",
        "retention",
        "rules",
    }
    missing = sorted(required_root - set(payload))
    if missing:
        raise ValueError(f"persona_memory_authority_missing_keys:{','.join(missing)}")
    if not isinstance(payload.get("memory_types"), dict) or not payload.get("memory_types"):
        raise ValueError("persona_memory_authority_invalid_memory_types")
    if not isinstance(payload.get("visibility_levels"), dict) or not payload.get(
        "visibility_levels"
    ):
        raise ValueError("persona_memory_authority_invalid_visibility_levels")
    retention = payload.get("retention")
    if not isinstance(retention, dict):
        raise ValueError("persona_memory_authority_invalid_retention")
    for key in {"max_memories_per_persona", "max_history_events_per_persona", "max_content_chars"}:
        if key not in retention:
            raise ValueError(f"persona_memory_authority_missing_retention:{key}")
    rules = payload.get("rules")
    if not isinstance(rules, dict):
        raise ValueError("persona_memory_authority_invalid_rules")
    if not isinstance(rules.get("allowed_sources"), list) or not rules.get("allowed_sources"):
        raise ValueError("persona_memory_authority_invalid_sources")


def _memory_collection(canonical_agent: str) -> str:
    return f"agent_memory_{canonical_agent}"


def _log_collection(canonical_agent: str) -> str:
    return f"agent_logs_{canonical_agent}"


def _history_limit(authority: dict[str, Any], limit: int | None = None) -> int:
    configured = int(authority.get("retention", {}).get("max_history_events_per_persona", 100))
    if limit is None:
        return configured
    return max(0, min(int(limit), configured))


def _memory_limit(authority: dict[str, Any]) -> int:
    return int(authority.get("retention", {}).get("max_memories_per_persona", 50))


def _content_limit(authority: dict[str, Any]) -> int:
    return int(authority.get("retention", {}).get("max_content_chars", 2000))


def _sort_desc(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = list(enumerate(records))
    indexed.sort(key=lambda item: (-int(item[1].get("ts", 0)), -item[0]))
    return [record for _, record in indexed]


def list_persona_memory(
    canonical_agent: str, store: JsonStore | None = None, limit: int | None = None
) -> list[dict[str, Any]]:
    authority = load_persona_memory_authority()
    runtime_store = store or JsonStore()
    memories = runtime_store.list(_memory_collection(canonical_agent))
    bounded = _sort_desc(memories)[: _history_limit(authority, limit or _memory_limit(authority))]
    return [dict(entry) for entry in bounded]


def create_persona_memory(
    canonical_agent: str, body: dict[str, Any], store: JsonStore | None = None
) -> dict[str, Any]:
    authority = load_persona_memory_authority()
    runtime_store = store or JsonStore()
    memories = runtime_store.list(_memory_collection(canonical_agent))
    if len(memories) >= _memory_limit(authority):
        raise ValueError(f"persona_memory_limit_reached:{canonical_agent}")

    memory_type = str(body.get("memory_type") or body.get("type") or "note").strip().lower()
    if memory_type not in authority.get("memory_types", {}):
        raise ValueError(f"invalid_persona_memory_type:{memory_type}")

    visibility = str(
        body.get("visibility") or authority.get("rules", {}).get("default_visibility") or "internal"
    ).strip()
    if visibility not in authority.get("visibility_levels", {}):
        raise ValueError(f"invalid_persona_memory_visibility:{visibility}")

    source = str(body.get("source") or "human").strip().lower()
    if source not in set(authority.get("rules", {}).get("allowed_sources") or []):
        raise ValueError(f"invalid_persona_memory_source:{source}")

    content = str(body.get("content") or body.get("memory") or "").strip()
    if not content:
        raise ValueError("persona_memory_content_required")
    if len(content) > _content_limit(authority):
        raise ValueError(f"persona_memory_content_too_long:{len(content)}")

    tags = body.get("tags") or []
    if not isinstance(tags, list):
        raise ValueError("persona_memory_tags_invalid")

    entry = {
        "agent": canonical_agent,
        "memory_type": memory_type,
        "content": content,
        "visibility": visibility,
        "source": source,
        "created_by": body.get("created_by", "system"),
        "tags": [str(tag) for tag in tags if str(tag).strip()],
    }
    record = runtime_store.append(_memory_collection(canonical_agent), entry)
    runtime_store.append(
        _log_collection(canonical_agent),
        {
            "type": "memory_entry",
            "memory_id": record["id"],
            "memory_type": memory_type,
            "visibility": visibility,
            "source": source,
            "created_by": entry["created_by"],
        },
    )
    return dict(record)


def build_persona_work_history(
    canonical_agent: str, store: JsonStore | None = None, limit: int | None = None
) -> dict[str, Any]:
    authority = load_persona_memory_authority()
    runtime_store = store or JsonStore()
    tasks = list_persona_tasks(canonical_agent, store=runtime_store)
    instructions = list_persona_instructions(canonical_agent, store=runtime_store)
    memories = list_persona_memory(canonical_agent, store=runtime_store)

    events: list[dict[str, Any]] = []
    for task in tasks:
        task_id = str(task.get("id") or "")
        events.append(
            {
                "event_type": "task_created",
                "event_id": f"task-created:{task_id}",
                "ts": int(task.get("ts", 0)),
                "task_id": task_id,
                "title": task.get("title"),
                "status": task.get("status"),
                "created_by": task.get("created_by"),
            }
        )
        for history_event in task.get("history") or []:
            events.append(
                {
                    "event_type": "task_update",
                    "event_id": history_event.get("event_id"),
                    "ts": int(history_event.get("ts", 0)),
                    "task_id": task_id,
                    "from_status": history_event.get("from_status"),
                    "to_status": history_event.get("to_status"),
                    "message": history_event.get("message"),
                    "percent": history_event.get("percent"),
                }
            )

    for instruction in instructions:
        events.append(
            {
                "event_type": "instruction",
                "event_id": str(instruction.get("id") or ""),
                "ts": int(instruction.get("ts", 0)),
                "instruction": instruction.get("instruction"),
                "mode": instruction.get("mode"),
                "status": instruction.get("status"),
                "created_by": instruction.get("created_by"),
            }
        )

    for memory in memories:
        events.append(
            {
                "event_type": "memory",
                "event_id": str(memory.get("id") or ""),
                "ts": int(memory.get("ts", 0)),
                "memory_type": memory.get("memory_type"),
                "content": memory.get("content"),
                "visibility": memory.get("visibility"),
                "source": memory.get("source"),
                "created_by": memory.get("created_by"),
            }
        )

    sorted_events = _sort_desc(events)[: _history_limit(authority, limit)]
    accountability = build_persona_accountability(canonical_agent, store=runtime_store)
    return {
        "canonical_agent": canonical_agent,
        "memory_count": len(memories),
        "task_count": len(tasks),
        "instruction_count": len(instructions),
        "event_count": len(sorted_events),
        "accountability_state": accountability.get("accountability_state"),
        "history": sorted_events,
    }
