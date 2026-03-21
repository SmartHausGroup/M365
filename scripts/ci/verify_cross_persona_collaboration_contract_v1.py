from __future__ import annotations

import json
from pathlib import Path

import yaml


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    contract_path = repo_root / "registry" / "cross_persona_collaboration_contract_v1.yaml"
    if not contract_path.exists():
        raise SystemExit("cross_persona_collaboration_contract_authority_missing")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "collaboration_primitives",
        "handoff_rules",
        "governance_rules",
        "kpis",
        "bounded_claims",
    }
    missing = sorted(required_keys - set(contract))
    if missing:
        raise SystemExit(f"cross_persona_collaboration_missing_keys:{','.join(missing)}")

    primitives = contract.get("collaboration_primitives") or []
    if len(primitives) != 4:
        raise SystemExit(f"collaboration_primitive_count:expected=4:got={len(primitives)}")

    handoff_rules = contract.get("handoff_rules") or {}
    if len(handoff_rules) != 5:
        raise SystemExit(f"handoff_rule_count:expected=5:got={len(handoff_rules)}")

    gov_rules = contract.get("governance_rules") or {}
    expected_rules = {
        "accountability_continuity",
        "no_circular_handoff",
        "risk_tier_boundary",
        "collaboration_audit",
    }
    missing_rules = sorted(expected_rules - set(gov_rules))
    if missing_rules:
        raise SystemExit(f"collaboration_missing_rules:{','.join(missing_rules)}")

    payload = {
        "contract_id": contract["contract"]["id"],
        "primitive_count": len(primitives),
        "handoff_rule_count": len(handoff_rules),
        "governance_rule_count": len(gov_rules),
        "primitives": [p["id"] for p in primitives],
    }

    output_path = (
        repo_root
        / "configs"
        / "generated"
        / "cross_persona_collaboration_contract_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASSED",
        f"contract={payload['contract_id']}",
        f"primitives={payload['primitive_count']}",
        f"handoff_rules={payload['handoff_rule_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
