from __future__ import annotations

import json
from pathlib import Path

import yaml


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "persona_discovery_contract_v1.yaml"
    if not contract_path.exists():
        raise SystemExit("persona_discovery_contract_authority_missing")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "discovery_dimensions",
        "selection_rules",
        "governance_rules",
        "kpis",
        "bounded_claims",
    }
    missing = sorted(required_keys - set(contract))
    if missing:
        raise SystemExit(f"persona_discovery_contract_missing_keys:{','.join(missing)}")

    dimensions = contract.get("discovery_dimensions") or []
    if len(dimensions) != 6:
        raise SystemExit(f"persona_discovery_dimension_count_mismatch:expected=6:got={len(dimensions)}")

    rules = contract.get("selection_rules") or {}
    for key in ("single_match", "multiple_matches", "no_match", "ambiguity_policy"):
        if key not in rules:
            raise SystemExit(f"persona_discovery_missing_selection_rule:{key}")

    gov_rules = contract.get("governance_rules") or {}
    for key in ("deterministic_discovery", "no_hidden_personas", "contract_only_transparency"):
        if key not in gov_rules:
            raise SystemExit(f"persona_discovery_missing_governance_rule:{key}")

    registry_path = repo_root / "registry" / "persona_registry_v2.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    total_personas = len(registry.get("personas") or {})

    kpis = contract.get("kpis") or {}
    if kpis.get("discoverable_persona_count") != total_personas:
        raise SystemExit("persona_discovery_persona_count_mismatch")
    if kpis.get("department_count") != 10:
        raise SystemExit("persona_discovery_department_count_mismatch")

    payload = {
        "contract_id": contract["contract"]["id"],
        "discovery_dimension_count": len(dimensions),
        "selection_rule_count": 4,
        "governance_rule_count": len(gov_rules),
        "discoverable_persona_count": kpis["discoverable_persona_count"],
        "department_count": kpis["department_count"],
        "dimensions": [d["id"] for d in dimensions],
    }

    output_path = (
        repo_root / "configs" / "generated" / "persona_discovery_contract_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASSED",
        f"contract={payload['contract_id']}",
        f"dimensions={payload['discovery_dimension_count']}",
        f"personas={payload['discoverable_persona_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
