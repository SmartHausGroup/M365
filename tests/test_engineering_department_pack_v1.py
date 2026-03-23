from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore


def test_e6d_builds_blocked_engineering_contract_pack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("engineering", store=store)

    assert pack["department"]["id"] == "engineering"
    assert pack["summary"]["persona_count"] == 7
    assert pack["summary"]["active_persona_count"] == 2
    assert pack["summary"]["registry_backed_persona_count"] == 2
    assert pack["summary"]["supported_action_count"] == 23
    assert pack["summary"]["pack_state"] == "blocked"
    coverage_statuses = {persona["coverage_status"] for persona in pack["personas"]}
    assert coverage_statuses == {"registry-backed", "persona-contract-only"}


def test_e6d_contract_only_pack_remains_blocked_even_without_queue_pressure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    pack = build_department_pack("engineering", store=JsonStore(tmp_path))

    assert pack["summary"]["pack_state"] == "blocked"
    statuses = {persona["persona_id"]: persona["status"] for persona in pack["personas"]}
    assert statuses["backend-architect"] == "active"
    assert statuses["devops-automator"] == "active"
    assert statuses["frontend-developer"] == "planned"


def test_e6d_fails_closed_when_contract_only_persona_declares_actions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_engineering_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["ai-engineer"]["supported_actions"] = ["mail.send"]

    overridden = tmp_path / "department_pack_engineering_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError, match="department_pack_persona_contract_only_has_actions:ai-engineer"
    ):
        build_department_pack("engineering", path=overridden)


def test_e6d_fails_closed_on_declared_coverage_status_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_engineering_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["frontend-developer"]["coverage_status"] = "registry-backed"

    overridden = tmp_path / "department_pack_engineering_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="department_pack_persona_registry_backed_missing_actions:frontend-developer",
    ):
        build_department_pack("engineering", path=overridden)
