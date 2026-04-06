"""Tests for workforce packaging contract v1."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "workforce_packaging_v1.yaml").read_text(encoding="utf-8")
    )


def test_e9a_packaging_has_four_layers() -> None:
    contract = _load_contract()
    assert len(contract["packaging_layers"]) == 4
    assert [layer["order"] for layer in contract["packaging_layers"]] == [1, 2, 3, 4]


def test_e9a_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "traceability",
    }


def test_e9a_tiers_match_registry() -> None:
    contract = _load_contract()
    registry = yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    personas = registry["personas"]
    rb = sum(1 for p in personas.values() if p.get("coverage_status") == "registry-backed")
    co = sum(1 for p in personas.values() if p.get("coverage_status") == "persona-contract-only")
    assert contract["product_tiers"]["core"]["persona_count"] == rb
    assert contract["product_tiers"]["expansion"]["persona_count"] == co
    assert contract["kpis"]["total_persona_count"] == len(personas)


def test_e9a_actions_match_activated_surface() -> None:
    contract = _load_contract()
    activated_surface = yaml.safe_load(
        (REPO_ROOT / "registry" / "activated_persona_surface_v1.yaml").read_text(encoding="utf-8")
    )
    registry = yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    active_departments = {
        persona["department"]
        for persona in registry["personas"].values()
        if persona["status"] == "active"
    }
    deferred_departments = {
        persona["department"]
        for persona in registry["personas"].values()
        if persona["status"] == "planned"
    }
    assert (
        contract["kpis"]["total_routed_actions"]
        == activated_surface["kpis"]["total_allowed_persona_actions"]
        == 430
    )
    assert contract["kpis"]["active_persona_count"] == 54
    assert contract["kpis"]["planned_persona_count"] == 5
    assert contract["product_tiers"]["core"]["action_count"] == 430
    assert contract["product_tiers"]["core"]["departments_with_active_personas"] == len(
        active_departments
    )
    assert contract["product_tiers"]["expansion"]["departments_covered"] == len(
        deferred_departments
    )
