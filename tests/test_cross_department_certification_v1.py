"""Tests for cross-department workflow certification contract v1."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "cross_department_certification_v1.yaml").read_text(
            encoding="utf-8"
        )
    )


def test_e8d_certification_has_four_ordered_phases() -> None:
    contract = _load_contract()
    phases = contract["certification_phases"]
    assert len(phases) == 4
    assert [p["order"] for p in phases] == [1, 2, 3, 4]


def test_e8d_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "prerequisite_alignment",
    }


def test_e8d_collaboration_contract_present() -> None:
    collab = yaml.safe_load(
        (REPO_ROOT / "registry" / "cross_persona_collaboration_contract_v1.yaml").read_text(
            encoding="utf-8"
        )
    )
    contract = _load_contract()
    kpis = contract["kpis"]
    assert kpis["collaboration_primitive_count"] == len(collab["collaboration_primitives"])
    assert kpis["handoff_rule_count"] == len(collab["handoff_rules"])


def test_e8d_department_prerequisite_alignment() -> None:
    contract = _load_contract()
    dept_cert = yaml.safe_load(
        (REPO_ROOT / "registry" / "department_certification_v1.yaml").read_text(encoding="utf-8")
    )
    assert contract["kpis"]["certified_department_count"] == len(
        dept_cert["department_certification_status"]
    )
    assert contract["cross_department_certification_summary"]["overall_verdict"] == "certified"
