from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

SENSITIVE_KEYS = {"password", "temporaryPassword", "Authorization", "token", "secret"}


def _registry_path() -> Path:
    return Path(__file__).resolve().parents[2] / "registry" / "unified_audit_schema_v2.yaml"


def _normalize_string(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def sanitize_audit_payload(obj: Any) -> Any:
    try:
        if isinstance(obj, dict):
            return {
                key: ("***" if key in SENSITIVE_KEYS else sanitize_audit_payload(value))
                for key, value in obj.items()
            }
        if isinstance(obj, list):
            return [sanitize_audit_payload(value) for value in obj]
        return obj
    except Exception:
        return obj


@lru_cache(maxsize=1)
def load_unified_audit_schema_registry() -> dict[str, Any]:
    path = _registry_path()
    if not path.exists():
        raise FileNotFoundError(f"unified_audit_schema_registry_missing:{path}")
    with path.open(encoding="utf-8") as handle:
        registry = yaml.safe_load(handle) or {}
    for key in ("schema_version", "required_top_level_fields", "surface_defaults"):
        if key not in registry:
            raise ValueError(f"unified_audit_schema_registry_missing_key:{key}")
    return registry


def reload_unified_audit_schema_registry() -> None:
    load_unified_audit_schema_registry.cache_clear()


def build_audit_record_v2(
    *,
    surface: str,
    action: str,
    status: str,
    details: Any,
    correlation_id: str | None = None,
    agent: str | None = None,
    event_class: str | None = None,
    actor: str | None = None,
    actor_tier: dict[str, Any] | None = None,
    actor_groups: list[str] | None = None,
    persona: str | None = None,
    persona_target: str | None = None,
    executor: dict[str, Any] | None = None,
    tenant: str | None = None,
    approval: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    legacy_user: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    registry = load_unified_audit_schema_registry()
    surface_defaults = (registry.get("surface_defaults") or {}).get(surface)
    if not isinstance(surface_defaults, dict):
        raise ValueError(f"unified_audit_schema_unknown_surface:{surface}")

    ts = timestamp or datetime.now(UTC).isoformat()
    resolved_agent = _normalize_string(agent) or _normalize_string(
        surface_defaults.get("default_agent")
    )
    resolved_result = sanitize_audit_payload(result or {"outcome": status})

    entry: dict[str, Any] = {
        "schema_version": _normalize_string(registry.get("schema_version")) or "2.0",
        "timestamp": ts,
        "ts": ts,
        "correlation_id": _normalize_string(correlation_id),
        "surface": surface,
        "agent": resolved_agent,
        "action": action,
        "status": status,
        "details": sanitize_audit_payload(details),
        "result": resolved_result,
    }
    if event_class:
        entry["event_class"] = event_class
    if actor:
        entry["actor"] = actor
    if actor_tier:
        entry["actor_tier"] = sanitize_audit_payload(actor_tier)
    if actor_groups:
        entry["actor_groups"] = sanitize_audit_payload(actor_groups)
    if persona:
        entry["persona"] = persona
    if persona_target:
        entry["persona_target"] = persona_target
    if executor:
        entry["executor"] = sanitize_audit_payload(executor)
    if tenant:
        entry["tenant"] = tenant
    if approval:
        entry["approval"] = sanitize_audit_payload(approval)
    if before is not None:
        entry["before"] = sanitize_audit_payload(before)
    if after is not None:
        entry["after"] = sanitize_audit_payload(after)
    if legacy_user is not None:
        entry["user"] = sanitize_audit_payload(legacy_user)

    missing = [
        key
        for key in (registry.get("required_top_level_fields") or [])
        if key not in entry or entry.get(key) is None
    ]
    if missing:
        raise ValueError(f"unified_audit_schema_missing_required:{','.join(sorted(missing))}")
    return entry
