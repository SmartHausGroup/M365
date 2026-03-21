"""CI verifier for support boundary v2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "support_boundary_v2.yaml"
    if not contract_path.exists():
        print("FAILED: support boundary contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "support_layers",
        "governance_rules",
        "kpis",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    layers = contract["support_layers"]
    if len(layers) != 4:
        print(f"FAILED: expected 4 layers, got {len(layers)}")
        sys.exit(1)

    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "customer_sovereignty",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    kpis = contract["kpis"]
    if kpis["support_tier_count"] != 3:
        print("FAILED: expected 3 support tiers")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "support_layer_count": len(layers),
        "governance_rule_count": len(contract["governance_rules"]),
        "support_tier_count": kpis["support_tier_count"],
        "escalation_severity_levels": kpis["escalation_severity_levels"],
    }
    output_path = (
        repo_root / "configs" / "generated" / "support_boundary_v2_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"PASSED: support boundary '{contract['contract']['id']}' — "
        f"{len(layers)} layers, {kpis['support_tier_count']} tiers"
    )


if __name__ == "__main__":
    main()
