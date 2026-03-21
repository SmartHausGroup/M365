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

    decision = contract["release_decision"]
    if decision["verdict"] != "GO":
        print(f"FAILED: release verdict is {decision['verdict']}, expected GO")
        sys.exit(1)

    if not decision.get("residual_gaps"):
        print("FAILED: residual_gaps must be documented")
        sys.exit(1)

    kpis = contract["kpis"]

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
