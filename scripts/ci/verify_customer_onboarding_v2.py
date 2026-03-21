"""CI verifier for customer onboarding v2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "customer_onboarding_v2.yaml"
    if not contract_path.exists():
        print("FAILED: customer onboarding contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "onboarding_phases",
        "governance_rules",
        "kpis",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    phases = contract["onboarding_phases"]
    if len(phases) != 4:
        print(f"FAILED: expected 4 phases, got {len(phases)}")
        sys.exit(1)

    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "sequential_activation",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    # Validate activation sequence against registry
    registry = yaml.safe_load(
        (repo_root / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    activation_seq = contract["kpis"]["core_tier_activation_sequence"]
    for pid in activation_seq:
        if pid not in registry["personas"]:
            print(f"FAILED: activation persona '{pid}' not in registry")
            sys.exit(1)
        if registry["personas"][pid].get("coverage_status") != "registry-backed":
            print(f"FAILED: activation persona '{pid}' not registry-backed")
            sys.exit(1)

    if len(activation_seq) != contract["kpis"]["active_personas_at_onboarding"]:
        print("FAILED: activation sequence count mismatch")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "onboarding_phase_count": len(phases),
        "governance_rule_count": len(contract["governance_rules"]),
        "activation_sequence": activation_seq,
        "active_personas_at_onboarding": len(activation_seq),
    }
    output_path = (
        repo_root / "configs" / "generated" / "customer_onboarding_v2_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"PASSED: customer onboarding '{contract['contract']['id']}' — "
        f"{len(phases)} phases, {len(activation_seq)} active personas"
    )


if __name__ == "__main__":
    main()
