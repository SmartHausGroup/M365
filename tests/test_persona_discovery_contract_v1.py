from __future__ import annotations

from pathlib import Path

import yaml


def _load_contract() -> dict:
    return yaml.safe_load(
        Path("registry/persona_discovery_contract_v1.yaml").read_text(encoding="utf-8")
    )


def test_e7b_discovery_contract_has_six_dimensions() -> None:
    contract = _load_contract()
    dimensions = contract["discovery_dimensions"]
    assert len(dimensions) == 6
    assert [d["id"] for d in dimensions] == [
        "by_name",
        "by_department",
        "by_capability_family",
        "by_workload_family",
        "by_risk_tier",
        "by_coverage_status",
    ]


def test_e7b_selection_rules_complete() -> None:
    contract = _load_contract()
    rules = contract["selection_rules"]
    for key in ("single_match", "multiple_matches", "no_match", "ambiguity_policy"):
        assert key in rules
    assert rules["ambiguity_policy"] == "fail_closed"


def test_e7b_governance_rules_complete() -> None:
    contract = _load_contract()
    rules = contract["governance_rules"]
    expected = {"deterministic_discovery", "no_hidden_personas", "contract_only_transparency"}
    assert set(rules.keys()) == expected


def test_e7b_persona_count_matches_registry() -> None:
    contract = _load_contract()
    registry = yaml.safe_load(
        Path("registry/persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    assert contract["kpis"]["discoverable_persona_count"] == len(registry["personas"])
    assert contract["kpis"]["department_count"] == 10
