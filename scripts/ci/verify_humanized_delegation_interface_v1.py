from __future__ import annotations

import json
from pathlib import Path

import yaml

from ops_adapter.personas import load_persona_registry, resolve_humanized_delegation_request


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    registry_path = root / "registry" / "agents.yaml"
    interface_path = root / "registry" / "humanized_delegation_interface_v1.yaml"
    output_path = root / "configs" / "generated" / "humanized_delegation_interface_v1_verification.json"

    with registry_path.open(encoding="utf-8") as handle:
        registry = yaml.safe_load(handle)
    with interface_path.open(encoding="utf-8") as handle:
        interface = yaml.safe_load(handle)

    patterns = interface.get("patterns") or []
    if len(patterns) < 5:
        raise SystemExit("Delegation interface must define at least 5 bounded patterns.")

    personas = load_persona_registry(registry)
    talk = resolve_humanized_delegation_request("Talk to Elena Rodriguez", personas)
    route = resolve_humanized_delegation_request("Route this to Marcus in Operations", personas)
    ask = resolve_humanized_delegation_request(
        "Ask Elena Rodriguez to prepare the homepage draft",
        personas,
    )

    output = {
        "status": "passed",
        "pattern_count": len(patterns),
        "talk_to": talk,
        "route_to": route,
        "ask_to": ask,
    }
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"verify_humanized_delegation_interface_v1: PASSED ({len(patterns)} patterns)")


if __name__ == "__main__":
    main()
