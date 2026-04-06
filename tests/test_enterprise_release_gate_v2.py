"""Tests for enterprise release gate v2."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_contract() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "enterprise_release_gate_v2.yaml").read_text(encoding="utf-8")
    )


def _load_persona_certification() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "persona_certification_v1.yaml").read_text(encoding="utf-8")
    )


def _load_department_certification() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "department_certification_v1.yaml").read_text(encoding="utf-8")
    )


def _load_workload_certification() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "workload_certification_v1.yaml").read_text(encoding="utf-8")
    )


def _load_activated_surface() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "activated_persona_surface_v1.yaml").read_text(encoding="utf-8")
    )


def _load_workforce_packaging() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "workforce_packaging_v1.yaml").read_text(encoding="utf-8")
    )


def test_e8e_gate_has_six_ordered_checks() -> None:
    contract = _load_contract()
    checks = contract["release_gate_checks"]
    assert len(checks) == 6
    assert [c["order"] for c in checks] == [1, 2, 3, 4, 5, 6]


def test_e8e_all_checks_green() -> None:
    contract = _load_contract()
    for check in contract["release_gate_checks"]:
        assert check["status"] == "green", f"check {check['id']} not green"


def test_e8e_governance_rules_complete() -> None:
    contract = _load_contract()
    assert set(contract["governance_rules"].keys()) == {
        "fail_closed",
        "audit_completeness",
        "bounded_claims",
        "determinism",
        "explicit_sign_off",
    }


def test_e8e_release_decision_go_with_gaps() -> None:
    contract = _load_contract()
    decision = contract["release_decision"]
    assert decision["verdict"] == "GO"
    assert len(decision["residual_gaps"]) > 0
    assert len(decision["conditions"]) > 0


def test_e8e_all_prerequisite_contracts_exist() -> None:
    prereqs = [
        "registry/workload_certification_v1.yaml",
        "registry/persona_certification_v1.yaml",
        "registry/department_certification_v1.yaml",
        "registry/cross_department_certification_v1.yaml",
        "registry/ucp_delegation_contract_v1.yaml",
        "registry/executive_oversight_contract_v1.yaml",
    ]
    for prereq in prereqs:
        assert (REPO_ROOT / prereq).exists(), f"missing: {prereq}"


def test_e8e_kpis_reconcile_to_certification_and_final_surfaces() -> None:
    contract = _load_contract()
    persona_cert = _load_persona_certification()
    department_cert = _load_department_certification()
    workload_cert = _load_workload_certification()
    activated_surface = _load_activated_surface()
    workforce_packaging = _load_workforce_packaging()

    kpis = contract["kpis"]
    persona_kpis = persona_cert["kpis"]
    department_kpis = department_cert["kpis"]
    workload_kpis = workload_cert["kpis"]
    activated_kpis = activated_surface["kpis"]
    packaging_kpis = workforce_packaging["kpis"]

    assert kpis["workload_domains_certified"] == workload_kpis["domains_with_routed_actions"]
    assert kpis["workload_domains_not_yet"] == workload_kpis["domains_without_routed_actions"]
    assert (
        kpis["personas_certified"]
        == persona_kpis["total_personas"]
        == activated_kpis["total_personas"]
        == packaging_kpis["total_persona_count"]
    )
    assert (
        kpis["active_personas_certified"]
        == persona_kpis["active_personas"]
        == department_kpis["active_department_personas"]
        == activated_kpis["certified_active_personas"]
        == packaging_kpis["active_persona_count"]
    )
    assert (
        kpis["planned_personas_certified"]
        == persona_kpis["planned_personas"]
        == department_kpis["planned_department_personas"]
        == activated_kpis["deferred_external_personas"]
        == packaging_kpis["planned_persona_count"]
    )
    assert (
        kpis["departments_certified"]
        == department_kpis["total_departments"]
        == activated_kpis["active_departments"]
        == packaging_kpis["department_count"]
    )
    assert (
        kpis["total_routed_actions"]
        == activated_kpis["total_allowed_persona_actions"]
        == packaging_kpis["total_routed_actions"]
    )


def test_e8e_release_boundary_is_final_post_h5_state() -> None:
    contract = _load_contract()
    rendered = yaml.safe_dump(contract, sort_keys=True)
    assert "pre-H5" not in rendered
    assert "before H5" not in rendered
    assert "34 active personas" not in rendered
    assert "298 routed actions" not in rendered
