"""CI verifier for P2C commercial growth and experience activation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def main() -> int:
    repo = Path(__file__).resolve().parents[2]

    agents = yaml.safe_load((repo / "registry" / "agents.yaml").read_text())["agents"]
    persona_reg = yaml.safe_load(
        (repo / "registry" / "persona_registry_v2.yaml").read_text()
    )["personas"]
    cap_map = yaml.safe_load(
        (repo / "registry" / "persona_capability_map.yaml").read_text()
    )

    P2C = {
        "content-creator": (8, "marketing"),
        "growth-hacker": (10, "marketing"),
        "ui-designer": (7, "design"),
        "brand-guardian": (8, "design"),
        "feedback-synthesizer": (7, "product"),
        "sprint-prioritizer": (8, "product"),
        "ux-researcher": (7, "design"),
        "studio-producer": (9, "project-management"),
    }

    results = []
    for pid, (expected, dept) in P2C.items():
        p = persona_reg[pid]
        a = agents[pid]
        c = cap_map["departments"][dept]["personas"][pid]
        actual = len(a["allowed_actions"])
        ok = (
            p["coverage_status"] == "registry-backed"
            and p["status"] == "active"
            and actual == expected
            and c["coverage_status"] == "registry-backed"
            and c["current_action_count"] == expected
        )
        results.append(
            {
                "persona": pid,
                "department": dept,
                "expected_actions": expected,
                "actual_actions": actual,
                "registry_backed": p["coverage_status"] == "registry-backed",
                "status": "passed" if ok else "FAILED",
            }
        )
        if not ok:
            print(f"FAILED {pid}: expected={expected} actual={actual}")
            return 1

    total = sum(r["actual_actions"] for r in results)
    verification = {
        "plan_ref": "plan:m365-post-expansion-promotion-and-persona-activation:P2C",
        "persona_count": len(P2C),
        "total_new_actions": total,
        "registry_backed_total": 18,
        "personas": results,
    }

    out = repo / "configs" / "generated" / "p2c_growth_experience_activation_v1_verification.json"
    out.write_text(json.dumps(verification, indent=2) + "\n")

    print(
        f"PASSED p2c_activation persona_count={len(P2C)} "
        f"total_new_actions={total} registry_backed_total=18"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
