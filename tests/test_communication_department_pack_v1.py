from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_task_queue import create_persona_task, update_persona_task


def test_e6c_builds_ready_communication_pack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("communication", store=store)

    assert pack["department"]["id"] == "communication"
    assert pack["summary"]["persona_count"] == 1
    assert pack["summary"]["supported_action_count"] == 7
    assert pack["summary"]["pack_state"] == "ready"
    assert [persona["persona_id"] for persona in pack["personas"]] == ["outreach-coordinator"]


def test_e6c_marks_pack_watch_when_communication_queue_hits_warning_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    for index in range(2):
        create_persona_task(
            "outreach-coordinator",
            {"title": f"Prepare outbound campaign {index + 1}"},
            store,
        )

    pack = build_department_pack("communication", store=store)

    assert pack["summary"]["pack_state"] == "watch"
    assert pack["personas"][0]["accountability_state"] == "warning"


def test_e6c_marks_pack_attention_required_when_communication_work_is_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    task = create_persona_task(
        "outreach-coordinator",
        {"title": "Send approved outbound campaign"},
        store,
    )
    update_persona_task(
        "outreach-coordinator",
        task["id"],
        {"status": "in_progress", "updated_by": "owner@smarthausgroup.com"},
        store,
    )
    update_persona_task(
        "outreach-coordinator",
        task["id"],
        {"status": "blocked", "updated_by": "owner@smarthausgroup.com"},
        store,
    )

    pack = build_department_pack("communication", store=store)

    assert pack["summary"]["pack_state"] == "attention_required"
    assert pack["personas"][0]["accountability_state"] == "escalated"


def test_e6c_fails_closed_on_declared_action_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_communication_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["outreach-coordinator"]["supported_actions"] = [
        "email.send_individual",
        "mail.send",
    ]
    payload["kpis"]["supported_action_count"] = 2

    overridden = tmp_path / "department_pack_communication_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(
        ValueError, match="department_pack_persona_action_mismatch:outreach-coordinator"
    ):
        build_department_pack("communication", path=overridden)
