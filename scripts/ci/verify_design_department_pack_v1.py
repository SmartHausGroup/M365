from __future__ import annotations

import json
from pathlib import Path

from smarthaus_common.department_pack import build_department_pack, load_department_pack_authority


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    authority = load_department_pack_authority(
        "design",
        path=repo_root / "registry" / "department_pack_design_v1.yaml",
    )
    pack = build_department_pack("design")

    summary = pack["summary"]
    if summary["persona_count"] != 5:
        raise SystemExit("design_department_pack_persona_count_mismatch")
    if summary["active_persona_count"] != 5:
        raise SystemExit("design_department_pack_active_count_mismatch")
    if summary["registry_backed_persona_count"] != 5:
        raise SystemExit("design_department_pack_registry_backed_count_mismatch")
    if summary["supported_action_count"] != 36:
        raise SystemExit("design_department_pack_supported_action_count_mismatch")
    if summary["pack_state"] != "ready":
        raise SystemExit("design_department_pack_expected_ready")

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
                "coverage_status": persona["coverage_status"],
                "accountability_state": persona["accountability_state"],
                "action_count": persona["action_count"],
            }
            for persona in pack["personas"]
        ],
    }

    output_path = (
        repo_root / "configs" / "generated" / "design_department_pack_v1_verification.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASSED",
        f"department={payload['department']}",
        f"pack_state={payload['pack_state']}",
        f"persona_count={payload['persona_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
