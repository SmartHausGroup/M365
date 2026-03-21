"""CI verifier for workforce expansion release decision v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PREREQUISITE_CONTRACTS = [
    "registry/enterprise_release_gate_v2.yaml",
    "registry/workforce_packaging_v1.yaml",
    "registry/customer_onboarding_v2.yaml",
    "registry/pilot_rollout_model_v2.yaml",
    "registry/support_boundary_v2.yaml",
]


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "workforce_release_decision_v1.yaml"
    if not contract_path.exists():
        print("FAILED: workforce release decision contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "decision_inputs",
        "governance_rules",
        "kpis",
        "release_decision",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    inputs = contract["decision_inputs"]
    if len(inputs) != 5:
        print(f"FAILED: expected 5 decision inputs, got {len(inputs)}")
        sys.exit(1)

    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "program_closure",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    for prereq in PREREQUISITE_CONTRACTS:
        if not (repo_root / prereq).exists():
            print(f"FAILED: prerequisite not found: {prereq}")
            sys.exit(1)

    decision = contract["release_decision"]
    if decision["verdict"] != "GO":
        print(f"FAILED: verdict is {decision['verdict']}, expected GO")
        sys.exit(1)
    if decision["program_status"] != "complete":
        print("FAILED: program_status is not complete")
        sys.exit(1)
    if not decision.get("residual_gaps"):
        print("FAILED: residual_gaps must be documented")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "decision_input_count": len(inputs),
        "governance_rule_count": len(contract["governance_rules"]),
        "release_verdict": decision["verdict"],
        "program_status": decision["program_status"],
        "residual_gap_count": len(decision["residual_gaps"]),
        "follow_on_count": len(decision.get("follow_on", [])),
    }
    output_path = (
        repo_root / "configs" / "generated" / "workforce_release_decision_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"PASSED: workforce release decision '{contract['contract']['id']}' — "
        f"verdict {decision['verdict']}, program {decision['program_status']}, "
        f"{len(decision['residual_gaps'])} residual gaps"
    )


if __name__ == "__main__":
    main()
