"""Tests for activated persona surface certification v1."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFERRED = {
    "instagram-curator",
    "tiktok-strategist",
    "reddit-community-builder",
    "twitter-engager",
    "app-store-optimizer",
}


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "activated_persona_surface_v1.yaml").read_text()
    )


def _load_registries() -> tuple[dict, dict, dict]:
    persona_registry = yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_registry_v2.yaml").read_text()
    )
    capability_map = yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_capability_map.yaml").read_text()
    )
    agents = yaml.safe_load((REPO_ROOT / "registry" / "agents.yaml").read_text())["agents"]
    return persona_registry, capability_map, agents


def test_p2e_contract_has_required_root_keys() -> None:
    contract = _load_contract()
    assert {
        "version",
        "authority",
        "contract",
        "certification_phases",
        "governance_rules",
        "kpis",
        "activated_surface",
        "bounded_claims",
    } <= set(contract)


def test_p2e_active_deferred_partition_matches_registry() -> None:
    contract = _load_contract()
    persona_registry, capability_map, _agents = _load_registries()
    personas = persona_registry["personas"]
    active = {k for k, v in personas.items() if v["coverage_status"] == "registry-backed"}
    deferred = {k for k, v in personas.items() if v["coverage_status"] == "persona-contract-only"}
    assert len(active) == contract["activated_surface"]["registry_backed_personas"] == 34
    assert len(deferred) == contract["activated_surface"]["deferred_external_personas"] == 5
    assert capability_map["summary"]["current_registry_backed_personas"] == 34
    assert capability_map["summary"]["persona_contract_only_personas"] == 5


def test_p2e_deferred_persona_set_is_exact() -> None:
    contract = _load_contract()
    deferred = set(contract["activated_surface"]["deferred_external_persona_ids"])
    assert deferred == DEFERRED


def test_p2e_total_allowed_persona_actions_is_298() -> None:
    _persona_registry, _capability_map, agents = _load_registries()
    persona_registry = yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_registry_v2.yaml").read_text()
    )
    active_ids = [
        pid
        for pid, details in persona_registry["personas"].items()
        if details["coverage_status"] == "registry-backed"
    ]
    total = sum(len(agents[pid]["allowed_actions"]) for pid in active_ids)
    assert total == 298


def test_p2e_wave_scorecards_are_green() -> None:
    for lemma_id in ("l73", "l74", "l75"):
        scorecard = json.loads(
            (REPO_ROOT / "artifacts" / "scorecards" / f"scorecard_{lemma_id}.json").read_text()
        )
        assert scorecard["status"] == "green"


def test_p2e_docs_define_branch_specific_boundary() -> None:
    surface_doc = (
        REPO_ROOT / "docs" / "commercialization" / "m365-activated-persona-surface-v1.md"
    ).read_text()
    packaging_doc = (
        REPO_ROOT / "docs" / "commercialization" / "m365-workforce-packaging-v1.md"
    ).read_text()
    assert "34 registry-backed personas" in surface_doc
    assert "activated_persona_surface_v1.yaml" in packaging_doc


def test_p2e_all_departments_have_an_active_persona() -> None:
    persona_registry, _capability_map, _agents = _load_registries()
    departments = {
        details["department"]
        for details in persona_registry["personas"].values()
        if details["coverage_status"] == "registry-backed"
    }
    assert len(departments) == 10
