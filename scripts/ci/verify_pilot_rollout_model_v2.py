"""CI verifier for pilot and rollout model v2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "pilot_rollout_model_v2.yaml"
    if not contract_path.exists():
        print("FAILED: pilot rollout model contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "rollout_phases",
        "governance_rules",
        "kpis",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    phases = contract["rollout_phases"]
    if len(phases) != 4:
        print(f"FAILED: expected 4 phases, got {len(phases)}")
        sys.exit(1)

    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "sequential_waves",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    kpis = contract["kpis"]
    if kpis["rollout_wave_count"] != 3:
        print("FAILED: expected 3 rollout waves")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "rollout_phase_count": len(phases),
        "governance_rule_count": len(contract["governance_rules"]),
        "rollout_wave_count": kpis["rollout_wave_count"],
        "pilot_personas": kpis["pilot_personas"],
    }
    output_path = repo_root / "configs" / "generated" / "pilot_rollout_model_v2_verification.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"PASSED: pilot rollout model '{contract['contract']['id']}' — "
        f"{len(phases)} phases, {kpis['rollout_wave_count']} waves"
    )


if __name__ == "__main__":
    main()
