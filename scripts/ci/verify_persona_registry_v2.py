from __future__ import annotations

import json
from pathlib import Path

import yaml
from ops_adapter.personas import load_persona_registry, validate_persona_registry_document

DEFERRED = {
    "app-store-optimizer",
    "instagram-curator",
    "reddit-community-builder",
    "tiktok-strategist",
    "twitter-engager",
}


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    registry_path = root / "registry" / "agents.yaml"
    persona_registry_path = root / "registry" / "persona_registry_v2.yaml"
    ai_team_path = root / "registry" / "ai_team.json"
    promoted_records_path = root / "registry" / "authoritative_digital_employee_records_v1.yaml"
    output_path = (
        root
        / "configs"
        / "generated"
        / "authoritative_persona_registry_rebase_v1_verification.json"
    )

    with registry_path.open(encoding="utf-8") as handle:
        registry = yaml.safe_load(handle)
    with persona_registry_path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    with ai_team_path.open(encoding="utf-8") as handle:
        ai_team = json.load(handle)
    with promoted_records_path.open(encoding="utf-8") as handle:
        promoted_records = yaml.safe_load(handle)["records"]

    validate_persona_registry_document(payload)
    personas = load_persona_registry(registry, path=persona_registry_path)
    roster_ids = {
        str(member["agent"])
        for members in (ai_team.get("departments") or {}).values()
        if isinstance(members, list)
        for member in members
        if isinstance(member, dict) and member.get("agent")
    }
    persona_ids = set(personas)
    if persona_ids != roster_ids:
        missing = sorted(roster_ids - persona_ids)
        extra = sorted(persona_ids - roster_ids)
        raise SystemExit(
            f"Persona registry roster mismatch. missing={missing or []} extra={extra or []}"
        )

    active = sorted(
        persona_id
        for persona_id, persona in personas.items()
        if str(persona.get("status")) == "active"
    )
    planned = sorted(
        persona_id
        for persona_id, persona in personas.items()
        if str(persona.get("status")) == "planned"
    )
    promoted_ids = sorted(promoted_records)
    for persona_id in promoted_ids:
        persona = personas.get(persona_id)
        if persona is None:
            raise SystemExit(f"Promoted persona missing from authoritative registry: {persona_id}")
        if str(persona.get("status")) != "active":
            raise SystemExit(f"Promoted persona not active after H5: {persona_id}")
        if not list(persona.get("allowed_actions") or []):
            raise SystemExit(f"Promoted persona missing actions after H5: {persona_id}")

    if set(planned) != DEFERRED:
        raise SystemExit(f"Deferred persona set mismatch after H5: {planned}")

    expected_summary = {
        "total_personas": 59,
        "total_departments": 10,
        "active_personas": 54,
        "planned_personas": 5,
        "registry_backed_personas": 54,
        "persona_contract_only_personas": 5,
    }
    for key, expected_value in expected_summary.items():
        actual_value = payload.get("summary", {}).get(key)
        if actual_value != expected_value:
            raise SystemExit(
                f"Persona registry summary mismatch for {key}: {actual_value} != {expected_value}"
            )

    output = {
        "status": "passed",
        "total_personas": len(personas),
        "total_departments": len({str(persona.get("department")) for persona in personas.values()}),
        "active_personas": active,
        "planned_personas": planned,
        "promoted_personas": promoted_ids,
        "deferred_personas": sorted(DEFERRED),
        "required_fields": payload.get("required_fields") or [],
    }
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        "verify_persona_registry_v2: PASSED "
        f"({len(personas)} personas, {len(active)} active, {len(planned)} planned)"
    )


if __name__ == "__main__":
    main()
