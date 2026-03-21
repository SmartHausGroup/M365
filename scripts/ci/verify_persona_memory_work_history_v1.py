from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_memory import (
    build_persona_work_history,
    create_persona_memory,
    load_persona_memory_authority,
)
from smarthaus_common.persona_task_queue import (
    create_persona_instruction,
    create_persona_task,
    update_persona_task,
)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    authority_path = root / "registry" / "persona_memory_work_history_v1.yaml"
    output_path = root / "configs" / "generated" / "persona_memory_work_history_v1_verification.json"

    authority = load_persona_memory_authority(authority_path)
    with TemporaryDirectory() as temp_dir:
        store = JsonStore(temp_dir)
        task = create_persona_task("website-manager", {"title": "Prepare launch site"}, store=store)
        update_persona_task(
            "website-manager",
            task["id"],
            {"status": "in_progress", "updated_by": "validator@smarthausgroup.com"},
            store=store,
        )
        create_persona_instruction(
            "website-manager",
            {"instruction": "Coordinate launch copy", "created_by": "validator@smarthausgroup.com"},
            store=store,
        )
        create_persona_memory(
            "website-manager",
            {
                "memory_type": "handoff",
                "content": "Escalate to brand review if copy changes again",
                "created_by": "validator@smarthausgroup.com",
            },
            store=store,
        )
        history = build_persona_work_history("website-manager", store=store)

    output = {
        "status": "passed",
        "memory_types": sorted(authority.get("memory_types", {})),
        "visibility_levels": sorted(authority.get("visibility_levels", {})),
        "memory_count": history["memory_count"],
        "event_count": history["event_count"],
        "event_types": sorted({event["event_type"] for event in history["history"]}),
        "accountability_state": history["accountability_state"],
    }
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        "verify_persona_memory_work_history_v1: PASSED "
        f"({len(output['memory_types'])} memory types, {output['event_count']} events)"
    )


if __name__ == "__main__":
    main()
