from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from smarthaus_common.executor_routing import executor_route_for_action

REQUIRED_PERSONA_FIELDS = (
    "persona_id",
    "canonical_agent",
    "display_name",
    "slug",
    "department",
    "title",
    "manager",
    "escalation_owner",
    "responsibilities",
    "allowed_actions",
    "allowed_domains",
    "approval_owner",
    "approval_profile",
    "risk_tier",
    "coverage_status",
    "status",
    "external_presence_policy",
    "aliases",
    "action_count",
)


def _normalize_alias(value: str) -> str:
    return value.strip().lower()


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _normalize_alias(value)).strip("-")


def _humanize_identifier(value: str) -> str:
    return value.replace("-", " ").replace("_", " ").title()


def _load_yaml_object(source: Path, label: str) -> dict[str, Any]:
    if not source.exists():
        return {}
    with source.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a YAML object")
    return payload


def _default_ai_team_file() -> Path:
    registry_file = Path(os.getenv("REGISTRY_FILE", "./registry/agents.yaml")).resolve()
    return registry_file.with_name("ai_team.json")


def _default_persona_map_file() -> Path:
    registry_file = Path(os.getenv("REGISTRY_FILE", "./registry/agents.yaml")).resolve()
    return registry_file.with_name("persona_capability_map.yaml")


def _default_persona_registry_file() -> Path:
    registry_file = Path(os.getenv("REGISTRY_FILE", "./registry/agents.yaml")).resolve()
    return registry_file.with_name("persona_registry_v2.yaml")


def _load_ai_team(path: Path | None = None) -> dict[str, Any]:
    source = path or Path(os.getenv("AI_TEAM_FILE") or _default_ai_team_file())
    if not source.exists():
        return {}
    with source.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("ai_team registry must be a JSON object")
    return payload


def _load_persona_capability_map(path: Path | None = None) -> dict[str, Any]:
    source = path or Path(os.getenv("PERSONA_CAPABILITY_MAP_FILE") or _default_persona_map_file())
    return _load_yaml_object(source, "persona capability map")


def _load_persona_registry_payload(path: Path | None = None) -> dict[str, Any]:
    source = path or Path(os.getenv("PERSONA_REGISTRY_FILE") or _default_persona_registry_file())
    return _load_yaml_object(source, "persona registry")


def _department_manager_token(department: str) -> str:
    return f"department-lead:{department}"


def _department_approval_token(department: str) -> str:
    return f"department-owner:{department}"


def _team_entries(ai_team: dict[str, Any]) -> dict[str, dict[str, Any]]:
    departments = ai_team.get("departments")
    if not isinstance(departments, dict):
        return {}

    entries: dict[str, dict[str, Any]] = {}
    for department, members in departments.items():
        if not isinstance(members, list):
            continue
        for member in members:
            if not isinstance(member, dict):
                continue
            agent = str(member.get("agent") or "").strip()
            if not agent:
                continue
            manager = str(member.get("manager") or _department_manager_token(str(department)))
            entries[agent] = {
                "department": str(department),
                "display_name": str(member.get("name") or _humanize_identifier(agent)),
                "title": str(
                    member.get("title") or member.get("role") or _humanize_identifier(agent)
                ),
                "manager": manager,
                "escalation_owner": str(member.get("escalation_owner") or manager),
            }
    return entries


