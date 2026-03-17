#!/usr/bin/env python3
"""
Verify capability registry against CAIO-M365 contract (MA-aligned).

Ensures: every action in A (ACTION_SPECIFICATION.md implemented set) appears
in registry/capability_registry.yaml with status: implemented.
Optional: emit artifact for CI.

Run: python scripts/ci/verify_capability_registry.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "registry" / "capability_registry.yaml"
ARTIFACT_PATH = REPO_ROOT / "configs" / "generated" / "capability_registry_verification.json"

# Implemented set A from docs/contracts/caio-m365/ACTION_SPECIFICATION.md
IMPLEMENTED_ACTIONS = {
    "list_users",
    "list_teams",
    "list_sites",
    "get_user",
    "reset_user_password",
    "create_site",
    "create_team",
    "add_channel",
    "provision_service",
}


def load_registry() -> dict:
    try:
        import yaml
        return yaml.safe_load(REGISTRY_PATH.read_text())
    except Exception as e:
        print(f"verify_capability_registry: failed to load registry: {e}", file=sys.stderr)
        return {}


def verify() -> dict:
    """Check every implemented action is in registry with status implemented."""
    reg = load_registry()
    actions_list = reg.get("actions") or []
    by_action = {a["action"]: a for a in actions_list if isinstance(a, dict) and a.get("action")}

    missing = []
    not_implemented = []
    for name in IMPLEMENTED_ACTIONS:
        if name not in by_action:
            missing.append(name)
        elif by_action[name].get("status") != "implemented":
            not_implemented.append(name)

    passed = len(missing) == 0 and len(not_implemented) == 0
    implemented_in_registry = [a for a in actions_list if isinstance(a, dict) and a.get("status") == "implemented"]
    planned_count = sum(1 for a in actions_list if isinstance(a, dict) and a.get("status") == "planned")

    artifact = {
        "passed": passed,
        "implemented_expected": list(IMPLEMENTED_ACTIONS),
        "implemented_in_registry": [a["action"] for a in implemented_in_registry],
        "missing_from_registry": missing,
        "wrong_status": not_implemented,
        "planned_count": planned_count,
        "total_in_registry": len(actions_list),
    }
    return artifact


def main() -> int:
    artifact = verify()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2))

    if not artifact["passed"]:
        print("verify_capability_registry: FAILED", file=sys.stderr)
        if artifact["missing_from_registry"]:
            print("  missing_from_registry:", artifact["missing_from_registry"], file=sys.stderr)
        if artifact["wrong_status"]:
            print("  wrong_status (not implemented):", artifact["wrong_status"], file=sys.stderr)
        return 1
    print("verify_capability_registry: passed (implemented:", len(artifact["implemented_in_registry"]), "planned:", artifact["planned_count"], ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
