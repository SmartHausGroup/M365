"""Tests for workload certification contract v1.

Validates that the workload certification contract is structurally complete,
per-domain verdicts align with the routing table, and bounded claims are
consistent.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    path = REPO_ROOT / "registry" / "workload_certification_v1.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_routing() -> dict:
    path = REPO_ROOT / "registry" / "executor_routing_v2.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_e8a_certification_has_four_ordered_phases() -> None:
    contract = _load_contract()
    phases = contract["certification_phases"]
    assert len(phases) == 4
    assert [p["order"] for p in phases] == [1, 2, 3, 4]
    assert [p["id"] for p in phases] == [
        "schema_validation",
        "action_coverage_audit",
        "auth_posture_alignment",
        "bounded_claim_consistency",
    ]


def test_e8a_certification_phases_have_required_fields() -> None:
    contract = _load_contract()
    for phase in contract["certification_phases"]:
        for field in ("id", "description", "inputs", "outputs", "failure_mode"):
            assert field in phase, f"phase {phase.get('id', '?')} missing '{field}'"


def test_e8a_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "wave_alignment",
    }


def test_e8a_domain_verdicts_match_routing_table() -> None:
    contract = _load_contract()
    routing = _load_routing()

    domains = routing["canonical_executor_domains"]
    routes = routing.get("exact_action_routes", {})
    domain_counts: dict[str, int] = {d: 0 for d in domains}
    for _action, domain in routes.items():
        if domain in domain_counts:
            domain_counts[domain] += 1

    cert_status = contract["domain_certification_status"]
    kpis = contract["kpis"]

    assert kpis["total_executor_domains"] == len(domains)

    certified = 0
    not_yet = 0
    total_routed = 0

    for d in domains:
        entry = cert_status[d]
        assert entry["routed_action_count"] == domain_counts[d]
        total_routed += entry["routed_action_count"]
        if domain_counts[d] == 0:
            assert entry["certification_verdict"] == "not-yet-certified"
            not_yet += 1
        else:
            assert entry["certification_verdict"] == "certified"
            certified += 1

    assert certified + not_yet == len(domains)
    assert kpis["domains_with_routed_actions"] == certified
    assert kpis["domains_without_routed_actions"] == not_yet
    assert kpis["total_routed_actions"] == total_routed
