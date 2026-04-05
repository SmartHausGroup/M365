from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore


def test_h4s_builds_blocked_communication_department_pack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("communication", store=store)

    assert pack["department"]["id"] == "communication"
    assert pack["summary"]["persona_count"] == 4
    assert pack["summary"]["active_persona_count"] == 1
    assert pack["summary"]["registry_backed_persona_count"] == 1
    assert pack["summary"]["supported_action_count"] == 7
    assert pack["summary"]["pack_state"] == "blocked"
    assert {persona["coverage_status"] for persona in pack["personas"]} == {
        "registry-backed",
        "persona-contract-only",
    }


def test_h4s_communication_pack_remains_blocked_without_queue_pressure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    pack = build_department_pack("communication", store=JsonStore(tmp_path))

    assert pack["summary"]["pack_state"] == "blocked"
    statuses = {persona["persona_id"]: persona["status"] for persona in pack["personas"]}
    assert statuses["outreach-coordinator"] == "active"
    assert statuses["calendar-management-agent"] == "planned"


def test_h4s_communication_fails_closed_when_contract_only_persona_declares_actions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_communication_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["calendar-management-agent"]["supported_actions"] = ["mail.send"]

    overridden = tmp_path / "department_pack_communication_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="department_pack_persona_contract_only_has_actions:calendar-management-agent",
    ):
        build_department_pack("communication", path=overridden)


def test_h4s_communication_fails_closed_on_declared_coverage_status_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_communication_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["calendar-management-agent"]["coverage_status"] = "registry-backed"

    overridden = tmp_path / "department_pack_communication_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="department_pack_persona_registry_backed_missing_actions:calendar-management-agent",
    ):
        build_department_pack("communication", path=overridden)
