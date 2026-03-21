from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def _load_contract() -> dict:
    return yaml.safe_load(Path("registry/ucp_delegation_contract_v1.yaml").read_text(encoding="utf-8"))


def test_e7a_delegation_contract_has_six_ordered_phases() -> None:
    contract = _load_contract()
    phases = contract["delegation_phases"]
    assert len(phases) == 6
    assert [p["order"] for p in phases] == [1, 2, 3, 4, 5, 6]
    assert [p["id"] for p in phases] == [
        "intent_capture",
        "persona_resolution",
        "risk_assessment",
        "approval_gating",
        "executor_routing",
        "audited_execution",
    ]


def test_e7a_delegation_phases_have_required_fields() -> None:
    contract = _load_contract()
    for phase in contract["delegation_phases"]:
        assert "id" in phase
        assert "description" in phase
        assert "inputs" in phase
        assert "outputs" in phase
        assert "failure_mode" in phase


def test_e7a_governance_rules_complete() -> None:
    contract = _load_contract()
    rules = contract["governance_rules"]
    expected = {
        "fail_closed",
        "audit_completeness",
        "contract_only_handling",
        "approval_integrity",
        "idempotency",
    }
    assert set(rules.keys()) == expected


def test_e7a_kpi_persona_counts_match_registry() -> None:
    contract = _load_contract()
    registry = yaml.safe_load(
        Path("registry/persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    personas = registry["personas"]
    total = len(personas)
    contract_only = sum(
        1 for p in personas.values() if p.get("coverage_status") == "persona-contract-only"
    )
    registry_backed = sum(
        1 for p in personas.values() if p.get("coverage_status") == "registry-backed"
    )

    kpis = contract["kpis"]
    assert kpis["supported_persona_count"] == total
    assert kpis["contract_only_persona_count"] == contract_only
    assert kpis["registry_backed_persona_count"] == registry_backed
    assert contract_only + registry_backed == total
