from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml

REQUIRED_FIELDS = {
    "canonical_agent",
    "display_name",
    "slug",
    "department",
    "title",
    "manager",
    "escalation_owner",
    "working_style",
    "communication_style",
    "decision_style",
}

ALLOWED_DEPARTMENTS = {
    "operations",
    "hr",
    "communication",
    "engineering",
    "marketing",
    "project-management",
    "studio-operations",
}


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    artifact_path = root / "registry" / "authoritative_digital_employee_records_v1.yaml"
    output_path = (
        root
        / "configs"
        / "generated"
        / "authoritative_digital_employee_records_v1_verification.json"
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    records = payload.get("records") or {}
    if len(records) != 20:
        raise SystemExit(f"expected 20 employee records, found {len(records)}")

    required_fields = set(payload.get("required_fields") or [])
    if required_fields != REQUIRED_FIELDS:
        raise SystemExit("required_fields contract mismatch")

    bounded_fields = set(payload.get("bounded_humanization_fields") or [])
    if bounded_fields != {"working_style", "communication_style", "decision_style"}:
        raise SystemExit("bounded_humanization_fields contract mismatch")

    names: set[str] = set()
    slugs: set[str] = set()
    departments: Counter[str] = Counter()
    for agent_id, record in records.items():
        keys = set(record.keys())
        if keys != REQUIRED_FIELDS:
            raise SystemExit(f"{agent_id} field set mismatch: {sorted(keys)}")
        if record["canonical_agent"] != agent_id:
            raise SystemExit(f"{agent_id} canonical_agent mismatch")
        if record["department"] not in ALLOWED_DEPARTMENTS:
            raise SystemExit(f"{agent_id} invalid department {record['department']}")
        if record["manager"] != f"department-lead:{record['department']}":
            raise SystemExit(f"{agent_id} manager token mismatch")
        if record["escalation_owner"] != f"department-owner:{record['department']}":
            raise SystemExit(f"{agent_id} escalation_owner token mismatch")
        if not all(str(record[field]).strip() for field in REQUIRED_FIELDS):
            raise SystemExit(f"{agent_id} contains blank required fields")
        if record["display_name"] in names:
            raise SystemExit(f"duplicate display_name {record['display_name']}")
        if record["slug"] in slugs:
            raise SystemExit(f"duplicate slug {record['slug']}")
        names.add(record["display_name"])
        slugs.add(record["slug"])
        departments[record["department"]] += 1

    output = {
        "status": "passed",
        "total_promoted_personas": len(records),
        "departments_covered": dict(sorted(departments.items())),
        "manager_token_policy": payload["summary"]["manager_token_policy"],
        "escalation_token_policy": payload["summary"]["escalation_token_policy"],
        "bounded_humanization_fields": sorted(bounded_fields),
    }
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "verify_authoritative_digital_employee_records_v1: PASSED "
        f"({len(records)} records across {len(departments)} departments)"
    )


if __name__ == "__main__":
    main()
