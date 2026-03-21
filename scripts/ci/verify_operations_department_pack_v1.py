from __future__ import annotations

import json
from pathlib import Path

from smarthaus_common.department_pack import build_department_pack, load_department_pack_authority


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    authority = load_department_pack_authority(
        "operations", path=repo_root / "registry" / "department_pack_operations_v1.yaml"
    )
    pack = build_department_pack("operations")

    summary = pack["summary"]
    if summary["persona_count"] != 2:
        raise SystemExit("operations_department_pack_persona_count_mismatch")
    if summary["supported_action_count"] != 43:
        raise SystemExit("operations_department_pack_supported_action_count_mismatch")

    payload = {
        "department": authority["department"]["id"],
        "pack_state": summary["pack_state"],
        "persona_count": summary["persona_count"],
        "active_persona_count": summary["active_persona_count"],
        "registry_backed_persona_count": summary["registry_backed_persona_count"],
        "supported_action_count": summary["supported_action_count"],
        "workflow_family_count": summary["workflow_family_count"],
        "workload_family_count": summary["workload_family_count"],
        "personas": [
            {
                "persona_id": persona["persona_id"],
                "status": persona["status"],
                "accountability_state": persona["accountability_state"],
                "action_count": persona["action_count"],
            }
            for persona in pack["personas"]
        ],
    }

    output_path = repo_root / "configs" / "generated" / "operations_department_pack_v1_verification.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASSED",
        f"department={payload['department']}",
        f"pack_state={payload['pack_state']}",
        f"supported_action_count={payload['supported_action_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
