from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CANONICAL_ACTION_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+\.[a-z0-9_]+$")


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


def _registry_path() -> Path:
    override = _normalize(os.getenv("EXECUTOR_ROUTING_REGISTRY_FILE"))
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "registry" / "executor_routing_v2.yaml"


@lru_cache(maxsize=1)
def load_executor_routing_registry() -> dict[str, Any]:
    path = _registry_path()
    if not path.exists():
        raise FileNotFoundError(f"executor_routing_registry_missing:{path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for key in (
        "canonical_executor_domains",
        "exact_action_routes",
        "prefix_routes",
        "agent_action_overrides",
    ):
        if key not in data:
            raise ValueError(f"executor_routing_registry_missing_key:{key}")
    return data


def reload_executor_routing_registry() -> None:
    load_executor_routing_registry.cache_clear()


def executor_route_for_action(agent: str | None, action: str) -> str:
    registry = load_executor_routing_registry()
    normalized_action = _normalize(action)
    normalized_agent = _normalize(agent)
    if not normalized_action:
        raise ValueError(f"executor_route_unknown:{normalized_agent}:{action}")

    agent_overrides = registry.get("agent_action_overrides", {}) or {}
    override = (agent_overrides.get(normalized_agent, {}) or {}).get(normalized_action)
    if override:
        return str(override)

    if _CANONICAL_ACTION_RE.fullmatch(normalized_action):
        domain = normalized_action.split(".", 1)[0]
        if domain in {str(item) for item in (registry.get("canonical_executor_domains") or [])}:
            return domain

    exact_routes = registry.get("exact_action_routes", {}) or {}
    exact_route = exact_routes.get(normalized_action)
    if exact_route:
        return str(exact_route)

    prefix_routes = registry.get("prefix_routes", {}) or {}
    for prefix, route_key in prefix_routes.items():
        if normalized_action.startswith(str(prefix).lower()):
            return str(route_key)

    raise ValueError(f"executor_route_unknown:{normalized_agent}:{action}")
