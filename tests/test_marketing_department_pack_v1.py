from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore


def test_e6e_builds_blocked_marketing_contract_pack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("marketing", store=store)

    assert pack["department"]["id"] == "marketing"
    assert pack["summary"]["persona_count"] == 7
    assert pack["summary"]["active_persona_count"] == 0
    assert pack["summary"]["registry_backed_persona_count"] == 0
    assert pack["summary"]["supported_action_count"] == 0
    assert pack["summary"]["pack_state"] == "blocked"
    assert {persona["coverage_status"] for persona in pack["personas"]} == {
        "persona-contract-only"
    }


def test_e6e_contract_only_pack_remains_blocked_even_without_queue_pressure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    pack = build_department_pack("marketing", store=JsonStore(tmp_path))

    assert pack["summary"]["pack_state"] == "blocked"
    assert all(persona["status"] == "planned" for persona in pack["personas"])


def test_e6e_fails_closed_when_contract_only_persona_declares_actions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_marketing_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["growth-hacker"]["supported_actions"] = ["mail.send"]

    overridden = tmp_path / "department_pack_marketing_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError, match="department_pack_persona_contract_only_has_actions:growth-hacker"
    ):
        build_department_pack("marketing", path=overridden)


def test_e6e_fails_closed_on_declared_coverage_status_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_marketing_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["content-creator"]["coverage_status"] = "registry-backed"

    overridden = tmp_path / "department_pack_marketing_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError, match="department_pack_persona_registry_backed_missing_actions:content-creator"
    ):
        build_department_pack("marketing", path=overridden)
