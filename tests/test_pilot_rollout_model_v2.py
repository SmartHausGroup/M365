"""Tests for pilot and rollout model v2."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "pilot_rollout_model_v2.yaml").read_text(encoding="utf-8")
    )


def test_e9c_rollout_has_four_phases() -> None:
    contract = _load_contract()
    assert len(contract["rollout_phases"]) == 4
    assert [p["order"] for p in contract["rollout_phases"]] == [1, 2, 3, 4]


def test_e9c_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "sequential_waves",
    }


def test_e9c_three_rollout_waves() -> None:
    contract = _load_contract()
    assert contract["kpis"]["rollout_wave_count"] == 3
    assert contract["kpis"]["pilot_personas"] == 4
