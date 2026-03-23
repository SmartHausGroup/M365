"""CI verifier for P2D specialist and regulated persona activation."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


def main() -> int:
    repo = Path(__file__).resolve().parents[2]

    agents = yaml.safe_load((repo / "registry" / "agents.yaml").read_text())["agents"]
    persona_reg_full = yaml.safe_load((repo / "registry" / "persona_registry_v2.yaml").read_text())
    persona_reg = persona_reg_full["personas"]
    cap_map = yaml.safe_load((repo / "registry" / "persona_capability_map.yaml").read_text())
    routing = yaml.safe_load((repo / "registry" / "executor_routing_v2.yaml").read_text())
    prefix_routes = routing["prefix_routes"]

    ACTIVATED: dict[str, tuple[int, str]] = {
        "ai-engineer": (10, "engineering"),
        "frontend-developer": (7, "engineering"),
        "mobile-app-builder": (7, "engineering"),
        "rapid-prototyper": (8, "engineering"),
        "test-writer-fixer": (7, "engineering"),
        "performance-benchmarker": (8, "testing"),
        "test-results-analyzer": (7, "testing"),
        "tool-evaluator": (7, "testing"),
        "workflow-optimizer": (8, "testing"),
        "finance-tracker": (8, "studio-operations"),
        "infrastructure-maintainer": (8, "studio-operations"),
        "legal-compliance-checker": (8, "studio-operations"),
        "visual-storyteller": (7, "design"),
        "whimsy-injector": (7, "design"),
        "experiment-tracker": (8, "project-management"),
        "trend-researcher": (7, "product"),
    }
    BLOCKED = [
        "instagram-curator",
        "tiktok-strategist",
        "reddit-community-builder",
        "twitter-engager",
        "app-store-optimizer",
    ]

    results = []
    for pid, (expected, dept) in ACTIVATED.items():
        p = persona_reg[pid]
        a = agents[pid]
        c = cap_map["departments"][dept]["personas"][pid]
        actual = len(a["allowed_actions"])
        routable = all(act.split(".")[0] + "." in prefix_routes for act in a["allowed_actions"])
        ok = (
            p["coverage_status"] == "registry-backed"
            and p["status"] == "active"
            and actual == expected
            and c["coverage_status"] == "registry-backed"
            and c["current_action_count"] == expected
            and routable
        )
        results.append(
            {
                "persona": pid,
                "department": dept,
                "expected_actions": expected,
                "actual_actions": actual,
                "registry_backed": p["coverage_status"] == "registry-backed",
                "routable": routable,
                "status": "passed" if ok else "FAILED",
            }
        )
        if not ok:
            print(f"FAILED {pid}: expected={expected} actual={actual} routable={routable}")
            return 1

    blocked_results = []
    for pid in BLOCKED:
        p = persona_reg[pid]
        a = agents[pid]
        ok = p["coverage_status"] == "persona-contract-only" and len(a["allowed_actions"]) == 0
        blocked_results.append({"persona": pid, "contract_only": ok})
        if not ok:
            print(f"FAILED blocked check: {pid}")
            return 1

    # --- Verify authoritative registry summary counts ---
    reg_summary = persona_reg_full["summary"]
    if reg_summary.get("registry_backed_personas") != 34:
        print(
            f"FAILED persona_registry summary: registry_backed={reg_summary.get('registry_backed_personas')} expected=34"
        )
        return 1
    if reg_summary.get("persona_contract_only_personas") != 5:
        print(
            f"FAILED persona_registry summary: contract_only={reg_summary.get('persona_contract_only_personas')} expected=5"
        )
        return 1

    cap_summary = cap_map["summary"]
    if cap_summary.get("current_registry_backed_personas") != 34:
        print(
            f"FAILED capability_map summary: registry_backed={cap_summary.get('current_registry_backed_personas')} expected=34"
        )
        return 1
    if cap_summary.get("persona_contract_only_personas") != 5:
        print(
            f"FAILED capability_map summary: contract_only={cap_summary.get('persona_contract_only_personas')} expected=5"
        )
        return 1

    total = sum(r["actual_actions"] for r in results)
    verification = {
        "plan_ref": "plan:m365-post-expansion-promotion-and-persona-activation:P2D",
        "activated_count": len(ACTIVATED),
        "blocked_count": len(BLOCKED),
        "total_new_actions": total,
        "registry_backed_total": 34,
        "activated": results,
        "blocked": blocked_results,
    }

    out = (
        repo / "configs" / "generated" / "p2d_specialist_regulated_activation_v1_verification.json"
    )
    out.write_text(json.dumps(verification, indent=2) + "\n")

    print(
        f"PASSED p2d_activation activated={len(ACTIVATED)} blocked={len(BLOCKED)} "
        f"total_new_actions={total} registry_backed_total=34"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
