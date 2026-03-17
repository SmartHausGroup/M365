#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from typing import Any

from smarthaus_graph.client import GraphClient


def load_services(path: str = "config/services.json") -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("services", [])


def _get_user_id(client: GraphClient, upn: str) -> str | None:
    try:
        r = client._request("GET", f"/users/{upn}", params={"$select": "id"})  # type: ignore[attr-defined]
        data = r.json()
        return data.get("id")
    except Exception:
        return None


def _list_group_owners(client: GraphClient, group_id: str) -> list[str]:
    try:
        r = client._request("GET", f"/groups/{group_id}/owners", params={"$select": "id"})  # type: ignore[attr-defined]
        data = r.json()
        return [o.get("id") for o in data.get("value", []) if o.get("id")]
    except Exception:
        return []


def _add_group_owner(client: GraphClient, group_id: str, user_id: str) -> bool:
    body = {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{user_id}"}
    try:
        client._request("POST", f"/groups/{group_id}/owners/$ref", json=body)  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


def ensure_team_and_channels(client: GraphClient, svc: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "key": svc.get("key"),
        "display_name": svc.get("display_name"),
        "mail_nickname": svc.get("mail_nickname"),
        "teamified": False,
        "channels_created": [],
        "error": None,
    }
    try:
        grp = client.find_group_by_mailnickname(svc.get("mail_nickname", ""))
        if not grp or not grp.get("id"):
            result["error"] = "group_not_found"
            return result
        group_id = grp.get("id")
        # Check if team exists
        try:
            _ = client.get_team(group_id)
            team_exists = True
        except Exception:
            team_exists = False

        if not team_exists:
            # Ensure at least one owner exists; if none, add OWNER_UPN
            owners = _list_group_owners(client, group_id)
            if not owners:
                owner_upn = os.getenv("OWNER_UPN", "phil@smarthausgroup.com")
                uid = _get_user_id(client, owner_upn)
                if not uid or not _add_group_owner(client, group_id, uid):
                    result["error"] = f"no_owner_and_add_failed:{owner_upn}"
                    return result
            try:
                client.teamify_group(group_id)
                result["teamified"] = True
            except Exception as e:
                result["error"] = f"teamify_failed:{e}"
                return result

        # Ensure channels
        try:
            existing = client.list_team_channels(group_id)
        except Exception as e:
            result["error"] = f"list_channels_failed:{e}"
            return result
        existing_names = {c.get("displayName", ""): c.get("id") for c in existing}
        for ch in svc.get("channels", []) or []:
            if ch.lower() == "general":
                continue
            if ch in existing_names:
                continue
            try:
                client.create_team_channel(group_id, ch, description=f"Channel for {svc.get('display_name')} - {ch}")
                result["channels_created"].append(ch)
            except Exception as e:
                # Collect but continue
                if not result.get("error"):
                    result["error"] = f"channel_create_partial:{e}"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def main() -> int:
    # Guard: ensure Graph creds exist
    missing = [k for k in ("GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET") if not os.getenv(k)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}", file=sys.stderr)
        return 2
    client = GraphClient()
    services = load_services()
    summary: list[dict[str, Any]] = []
    for svc in services:
        res = ensure_team_and_channels(client, svc)
        summary.append(res)
        print(json.dumps(res))
    # Final compact report
    report = {
        "updated": sum(1 for r in summary if r.get("teamified") or r.get("channels_created")),
        "errors": [r for r in summary if r.get("error")],
    }
    print("SUMMARY:", json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
