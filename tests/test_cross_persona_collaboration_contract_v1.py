from __future__ import annotations

from pathlib import Path

import yaml


def _load_contract() -> dict:
    return yaml.safe_load(
        Path("registry/cross_persona_collaboration_contract_v1.yaml").read_text(encoding="utf-8")
    )


def test_e7d_collaboration_has_four_primitives() -> None:
    contract = _load_contract()
    primitives = contract["collaboration_primitives"]
    assert len(primitives) == 4
    assert [p["id"] for p in primitives] == [
        "handoff",
        "consultation",
        "co_execution",
        "escalation",
    ]


def test_e7d_accountability_transfer_semantics() -> None:
    contract = _load_contract()
    primitives = {p["id"]: p for p in contract["collaboration_primitives"]}
    assert primitives["handoff"]["accountability_transfer"] is True
    assert primitives["consultation"]["accountability_transfer"] is False
    assert primitives["co_execution"]["accountability_transfer"] is False
    assert primitives["escalation"]["accountability_transfer"] is True


def test_e7d_handoff_rules_complete() -> None:
    contract = _load_contract()
    rules = contract["handoff_rules"]
    assert len(rules) == 5
    expected = {
        "context_required",
        "cross_department_allowed",
        "cross_department_approval",
        "contract_only_target",
        "audit_chain",
    }
    assert set(rules.keys()) == expected


def test_e7d_governance_rules_complete() -> None:
    contract = _load_contract()
    rules = contract["governance_rules"]
    expected = {
        "accountability_continuity",
        "no_circular_handoff",
        "risk_tier_boundary",
        "collaboration_audit",
    }
    assert set(rules.keys()) == expected
