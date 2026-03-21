from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_task_queue import create_persona_task, update_persona_task


def test_e6b_builds_ready_hr_pack(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("hr", store=store)

    assert pack["department"]["id"] == "hr"
    assert pack["summary"]["persona_count"] == 1
    assert pack["summary"]["supported_action_count"] == 5
    assert pack["summary"]["pack_state"] == "ready"
    assert [persona["persona_id"] for persona in pack["personas"]] == ["hr-generalist"]


def test_e6b_marks_pack_watch_when_hr_queue_hits_warning_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    create_persona_task("hr-generalist", {"title": "Review onboarding packet"}, store)

    pack = build_department_pack("hr", store=store)

    assert pack["summary"]["pack_state"] == "watch"
    hr_generalist = pack["personas"][0]
    assert hr_generalist["accountability_state"] == "warning"


def test_e6b_marks_pack_attention_required_when_hr_work_is_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    task = create_persona_task("hr-generalist", {"title": "Process offboarding request"}, store)
    update_persona_task(
        "hr-generalist",
        task["id"],
        {"status": "in_progress", "updated_by": "owner@smarthausgroup.com"},
        store,
    )
    update_persona_task(
        "hr-generalist",
        task["id"],
        {"status": "blocked", "updated_by": "owner@smarthausgroup.com"},
        store,
    )

    pack = build_department_pack("hr", store=store)

    assert pack["summary"]["pack_state"] == "attention_required"
    assert pack["personas"][0]["accountability_state"] == "escalated"


def test_e6b_fails_closed_on_declared_action_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_hr_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["hr-generalist"]["supported_actions"] = [
        "employee.onboard",
        "employee.offboard",
    ]
    payload["kpis"]["supported_action_count"] = 2

    overridden = tmp_path / "department_pack_hr_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="department_pack_persona_action_mismatch:hr-generalist"):
        build_department_pack("hr", path=overridden)
