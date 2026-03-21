from __future__ import annotations

import json
from pathlib import Path

import yaml


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    # Load contract authority
    contract_path = repo_root / "registry" / "ucp_delegation_contract_v1.yaml"
    if not contract_path.exists():
        raise SystemExit("ucp_delegation_contract_authority_missing")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    # Validate required root keys
    required_keys = {
        "version",
        "authority",
        "contract",
        "delegation_phases",
        "governance_rules",
        "kpis",
        "bounded_claims",
    }
    missing = sorted(required_keys - set(contract))
    if missing:
        raise SystemExit(f"ucp_delegation_contract_missing_keys:{','.join(missing)}")

    # Validate delegation phases
    phases = contract.get("delegation_phases") or []
    if len(phases) != 6:
        raise SystemExit(f"ucp_delegation_contract_phase_count_mismatch:expected=6:got={len(phases)}")
    for i, phase in enumerate(phases):
        if phase.get("order") != i + 1:
            raise SystemExit(f"ucp_delegation_contract_phase_order_mismatch:{phase.get('id')}")
        for key in ("id", "description", "inputs", "outputs", "failure_mode"):
            if key not in phase:
                raise SystemExit(f"ucp_delegation_contract_phase_missing_key:{phase.get('id')}:{key}")

    # Validate governance rules
    rules = contract.get("governance_rules") or {}
    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "contract_only_handling",
        "approval_integrity",
        "idempotency",
    }
    missing_rules = sorted(expected_rules - set(rules))
    if missing_rules:
        raise SystemExit(f"ucp_delegation_contract_missing_rules:{','.join(missing_rules)}")

    # Validate KPIs against persona registry
    kpis = contract.get("kpis") or {}
    registry_path = repo_root / "registry" / "persona_registry_v2.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    registry_personas = registry.get("personas") or {}
    total_personas = len(registry_personas)
    contract_only = sum(
        1
        for p in registry_personas.values()
        if isinstance(p, dict) and p.get("coverage_status") == "persona-contract-only"
    )
    registry_backed = sum(
        1
        for p in registry_personas.values()
        if isinstance(p, dict) and p.get("coverage_status") == "registry-backed"
    )

    if kpis.get("supported_persona_count") != total_personas:
        raise SystemExit(
            f"ucp_delegation_contract_persona_count_mismatch:"
            f"contract={kpis.get('supported_persona_count')}:registry={total_personas}"
        )
    if kpis.get("contract_only_persona_count") != contract_only:
        raise SystemExit("ucp_delegation_contract_contract_only_count_mismatch")
    if kpis.get("registry_backed_persona_count") != registry_backed:
        raise SystemExit("ucp_delegation_contract_registry_backed_count_mismatch")

    payload = {
        "contract_id": contract["contract"]["id"],
        "delegation_phase_count": len(phases),
        "governance_rule_count": len(rules),
        "supported_persona_count": kpis["supported_persona_count"],
        "contract_only_persona_count": kpis["contract_only_persona_count"],
        "registry_backed_persona_count": kpis["registry_backed_persona_count"],
        "phases": [p["id"] for p in phases],
        "rules": sorted(rules.keys()),
    }

    output_path = (
        repo_root / "configs" / "generated" / "ucp_delegation_contract_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASSED",
        f"contract={payload['contract_id']}",
        f"phases={payload['delegation_phase_count']}",
        f"personas={payload['supported_persona_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
