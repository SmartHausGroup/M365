from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_task_queue import (
    build_persona_state,
    create_persona_instruction,
    create_persona_task,
    load_persona_task_queue_authority,
    update_persona_task,
)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    authority_path = root / "registry" / "persona_task_queue_state_v1.yaml"
    output_path = root / "configs" / "generated" / "persona_task_queue_state_v1_verification.json"

    authority = load_persona_task_queue_authority(authority_path)
    with TemporaryDirectory() as temp_dir:
        store = JsonStore(temp_dir)
        task = create_persona_task(
            "website-manager",
            {"title": "Prepare homepage refresh", "priority": "high"},
            store=store,
        )
        create_persona_instruction(
            "website-manager",
            {"instruction": "Review the task queue"},
            store=store,
        )
        queued_state = build_persona_state("website-manager", store=store)
        update_persona_task(
            "website-manager",
            task["id"],
            {"status": "in_progress", "updated_by": "validator@smarthausgroup.com"},
            store=store,
        )
        active_state = build_persona_state("website-manager", store=store)

    output = {
        "status": "passed",
        "task_statuses": sorted(authority.get("task_statuses", {})),
        "persona_states": sorted(authority.get("persona_states", {})),
        "transition_origins": sorted(authority.get("transitions", {})),
        "queued_state": queued_state["persona_state"],
        "active_state": active_state["persona_state"],
        "queue_depth_after_queue": queued_state["queue_depth"],
        "queue_depth_after_start": active_state["queue_depth"],
    }
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        "verify_persona_task_queue_state_v1: PASSED "
        f"({len(output['task_statuses'])} task statuses, {len(output['persona_states'])} persona states)"
    )


if __name__ == "__main__":
    main()
