from __future__ import annotations

from pathlib import Path

import yaml


def _load_contract() -> dict:
    return yaml.safe_load(
        Path("registry/executive_oversight_contract_v1.yaml").read_text(encoding="utf-8")
    )


def test_e7e_oversight_has_five_queries() -> None:
    contract = _load_contract()
    queries = contract["oversight_queries"]
    assert len(queries) == 5
    assert [q["id"] for q in queries] == [
        "workforce_status",
        "department_status",
        "persona_status",
        "delegation_audit",
        "risk_summary",
    ]


def test_e7e_intervention_primitives_complete() -> None:
    contract = _load_contract()
    interventions = contract["intervention_primitives"]
    assert len(interventions) == 5
    assert [i["id"] for i in interventions] == [
        "pause_persona",
        "pause_department",
        "redirect_task",
        "override_decision",
        "emergency_halt",
    ]


def test_e7e_intervention_approval_and_reversibility() -> None:
    contract = _load_contract()
    interventions = {i["id"]: i for i in contract["intervention_primitives"]}
    assert interventions["pause_persona"]["reversible"] is True
    assert interventions["override_decision"]["reversible"] is False
    assert interventions["emergency_halt"]["approval_required"] == "executive_dual"


def test_e7e_escalation_paths_complete() -> None:
    contract = _load_contract()
    paths = contract["escalation_paths"]
    expected = {
        "persona_to_department",
        "department_to_executive",
        "executive_to_audit",
    }
    assert set(paths.keys()) == expected


def test_e7e_governance_rules_complete() -> None:
    contract = _load_contract()
    rules = contract["governance_rules"]
    expected = {
        "visibility_completeness",
        "intervention_audit",
        "intervention_approval",
        "escalation_determinism",
        "no_silent_override",
    }
    assert set(rules.keys()) == expected
