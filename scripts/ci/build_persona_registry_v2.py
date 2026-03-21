from __future__ import annotations

import json
from pathlib import Path

import yaml

from ops_adapter.personas import build_authoritative_persona_registry_document


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    registry_path = root / "registry" / "agents.yaml"
    ai_team_path = root / "registry" / "ai_team.json"
    persona_map_path = root / "registry" / "persona_capability_map.yaml"
    output_path = root / "registry" / "persona_registry_v2.yaml"

    with registry_path.open(encoding="utf-8") as handle:
        registry = yaml.safe_load(handle)
    with ai_team_path.open(encoding="utf-8") as handle:
        ai_team = json.load(handle)
    with persona_map_path.open(encoding="utf-8") as handle:
        persona_map = yaml.safe_load(handle)

    payload = build_authoritative_persona_registry_document(
        registry,
        ai_team=ai_team,
        persona_map=persona_map,
    )
    output_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    print(f"Wrote {output_path} with {len(payload['personas'])} personas.")


if __name__ == "__main__":
    main()
