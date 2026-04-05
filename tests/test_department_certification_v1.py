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

    dept_counts: dict[str, dict[str, int]] = {}
    for p in registry["personas"].values():
        d = p["department"]
        dept = dept_counts.setdefault(
            d,
            {
                "persona_count": 0,
                "active_persona_count": 0,
                "planned_persona_count": 0,
                "registry_backed_persona_count": 0,
                "contract_only_persona_count": 0,
            },
        )
        dept["persona_count"] += 1
        if p["status"] == "active":
            dept["active_persona_count"] += 1
        else:
            dept["planned_persona_count"] += 1
        if p["coverage_status"] == "registry-backed":
            dept["registry_backed_persona_count"] += 1
        else:
            dept["contract_only_persona_count"] += 1

    total = 0
    active_total = 0
    planned_total = 0
    registry_backed_total = 0
    contract_only_total = 0
    for dept_id, entry in contract["department_certification_status"].items():
        pack_name = f"department_pack_{dept_id.replace('-', '_')}_v1.yaml"
        pack = yaml.safe_load((REPO_ROOT / "registry" / pack_name).read_text(encoding="utf-8"))
        assert len(pack.get("personas", {})) == entry["persona_count"]
        assert entry["persona_count"] == dept_counts[dept_id]["persona_count"]
        assert entry["active_persona_count"] == dept_counts[dept_id]["active_persona_count"]
        assert entry["planned_persona_count"] == dept_counts[dept_id]["planned_persona_count"]
        assert (
            entry["registry_backed_persona_count"]
            == dept_counts[dept_id]["registry_backed_persona_count"]
        )
        assert (
            entry["contract_only_persona_count"]
            == dept_counts[dept_id]["contract_only_persona_count"]
        )
        assert entry["workflow_family_count"] == len(pack.get("workflow_families", []))
        assert entry["workload_family_count"] == len(pack.get("workload_families", []))
        assert entry["workflow_family_count"] > 0
        assert entry["workload_family_count"] > 0
        assert entry["department_status"] == pack["department"]["status"]
        total += entry["persona_count"]
        active_total += entry["active_persona_count"]
        planned_total += entry["planned_persona_count"]
        registry_backed_total += entry["registry_backed_persona_count"]
        contract_only_total += entry["contract_only_persona_count"]

    assert total == contract["kpis"]["total_department_personas"]
    assert active_total == contract["kpis"]["active_department_personas"]
    assert planned_total == contract["kpis"]["planned_department_personas"]
    assert registry_backed_total == contract["kpis"]["registry_backed_department_personas"]
    assert contract_only_total == contract["kpis"]["contract_only_department_personas"]
    assert len(contract["department_certification_status"]) == contract["kpis"]["total_departments"]
