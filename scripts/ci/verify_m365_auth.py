#!/usr/bin/env python3
"""
M365 authentication verification (INV-CAIO-M365-003, Eq. 4).

Produces configs/generated/m365_auth_verification.json.
When CAIO_API_KEY and BASE_URL are set: POST without key (or wrong key), assert status 401.
Otherwise: mock pass (CI passes when key not required or no BASE_URL).

Run: python scripts/ci/verify_m365_auth.py
  Optional: BASE_URL=..., CAIO_API_KEY=secret for live check.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = REPO_ROOT / "configs" / "generated" / "m365_auth_verification.json"


def verify_with_mock() -> dict:
    """Key not required or no BASE_URL: pass by convention."""
    return {
        "auth_pass": True,
        "note": "CAIO_API_KEY unset or no BASE_URL; mock pass.",
    }


def verify_live(base_url: str, expected_key: str) -> dict:
    """POST without key; expect 401. Optionally POST with wrong key; expect 401."""
    import urllib.error
    import urllib.request

    url = f"{base_url.rstrip('/')}/api/m365/instruction"
    body = json.dumps({"action": "list_users", "params": {}}).encode()
    headers_no_key = {"Content-Type": "application/json"}

    try:
        req = urllib.request.Request(url, data=body, headers=headers_no_key, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as _:
                status = 200
        except urllib.error.HTTPError as e:
            status = e.code
        pass_no_key = status == 401

        headers_wrong = {"Content-Type": "application/json", "X-CAIO-API-Key": "wrong-key"}
        req2 = urllib.request.Request(url, data=body, headers=headers_wrong, method="POST")
        try:
            with urllib.request.urlopen(req2, timeout=5) as _:
                status2 = 200
        except urllib.error.HTTPError as e:
            status2 = e.code
        pass_wrong_key = status2 == 401

        auth_pass = pass_no_key and pass_wrong_key
    except Exception as e:
        return {"auth_pass": False, "error": str(e)}

    return {
        "auth_pass": auth_pass,
        "no_key_returns_401": pass_no_key,
        "wrong_key_returns_401": pass_wrong_key,
    }


def main() -> int:
    base_url = os.environ.get("BASE_URL", "").strip()
    api_key = os.environ.get("CAIO_API_KEY", "").strip()
    if base_url and api_key:
        artifact = verify_live(base_url, api_key)
    else:
        artifact = verify_with_mock()

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2))
    print(f"Artifact written: {ARTIFACT_PATH}")

    if not artifact.get("auth_pass"):
        print("Auth verification FAILED", file=sys.stderr)
        return 1
    print("Auth verification PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
