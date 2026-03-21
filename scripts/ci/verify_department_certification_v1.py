"""CI verifier for department certification contract v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract_path = repo_root / "registry" / "department_certification_v1.yaml"
    if not contract_path.exists():
        print("FAILED: department certification contract not found")
        sys.exit(1)
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    required_keys = {
        "version",
        "authority",
        "contract",
        "certification_phases",
        "governance_rules",
        "kpis",
        "department_certification_status",
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
        "exhaustive_coverage",
    }
    if set(contract["governance_rules"].keys()) != expected_rules:
        print("FAILED: governance rules mismatch")
        sys.exit(1)

    registry = yaml.safe_load(
        (repo_root / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )
    dept_counts: dict[str, int] = {}
    for p in registry["personas"].values():
        d = p["department"]
        dept_counts[d] = dept_counts.get(d, 0) + 1

    cert_status = contract["department_certification_status"]
    kpis = contract["kpis"]

    if len(cert_status) != kpis["total_departments"]:
        print("FAILED: total_departments mismatch")
        sys.exit(1)

    total_personas = 0
    dept_names = []
    for dept_id, entry in cert_status.items():
        pack_name = f"department_pack_{dept_id.replace('-', '_')}_v1.yaml"
        pack_path = repo_root / "registry" / pack_name
        if not pack_path.exists():
            print(f"FAILED: missing pack file for {dept_id}")
            sys.exit(1)
        pack = yaml.safe_load(pack_path.read_text(encoding="utf-8"))

        pack_personas = len(pack.get("personas", {}))
        if pack_personas != entry["persona_count"]:
            print(
                f"FAILED: {dept_id} pack persona count {pack_personas} != {entry['persona_count']}"
            )
            sys.exit(1)

        registry_count = dept_counts.get(dept_id, 0)
        if entry["persona_count"] != registry_count:
            print(
                f"FAILED: {dept_id} persona count {entry['persona_count']} != registry {registry_count}"
            )
            sys.exit(1)

        wf_count = len(pack.get("workflow_families", []))
        if wf_count != entry["workflow_family_count"]:
            print(f"FAILED: {dept_id} workflow_family_count mismatch")
            sys.exit(1)
        if wf_count == 0:
            print(f"FAILED: {dept_id} has zero workflow families")
            sys.exit(1)

        total_personas += entry["persona_count"]
        dept_names.append(dept_id)

    if total_personas != kpis["total_department_personas"]:
        print(
            f"FAILED: total department personas {total_personas} != {kpis['total_department_personas']}"
        )
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "certification_phase_count": len(phases),
        "governance_rule_count": len(contract["governance_rules"]),
        "total_departments": len(cert_status),
        "total_department_personas": total_personas,
        "departments": sorted(dept_names),
    }

    output_path = (
        repo_root / "configs" / "generated" / "department_certification_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"PASSED: department certification '{contract['contract']['id']}' — "
        f"{len(phases)} phases, {len(contract['governance_rules'])} rules, "
        f"{len(cert_status)} departments, {total_personas} total personas"
    )


if __name__ == "__main__":
    main()