def _persona_map_entries(persona_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    departments = persona_map.get("departments")
    if not isinstance(departments, dict):
        return {}

    entries: dict[str, dict[str, Any]] = {}
    for department, payload in departments.items():
        if not isinstance(payload, dict):
            continue
        personas = payload.get("personas") or {}
        if not isinstance(personas, dict):
            continue
        for persona_id, details in personas.items():
            if not isinstance(details, dict):
                continue
            entries[str(persona_id)] = {
                "department": str(department),
                "risk_tier": str(details.get("current_risk_tier") or "low"),
                "approval_profile": str(details.get("approval_profile") or "low-observe-create"),
                "coverage_status": str(details.get("coverage_status") or "persona-contract-only"),
                "workload_families": [
                    str(item) for item in (details.get("workload_families") or []) if item
                ],
                "capability_families": [
                    str(item) for item in (details.get("capability_families") or []) if item
                ],
            }
    return entries


def _derive_allowed_domains(agent: str, allowed_actions: list[str]) -> list[str]:
    domains: list[str] = []
    for action in allowed_actions:
        try:
            route = executor_route_for_action(agent, action)
        except ValueError:
            continue
        if route and route not in domains:
            domains.append(route)
    return domains


def _approval_owner(agent_definition: dict[str, Any], department: str) -> str:
    for rule in agent_definition.get("approval_rules", []) or []:
        approvers = [str(approver) for approver in (rule.get("approvers") or []) if approver]
        if approvers:
            return approvers[0]
    return _department_approval_token(department)


def _persona_status(coverage_status: str) -> str:
    if coverage_status == "registry-backed":
        return "active"
    if coverage_status == "persona-contract-only":
        return "planned"
    return "inactive"


def _persona_alias_candidates(persona_id: str, display_name: str) -> set[str]:
    candidates = {
        _normalize_alias(persona_id),
        _normalize_alias(display_name),
        _slugify(display_name),
    }
    return {candidate for candidate in candidates if candidate}


def _legacy_build_persona_registry(
    registry: dict[str, Any], ai_team: dict[str, Any] | None = None
) -> dict[str, dict[str, Any]]:
    agent_definitions = registry.get("agents", {}) or {}
    team_entries = _team_entries(ai_team or {})

    personas: dict[str, dict[str, Any]] = {}
    alias_candidates: dict[str, set[str]] = {}

    for canonical_agent, agent_definition in agent_definitions.items():
        allowed_actions = [
            str(action) for action in (agent_definition.get("allowed_actions") or [])
        ]
        team_entry = team_entries.get(canonical_agent, {})
        display_name = str(team_entry.get("display_name") or _humanize_identifier(canonical_agent))
        department = str(team_entry.get("department") or "unassigned")
        persona = {
            "persona_id": canonical_agent,
            "canonical_agent": canonical_agent,
            "display_name": display_name,
            "slug": _slugify(display_name),
            "department": department,
            "title": str(team_entry.get("title") or _humanize_identifier(canonical_agent)),
            "manager": str(team_entry.get("manager") or _department_manager_token(department)),
            "escalation_owner": str(
                team_entry.get("escalation_owner") or _department_manager_token(department)
            ),
            "responsibilities": allowed_actions,
            "allowed_actions": allowed_actions,
            "allowed_domains": _derive_allowed_domains(canonical_agent, allowed_actions),
            "approval_owner": _approval_owner(agent_definition, department),
            "approval_profile": "high-impact",
            "risk_tier": str(agent_definition.get("risk_tier") or "medium"),
            "coverage_status": "legacy-derived",
            "status": "active",
            "external_presence_policy": "internal_only",
            "aliases": [],
            "action_count": len(allowed_actions),
            "workload_families": [],
            "capability_families": [],
        }
        personas[canonical_agent] = persona
        for alias in _persona_alias_candidates(canonical_agent, display_name):
            alias_candidates.setdefault(alias, set()).add(canonical_agent)

    for canonical_agent, team_entry in team_entries.items():
        if canonical_agent in personas:
            continue
        display_name = str(team_entry.get("display_name") or _humanize_identifier(canonical_agent))
        department = str(team_entry.get("department") or "unassigned")
        persona = {
            "persona_id": canonical_agent,
            "canonical_agent": canonical_agent,
            "display_name": display_name,
            "slug": _slugify(display_name),
            "department": department,
            "title": str(team_entry.get("title") or _humanize_identifier(canonical_agent)),
            "manager": str(team_entry.get("manager") or _department_manager_token(department)),
            "escalation_owner": str(
                team_entry.get("escalation_owner") or _department_manager_token(department)
            ),
            "responsibilities": [],
            "allowed_actions": [],
            "allowed_domains": [],
            "approval_owner": _department_approval_token(department),
            "approval_profile": "low-observe-create",
            "risk_tier": "low",
            "coverage_status": "legacy-derived",
            "status": "planned",
            "external_presence_policy": "internal_only",
            "aliases": [],
            "action_count": 0,
            "workload_families": [],
            "capability_families": [],
        }
        personas[canonical_agent] = persona
        for alias in _persona_alias_candidates(canonical_agent, display_name):
            alias_candidates.setdefault(alias, set()).add(canonical_agent)

    for canonical_agent, persona in personas.items():
        aliases = []
        for alias in _persona_alias_candidates(
            canonical_agent, str(persona.get("display_name") or "")
        ):
            if alias == _normalize_alias(canonical_agent) or alias_candidates.get(alias) == {
                canonical_agent
            }:
                aliases.append(alias)
        persona["aliases"] = sorted(set(aliases))

    return personas


def build_authoritative_persona_registry_document(
    registry: dict[str, Any],
    ai_team: dict[str, Any],
    persona_map: dict[str, Any],
) -> dict[str, Any]:
    team_entries = _team_entries(ai_team)
    if not team_entries:
        raise ValueError("authoritative_ai_team_missing")

    map_entries = _persona_map_entries(persona_map)
    if not map_entries:
        raise ValueError("authoritative_persona_map_missing")

    agent_definitions = registry.get("agents", {}) or {}
    personas: dict[str, dict[str, Any]] = {}
    alias_owner: dict[str, str] = {}

    for persona_id in sorted(team_entries):
        team_entry = team_entries[persona_id]
        map_entry = map_entries.get(persona_id)
        if not map_entry:
            raise ValueError(f"persona_map_missing:{persona_id}")
        department = str(team_entry["department"])
        agent_definition = agent_definitions.get(persona_id, {})
        allowed_actions = [
            str(action) for action in (agent_definition.get("allowed_actions") or []) if action
        ]
        coverage_status = str(map_entry["coverage_status"])
        display_name = str(team_entry["display_name"])
        aliases = sorted(_persona_alias_candidates(persona_id, display_name))
        persona = {
            "persona_id": persona_id,
            "canonical_agent": persona_id,
            "display_name": display_name,
            "slug": _slugify(display_name),
            "department": department,
            "title": str(team_entry["title"]),
            "manager": str(team_entry["manager"]),
            "escalation_owner": str(team_entry["escalation_owner"]),
            "responsibilities": list(map_entry["capability_families"]),
            "allowed_actions": allowed_actions,
            "allowed_domains": _derive_allowed_domains(persona_id, allowed_actions),
            "approval_owner": _approval_owner(agent_definition, department),
            "approval_profile": str(map_entry["approval_profile"]),
            "risk_tier": str(map_entry["risk_tier"]),
            "coverage_status": coverage_status,
            "status": _persona_status(coverage_status),
            "external_presence_policy": "internal_only",
            "aliases": aliases,
            "action_count": len(allowed_actions),
            "workload_families": list(map_entry["workload_families"]),
            "capability_families": list(map_entry["capability_families"]),
        }
        personas[persona_id] = persona
        for alias in aliases:
            owner = alias_owner.setdefault(alias, persona_id)
            if owner != persona_id:
                raise ValueError(f"persona_alias_collision:{alias}:{owner}:{persona_id}")

    payload = {
        "version": "2.0.0",
        "last_updated": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "authority": {
            "roster": "registry/ai_team.json",
            "registry": "registry/agents.yaml",
            "persona_map": "registry/persona_capability_map.yaml",
        },
        "summary": {
            "total_personas": len(personas),
            "total_departments": len({persona["department"] for persona in personas.values()}),
            "active_personas": sum(
                1 for persona in personas.values() if persona.get("status") == "active"
            ),
            "planned_personas": sum(
                1 for persona in personas.values() if persona.get("status") == "planned"
            ),
            "registry_backed_personas": sum(
                1
                for persona in personas.values()
                if persona.get("coverage_status") == "registry-backed"
            ),
            "persona_contract_only_personas": sum(
                1
                for persona in personas.values()
                if persona.get("coverage_status") == "persona-contract-only"
            ),
        },
        "required_fields": list(REQUIRED_PERSONA_FIELDS),
        "status_definitions": {
            "active": "Persona is authoritative and currently backed by implemented runtime actions.",
            "planned": "Persona is authoritative but still waiting on later action-surface implementation.",
            "inactive": "Persona is explicitly unavailable for delegation or execution.",
        },
        "external_presence_policies": {
            "internal_only": "Persona may only be used for internal delegation and non-public channels.",
            "review_required": "Persona may operate in constrained external channels only with human review.",
            "public_disclosed": "Persona may operate publicly only with explicit AI disclosure and brand controls.",
        },
        "personas": personas,
    }
    validate_persona_registry_document(payload)
    return payload


def validate_persona_registry_document(payload: dict[str, Any]) -> None:
    required_fields = [
        str(field) for field in (payload.get("required_fields") or REQUIRED_PERSONA_FIELDS)
    ]
    personas = payload.get("personas")
    if not isinstance(personas, dict) or not personas:
        raise ValueError("persona_registry_missing_personas")

    summary = payload.get("summary") or {}
    if not isinstance(summary, dict):
        raise ValueError("persona_registry_summary_invalid")

    alias_owner: dict[str, str] = {}
    departments: set[str] = set()
    active_count = 0
    planned_count = 0
    registry_backed = 0
    contract_only = 0

    for persona_id, persona in personas.items():
        if not isinstance(persona, dict):
            raise ValueError(f"persona_registry_entry_invalid:{persona_id}")
        missing = [field for field in required_fields if field not in persona]
        if missing:
            raise ValueError(f"persona_registry_missing_fields:{persona_id}:{','.join(missing)}")
        if str(persona.get("persona_id")) != str(persona_id):
            raise ValueError(f"persona_registry_id_mismatch:{persona_id}")
        if str(persona.get("canonical_agent") or "") != str(persona_id):
            raise ValueError(f"persona_registry_canonical_agent_mismatch:{persona_id}")
        department = str(persona.get("department") or "")
        if not department:
            raise ValueError(f"persona_registry_department_missing:{persona_id}")
        departments.add(department)
        allowed_actions = [
            str(action) for action in (persona.get("allowed_actions") or []) if action
        ]
        if int(persona.get("action_count") or 0) != len(allowed_actions):
            raise ValueError(f"persona_registry_action_count_mismatch:{persona_id}")
        aliases = [str(alias) for alias in (persona.get("aliases") or []) if alias]
        if _normalize_alias(persona_id) not in aliases:
            raise ValueError(f"persona_registry_missing_canonical_alias:{persona_id}")
        for alias in aliases:
            owner = alias_owner.setdefault(alias, str(persona_id))
            if owner != str(persona_id):
                raise ValueError(f"persona_registry_alias_collision:{alias}:{owner}:{persona_id}")
        coverage_status = str(persona.get("coverage_status") or "")
        status = str(persona.get("status") or "")
        if coverage_status == "registry-backed":
            registry_backed += 1
            if status != "active":
                raise ValueError(f"persona_registry_registry_backed_not_active:{persona_id}")
        elif coverage_status == "persona-contract-only":
            contract_only += 1
            if status != "planned":
                raise ValueError(f"persona_registry_contract_only_not_planned:{persona_id}")
            if allowed_actions:
                raise ValueError(f"persona_registry_contract_only_has_actions:{persona_id}")
        if status == "active":
            active_count += 1
        elif status == "planned":
            planned_count += 1

    expected_total = len(personas)
    if int(summary.get("total_personas") or -1) != expected_total:
        raise ValueError("persona_registry_total_persona_count_mismatch")
    if int(summary.get("total_departments") or -1) != len(departments):
        raise ValueError("persona_registry_total_department_count_mismatch")
    if int(summary.get("active_personas") or -1) != active_count:
        raise ValueError("persona_registry_active_count_mismatch")
    if int(summary.get("planned_personas") or -1) != planned_count:
        raise ValueError("persona_registry_planned_count_mismatch")
    if int(summary.get("registry_backed_personas") or -1) != registry_backed:
        raise ValueError("persona_registry_registry_backed_count_mismatch")
    if int(summary.get("persona_contract_only_personas") or -1) != contract_only:
        raise ValueError("persona_registry_contract_only_count_mismatch")


def build_persona_registry(
    registry: dict[str, Any],
    ai_team: dict[str, Any] | None = None,
    persona_map: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    if ai_team is not None and persona_map is not None:
        return build_authoritative_persona_registry_document(
            registry,
            ai_team=ai_team,
            persona_map=persona_map,
        )["personas"]
    return _legacy_build_persona_registry(registry, ai_team)


def load_persona_registry(
    registry: dict[str, Any], *, path: str | os.PathLike[str] | None = None
) -> dict[str, dict[str, Any]]:
    source = Path(path) if path is not None else None
    payload = _load_persona_registry_payload(source)
    if payload:
        validate_persona_registry_document(payload)
        personas = payload.get("personas") or {}
        return {str(key): value for key, value in personas.items() if isinstance(value, dict)}

    ai_team = _load_ai_team()
    persona_map = _load_persona_capability_map()
    if ai_team and persona_map:
        return build_authoritative_persona_registry_document(
            registry,
            ai_team=ai_team,
            persona_map=persona_map,
        )["personas"]
    return _legacy_build_persona_registry(registry, ai_team)


def project_persona_context(persona: dict[str, Any]) -> dict[str, Any]:
    return {
        "persona_id": persona.get("persona_id"),
        "canonical_agent": persona.get("canonical_agent"),
        "display_name": persona.get("display_name"),
        "slug": persona.get("slug"),
        "department": persona.get("department"),
        "title": persona.get("title"),
        "manager": persona.get("manager"),
        "escalation_owner": persona.get("escalation_owner"),
        "responsibilities": list(persona.get("responsibilities") or []),
        "allowed_actions": list(persona.get("allowed_actions") or []),
        "allowed_domains": list(persona.get("allowed_domains") or []),
        "approval_owner": persona.get("approval_owner"),
        "approval_profile": persona.get("approval_profile"),
        "risk_tier": persona.get("risk_tier"),
        "coverage_status": persona.get("coverage_status"),
        "status": persona.get("status"),
        "external_presence_policy": persona.get("external_presence_policy"),
        "action_count": int(persona.get("action_count") or 0),
        "workload_families": list(persona.get("workload_families") or []),
        "capability_families": list(persona.get("capability_families") or []),
    }


def resolve_persona_target(
    target: str, personas: dict[str, dict[str, Any]]
) -> tuple[str, dict[str, Any]]:
    normalized_target = _normalize_alias(target)
    slug_target = _slugify(target)
    for canonical_agent, persona in personas.items():
        aliases = {str(alias) for alias in (persona.get("aliases") or []) if alias}
        if normalized_target in aliases or slug_target in aliases:
            return canonical_agent, project_persona_context(persona)
    raise ValueError(f"persona_not_found:{target}")
