from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore


def test_post_h5_builds_studio_operations_department_pack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("studio-operations", store=store)

    assert pack["department"]["id"] == "studio-operations"
    assert pack["summary"]["persona_count"] == 9
    assert pack["summary"]["active_persona_count"] == 9
    assert pack["summary"]["registry_backed_persona_count"] == 9
    assert pack["summary"]["supported_action_count"] == 61
    assert pack["summary"]["pack_state"] == "ready"
    assert {persona["coverage_status"] for persona in pack["personas"]} == {"registry-backed"}


def test_post_h5_studio_operations_pack_personas_are_all_active_without_queue_pressure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    pack = build_department_pack("studio-operations", store=JsonStore(tmp_path))

    assert pack["summary"]["pack_state"] == "ready"
    assert all(persona["status"] == "active" for persona in pack["personas"])
    assert [persona["persona_id"] for persona in pack["personas"]] == [
        "analytics-reporter",
        "finance-tracker",
        "infrastructure-maintainer",
        "legal-compliance-checker",
        "support-responder",
        "client-relationship-agent",
        "financial-operations-agent",
        "knowledge-management-agent",
        "reports",
    ]


def test_post_h5_studio_operations_fails_closed_on_declared_action_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_studio_operations_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["analytics-reporter"]["supported_actions"] = payload["personas"][
        "analytics-reporter"
    ]["supported_actions"][:-1]
    payload["kpis"]["supported_action_count"] = 60

    overridden = tmp_path / "department_pack_studio_operations_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError, match="department_pack_persona_action_mismatch:analytics-reporter"
    ):
        build_department_pack("studio-operations", path=overridden)


def test_post_h5_studio_operations_fails_closed_when_registry_backed_persona_is_reclassified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_studio_operations_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["analytics-reporter"]["coverage_status"] = "persona-contract-only"

    overridden = tmp_path / "department_pack_studio_operations_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="department_pack_persona_contract_only_has_actions:analytics-reporter",
    ):
        build_department_pack("studio-operations", path=overridden)
