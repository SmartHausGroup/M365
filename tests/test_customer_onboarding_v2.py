"""Tests for customer onboarding v2."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "customer_onboarding_v2.yaml").read_text(encoding="utf-8")
    )


def test_e9b_onboarding_has_four_phases() -> None:
    contract = _load_contract()
    assert len(contract["onboarding_phases"]) == 4
    assert [p["order"] for p in contract["onboarding_phases"]] == [1, 2, 3, 4]


def test_e9b_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "sequential_activation",
    }


def test_e9b_activation_sequence_valid() -> None:
    contract = _load_contract()
    registry = yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    for pid in contract["kpis"]["core_tier_activation_sequence"]:
        assert pid in registry["personas"]
        assert registry["personas"][pid]["coverage_status"] == "registry-backed"
