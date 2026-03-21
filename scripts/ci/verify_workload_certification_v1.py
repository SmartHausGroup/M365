"""CI verifier for workload certification contract v1.

Validates the workload certification contract against the authoritative
executor routing table and capability registry, ensuring per-domain
certification verdicts are deterministic and bounded.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    # --- Load contract ---
    contract_path = repo_root / "registry" / "workload_certification_v1.yaml"
    if not contract_path.exists():
        print("FAILED: workload certification contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    # --- Validate root keys ---
    required_keys = {
        "version",
        "authority",
        "contract",
        "certification_phases",
        "governance_rules",
        "kpis",
        "domain_certification_status",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    # --- Validate certification phases ---
    phases = contract["certification_phases"]
    if len(phases) != 4:
        print(f"FAILED: expected 4 certification phases, got {len(phases)}")
        sys.exit(1)
    for i, phase in enumerate(phases, start=1):
        if phase["order"] != i:
            print(f"FAILED: phase {i} has order {phase['order']}")
            sys.exit(1)
        for field in ("id", "description", "inputs", "outputs", "failure_mode"):
            if field not in phase:
                print(f"FAILED: phase {i} missing field '{field}'")
                sys.exit(1)

    expected_phase_ids = [
        "schema_validation",
        "action_coverage_audit",
        "auth_posture_alignment",
        "bounded_claim_consistency",
    ]
    actual_phase_ids = [p["id"] for p in phases]
    if actual_phase_ids != expected_phase_ids:
        print(f"FAILED: phase IDs {actual_phase_ids} != {expected_phase_ids}")
        sys.exit(1)

    # --- Validate governance rules ---
    rules = contract["governance_rules"]
    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "wave_alignment",
    }
    if set(rules.keys()) != expected_rules:
        print(f"FAILED: governance rules {set(rules.keys())} != {expected_rules}")
        sys.exit(1)

    # --- Load routing table ---
    routing_path = repo_root / "registry" / "executor_routing_v2.yaml"
    routing = yaml.safe_load(routing_path.read_text(encoding="utf-8"))
    domains = routing["canonical_executor_domains"]
    routes = routing.get("exact_action_routes", {})

    domain_action_counts: dict[str, int] = {d: 0 for d in domains}
    for _action, domain in routes.items():
        if domain in domain_action_counts:
            domain_action_counts[domain] += 1

    # --- Validate per-domain certification ---
    cert_status = contract["domain_certification_status"]
    kpis = contract["kpis"]

    if kpis["total_executor_domains"] != len(domains):
        print(
            f"FAILED: KPI total_executor_domains {kpis['total_executor_domains']} != {len(domains)}"
        )
        sys.exit(1)

    certified_count = 0
    not_yet_count = 0
    total_routed = 0

    for d in domains:
        if d not in cert_status:
            print(f"FAILED: domain '{d}' missing from certification status")
            sys.exit(1)
        entry = cert_status[d]
        if entry["routed_action_count"] != domain_action_counts[d]:
            print(
                f"FAILED: domain '{d}' routed_action_count "
                f"{entry['routed_action_count']} != {domain_action_counts[d]}"
            )
            sys.exit(1)
        total_routed += entry["routed_action_count"]
        if domain_action_counts[d] == 0:
            if entry["certification_verdict"] != "not-yet-certified":
                print(f"FAILED: zero-action domain '{d}' not marked not-yet-certified")
                sys.exit(1)
            not_yet_count += 1
        else:
            if entry["certification_verdict"] != "certified":
                print(f"FAILED: domain '{d}' with actions not marked certified")
                sys.exit(1)
            certified_count += 1

    if certified_count + not_yet_count != len(domains):
        print("FAILED: certified + not-yet-certified != total domains")
        sys.exit(1)

    if kpis["domains_with_routed_actions"] != certified_count:
        print("FAILED: KPI domains_with_routed_actions mismatch")
        sys.exit(1)

    if kpis["domains_without_routed_actions"] != not_yet_count:
        print("FAILED: KPI domains_without_routed_actions mismatch")
        sys.exit(1)

    if kpis["total_routed_actions"] != total_routed:
        print("FAILED: KPI total_routed_actions mismatch")
        sys.exit(1)

    # --- Write verification output ---
    output = {
        "contract_id": contract["contract"]["id"],
        "certification_phase_count": len(phases),
        "governance_rule_count": len(rules),
        "total_executor_domains": len(domains),
        "domains_with_routed_actions": certified_count,
        "domains_without_routed_actions": not_yet_count,
        "total_routed_actions": total_routed,
        "phase_ids": actual_phase_ids,
        "rule_keys": sorted(rules.keys()),
        "certified_domains": sorted(
            d for d in domains if cert_status[d]["certification_verdict"] == "certified"
        ),
        "not_yet_certified_domains": sorted(
            d for d in domains if cert_status[d]["certification_verdict"] == "not-yet-certified"
        ),
    }

    output_path = (
        repo_root / "configs" / "generated" / "workload_certification_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"PASSED: workload certification contract '{contract['contract']['id']}' — "
        f"{len(phases)} phases, {len(rules)} rules, "
        f"{certified_count} certified / {not_yet_count} not-yet-certified domains, "
        f"{total_routed} routed actions"
    )


if __name__ == "__main__":
    main()
