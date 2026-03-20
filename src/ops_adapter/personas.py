from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .actions import executor_route_for_action


def _normalize_alias(value: str) -> str:
    return value.strip().lower()


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _normalize_alias(value)).strip("-")


def _humanize_identifier(value: str) -> str:
    return value.replace("-", " ").replace("_", " ").title()


def _default_ai_team_file() -> Path:
    registry_file = Path(os.getenv("REGISTRY_FILE", "./registry/agents.yaml")).resolve()
    return registry_file.with_name("ai_team.json")


def _load_ai_team(path: Path | None = None) -> dict[str, Any]:
    source = path or Path(os.getenv("AI_TEAM_FILE") or _default_ai_team_file())
    if not source.exists():
        return {}
    with source.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("ai_team registry must be a JSON object")
    return payload


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
            entries[agent] = {
                "department": str(department),
                "display_name": str(member.get("name") or _humanize_identifier(agent)),
                "title": str(
                    member.get("title") or member.get("role") or _humanize_identifier(agent)
                ),
                "manager": str(member.get("manager") or "unassigned"),
            }
    return entries


def _derive_allowed_domains(agent: str, responsibilities: list[str]) -> list[str]:
    domains: list[str] = []
    for action in responsibilities:
        try:
            route = executor_route_for_action(agent, action)
        except ValueError:
            continue
        if route not in domains:
            domains.append(route)
    return domains


def _approval_owner(agent_definition: dict[str, Any]) -> str:
    for rule in agent_definition.get("approval_rules", []) or []:
        approvers = [str(approver) for approver in (rule.get("approvers") or []) if approver]
        if approvers:
            return approvers[0]
    return "unassigned"


def _persona_alias_candidates(persona: dict[str, Any]) -> set[str]:
    display_name = str(persona.get("display_name") or "")
    candidates = {
        _normalize_alias(str(persona.get("canonical_agent") or "")),
        _normalize_alias(str(persona.get("persona_id") or "")),
        _normalize_alias(display_name),
        _slugify(display_name),
    }
    return {candidate for candidate in candidates if candidate}


def build_persona_registry(
    registry: dict[str, Any], ai_team: dict[str, Any] | None = None
) -> dict[str, dict[str, Any]]:
    agent_definitions = registry.get("agents", {}) or {}
    team_entries = _team_entries(ai_team or {})

    personas: dict[str, dict[str, Any]] = {}
    alias_candidates: dict[str, set[str]] = {}

    for canonical_agent, agent_definition in agent_definitions.items():
        responsibilities = [
            str(action) for action in (agent_definition.get("allowed_actions") or [])
        ]
        team_entry = team_entries.get(canonical_agent, {})
        display_name = str(team_entry.get("display_name") or _humanize_identifier(canonical_agent))
        persona = {
            "persona_id": canonical_agent,
            "canonical_agent": canonical_agent,
            "display_name": display_name,
            "slug": _slugify(display_name),
            "department": str(team_entry.get("department") or "unassigned"),
            "title": str(team_entry.get("title") or _humanize_identifier(canonical_agent)),
            "manager": str(team_entry.get("manager") or "unassigned"),
            "responsibilities": responsibilities,
            "allowed_domains": _derive_allowed_domains(canonical_agent, responsibilities),
            "approval_owner": _approval_owner(agent_definition),
            "status": "active",
            "external_presence_policy": "internal_only",
        }
        personas[canonical_agent] = persona
        for alias in _persona_alias_candidates(persona):
            alias_candidates.setdefault(alias, set()).add(canonical_agent)

    for canonical_agent, team_entry in team_entries.items():
        if canonical_agent in personas:
            continue
        display_name = str(team_entry.get("display_name") or _humanize_identifier(canonical_agent))
        persona = {
            "persona_id": canonical_agent,
            "canonical_agent": canonical_agent,
            "display_name": display_name,
            "slug": _slugify(display_name),
            "department": str(team_entry.get("department") or "unassigned"),
            "title": str(team_entry.get("title") or _humanize_identifier(canonical_agent)),
            "manager": str(team_entry.get("manager") or "unassigned"),
            "responsibilities": [],
            "allowed_domains": [],
            "approval_owner": "unassigned",
            "status": "inactive",
            "external_presence_policy": "internal_only",
        }
        personas[canonical_agent] = persona
        for alias in _persona_alias_candidates(persona):
            alias_candidates.setdefault(alias, set()).add(canonical_agent)

    for canonical_agent, persona in personas.items():
        aliases = []
        for alias in _persona_alias_candidates(persona):
            if alias == _normalize_alias(canonical_agent) or alias_candidates.get(alias) == {
                canonical_agent
            }:
                aliases.append(alias)
        persona["aliases"] = sorted(set(aliases))

    return personas


def load_persona_registry(
    registry: dict[str, Any], *, path: str | os.PathLike[str] | None = None
) -> dict[str, dict[str, Any]]:
    source = Path(path) if path is not None else None
    ai_team = _load_ai_team(source)
    return build_persona_registry(registry, ai_team)


def project_persona_context(persona: dict[str, Any]) -> dict[str, Any]:
    return {
        "persona_id": persona.get("persona_id"),
        "canonical_agent": persona.get("canonical_agent"),
        "display_name": persona.get("display_name"),
        "slug": persona.get("slug"),
        "department": persona.get("department"),
        "title": persona.get("title"),
        "manager": persona.get("manager"),
        "responsibilities": list(persona.get("responsibilities") or []),
        "allowed_domains": list(persona.get("allowed_domains") or []),
        "approval_owner": persona.get("approval_owner"),
        "status": persona.get("status"),
        "external_presence_policy": persona.get("external_presence_policy"),
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
