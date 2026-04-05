from __future__ import annotations

import json
from pathlib import Path

import yaml


def _load_h3_sources() -> tuple[dict, dict, dict, dict]:
    root = Path(__file__).resolve().parents[1]
    ai_team = json.loads((root / "registry" / "ai_team.json").read_text(encoding="utf-8"))
    persona_map = yaml.safe_load(
        (root / "registry" / "persona_capability_map.yaml").read_text(encoding="utf-8")
    )
    persona_registry = yaml.safe_load(
        (root / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    promoted_records = yaml.safe_load(
        (root / "registry" / "authoritative_digital_employee_records_v1.yaml").read_text(
            encoding="utf-8"
        )
    )["records"]
    return ai_team, persona_map, persona_registry, promoted_records


def test_h3_authoritative_surfaces_reconcile_to_staged_truth() -> None:
    ai_team, persona_map, persona_registry, promoted_records = _load_h3_sources()

    assert ai_team["total_agents"] == 59
    assert len(ai_team["departments"]) == 10
    assert persona_map["summary"] == {
        "total_personas": 59,
        "total_departments": 10,
        "current_registry_backed_personas": 34,
        "persona_contract_only_personas": 25,
        "non_authoritative_registry_agents": 0,
        "non_authoritative_registry_departments": [],
    }
    assert persona_registry["summary"] == {
        "total_personas": 59,
        "total_departments": 10,
        "active_personas": 34,
        "planned_personas": 25,
        "registry_backed_personas": 34,
        "persona_contract_only_personas": 25,
    }
    assert len(promoted_records) == 20


def test_h3_promoted_personas_are_authoritative_but_still_planned() -> None:
    ai_team, persona_map, persona_registry, promoted_records = _load_h3_sources()

    roster_members = {
        member["agent"]: member for members in ai_team["departments"].values() for member in members
    }
    for agent_id, record in promoted_records.items():
        roster_entry = roster_members[agent_id]
        persona_map_entry = persona_map["departments"][record["department"]]["personas"][agent_id]
        registry_entry = persona_registry["personas"][agent_id]

        assert roster_entry["name"] == record["display_name"]
        assert roster_entry["role"] == record["title"]
        assert roster_entry["manager"] == record["manager"]
        assert roster_entry["escalation_owner"] == record["escalation_owner"]

        assert persona_map_entry["display_name"] == record["display_name"]
        assert persona_map_entry["title"] == record["title"]
        assert persona_map_entry["coverage_status"] == "persona-contract-only"
        assert persona_map_entry["current_action_count"] == 0

        assert registry_entry["display_name"] == record["display_name"]
        assert registry_entry["department"] == record["department"]
        assert registry_entry["manager"] == record["manager"]
        assert registry_entry["escalation_owner"] == record["escalation_owner"]
        assert registry_entry["status"] == "planned"
        assert registry_entry["coverage_status"] == "persona-contract-only"
        assert registry_entry["allowed_actions"] == []
        assert registry_entry["allowed_domains"] == []
        assert registry_entry["action_count"] == 0
