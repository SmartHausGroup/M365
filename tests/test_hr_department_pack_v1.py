from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore


def test_post_h5_builds_hr_department_pack(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("hr", store=store)

    assert pack["department"]["id"] == "hr"
    assert pack["summary"]["persona_count"] == 2
    assert pack["summary"]["active_persona_count"] == 2
    assert pack["summary"]["registry_backed_persona_count"] == 2
    assert pack["summary"]["supported_action_count"] == 10
    assert pack["summary"]["pack_state"] == "ready"
    assert {persona["coverage_status"] for persona in pack["personas"]} == {"registry-backed"}


def test_post_h5_hr_pack_personas_are_all_active_without_queue_pressure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    pack = build_department_pack("hr", store=JsonStore(tmp_path))

    assert pack["summary"]["pack_state"] == "ready"
    assert all(persona["status"] == "active" for persona in pack["personas"])
    assert [persona["persona_id"] for persona in pack["personas"]] == [
        "hr-generalist",
        "recruitment-assistance-agent",
    ]


def test_post_h5_hr_fails_closed_on_declared_action_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_hr_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["hr-generalist"]["supported_actions"] = payload["personas"][
        "hr-generalist"
    ]["supported_actions"][:-1]
    payload["kpis"]["supported_action_count"] = 9

    overridden = tmp_path / "department_pack_hr_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="department_pack_persona_action_mismatch:hr-generalist"):
        build_department_pack("hr", path=overridden)


def test_post_h5_hr_fails_closed_when_registry_backed_persona_is_reclassified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_hr_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["hr-generalist"]["coverage_status"] = "persona-contract-only"

    overridden = tmp_path / "department_pack_hr_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="department_pack_persona_contract_only_has_actions:hr-generalist",
    ):
        build_department_pack("hr", path=overridden)
