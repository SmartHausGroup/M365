"""Tests for department certification contract v1."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "department_certification_v1.yaml").read_text(encoding="utf-8")
    )


def _load_registry() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_registry_v2.yaml").read_text(encoding="utf-8")
    )


def test_e8c_certification_has_four_ordered_phases() -> None:
    contract = _load_contract()
    phases = contract["certification_phases"]
    assert len(phases) == 4
    assert [p["order"] for p in phases] == [1, 2, 3, 4]


def test_e8c_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "exhaustive_coverage",
    }


def test_e8c_all_departments_have_packs() -> None:
    contract = _load_contract()
    for dept_id in contract["department_certification_status"]:
        pack_name = f"department_pack_{dept_id.replace('-', '_')}_v1.yaml"
        assert (REPO_ROOT / "registry" / pack_name).exists(), f"missing {pack_name}"


def test_e8c_persona_counts_and_total() -> None:
    contract = _load_contract()
    registry = _load_registry()

    dept_counts: dict[str, int] = {}
    for p in registry["personas"].values():
        d = p["department"]
        dept_counts[d] = dept_counts.get(d, 0) + 1

    total = 0
    for dept_id, entry in contract["department_certification_status"].items():
        pack_name = f"department_pack_{dept_id.replace('-', '_')}_v1.yaml"
        pack = yaml.safe_load((REPO_ROOT / "registry" / pack_name).read_text(encoding="utf-8"))
        assert len(pack.get("personas", {})) == entry["persona_count"]
        assert entry["persona_count"] == dept_counts.get(dept_id, 0)
        assert entry["workflow_family_count"] > 0
        total += entry["persona_count"]

    assert total == contract["kpis"]["total_department_personas"]
    assert len(contract["department_certification_status"]) == contract["kpis"]["total_departments"]
