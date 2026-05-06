from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_ucp_m365_inference_binding import build_binding


def test_ucp_binding_projects_all_authoritative_personas() -> None:
    binding = build_binding()

    assert binding["summary"]["persona_count"] == 59
    assert binding["summary"]["active_personas"] == 54
    assert binding["summary"]["planned_personas"] == 5
    assert binding["summary"]["source_total_agents"] == 59
    assert binding["summary"]["source_registry_agents"] == 59


def test_ucp_binding_has_contract_for_every_persona() -> None:
    binding = build_binding()
    personas = binding["personas"]

    assert len(personas) == 59
    for persona in personas:
        contract = persona["contract"]
        assert contract["contract_id"] == f"m365-agent-contract:{persona['agent_id']}:v1"
        assert contract["identity"]["person_name"] == persona["person_name"]
        assert contract["access_boundary"]["denied_by_default"] is True
        assert "UCP Execute" in contract["approval_profile"]["mutations_require"]
        assert contract["said_scope"]["refuse"]


def test_active_personas_are_executable_and_planned_personas_are_visible_only() -> None:
    binding = build_binding()

    active = [persona for persona in binding["personas"] if persona["status"] == "active"]
    planned = [persona for persona in binding["personas"] if persona["status"] == "planned"]
    assert len(active) == 54
    assert len(planned) == 5
    assert all(persona["allowed_actions"] for persona in active)
    assert all(not persona["allowed_actions"] for persona in planned)
    assert {persona["coverage_status"] for persona in planned} == {"persona-contract-only"}


def test_generated_binding_is_deterministic(tmp_path: Path) -> None:
    first = json.dumps(build_binding(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(build_binding(), sort_keys=True, separators=(",", ":"))

    assert first == second
