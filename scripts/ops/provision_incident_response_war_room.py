#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from provisioning_api.routers.m365 import _graph_client, _normalize_params
from smarthaus_common.config import load_bootstrap_env
from smarthaus_common.incident_response_war_room import (
    IncidentResponseWarRoomRequest,
    provision_incident_response_war_room,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_bootstrap_env(_REPO_ROOT / ".env")
ucp_root = os.getenv("UCP_ROOT", "").strip()
if ucp_root:
    load_bootstrap_env(Path(ucp_root) / ".env")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Provision an incident response war room workflow."
    )
    parser.add_argument("--incident-name", required=True)
    parser.add_argument("--team-name", required=True)
    parser.add_argument("--site-name", required=True)
    parser.add_argument("--incident-lead", required=True)
    parser.add_argument("--mail-nickname")
    parser.add_argument("--command-channel-name", default="Command")
    parser.add_argument("--runbook-path")
    parser.add_argument("--plan-title")
    parser.add_argument("--bucket-name", default="Active Response")
    parser.add_argument("--seed-task-title", default="Establish incident command")
    parser.add_argument(
        "--seed-task-description",
        default="Open the incident bridge, assign owners, and start the response log.",
    )
    parser.add_argument("--activation-recipient", action="append")
    parser.add_argument("--activation-sender")
    parser.add_argument("--activation-subject")
    parser.add_argument("--skip-activation-mail", action="store_true")
    parser.add_argument("--force-send-activation", action="store_true")
    args = parser.parse_args()

    raw_params = {
        "incidentName": args.incident_name,
        "teamName": args.team_name,
        "siteName": args.site_name,
        "incidentLeadUpn": args.incident_lead,
        "commandChannelName": args.command_channel_name,
        "bucketName": args.bucket_name,
        "seedTaskTitle": args.seed_task_title,
        "seedTaskDescription": args.seed_task_description,
        "sendActivationMail": not args.skip_activation_mail,
        "forceSendActivation": args.force_send_activation,
    }
    if args.mail_nickname:
        raw_params["mailNickname"] = args.mail_nickname
    if args.runbook_path:
        raw_params["runbookPath"] = args.runbook_path
    if args.plan_title:
        raw_params["planTitle"] = args.plan_title
    if args.activation_recipient:
        raw_params["activationRecipients"] = args.activation_recipient
    if args.activation_sender:
        raw_params["activationSenderUserPrincipalName"] = args.activation_sender
    if args.activation_subject:
        raw_params["activationSubject"] = args.activation_subject

    normalized = _normalize_params("provision_incident_response_war_room", raw_params)
    result = provision_incident_response_war_room(
        workspace_client=_graph_client("create_site"),
        collaboration_client=_graph_client("create_team"),
        document_client=_graph_client("create_document"),
        planner_client=_graph_client("create_plan"),
        messaging_client=_graph_client("send_mail"),
        request=IncidentResponseWarRoomRequest(
            incident_name=normalized["incident_name"],
            team_name=normalized["team_name"],
            site_name=normalized["site_name"],
            mail_nickname=normalized["mail_nickname"],
            incident_lead_upn=normalized["incident_lead_upn"],
            command_channel_name=normalized["command_channel_name"],
            runbook_path=normalized["runbook_path"],
            plan_title=normalized["plan_title"],
            bucket_name=normalized["bucket_name"],
            seed_task_title=normalized["seed_task_title"],
            seed_task_description=normalized["seed_task_description"],
            activation_recipients=tuple(normalized["activation_recipients"]),
            activation_sender_user_id_or_upn=normalized["activation_sender_user_id_or_upn"],
            activation_subject=normalized["activation_subject"],
            send_activation_mail=normalized["send_activation_mail"],
            force_send_activation=normalized["force_send_activation"],
        ),
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
