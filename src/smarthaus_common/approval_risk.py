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


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


def _matrix_path() -> Path:
    override = _normalize(os.getenv("APPROVAL_RISK_MATRIX_FILE"))
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "registry" / "approval_risk_matrix_v2.yaml"


def _persona_map_path() -> Path:
    override = _normalize(os.getenv("PERSONA_CAPABILITY_MAP_FILE"))
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "registry" / "persona_capability_map.yaml"


@dataclass(frozen=True)
class ApprovalRiskResolution:
    risk_class: str
    approval_profile: str
    approval_required: bool
    executor_domain: str
    rule_source: str
    approvers: tuple[str, ...]


def _risk_from_approval_profile(profile: str) -> str:
    mapping = {
        "low-observe-create": "low",
        "medium-operational": "medium",
        "high-impact": "high",
        "critical-regulated": "critical",
    }
    return mapping.get(profile, "medium")


def _resolve_executor_domain(
    agent: str | None, action: str, policy: dict[str, Any] | None = None
) -> str:
    explicit_domain = _normalize((policy or {}).get("executor_domain"))
    if explicit_domain:
        return explicit_domain
    if _CANONICAL_ACTION_RE.fullmatch(action):
        return action.split(".", 1)[0]
    return executor_route_for_action(agent, action)


def _to_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    try:
        return float(str(value))
    except Exception:
        return None


def _condition_matches(condition: dict[str, Any], params: dict[str, Any]) -> bool:
    field = str(condition.get("field") or "").strip()
    operator = _normalize(condition.get("operator"))
    expected = condition.get("value")
    actual = params.get(field)

    if operator == "gt":
        actual_number = _to_number(actual)
        expected_number = _to_number(expected)
        return (
            actual_number is not None
            and expected_number is not None
            and actual_number > expected_number
        )
    if operator == "gte":
        actual_number = _to_number(actual)
        expected_number = _to_number(expected)
        return (
            actual_number is not None
            and expected_number is not None
            and actual_number >= expected_number
        )
    if operator == "eq":
        return actual == expected
    if operator == "truthy":
        return bool(actual)
    if operator == "not_empty":
        return actual not in (None, "", [], {})
    raise ValueError(f"approval_risk_unknown_operator:{operator}")


def _evaluate_approval_requirement(policy: dict[str, Any], params: dict[str, Any]) -> bool:
    requirement = _normalize(policy.get("approval_requirement"))
    if not requirement or requirement == "never":
        return False
    if requirement == "always":
        return True
    if requirement != "conditional":
        raise ValueError(f"approval_risk_unknown_requirement:{requirement}")

    conditions = list(policy.get("conditions") or [])
    if not conditions:
        return False

    mode = _normalize(policy.get("condition_mode")) or "any"
    matches = [_condition_matches(condition, params) for condition in conditions]
    if mode == "all":
        return all(matches)
    return any(matches)


@lru_cache(maxsize=1)
def load_approval_risk_registry() -> dict[str, Any]:
    path = _matrix_path()
    if not path.exists():
        raise FileNotFoundError(f"approval_risk_registry_missing:{path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for key in (
        "approval_profiles",
        "risk_classes",
        "executor_domain_defaults",
        "exact_action_policies",
        "prefix_action_policies",
    ):
        if key not in data:
            raise ValueError(f"approval_risk_registry_missing_key:{key}")
    return data


@lru_cache(maxsize=1)
def load_persona_approval_profiles() -> dict[str, str]:
    path = _persona_map_path()
    if not path.exists():
        return {}

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    departments = data.get("departments") or {}
    flattened: dict[str, str] = {}
    for department in departments.values():
        personas = (department or {}).get("personas") or {}
        for persona_id, persona in personas.items():
            profile = _normalize((persona or {}).get("approval_profile"))
            if profile:
                flattened[_normalize(str(persona_id))] = profile
    return flattened


def reload_approval_risk_registry() -> None:
    load_approval_risk_registry.cache_clear()
    load_persona_approval_profiles.cache_clear()


def resolve_action_approval_risk(
    agent: str | None,
    action: str,
    params: dict[str, Any] | None = None,
) -> ApprovalRiskResolution:
    registry = load_approval_risk_registry()
    normalized_action = _normalize(action)
    normalized_agent = _normalize(agent)
    normalized_params = params or {}
    if not normalized_action:
        raise ValueError(f"approval_risk_unknown_action:{agent}:{action}")

    exact_policy = (registry.get("exact_action_policies") or {}).get(normalized_action)
    if exact_policy:
        executor_domain = _resolve_executor_domain(agent, normalized_action, exact_policy)
        profile = _normalize(
            exact_policy.get("approval_profile")
        ) or load_persona_approval_profiles().get(
            normalized_agent,
            "medium-operational",
        )
        return ApprovalRiskResolution(
            risk_class=_normalize(exact_policy.get("risk_class"))
            or _risk_from_approval_profile(profile),
            approval_profile=profile,
            approval_required=_evaluate_approval_requirement(exact_policy, normalized_params),
            executor_domain=executor_domain,
            rule_source=f"exact:{normalized_action}",
            approvers=tuple(str(item) for item in (exact_policy.get("approvers") or [])),
        )

    prefix_policies = registry.get("prefix_action_policies") or {}
    for prefix in sorted(prefix_policies.keys(), key=len, reverse=True):
        if normalized_action.startswith(str(prefix).lower()):
            policy = prefix_policies[prefix] or {}
            executor_domain = _resolve_executor_domain(agent, normalized_action, policy)
            profile = _normalize(
                policy.get("approval_profile")
            ) or load_persona_approval_profiles().get(
                normalized_agent,
                "medium-operational",
            )
            return ApprovalRiskResolution(
                risk_class=_normalize(policy.get("risk_class"))
                or _risk_from_approval_profile(profile),
                approval_profile=profile,
                approval_required=_evaluate_approval_requirement(policy, normalized_params),
                executor_domain=executor_domain,
                rule_source=f"prefix:{prefix}",
                approvers=tuple(str(item) for item in (policy.get("approvers") or [])),
            )

    executor_domain = _resolve_executor_domain(agent, normalized_action)

    defaults = (registry.get("executor_domain_defaults") or {}).get(executor_domain)
    if not defaults:
        raise ValueError(f"approval_risk_unknown_domain:{executor_domain}:{normalized_action}")

    profile = _normalize(defaults.get("approval_profile")) or load_persona_approval_profiles().get(
        normalized_agent,
        "medium-operational",
    )
    return ApprovalRiskResolution(
        risk_class=_normalize(defaults.get("risk_class")) or _risk_from_approval_profile(profile),
        approval_profile=profile,
        approval_required=_evaluate_approval_requirement(defaults, normalized_params),
        executor_domain=executor_domain,
        rule_source=f"domain:{executor_domain}",
        approvers=tuple(str(item) for item in (defaults.get("approvers") or [])),
    )
