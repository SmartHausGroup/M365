"""Tests for P2C commercial growth and experience activation."""

from __future__ import annotations

from pathlib import Path

import yaml


def _load_registries() -> tuple[dict, dict, dict]:
    repo = Path(__file__).resolve().parents[1]
    agents = yaml.safe_load((repo / "registry" / "agents.yaml").read_text())["agents"]
    persona_reg = yaml.safe_load((repo / "registry" / "persona_registry_v2.yaml").read_text())[
        "personas"
    ]
    cap_map = yaml.safe_load((repo / "registry" / "persona_capability_map.yaml").read_text())
    return agents, persona_reg, cap_map


P2C_PERSONAS = {
    "content-creator": (8, "marketing"),
    "growth-hacker": (10, "marketing"),
    "ui-designer": (7, "design"),
    "brand-guardian": (8, "design"),
    "feedback-synthesizer": (7, "product"),
    "sprint-prioritizer": (8, "product"),
    "ux-researcher": (7, "design"),
    "studio-producer": (9, "project-management"),
}


def test_p2c_all_personas_registry_backed() -> None:
    _agents, persona_reg, _cap_map = _load_registries()
    for pid, (_expected, _dept) in P2C_PERSONAS.items():
        assert persona_reg[pid]["coverage_status"] == "registry-backed", pid
        assert persona_reg[pid]["status"] == "active", pid


def test_p2c_action_counts_match() -> None:
    agents, _persona_reg, _cap_map = _load_registries()
    for pid, (expected, _dept) in P2C_PERSONAS.items():
        actual = len(agents[pid]["allowed_actions"])
        assert actual == expected, f"{pid}: {actual} != {expected}"


def test_p2c_capability_map_parity() -> None:
    agents, persona_reg, cap_map = _load_registries()
    for pid, (expected, dept) in P2C_PERSONAS.items():
        c = cap_map["departments"][dept]["personas"][pid]
        assert c["coverage_status"] == "registry-backed", pid
        assert c["current_action_count"] == expected, pid


def test_p2c_total_actions() -> None:
    agents, _, _ = _load_registries()
    total = sum(len(agents[pid]["allowed_actions"]) for pid in P2C_PERSONAS)
    assert total == 64


def test_p2c_growth_hacker_has_approval_rules() -> None:
    agents, _, _ = _load_registries()
    gh = agents["growth-hacker"]
    assert "approval_rules" in gh
    assert len(gh["approval_rules"]) >= 1


def test_p2c_department_packs_updated() -> None:
    repo = Path(__file__).resolve().parents[1]
    for dept in ["marketing", "design", "product", "project_management"]:
        pack = yaml.safe_load((repo / "registry" / f"department_pack_{dept}_v1.yaml").read_text())
        assert pack["kpis"]["supported_action_count"] > 0, dept


def test_p2c_routing_coverage() -> None:
    repo = Path(__file__).resolve().parents[1]
    agents = yaml.safe_load((repo / "registry" / "agents.yaml").read_text())["agents"]
    routing = yaml.safe_load((repo / "registry" / "executor_routing_v2.yaml").read_text())
    prefix_routes = routing["prefix_routes"]
    for pid in P2C_PERSONAS:
        for action in agents[pid]["allowed_actions"]:
            prefix = action.split(".")[0] + "."
            assert prefix in prefix_routes, f"{pid}: {action} unroutable"
