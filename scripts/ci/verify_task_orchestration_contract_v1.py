from __future__ import annotations

import json
from pathlib import Path

import yaml


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    contract_path = repo_root / "registry" / "task_orchestration_contract_v1.yaml"
    if not contract_path.exists():
        raise SystemExit("task_orchestration_contract_authority_missing")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "orchestration_primitives",
        "step_contract",
        "governance_rules",
        "kpis",
        "bounded_claims",
    }
    missing = sorted(required_keys - set(contract))
    if missing:
        raise SystemExit(f"task_orchestration_contract_missing_keys:{','.join(missing)}")

    primitives = contract.get("orchestration_primitives") or []
    if len(primitives) != 4:
        raise SystemExit(f"task_orchestration_primitive_count:expected=4:got={len(primitives)}")

    step = contract.get("step_contract") or {}
    states = step.get("step_states") or []
    if len(states) != 6:
        raise SystemExit(f"task_orchestration_step_state_count:expected=6:got={len(states)}")
    required_fields = step.get("required_fields") or []
    if len(required_fields) != 6:
        raise SystemExit(
            f"task_orchestration_required_field_count:expected=6:got={len(required_fields)}"
        )

    gov_rules = contract.get("governance_rules") or {}
    expected_rules = {
        "deterministic_ordering",
        "fail_closed_on_missing_persona",
        "audit_per_step",
        "no_implicit_escalation",
    }
    missing_rules = sorted(expected_rules - set(gov_rules))
    if missing_rules:
        raise SystemExit(f"task_orchestration_missing_rules:{','.join(missing_rules)}")

    payload = {
        "contract_id": contract["contract"]["id"],
        "primitive_count": len(primitives),
        "step_state_count": len(states),
        "governance_rule_count": len(gov_rules),
        "primitives": [p["id"] for p in primitives],
        "step_states": states,
    }

    output_path = (
        repo_root / "configs" / "generated" / "task_orchestration_contract_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASSED",
        f"contract={payload['contract_id']}",
        f"primitives={payload['primitive_count']}",
        f"states={payload['step_state_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
