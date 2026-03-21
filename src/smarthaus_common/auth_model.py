from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from smarthaus_common.executor_routing import executor_route_for_action

_CANONICAL_ACTION_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+\.[a-z0-9_]+$")
_SELF_SENTINELS = {"", "me", "self", "current"}


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


def _registry_path() -> Path:
    override = _normalize(os.getenv("AUTH_MODEL_REGISTRY_FILE"))
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "registry" / "auth_model_v2.yaml"


@dataclass(frozen=True)
class AuthResolution:
    auth_class: str
    prefer_delegated: bool
    requires_delegated_token: bool
    executor_domain: str
    rule_source: str


def _normalize_auth_class(value: str | None) -> str:
    normalized = _normalize(value).replace("-", "_")
    return normalized or "mixed"


def _context_value(params: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        raw = params.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if text:
            return text
    return None


def _has_explicit_context(params: dict[str, Any], keys: list[str]) -> bool:
    value = _context_value(params, keys)
    if value is None:
        return False
    return _normalize(value) not in _SELF_SENTINELS


def _prefers_delegated(
    auth_class: str,
    policy: dict[str, Any],
    params: dict[str, Any],
) -> bool:
    normalized_class = _normalize_auth_class(auth_class)
    if normalized_class == "delegated":
        return True
    if normalized_class not in {"hybrid", "mixed"}:
        return False

    delegated_preference = _normalize(policy.get("delegated_preference"))
    context_keys = [str(item) for item in (policy.get("self_context_keys") or [])]
    explicit_context_present = _has_explicit_context(params, context_keys)

    if delegated_preference == "prefer_self_when_implicit":
        return not explicit_context_present
    if delegated_preference == "always":
        return True
    return False


@lru_cache(maxsize=1)
def load_auth_model_registry() -> dict[str, Any]:
    path = _registry_path()
    if not path.exists():
        raise FileNotFoundError(f"auth_model_registry_missing:{path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for key in ("executor_domain_defaults", "exact_action_policies", "prefix_action_policies"):
        if key not in data:
            raise ValueError(f"auth_model_registry_missing_key:{key}")
    return data


def reload_auth_model_registry() -> None:
    load_auth_model_registry.cache_clear()


def resolve_action_auth(
    agent: str | None,
    action: str,
    params: dict[str, Any] | None = None,
) -> AuthResolution:
    registry = load_auth_model_registry()
    normalized_action = _normalize(action)
    normalized_params = params or {}
    if not normalized_action:
        raise ValueError(f"auth_model_unknown_action:{agent}:{action}")

    exact_policy = (registry.get("exact_action_policies") or {}).get(normalized_action)
    if exact_policy:
        executor_domain = executor_route_for_action(agent, normalized_action)
        auth_class = _normalize_auth_class(exact_policy.get("auth_class"))
        return AuthResolution(
            auth_class=auth_class,
            prefer_delegated=_prefers_delegated(auth_class, exact_policy, normalized_params),
            requires_delegated_token=auth_class == "delegated",
            executor_domain=executor_domain,
            rule_source=f"exact:{normalized_action}",
        )

    for prefix, policy in (registry.get("prefix_action_policies") or {}).items():
        if normalized_action.startswith(str(prefix).lower()):
            executor_domain = executor_route_for_action(agent, normalized_action)
            auth_class = _normalize_auth_class(policy.get("auth_class"))
            return AuthResolution(
                auth_class=auth_class,
                prefer_delegated=_prefers_delegated(auth_class, policy, normalized_params),
                requires_delegated_token=auth_class == "delegated",
                executor_domain=executor_domain,
                rule_source=f"prefix:{prefix}",
            )

    if _CANONICAL_ACTION_RE.fullmatch(normalized_action):
        executor_domain = normalized_action.split(".", 1)[0]
    else:
        executor_domain = executor_route_for_action(agent, normalized_action)

    domain_defaults = registry.get("executor_domain_defaults") or {}
    policy = domain_defaults.get(executor_domain)
    if not policy:
        raise ValueError(f"auth_model_unknown_domain:{executor_domain}:{normalized_action}")

    auth_class = _normalize_auth_class(policy.get("auth_class"))
    return AuthResolution(
        auth_class=auth_class,
        prefer_delegated=_prefers_delegated(auth_class, policy, normalized_params),
        requires_delegated_token=auth_class == "delegated",
        executor_domain=executor_domain,
        rule_source=f"domain:{executor_domain}",
    )
