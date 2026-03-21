#!/usr/bin/env python3
"""
M365 audit verification (INV-M365-AUDIT-001, Eq. 5).

Produces configs/generated/m365_audit_verification.json.
Verifies that when audit is enabled, each log_event call produces exactly one record
with the unified audit schema v2. Uses in-process log_event; no server.

Run: python scripts/ci/verify_m365_audit.py
  Optional: ENABLE_AUDIT_LOGGING=1 (default for this script); APP_DATA for audit path.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = REPO_ROOT / "configs" / "generated" / "m365_audit_verification.json"


def verify_audit_writer() -> dict:
    """Enable audit, call log_event twice, assert two new lines with unified schema."""
    # Set env before importing so audit module sees it
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["ENABLE_AUDIT_LOGGING"] = "1"
        os.environ["APP_DATA"] = tmp
        # Ensure we're not importing cached module with old env
        if "provisioning_api.audit" in sys.modules:
            del sys.modules["provisioning_api.audit"]
        from provisioning_api.audit import _paths, log_event

        jpath, _ = _paths()
        jpath.parent.mkdir(parents=True, exist_ok=True)
        initial_lines = len(jpath.read_text().splitlines()) if jpath.exists() else 0

        log_event(
            "m365_instruction",
            {
                "action": "list_users",
                "params": {},
                "ok": True,
                "result": {"users": [], "count": 0},
                "trace_id": "trace-1",
            },
            user_info={"userPrincipalName": "test@test"},
        )
        log_event(
            "m365_instruction",
            {
                "action": "get_user",
                "params": {},
                "ok": False,
                "error": "not_found",
                "trace_id": "trace-2",
            },
            user_info={},
        )

        if not jpath.exists():
            return {"audit_pass": False, "error": "audit file not created"}

        lines = jpath.read_text().splitlines()
        new_lines = lines[initial_lines:]
        if len(new_lines) != 2:
            return {"audit_pass": False, "expected": 2, "got": len(new_lines)}

        required_keys = {
            "schema_version",
            "timestamp",
            "ts",
            "correlation_id",
            "surface",
            "action",
            "status",
            "user",
            "details",
            "result",
        }
        for i, line in enumerate(new_lines):
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                return {"audit_pass": False, "line": i, "parse_error": str(e)}
            if not required_keys.issubset(rec.keys()):
                return {
                    "audit_pass": False,
                    "line": i,
                    "missing_keys": list(required_keys - rec.keys()),
                }

        return {
            "audit_pass": True,
            "records_checked": 2,
            "schema": "schema_version, timestamp, ts, correlation_id, surface, action, status, user, details, result",
        }


def main() -> int:
    # Add src to path so provisioning_api is importable
    src = REPO_ROOT / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

    try:
        artifact = verify_audit_writer()
    except Exception as e:
        artifact = {"audit_pass": False, "error": str(e)}

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2))
    print(f"Artifact written: {ARTIFACT_PATH}")

    if not artifact.get("audit_pass"):
        print("Audit verification FAILED", file=sys.stderr)
        return 1
    print("Audit verification PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
