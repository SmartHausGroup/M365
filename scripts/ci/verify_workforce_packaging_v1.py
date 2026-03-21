"""CI verifier for workforce packaging contract v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "workforce_packaging_v1.yaml"
    if not contract_path.exists():
        print("FAILED: workforce packaging contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "packaging_layers",
        "governance_rules",
        "kpis",
        "product_tiers",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    layers = contract["packaging_layers"]
    if len(layers) != 4:
        print(f"FAILED: expected 4 packaging layers, got {len(layers)}")
        sys.exit(1)

    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "traceability",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    # Validate against persona registry
    registry = yaml.safe_load(
        (repo_root / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    personas = registry["personas"]
    rb = sum(1 for p in personas.values() if p.get("coverage_status") == "registry-backed")
    co = sum(1 for p in personas.values() if p.get("coverage_status") == "persona-contract-only")

    kpis = contract["kpis"]
    tiers = contract["product_tiers"]

    if tiers["core"]["persona_count"] != rb:
        print(f"FAILED: core persona count {tiers['core']['persona_count']} != {rb}")
        sys.exit(1)
    if tiers["expansion"]["persona_count"] != co:
        print(f"FAILED: expansion persona count {tiers['expansion']['persona_count']} != {co}")
        sys.exit(1)
    if kpis["total_persona_count"] != len(personas):
        print("FAILED: total persona count mismatch")
        sys.exit(1)

    # Validate against release gate
    gate = yaml.safe_load(
        (repo_root / "registry" / "enterprise_release_gate_v2.yaml").read_text(encoding="utf-8")
    )
    if kpis["total_routed_actions"] != gate["kpis"]["total_routed_actions"]:
        print("FAILED: routed actions mismatch with release gate")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "packaging_layer_count": len(layers),
        "governance_rule_count": len(contract["governance_rules"]),
        "core_personas": rb,
        "expansion_personas": co,
        "total_personas": len(personas),
        "total_routed_actions": kpis["total_routed_actions"],
    }
    output_path = repo_root / "configs" / "generated" / "workforce_packaging_v1_verification.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"PASSED: workforce packaging '{contract['contract']['id']}' — "
        f"{len(layers)} layers, core={rb}/expansion={co}, "
        f"{kpis['total_routed_actions']} actions"
    )


if __name__ == "__main__":
    main()
