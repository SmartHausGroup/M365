"""CI verifier for persona certification contract v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

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

# Approval strictness order (higher index = more restrictive)
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


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "persona_certification_v1.yaml"
    if not contract_path.exists():
        print("FAILED: persona certification contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    # Validate root keys
    required_keys = {
        "version",
        "authority",
        "contract",
        "certification_phases",
        "governance_rules",
        "kpis",
        "persona_certification_summary",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    # Validate phases
    phases = contract["certification_phases"]
    if len(phases) != 4:
        print(f"FAILED: expected 4 phases, got {len(phases)}")
        sys.exit(1)
    expected_ids = [
        "field_completeness",
        "coverage_status_consistency",
        "approval_posture_alignment",
        "domain_alignment",
    ]
    actual_ids = [p["id"] for p in phases]
    if actual_ids != expected_ids:
        print("FAILED: phase IDs mismatch")
        sys.exit(1)

    # Validate governance rules
    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "coverage_partition",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    # Load persona registry
    registry = yaml.safe_load(
        (repo_root / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    personas = registry["personas"]
    kpis = contract["kpis"]

    if kpis["total_personas"] != len(personas):
        print(f"FAILED: total_personas {kpis['total_personas']} != {len(personas)}")
        sys.exit(1)

    rb_count = 0
    co_count = 0
    active_count = 0
    planned_count = 0
    risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for pid, p in personas.items():
        missing_fields = REQUIRED_PERSONA_FIELDS - set(p.keys())
        if missing_fields:
            print(f"FAILED: {pid} missing fields: {sorted(missing_fields)}")
            sys.exit(1)
        if p["approval_profile"] not in VALID_APPROVAL_PROFILES:
            print(f"FAILED: {pid} invalid approval_profile: {p['approval_profile']}")
            sys.exit(1)
        baseline = RISK_BASELINE.get(p["risk_tier"])
        if baseline and APPROVAL_STRICTNESS[p["approval_profile"]] < APPROVAL_STRICTNESS[baseline]:
            print(
                f"FAILED: {pid} approval less strict than risk baseline: "
                f"{p['approval_profile']} < {baseline}"
            )
            sys.exit(1)
        if p["status"] == "active":
            active_count += 1
        elif p["status"] == "planned":
            planned_count += 1
        else:
            print(f"FAILED: {pid} unexpected status: {p['status']}")
            sys.exit(1)
        if p["risk_tier"] not in risk_counts:
            print(f"FAILED: {pid} unexpected risk_tier: {p['risk_tier']}")
            sys.exit(1)
        risk_counts[p["risk_tier"]] += 1
        if p["coverage_status"] == "registry-backed":
            if p["action_count"] == 0:
                print(f"FAILED: {pid} registry-backed with 0 actions")
                sys.exit(1)
            rb_count += 1
        else:
            if p["action_count"] != 0:
                print(f"FAILED: {pid} contract-only with {p['action_count']} actions")
                sys.exit(1)
            co_count += 1

    if rb_count + co_count != len(personas):
        print("FAILED: coverage partition mismatch")
        sys.exit(1)

    if kpis["registry_backed_personas"] != rb_count:
        print("FAILED: KPI registry_backed_personas mismatch")
        sys.exit(1)

    if kpis["contract_only_personas"] != co_count:
        print("FAILED: KPI contract_only_personas mismatch")
        sys.exit(1)

    if kpis["active_personas"] != active_count:
        print("FAILED: KPI active_personas mismatch")
        sys.exit(1)

    if kpis["planned_personas"] != planned_count:
        print("FAILED: KPI planned_personas mismatch")
        sys.exit(1)

    for risk_tier, count in risk_counts.items():
        key = f"risk_tier_{risk_tier}"
        if kpis[key] != count:
            print(f"FAILED: KPI {key} mismatch")
            sys.exit(1)

    # Write verification output
    output = {
        "contract_id": contract["contract"]["id"],
        "certification_phase_count": len(phases),
        "governance_rule_count": len(contract["governance_rules"]),
        "total_personas": len(personas),
        "active_personas": active_count,
        "planned_personas": planned_count,
        "registry_backed_personas": rb_count,
        "contract_only_personas": co_count,
        "risk_distribution": risk_counts,
        "phase_ids": actual_ids,
        "rule_keys": sorted(contract["governance_rules"].keys()),
        "all_fields_complete": True,
        "all_approval_aligned": True,
        "overall_verdict": "certified",
    }

    output_path = repo_root / "configs" / "generated" / "persona_certification_v1_verification.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"PASSED: persona certification '{contract['contract']['id']}' — "
        f"{len(phases)} phases, {len(contract['governance_rules'])} rules, "
        f"{active_count} active / {planned_count} planned, "
        f"{rb_count} registry-backed / {co_count} contract-only, {len(personas)} total personas"
    )


if __name__ == "__main__":
    main()
