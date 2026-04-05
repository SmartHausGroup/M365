from __future__ import annotations

import json
from pathlib import Path

import yaml
from ops_adapter.personas import (
    build_authoritative_persona_registry_document,
    load_persona_registry,
    resolve_persona_target,
)


def _load_repo_sources() -> tuple[dict, dict, dict]:
    root = Path(__file__).resolve().parents[1]
    with (root / "registry" / "agents.yaml").open(encoding="utf-8") as handle:
        registry = yaml.safe_load(handle)
    with (root / "registry" / "ai_team.json").open(encoding="utf-8") as handle:
        ai_team = json.load(handle)
    with (root / "registry" / "persona_capability_map.yaml").open(encoding="utf-8") as handle:
        persona_map = yaml.safe_load(handle)
    return registry, ai_team, persona_map


def test_e5a_authoritative_persona_registry_is_roster_bound() -> None:
    registry, ai_team, persona_map = _load_repo_sources()
    payload = build_authoritative_persona_registry_document(registry, ai_team, persona_map)

    assert payload["summary"]["total_personas"] == 59
    assert payload["summary"]["total_departments"] == 10
    assert payload["summary"]["active_personas"] == 34
    assert payload["summary"]["planned_personas"] == 25
    assert payload["summary"]["registry_backed_personas"] == 34
    assert payload["summary"]["persona_contract_only_personas"] == 25
    assert payload["personas"]["teams-manager"]["status"] == "planned"
    assert payload["personas"]["teams-manager"]["allowed_actions"] == []
    assert payload["personas"]["teams-manager"]["action_count"] == 0
    assert payload["personas"]["calendar-management-agent"]["status"] == "planned"
    assert payload["personas"]["m365-administrator"]["status"] == "active"
    assert payload["personas"]["ai-engineer"]["status"] == "active"


def test_e5a_load_persona_registry_prefers_authoritative_registry_file(tmp_path: Path) -> None:
    registry, ai_team, persona_map = _load_repo_sources()
    payload = build_authoritative_persona_registry_document(registry, ai_team, persona_map)

    persona_registry_path = tmp_path / "persona_registry_v2.yaml"
    persona_registry_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )

    personas = load_persona_registry(registry, path=persona_registry_path)

    assert len(personas) == 59
    assert personas["teams-manager"]["display_name"] == "Alicia Nguyen"
    assert personas["teams-manager"]["status"] == "planned"
    assert personas["website-manager"]["display_name"] == "Elena Rodriguez"
    assert personas["hr-generalist"]["approval_profile"] == "critical-regulated"


def test_e5a_resolve_persona_target_uses_authoritative_aliases() -> None:
    registry, ai_team, persona_map = _load_repo_sources()
    personas = build_authoritative_persona_registry_document(registry, ai_team, persona_map)[
        "personas"
    ]

    canonical_agent, persona = resolve_persona_target("Elena Rodriguez", personas)
    assert canonical_agent == "website-manager"
    assert persona["display_name"] == "Elena Rodriguez"

    canonical_agent, persona = resolve_persona_target("marcus-chen", personas)
    assert canonical_agent == "m365-administrator"
    assert persona["department"] == "operations"

    canonical_agent, persona = resolve_persona_target("Alicia Nguyen", personas)
    assert canonical_agent == "teams-manager"
    assert persona["department"] == "communication"
