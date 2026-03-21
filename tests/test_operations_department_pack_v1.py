from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from smarthaus_common.department_pack import build_department_pack
from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_task_queue import create_persona_task, update_persona_task


def test_e6a_builds_ready_operations_pack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    pack = build_department_pack("operations", store=store)

    assert pack["department"]["id"] == "operations"
    assert pack["summary"]["persona_count"] == 2
    assert pack["summary"]["supported_action_count"] == 43
    assert pack["summary"]["pack_state"] == "ready"
    assert [persona["persona_id"] for persona in pack["personas"]] == [
        "m365-administrator",
        "website-manager",
    ]


def test_e6a_marks_pack_watch_when_operations_queue_hits_warning_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    for index in range(3):
        create_persona_task("website-manager", {"title": f"Publish task {index + 1}"}, store)

    pack = build_department_pack("operations", store=store)

    assert pack["summary"]["pack_state"] == "watch"
    website_manager = next(
        persona for persona in pack["personas"] if persona["persona_id"] == "website-manager"
    )
    assert website_manager["accountability_state"] == "warning"


def test_e6a_marks_pack_attention_required_when_operations_work_is_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    store = JsonStore(tmp_path)

    task = create_persona_task("m365-administrator", {"title": "Review tenant access"}, store)
    update_persona_task(
        "m365-administrator",
        task["id"],
        {"status": "in_progress", "updated_by": "owner@smarthausgroup.com"},
        store,
    )
    update_persona_task(
        "m365-administrator",
        task["id"],
        {"status": "blocked", "updated_by": "owner@smarthausgroup.com"},
        store,
    )

    pack = build_department_pack("operations", store=store)

    assert pack["summary"]["pack_state"] == "attention_required"
    admin = next(persona for persona in pack["personas"] if persona["persona_id"] == "m365-administrator")
    assert admin["accountability_state"] == "escalated"


def test_e6a_fails_closed_on_declared_action_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

    source = Path("registry/department_pack_operations_v1.yaml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["personas"]["website-manager"]["supported_actions"] = [
        "deployment.preview",
        "content.update",
    ]
    payload["kpis"]["supported_action_count"] = 39

    overridden = tmp_path / "department_pack_operations_v1.yaml"
    overridden.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="department_pack_persona_action_mismatch:website-manager"):
        build_department_pack("operations", path=overridden)
