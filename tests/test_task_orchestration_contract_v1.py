from __future__ import annotations

from pathlib import Path

import yaml


def _load_contract() -> dict:
    return yaml.safe_load(
        Path("registry/task_orchestration_contract_v1.yaml").read_text(encoding="utf-8")
    )


def test_e7c_orchestration_has_four_primitives() -> None:
    contract = _load_contract()
    primitives = contract["orchestration_primitives"]
    assert len(primitives) == 4
    assert [p["id"] for p in primitives] == [
        "sequential",
        "parallel",
        "conditional",
        "fallback",
    ]


def test_e7c_step_contract_has_required_fields_and_states() -> None:
    contract = _load_contract()
    step = contract["step_contract"]
    assert len(step["required_fields"]) == 6
    assert len(step["step_states"]) == 6
    assert set(step["step_states"]) == {
        "pending",
        "running",
        "completed",
        "failed",
        "skipped",
        "blocked",
    }


def test_e7c_governance_rules_complete() -> None:
    contract = _load_contract()
    rules = contract["governance_rules"]
    expected = {
        "deterministic_ordering",
        "fail_closed_on_missing_persona",
        "audit_per_step",
        "no_implicit_escalation",
    }
    assert set(rules.keys()) == expected
