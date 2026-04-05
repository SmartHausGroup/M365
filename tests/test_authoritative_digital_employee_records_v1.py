from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = {
    "canonical_agent",
    "display_name",
    "slug",
    "department",
    "title",
    "manager",
    "escalation_owner",
    "working_style",
    "communication_style",
    "decision_style",
}


def _load_payload() -> dict:
    return yaml.safe_load(
        (REPO_ROOT / "registry" / "authoritative_digital_employee_records_v1.yaml").read_text(
            encoding="utf-8"
        )
    )


def test_h2_employee_record_count_and_department_summary() -> None:
    payload = _load_payload()
    records = payload["records"]
    assert len(records) == 20
    assert payload["summary"]["total_promoted_personas"] == 20
    assert payload["summary"]["departments_covered"] == 7


def test_h2_records_use_only_bounded_fields() -> None:
    payload = _load_payload()
    assert set(payload["required_fields"]) == REQUIRED_FIELDS
    assert set(payload["bounded_humanization_fields"]) == {
        "working_style",
        "communication_style",
        "decision_style",
    }
    for agent_id, record in payload["records"].items():
        assert set(record.keys()) == REQUIRED_FIELDS, agent_id


def test_h2_manager_and_escalation_tokens_match_department() -> None:
    payload = _load_payload()
    for agent_id, record in payload["records"].items():
        department = record["department"]
        assert record["manager"] == f"department-lead:{department}", agent_id
        assert record["escalation_owner"] == f"department-owner:{department}", agent_id


def test_h2_display_names_and_slugs_are_unique() -> None:
    payload = _load_payload()
    records = payload["records"].values()
    names = [record["display_name"] for record in records]
    slugs = [record["slug"] for record in payload["records"].values()]
    assert len(names) == len(set(names))
    assert len(slugs) == len(set(slugs))
