"""Tests for P2D specialist and regulated persona activation."""

from __future__ import annotations

from pathlib import Path

import yaml

P2D_ACTIVATED: dict[str, tuple[int, str]] = {
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

P2D_BLOCKED = [
    "instagram-curator",
    "tiktok-strategist",
    "reddit-community-builder",
    "twitter-engager",
    "app-store-optimizer",
]


def _load() -> tuple[dict, dict, dict]:
    repo = Path(__file__).resolve().parents[1]
    agents = yaml.safe_load((repo / "registry" / "agents.yaml").read_text())["agents"]
    persona_reg = yaml.safe_load((repo / "registry" / "persona_registry_v2.yaml").read_text())[
        "personas"
    ]
    cap_map = yaml.safe_load((repo / "registry" / "persona_capability_map.yaml").read_text())
    return agents, persona_reg, cap_map


def test_p2d_all_activated_personas_registry_backed() -> None:
    _agents, persona_reg, _cap_map = _load()
    for pid in P2D_ACTIVATED:
        assert persona_reg[pid]["coverage_status"] == "registry-backed", pid
        assert persona_reg[pid]["status"] == "active", pid


def test_p2d_action_counts_match() -> None:
    agents, _persona_reg, _cap_map = _load()
    for pid, (expected, _dept) in P2D_ACTIVATED.items():
        actual = len(agents[pid]["allowed_actions"])
        assert actual == expected, f"{pid}: {actual} != {expected}"


def test_p2d_capability_map_parity() -> None:
    _agents, _persona_reg, cap_map = _load()
    for pid, (expected, dept) in P2D_ACTIVATED.items():
        c = cap_map["departments"][dept]["personas"][pid]
        assert c["coverage_status"] == "registry-backed", pid
        assert c["current_action_count"] == expected, pid


def test_p2d_total_actions() -> None:
    agents, _persona_reg, _cap_map = _load()
    total = sum(len(agents[pid]["allowed_actions"]) for pid in P2D_ACTIVATED)
    assert total == 122


def test_p2d_blocked_personas_stay_contract_only() -> None:
    agents, persona_reg, _cap_map = _load()
    for pid in P2D_BLOCKED:
        assert persona_reg[pid]["coverage_status"] == "persona-contract-only", pid
        assert len(agents[pid]["allowed_actions"]) == 0, pid


def test_p2d_high_risk_personas_have_approval_rules() -> None:
    agents, _persona_reg, _cap_map = _load()
    for pid in ["finance-tracker", "legal-compliance-checker", "infrastructure-maintainer"]:
        assert "approval_rules" in agents[pid], f"{pid} missing approval_rules"
        assert len(agents[pid]["approval_rules"]) >= 1, pid


def test_p2d_routing_coverage() -> None:
    repo = Path(__file__).resolve().parents[1]
    agents = yaml.safe_load((repo / "registry" / "agents.yaml").read_text())["agents"]
    routing = yaml.safe_load((repo / "registry" / "executor_routing_v2.yaml").read_text())
    prefix_routes = routing["prefix_routes"]
    for pid in P2D_ACTIVATED:
        for action in agents[pid]["allowed_actions"]:
            prefix = action.split(".")[0] + "."
            assert prefix in prefix_routes, f"{pid}: {action} unroutable"


def test_p2d_department_packs_updated() -> None:
    repo = Path(__file__).resolve().parents[1]
    for dept in [
        "engineering",
        "testing",
        "studio_operations",
        "design",
        "project_management",
        "product",
    ]:
        pack = yaml.safe_load((repo / "registry" / f"department_pack_{dept}_v1.yaml").read_text())
        assert pack["kpis"]["supported_action_count"] > 0, dept
