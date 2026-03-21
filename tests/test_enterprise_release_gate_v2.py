"""Tests for enterprise release gate v2."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "enterprise_release_gate_v2.yaml").read_text(encoding="utf-8")
    )


def test_e8e_gate_has_six_ordered_checks() -> None:
    contract = _load_contract()
    checks = contract["release_gate_checks"]
    assert len(checks) == 6
    assert [c["order"] for c in checks] == [1, 2, 3, 4, 5, 6]


def test_e8e_all_checks_green() -> None:
    contract = _load_contract()
    for check in contract["release_gate_checks"]:
        assert check["status"] == "green", f"check {check['id']} not green"


def test_e8e_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "explicit_sign_off",
    }


def test_e8e_release_decision_go_with_gaps() -> None:
    contract = _load_contract()
    decision = contract["release_decision"]
    assert decision["verdict"] == "GO"
    assert len(decision["residual_gaps"]) > 0
    assert len(decision["conditions"]) > 0


def test_e8e_all_prerequisite_contracts_exist() -> None:
    prereqs = [
        "registry/workload_certification_v1.yaml",
        "registry/persona_certification_v1.yaml",
        "registry/department_certification_v1.yaml",
        "registry/cross_department_certification_v1.yaml",
        "registry/ucp_delegation_contract_v1.yaml",
        "registry/executive_oversight_contract_v1.yaml",
    ]
    for prereq in prereqs:
        assert (REPO_ROOT / prereq).exists(), f"missing: {prereq}"
