"""CI verifier for cross-department workflow certification contract v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "cross_department_certification_v1.yaml"
    if not contract_path.exists():
        print("FAILED: cross-department certification contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    # Validate root keys
    required_keys = {
        "version",
        "authority",
        "contract",
        "certification_phases",
        "governance_rules",
        "kpis",
        "cross_department_certification_summary",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing root keys: {sorted(missing)}")
        sys.exit(1)

    phases = contract["certification_phases"]
    if len(phases) != 4:
        print(f"FAILED: expected 4 phases, got {len(phases)}")
        sys.exit(1)

    expected_rules = {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "prerequisite_alignment",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    # Validate collaboration contract exists
    collab_path = repo_root / "registry" / "cross_persona_collaboration_contract_v1.yaml"
    if not collab_path.exists():
        print("FAILED: collaboration contract not found")
        sys.exit(1)
    collab = yaml.safe_load(collab_path.read_text(encoding="utf-8"))

    primitives = collab.get("collaboration_primitives", [])
    handoff_rules = collab.get("handoff_rules", [])

    kpis = contract["kpis"]
    if kpis["collaboration_primitive_count"] != len(primitives):
        print("FAILED: collaboration_primitive_count mismatch")
        sys.exit(1)
    if kpis["handoff_rule_count"] != len(handoff_rules):
        print("FAILED: handoff_rule_count mismatch")
        sys.exit(1)

    # Validate department certification prerequisite
    dept_cert_path = repo_root / "registry" / "department_certification_v1.yaml"
    if not dept_cert_path.exists():
        print("FAILED: department certification prerequisite not found")
        sys.exit(1)
    dept_cert = yaml.safe_load(dept_cert_path.read_text(encoding="utf-8"))
    dept_count = len(dept_cert["department_certification_status"])

    if kpis["certified_department_count"] != dept_count:
        print("FAILED: certified_department_count mismatch")
        sys.exit(1)

    summary = contract["cross_department_certification_summary"]
    if summary["overall_verdict"] != "certified":
        print("FAILED: overall verdict is not certified")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "certification_phase_count": len(phases),
        "governance_rule_count": len(contract["governance_rules"]),
        "collaboration_primitive_count": len(primitives),
        "handoff_rule_count": len(handoff_rules),
        "certified_department_count": dept_count,
        "overall_verdict": "certified",
    }

    output_path = (
        repo_root
        / "configs"
        / "generated"
        / "cross_department_certification_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"PASSED: cross-department certification '{contract['contract']['id']}' — "
        f"{len(phases)} phases, {len(contract['governance_rules'])} rules, "
        f"{len(primitives)} primitives, {len(handoff_rules)} handoff rules, "
        f"{dept_count} certified departments"
    )


if __name__ == "__main__":
    main()
