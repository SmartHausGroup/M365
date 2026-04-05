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
    dept_counts: dict[str, dict[str, int]] = {}
    for p in registry["personas"].values():
        d = p["department"]
        dept = dept_counts.setdefault(
            d,
            {
                "persona_count": 0,
                "active_persona_count": 0,
                "planned_persona_count": 0,
                "registry_backed_persona_count": 0,
                "contract_only_persona_count": 0,
            },
        )
        dept["persona_count"] += 1
        if p["status"] == "active":
            dept["active_persona_count"] += 1
        elif p["status"] == "planned":
            dept["planned_persona_count"] += 1
        else:
            print(f"FAILED: unexpected persona status for {p['persona_id']}: {p['status']}")
            sys.exit(1)
        if p["coverage_status"] == "registry-backed":
            dept["registry_backed_persona_count"] += 1
        elif p["coverage_status"] == "persona-contract-only":
            dept["contract_only_persona_count"] += 1
        else:
            print(
                f"FAILED: unexpected coverage_status for {p['persona_id']}: {p['coverage_status']}"
            )
            sys.exit(1)

    cert_status = contract["department_certification_status"]
    kpis = contract["kpis"]

    if len(cert_status) != kpis["total_departments"]:
        print("FAILED: total_departments mismatch")
        sys.exit(1)

    total_personas = 0
    active_personas = 0
    planned_personas = 0
    registry_backed_personas = 0
    contract_only_personas = 0
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

        registry_count = dept_counts.get(dept_id, {})
        if entry["persona_count"] != registry_count.get("persona_count", 0):
            print(
                "FAILED: "
                f"{dept_id} persona count {entry['persona_count']} != registry "
                f"{registry_count.get('persona_count', 0)}"
            )
            sys.exit(1)

        for key in (
            "active_persona_count",
            "planned_persona_count",
            "registry_backed_persona_count",
            "contract_only_persona_count",
        ):
            if entry[key] != registry_count.get(key, 0):
                print(
                    f"FAILED: {dept_id} {key} {entry[key]} != registry "
                    f"{registry_count.get(key, 0)}"
                )
                sys.exit(1)

        wf_count = len(pack.get("workflow_families", []))
        if wf_count != entry["workflow_family_count"]:
            print(f"FAILED: {dept_id} workflow_family_count mismatch")
            sys.exit(1)
        if wf_count == 0:
            print(f"FAILED: {dept_id} has zero workflow families")
            sys.exit(1)

        workload_count = len(pack.get("workload_families", []))
        if workload_count != entry["workload_family_count"]:
            print(f"FAILED: {dept_id} workload_family_count mismatch")
            sys.exit(1)
        if workload_count == 0:
            print(f"FAILED: {dept_id} has zero workload families")
            sys.exit(1)

        if entry["department_status"] != pack["department"]["status"]:
            print(f"FAILED: {dept_id} department_status mismatch")
            sys.exit(1)

        total_personas += entry["persona_count"]
        active_personas += entry["active_persona_count"]
        planned_personas += entry["planned_persona_count"]
        registry_backed_personas += entry["registry_backed_persona_count"]
        contract_only_personas += entry["contract_only_persona_count"]
        dept_names.append(dept_id)

    if total_personas != kpis["total_department_personas"]:
        print(
            f"FAILED: total department personas {total_personas} != {kpis['total_department_personas']}"
        )
        sys.exit(1)

    if active_personas != kpis["active_department_personas"]:
        print("FAILED: active_department_personas mismatch")
        sys.exit(1)

    if planned_personas != kpis["planned_department_personas"]:
        print("FAILED: planned_department_personas mismatch")
        sys.exit(1)

    if registry_backed_personas != kpis["registry_backed_department_personas"]:
        print("FAILED: registry_backed_department_personas mismatch")
        sys.exit(1)

    if contract_only_personas != kpis["contract_only_department_personas"]:
        print("FAILED: contract_only_department_personas mismatch")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "certification_phase_count": len(phases),
        "governance_rule_count": len(contract["governance_rules"]),
        "total_departments": len(cert_status),
        "total_department_personas": total_personas,
        "active_department_personas": active_personas,
        "planned_department_personas": planned_personas,
        "registry_backed_department_personas": registry_backed_personas,
        "contract_only_department_personas": contract_only_personas,
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
        f"{len(cert_status)} departments, {total_personas} total personas, "
        f"{active_personas} active / {planned_personas} planned"
    )


if __name__ == "__main__":
    main()
