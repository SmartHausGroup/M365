"""Tests for persona certification contract v1."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PERSONA_FIELDS = {
    "persona_id",
    "display_name",
    "slug",
    "title",
    "department",
    "status",
    "coverage_status",
    "risk_tier",
    "approval_profile",
    "approval_owner",
    "escalation_owner",
    "manager",
    "canonical_agent",
    "external_presence_policy",
    "responsibilities",
    "capability_families",
    "workload_families",
    "allowed_domains",
    "allowed_actions",
    "action_count",
    "aliases",
}

VALID_APPROVAL_PROFILES = {
    "critical-regulated",
    "high-impact",
    "medium-operational",
    "low-observe-create",
}

APPROVAL_STRICTNESS = {
    "low-observe-create": 0,
    "medium-operational": 1,
    "high-impact": 2,
    "critical-regulated": 3,
}

RISK_BASELINE = {
    "low": "low-observe-create",
    "medium": "medium-operational",
    "high": "high-impact",
    "critical": "critical-regulated",
}


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_certification_v1.yaml").read_text(encoding="utf-8")
    )


def _load_registry() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )


def test_e8b_certification_has_four_ordered_phases() -> None:
    contract = _load_contract()
    phases = contract["certification_phases"]
    assert len(phases) == 4
    assert [p["order"] for p in phases] == [1, 2, 3, 4]
    assert [p["id"] for p in phases] == [
        "field_completeness",
        "coverage_status_consistency",
        "approval_posture_alignment",
        "domain_alignment",
    ]


def test_e8b_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "coverage_partition",
    }


def test_e8b_all_personas_have_required_fields() -> None:
    registry = _load_registry()
    for pid, p in registry["personas"].items():
        missing = REQUIRED_PERSONA_FIELDS - set(p.keys())
        assert not missing, f"{pid} missing fields: {sorted(missing)}"


def test_e8b_coverage_partition_and_approval_alignment() -> None:
    contract = _load_contract()
    registry = _load_registry()
    personas = registry["personas"]
    kpis = contract["kpis"]

    assert kpis["total_personas"] == len(personas)

    rb = 0
    co = 0
    active = 0
    planned = 0
    risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for pid, p in personas.items():
        assert (
            p["approval_profile"] in VALID_APPROVAL_PROFILES
        ), f"{pid}: invalid approval_profile {p['approval_profile']}"
        baseline = RISK_BASELINE[p["risk_tier"]]
        assert (
            APPROVAL_STRICTNESS[p["approval_profile"]] >= APPROVAL_STRICTNESS[baseline]
        ), f"{pid}: approval less strict than baseline: {p['approval_profile']} < {baseline}"
        assert p["status"] in {"active", "planned"}, f"{pid}: unexpected status {p['status']}"
        if p["status"] == "active":
            active += 1
        else:
            planned += 1
        assert p["risk_tier"] in risk_counts, f"{pid}: unexpected risk_tier {p['risk_tier']}"
        risk_counts[p["risk_tier"]] += 1
        if p["coverage_status"] == "registry-backed":
            assert p["action_count"] > 0
            rb += 1
        else:
            assert p["action_count"] == 0
            co += 1

    assert active == kpis["active_personas"]
    assert planned == kpis["planned_personas"]
    assert rb == kpis["registry_backed_personas"]
    assert co == kpis["contract_only_personas"]
    assert rb + co == kpis["total_personas"]
    assert risk_counts["critical"] == kpis["risk_tier_critical"]
    assert risk_counts["high"] == kpis["risk_tier_high"]
    assert risk_counts["medium"] == kpis["risk_tier_medium"]
    assert risk_counts["low"] == kpis["risk_tier_low"]
