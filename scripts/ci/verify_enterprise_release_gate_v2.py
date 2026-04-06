"""CI verifier for enterprise release gate v2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

CERTIFICATION_PREREQUISITES = [
    "registry/workload_certification_v1.yaml",
    "registry/persona_certification_v1.yaml",
    "registry/department_certification_v1.yaml",
    "registry/activated_persona_surface_v1.yaml",
    "registry/workforce_packaging_v1.yaml",
    "registry/cross_department_certification_v1.yaml",
    "registry/ucp_delegation_contract_v1.yaml",
    "registry/executive_oversight_contract_v1.yaml",
]


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "enterprise_release_gate_v2.yaml"
    if not contract_path.exists():
        print("FAILED: enterprise release gate v2 not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "release_gate_checks",
        "governance_rules",
        "kpis",
        "release_decision",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    checks = contract["release_gate_checks"]
    if len(checks) != 6:
        print(f"FAILED: expected 6 gate checks, got {len(checks)}")
        sys.exit(1)

    for check in checks:
        if check["status"] != "green":
            print(f"FAILED: gate check '{check['id']}' is not green")
            sys.exit(1)

    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "explicit_sign_off",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    # Verify all prerequisite contracts exist
    for prereq in CERTIFICATION_PREREQUISITES:
        prereq_path = repo_root / prereq
        if not prereq_path.exists():
            print(f"FAILED: prerequisite not found: {prereq}")
            sys.exit(1)

    workload = yaml.safe_load(
        (repo_root / "registry" / "workload_certification_v1.yaml").read_text(encoding="utf-8")
    )
    persona_cert = yaml.safe_load(
        (repo_root / "registry" / "persona_certification_v1.yaml").read_text(encoding="utf-8")
    )
    department_cert = yaml.safe_load(
        (repo_root / "registry" / "department_certification_v1.yaml").read_text(encoding="utf-8")
    )
    activated_surface = yaml.safe_load(
        (repo_root / "registry" / "activated_persona_surface_v1.yaml").read_text(encoding="utf-8")
    )
    workforce_packaging = yaml.safe_load(
        (repo_root / "registry" / "workforce_packaging_v1.yaml").read_text(encoding="utf-8")
    )

    decision = contract["release_decision"]
    if decision["verdict"] != "GO":
        print(f"FAILED: release verdict is {decision['verdict']}, expected GO")
        sys.exit(1)

    if not decision.get("residual_gaps"):
        print("FAILED: residual_gaps must be documented")
        sys.exit(1)

    kpis = contract["kpis"]
    workload_kpis = workload["kpis"]
    persona_kpis = persona_cert["kpis"]
    department_kpis = department_cert["kpis"]
    activated_kpis = activated_surface["kpis"]
    packaging_kpis = workforce_packaging["kpis"]

    if kpis["workload_domains_certified"] != workload_kpis["domains_with_routed_actions"]:
        print("FAILED: workload_domains_certified mismatch")
        sys.exit(1)

    if kpis["workload_domains_not_yet"] != workload_kpis["domains_without_routed_actions"]:
        print("FAILED: workload_domains_not_yet mismatch")
        sys.exit(1)

    if kpis["personas_certified"] != persona_kpis["total_personas"]:
        print("FAILED: personas_certified mismatch")
        sys.exit(1)

    if kpis["active_personas_certified"] != persona_kpis["active_personas"]:
        print("FAILED: active_personas_certified mismatch")
        sys.exit(1)

    if kpis["planned_personas_certified"] != persona_kpis["planned_personas"]:
        print("FAILED: planned_personas_certified mismatch")
        sys.exit(1)

    if kpis["departments_certified"] != department_kpis["total_departments"]:
        print("FAILED: departments_certified mismatch")
        sys.exit(1)

    if persona_kpis["active_personas"] != department_kpis["active_department_personas"]:
        print("FAILED: persona/department active count mismatch")
        sys.exit(1)

    if persona_kpis["planned_personas"] != department_kpis["planned_department_personas"]:
        print("FAILED: persona/department planned count mismatch")
        sys.exit(1)

    if (
        persona_kpis["registry_backed_personas"]
        != department_kpis["registry_backed_department_personas"]
    ):
        print("FAILED: persona/department registry-backed count mismatch")
        sys.exit(1)

    if (
        persona_kpis["contract_only_personas"]
        != department_kpis["contract_only_department_personas"]
    ):
        print("FAILED: persona/department contract-only count mismatch")
        sys.exit(1)

    if kpis["personas_certified"] != activated_kpis["total_personas"]:
        print("FAILED: release gate / activated surface total persona mismatch")
        sys.exit(1)

    if kpis["active_personas_certified"] != activated_kpis["certified_active_personas"]:
        print("FAILED: release gate / activated surface active persona mismatch")
        sys.exit(1)

    if kpis["planned_personas_certified"] != activated_kpis["deferred_external_personas"]:
        print("FAILED: release gate / activated surface planned persona mismatch")
        sys.exit(1)

    if kpis["departments_certified"] != activated_kpis["active_departments"]:
        print("FAILED: release gate / activated surface department mismatch")
        sys.exit(1)

    if kpis["total_routed_actions"] != activated_kpis["total_allowed_persona_actions"]:
        print("FAILED: release gate / activated surface routed action mismatch")
        sys.exit(1)

    if kpis["workload_domains_certified"] != packaging_kpis["certified_workload_domains"]:
        print("FAILED: release gate / packaging domain mismatch")
        sys.exit(1)

    if kpis["personas_certified"] != packaging_kpis["total_persona_count"]:
        print("FAILED: release gate / packaging total persona mismatch")
        sys.exit(1)

    if kpis["active_personas_certified"] != packaging_kpis["active_persona_count"]:
        print("FAILED: release gate / packaging active persona mismatch")
        sys.exit(1)

    if kpis["planned_personas_certified"] != packaging_kpis["planned_persona_count"]:
        print("FAILED: release gate / packaging planned persona mismatch")
        sys.exit(1)

    if kpis["departments_certified"] != packaging_kpis["department_count"]:
        print("FAILED: release gate / packaging department mismatch")
        sys.exit(1)

    if kpis["total_routed_actions"] != packaging_kpis["total_routed_actions"]:
        print("FAILED: release gate / packaging routed action mismatch")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "release_gate_check_count": len(checks),
        "governance_rule_count": len(contract["governance_rules"]),
        "all_checks_green": all(c["status"] == "green" for c in checks),
        "release_verdict": decision["verdict"],
        "residual_gap_count": len(decision["residual_gaps"]),
        "workload_domains_certified": kpis["workload_domains_certified"],
        "personas_certified": kpis["personas_certified"],
        "departments_certified": kpis["departments_certified"],
        "active_personas_certified": kpis["active_personas_certified"],
        "planned_personas_certified": kpis["planned_personas_certified"],
        "total_routed_actions": kpis["total_routed_actions"],
    }

    output_path = (
        repo_root / "configs" / "generated" / "enterprise_release_gate_v2_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"PASSED: enterprise release gate '{contract['contract']['id']}' — "
        f"{len(checks)} checks all green, verdict {decision['verdict']}, "
        f"{len(decision['residual_gaps'])} residual gaps documented"
    )


if __name__ == "__main__":
    main()
