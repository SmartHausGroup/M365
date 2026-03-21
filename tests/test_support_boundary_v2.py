"""Tests for support boundary v2."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "support_boundary_v2.yaml").read_text(encoding="utf-8")
    )


def test_e9d_support_has_four_layers() -> None:
    contract = _load_contract()
    assert len(contract["support_layers"]) == 4
    assert [layer["order"] for layer in contract["support_layers"]] == [1, 2, 3, 4]


def test_e9d_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "customer_sovereignty",
    }


def test_e9d_support_tiers_and_escalation() -> None:
    contract = _load_contract()
    assert contract["kpis"]["support_tier_count"] == 3
    assert contract["kpis"]["escalation_severity_levels"] == 3
