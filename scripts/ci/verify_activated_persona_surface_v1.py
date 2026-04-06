"""CI verifier for activated persona surface certification v1."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import yaml

DEFERRED = {
    "instagram-curator",
    "tiktok-strategist",
    "reddit-community-builder",
    "twitter-engager",
    "app-store-optimizer",
}


def main() -> None:
    repo = Path(__file__).resolve().parents[2]

    contract_path = repo / "registry" / "activated_persona_surface_v1.yaml"
    if not contract_path.exists():
        print("FAILED: activated persona surface contract not found")
        sys.exit(1)

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    persona_registry = yaml.safe_load((repo / "registry" / "persona_registry_v2.yaml").read_text())
    capability_map = yaml.safe_load((repo / "registry" / "persona_capability_map.yaml").read_text())
    agents = yaml.safe_load((repo / "registry" / "agents.yaml").read_text())["agents"]

    required_keys = {
        "version",
        "authority",
        "contract",
        "certification_phases",
        "governance_rules",
        "kpis",
        "activated_surface",
        "bounded_claims",
    }
    missing = required_keys - set(contract.keys())
    if missing:
        print(f"FAILED: missing contract keys: {sorted(missing)}")
        sys.exit(1)

    personas = persona_registry["personas"]
    active = {k: v for k, v in personas.items() if v["coverage_status"] == "registry-backed"}
    deferred = {
        k: v for k, v in personas.items() if v["coverage_status"] == "persona-contract-only"
    }

    if len(active) != 54:
        print(f"FAILED: expected 54 active personas, got {len(active)}")
        sys.exit(1)
    if len(deferred) != 5:
        print(f"FAILED: expected 5 deferred personas, got {len(deferred)}")
        sys.exit(1)
    if set(deferred) != DEFERRED:
        print(f"FAILED: deferred persona set mismatch: {sorted(deferred)}")
        sys.exit(1)

    total_actions = sum(len(agents[pid]["allowed_actions"]) for pid in active)
    if total_actions != 430:
        print(f"FAILED: expected 430 total persona actions, got {total_actions}")
        sys.exit(1)

    active_departments = Counter(v["department"] for v in active.values())
    if len(active_departments) != 10:
        print(f"FAILED: expected 10 active departments, got {len(active_departments)}")
        sys.exit(1)

    reg_summary = persona_registry["summary"]
    if (
        reg_summary["registry_backed_personas"] != 54
        or reg_summary["persona_contract_only_personas"] != 5
    ):
        print("FAILED: persona_registry summary mismatch")
        sys.exit(1)

    cap_summary = capability_map["summary"]
    if (
        cap_summary["current_registry_backed_personas"] != 54
        or cap_summary["persona_contract_only_personas"] != 5
    ):
        print("FAILED: capability_map summary mismatch")
        sys.exit(1)

    for pid in DEFERRED:
        if len(agents[pid]["allowed_actions"]) != 0:
            print(f"FAILED: deferred persona {pid} has non-zero allowed_actions")
            sys.exit(1)

    for lemma_id in ("l81",):
        scorecard_path = repo / "artifacts" / "scorecards" / f"scorecard_{lemma_id}.json"
        if not scorecard_path.exists():
            print(f"FAILED: missing scorecard {scorecard_path}")
            sys.exit(1)
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
        if scorecard["status"] != "green":
            print(f"FAILED: {scorecard_path.name} is not green")
            sys.exit(1)

    doc_text = (
        repo / "docs" / "commercialization" / "m365-activated-persona-surface-v1.md"
    ).read_text(encoding="utf-8")
    packaging_text = (
        repo / "docs" / "commercialization" / "m365-workforce-packaging-v1.md"
    ).read_text(encoding="utf-8")
    if "54 registry-backed personas" not in doc_text:
        print("FAILED: activated persona surface doc missing 54-person boundary")
        sys.exit(1)
    if "activated_persona_surface_v1.yaml" not in packaging_text:
        print("FAILED: packaging v1 doc missing branch-specific activated surface reference")
        sys.exit(1)

    output = {
        "contract_id": contract["contract"]["id"],
        "active_personas": len(active),
        "deferred_personas": len(deferred),
        "total_allowed_persona_actions": total_actions,
        "active_departments": dict(active_departments),
        "deferred_persona_ids": sorted(deferred),
        "scorecards_green": ["l81"],
    }
    output_path = repo / "configs" / "generated" / "activated_persona_surface_v1_verification.json"
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        "PASSED activated_persona_surface "
        f"active={len(active)} deferred={len(deferred)} "
        f"total_allowed_persona_actions={total_actions}"
    )


if __name__ == "__main__":
    main()
