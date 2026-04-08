#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from smarthaus_common.config import load_bootstrap_env
from provisioning_api.routers.m365 import _graph_client, _power_apps_client, _power_automate_client
from smarthaus_common.team_status_workflow import (
    TeamStatusWorkflowRequest,
    provision_team_status_workflow,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_bootstrap_env(_REPO_ROOT / ".env")
ucp_root = os.getenv("UCP_ROOT", "").strip()
if ucp_root:
    load_bootstrap_env(Path(ucp_root) / ".env")


def _datetime_value(raw: str, time_zone: str) -> dict[str, str]:
    return {"dateTime": raw, "timeZone": time_zone}


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision a weekly team status workflow.")
    parser.add_argument("--site-id", required=True)
    parser.add_argument("--organizer", required=True)
    parser.add_argument("--recipient", action="append", required=True)
    parser.add_argument("--meeting-start", required=True)
    parser.add_argument("--meeting-end", required=True)
    parser.add_argument("--meeting-subject", default="Weekly Team Status Meeting")
    parser.add_argument("--workflow-name", default="Weekly Team Status")
    parser.add_argument("--tracker-list-name", default="Weekly Team Status Tracker")
    parser.add_argument("--time-zone", default="Eastern Standard Time")
    parser.add_argument("--reminder-day", default="Friday")
    parser.add_argument("--reminder-hour", type=int, default=9)
    parser.add_argument("--reminder-minute", type=int, default=0)
    parser.add_argument("--digest-day", default="Friday")
    parser.add_argument("--digest-hour", type=int, default=16)
    parser.add_argument("--digest-minute", type=int, default=0)
    parser.add_argument("--site-url")
    args = parser.parse_args()

    result = provision_team_status_workflow(
        sharepoint_client=_graph_client("create_list"),
        messaging_client=_graph_client("create_event"),
        power_apps_client=_power_apps_client("list_powerapp_environments"),
        power_automate_client=_power_automate_client("list_flows_admin"),
        request=TeamStatusWorkflowRequest(
            site_id=args.site_id,
            site_url=args.site_url,
            organizer_user_id_or_upn=args.organizer,
            recipients=tuple(args.recipient),
            meeting_start=_datetime_value(args.meeting_start, args.time_zone),
            meeting_end=_datetime_value(args.meeting_end, args.time_zone),
            meeting_subject=args.meeting_subject,
            workflow_name=args.workflow_name,
            tracker_list_name=args.tracker_list_name,
            time_zone=args.time_zone,
            reminder_day=args.reminder_day,
            reminder_hour=args.reminder_hour,
            reminder_minute=args.reminder_minute,
            digest_day=args.digest_day,
            digest_hour=args.digest_hour,
            digest_minute=args.digest_minute,
            meeting_attendees=tuple(args.recipient),
        ),
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
