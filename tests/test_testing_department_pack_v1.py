from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore


def test_e6i_builds_blocked_testing_contract_pack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("testing", store=store)

    assert pack["department"]["id"] == "testing"
    assert pack["summary"]["persona_count"] == 5
    assert pack["summary"]["active_persona_count"] == 0
    assert pack["summary"]["registry_backed_persona_count"] == 0
    assert pack["summary"]["supported_action_count"] == 0
    assert pack["summary"]["pack_state"] == "blocked"
    assert {persona["coverage_status"] for persona in pack["personas"]} == {
        "persona-contract-only"
    }


def test_e6i_contract_only_pack_remains_blocked_even_without_queue_pressure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    pack = build_department_pack("testing", store=JsonStore(tmp_path))

    assert pack["summary"]["pack_state"] == "blocked"
    assert all(persona["status"] == "planned" for persona in pack["personas"])


def test_e6i_fails_closed_when_contract_only_persona_declares_actions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_testing_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["api-tester"]["supported_actions"] = ["testing.api.validate"]

    overridden = tmp_path / "department_pack_testing_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError, match="department_pack_persona_contract_only_has_actions:api-tester"
    ):
        build_department_pack("testing", path=overridden)


def test_e6i_fails_closed_on_declared_coverage_status_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_testing_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["api-tester"]["coverage_status"] = "registry-backed"

    overridden = tmp_path / "department_pack_testing_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError, match="department_pack_persona_registry_backed_missing_actions:api-tester"
    ):
        build_department_pack("testing", path=overridden)
