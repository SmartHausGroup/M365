"""Tests for workforce expansion release decision v1."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

PREREQUISITE_CONTRACTS = [
    "registry/enterprise_release_gate_v2.yaml",
    "registry/workforce_packaging_v1.yaml",
    "registry/customer_onboarding_v2.yaml",
    "registry/pilot_rollout_model_v2.yaml",
    "registry/support_boundary_v2.yaml",
]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "workforce_release_decision_v1.yaml").read_text(encoding="utf-8")
    )


def test_e9e_decision_has_five_inputs() -> None:
    contract = _load_contract()
    assert len(contract["decision_inputs"]) == 5
    assert [i["order"] for i in contract["decision_inputs"]] == [1, 2, 3, 4, 5]


def test_e9e_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "program_closure",
    }


def test_e9e_verdict_go_with_gaps() -> None:
    contract = _load_contract()
    decision = contract["release_decision"]
    assert decision["verdict"] == "GO"
    assert decision["program_status"] == "complete"
    assert len(decision["residual_gaps"]) > 0
    assert len(decision.get("follow_on", [])) > 0


def test_e9e_all_prerequisites_exist() -> None:
    for prereq in PREREQUISITE_CONTRACTS:
        assert (REPO_ROOT / prereq).exists(), f"missing: {prereq}"
