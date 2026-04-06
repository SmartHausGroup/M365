from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore


def test_post_h5_builds_project_management_department_pack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("project-management", store=store)

    assert pack["department"]["id"] == "project-management"
    assert pack["summary"]["persona_count"] == 5
    assert pack["summary"]["active_persona_count"] == 5
    assert pack["summary"]["registry_backed_persona_count"] == 5
    assert pack["summary"]["supported_action_count"] == 40
    assert pack["summary"]["pack_state"] == "ready"
    assert {persona["coverage_status"] for persona in pack["personas"]} == {"registry-backed"}


def test_post_h5_project_management_pack_personas_are_all_active_without_queue_pressure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    pack = build_department_pack("project-management", store=JsonStore(tmp_path))

    assert pack["summary"]["pack_state"] == "ready"
    assert all(persona["status"] == "active" for persona in pack["personas"])
    assert [persona["persona_id"] for persona in pack["personas"]] == [
        "experiment-tracker",
        "project-shipper",
        "studio-producer",
        "project-coordination-agent",
        "project-manager",
    ]


def test_post_h5_project_management_fails_closed_on_declared_action_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_project_management_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["experiment-tracker"]["supported_actions"] = payload["personas"][
        "experiment-tracker"
    ]["supported_actions"][:-1]
    payload["kpis"]["supported_action_count"] = 39

    overridden = tmp_path / "department_pack_project_management_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError, match="department_pack_persona_action_mismatch:experiment-tracker"
    ):
        build_department_pack("project-management", path=overridden)


def test_post_h5_project_management_fails_closed_when_registry_backed_persona_is_reclassified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_project_management_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["experiment-tracker"]["coverage_status"] = "persona-contract-only"

    overridden = tmp_path / "department_pack_project_management_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="department_pack_persona_contract_only_has_actions:experiment-tracker",
    ):
        build_department_pack("project-management", path=overridden)
