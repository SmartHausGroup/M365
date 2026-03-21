from __future__ import annotations

import json
from pathlib import Path

import yaml


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    contract_path = repo_root / "registry" / "executive_oversight_contract_v1.yaml"
    if not contract_path.exists():
        raise SystemExit("executive_oversight_contract_authority_missing")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "oversight_queries",
        "intervention_primitives",
        "escalation_paths",
        "governance_rules",
        "kpis",
        "bounded_claims",
    }
    missing = sorted(required_keys - set(contract))
    if missing:
        raise SystemExit(f"executive_oversight_missing_keys:{','.join(missing)}")

    queries = contract.get("oversight_queries") or []
    if len(queries) != 5:
        raise SystemExit(f"oversight_query_count:expected=5:got={len(queries)}")

    interventions = contract.get("intervention_primitives") or []
    if len(interventions) != 5:
        raise SystemExit(f"intervention_primitive_count:expected=5:got={len(interventions)}")

    escalation = contract.get("escalation_paths") or {}
    if len(escalation) != 3:
        raise SystemExit(f"escalation_path_count:expected=3:got={len(escalation)}")

    gov_rules = contract.get("governance_rules") or {}
    expected_rules = {
        "visibility_completeness",
        "intervention_audit",
        "intervention_approval",
        "escalation_determinism",
        "no_silent_override",
    }
    missing_rules = sorted(expected_rules - set(gov_rules))
    if missing_rules:
        raise SystemExit(f"executive_oversight_missing_rules:{','.join(missing_rules)}")

    payload = {
        "contract_id": contract["contract"]["id"],
        "oversight_query_count": len(queries),
        "intervention_primitive_count": len(interventions),
        "escalation_path_count": len(escalation),
        "governance_rule_count": len(gov_rules),
        "queries": [q["id"] for q in queries],
        "interventions": [i["id"] for i in interventions],
    }

    output_path = (
        repo_root / "configs" / "generated" / "executive_oversight_contract_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASSED",
        f"contract={payload['contract_id']}",
        f"queries={payload['oversight_query_count']}",
        f"interventions={payload['intervention_primitive_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
