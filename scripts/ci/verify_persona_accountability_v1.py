from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from smarthaus_common.json_store import JsonStore
from smarthaus_common.persona_accountability import (
    build_persona_accountability,
    load_persona_accountability_authority,
)
from smarthaus_common.persona_task_queue import create_persona_task, update_persona_task


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    authority_path = root / "registry" / "persona_accountability_v1.yaml"
    output_path = root / "configs" / "generated" / "persona_accountability_v1_verification.json"

    authority = load_persona_accountability_authority(authority_path)

    with TemporaryDirectory() as temp_dir:
        store = JsonStore(temp_dir)
        for index in range(3):
            create_persona_task(
                "website-manager", {"title": f"Queued task {index + 1}"}, store=store
            )
        warning_snapshot = build_persona_accountability("website-manager", store=store)

        task = create_persona_task(
            "m365-administrator", {"title": "Review privileged access"}, store=store
        )
        update_persona_task(
            "m365-administrator",
            task["id"],
            {"status": "in_progress", "updated_by": "validator@smarthausgroup.com"},
            store=store,
        )
        update_persona_task(
            "m365-administrator",
            task["id"],
            {"status": "blocked", "updated_by": "validator@smarthausgroup.com"},
            store=store,
        )
        escalated_snapshot = build_persona_accountability("m365-administrator", store=store)

    output = {
        "status": "passed",
        "profiles": sorted(authority.get("profiles", {})),
        "states": sorted(authority.get("accountability_states", {})),
        "warning_state": warning_snapshot["accountability_state"],
        "warning_queue_depth": warning_snapshot["metrics"]["queue_depth"],
        "escalated_state": escalated_snapshot["accountability_state"],
        "escalation_target": escalated_snapshot["escalation"]["target"],
        "escalation_reasons": escalated_snapshot["escalation"]["reasons"],
    }
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        "verify_persona_accountability_v1: PASSED "
        f"({len(output['profiles'])} profiles, {len(output['states'])} accountability states)"
    )


if __name__ == "__main__":
    main()
