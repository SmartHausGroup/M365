from __future__ import annotations

import json
from pathlib import Path

import yaml
from ops_adapter.personas import load_persona_registry, validate_persona_registry_document


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    registry_path = root / "registry" / "agents.yaml"
    persona_registry_path = root / "registry" / "persona_registry_v2.yaml"
    ai_team_path = root / "registry" / "ai_team.json"
    output_path = root / "configs" / "generated" / "persona_registry_v2_verification.json"

    with registry_path.open(encoding="utf-8") as handle:
        registry = yaml.safe_load(handle)
    with persona_registry_path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    with ai_team_path.open(encoding="utf-8") as handle:
        ai_team = json.load(handle)

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

    output = {
        "status": "passed",
        "total_personas": len(personas),
        "total_departments": len({str(persona.get("department")) for persona in personas.values()}),
        "active_personas": active,
        "planned_personas": planned,
        "required_fields": payload.get("required_fields") or [],
    }
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        "verify_persona_registry_v2: PASSED "
        f"({len(personas)} personas, {len(active)} active, {len(planned)} planned)"
    )


if __name__ == "__main__":
    main()
