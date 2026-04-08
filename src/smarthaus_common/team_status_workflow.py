from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from smarthaus_common.errors import SmarthausError
from smarthaus_common.power_apps_client import PowerAppsClient
from smarthaus_common.power_automate_client import PowerAutomateClient
from smarthaus_graph.client import GraphClient

_DEFAULT_TIME_ZONE = "Eastern Standard Time"
_IANA_TO_WINDOWS = {
    "America/New_York": "Eastern Standard Time",
    "UTC": "UTC",
}
_GRAPH_DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}
_FLOW_DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}
_FLOW_DEFINITION_SCHEMA = (
    "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/"
    "2016-06-01/workflowdefinition.json#"
)


@dataclass(frozen=True)
class TeamStatusWorkflowRequest:
    site_id: str
    organizer_user_id_or_upn: str
    recipients: tuple[str, ...]
    meeting_start: dict[str, Any]
    meeting_end: dict[str, Any]
    meeting_subject: str
    workflow_name: str
    tracker_list_name: str
    time_zone: str
    reminder_day: str
    reminder_hour: int
    reminder_minute: int
    digest_day: str
    digest_hour: int
    digest_minute: int
    meeting_attendees: tuple[str, ...]
    site_url: str | None = None


def default_tracker_columns() -> list[dict[str, Any]]:
    return [
        {"name": "ReportingWeek", "text": {"allowMultipleLines": False}},
        {"name": "StatusUpdate", "text": {"allowMultipleLines": True}},
        {"name": "Blockers", "text": {"allowMultipleLines": True}},
        {"name": "NextSteps", "text": {"allowMultipleLines": True}},
        {"name": "Confidence", "text": {"allowMultipleLines": False}},
        {"name": "NeedsHelp", "text": {"allowMultipleLines": False}},
    ]


def _normalize_windows_time_zone(value: str | None) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        return _DEFAULT_TIME_ZONE
    return _IANA_TO_WINDOWS.get(cleaned, cleaned)


def _parse_datetime(value: dict[str, Any]) -> datetime:
    raw = str(value.get("dateTime") or "").strip()
    if not raw:
        raise SmarthausError("team_status_workflow_invalid_datetime")
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def _join_recipients(recipients: tuple[str, ...]) -> str:
    return ";".join(recipient.strip() for recipient in recipients if recipient.strip())


def _flow_recurrence(day_name: str, hour: int, minute: int, time_zone: str) -> dict[str, Any]:
    recurrence = {
        "frequency": "Week",
        "interval": 1,
        "timeZone": _normalize_windows_time_zone(time_zone),
        "schedule": {
            "weekDays": [day_name],
            "hours": [str(hour)],
            "minutes": [minute],
        },
    }
    return {
        "Recurrence": {
            "recurrence": recurrence,
            "evaluatedRecurrence": recurrence,
            "type": "Recurrence",
        }
    }


def _environment_name(environment: dict[str, Any]) -> str:
    internal = environment.get("Internal", {})
    internal_name = ""
    if isinstance(internal, dict):
        internal_name = str(internal.get("name") or "").strip()
    return (
        str(environment.get("name") or "").strip()
        or str(environment.get("EnvironmentName") or "").strip()
        or internal_name
    )


def _environment_display_name(environment: dict[str, Any]) -> str:
    internal = environment.get("Internal", {})
    properties = internal.get("properties", {}) if isinstance(internal, dict) else {}
    internal_display = ""
    if isinstance(properties, dict):
        internal_display = str(properties.get("displayName") or "").strip()
    return (
        str(environment.get("displayName") or "").strip()
        or str(environment.get("DisplayName") or "").strip()
        or internal_display
    )


def _is_default_environment(environment: dict[str, Any]) -> bool:
    if bool(environment.get("IsDefault")):
        return True
    internal = environment.get("Internal", {})
    properties = internal.get("properties", {}) if isinstance(internal, dict) else {}
    if isinstance(properties, dict) and bool(properties.get("isDefault")):
        return True
    return _environment_name(environment).startswith("Default-")


def _tracker_summary_html(title: str) -> str:
    return (
        f"<p>{title}</p>"
        "@{if(empty(body('Get_tracker_items')?['value']),"
        "'<p>No updates were submitted for this period.</p>',"
        "outputs('Create_HTML_table'))}"
    )


def _flow_definition_envelope(
    *,
    description: str,
    triggers: dict[str, Any],
    actions: dict[str, Any],
) -> dict[str, Any]:
    return {
        "$schema": _FLOW_DEFINITION_SCHEMA,
        "contentVersion": "1.0.0.0",
        "description": description,
        "parameters": {
            "$connections": {"defaultValue": {}, "type": "Object"},
            "$authentication": {"defaultValue": {}, "type": "SecureObject"},
        },
        "triggers": triggers,
        "actions": actions,
        "outputs": {},
    }


def build_reminder_flow_definition(
    *,
    tracker_name: str,
    tracker_url: str,
    meeting_subject: str,
    meeting_link: str | None,
    recipients: tuple[str, ...],
    reminder_day: str,
    reminder_hour: int,
    reminder_minute: int,
    time_zone: str,
) -> dict[str, Any]:
    body = (
        f"<p>Please update the <a href=\"{tracker_url}\">{tracker_name}</a> "
        "before the weekly digest is sent.</p>"
    )
    if meeting_link:
        body += (
            f"<p>The recurring meeting \"{meeting_subject}\" is available here: "
            f"<a href=\"{meeting_link}\">Join meeting</a>.</p>"
        )
    return _flow_definition_envelope(
        description=f"Send a weekly reminder to update {tracker_name}.",
        triggers=_flow_recurrence(reminder_day, reminder_hour, reminder_minute, time_zone),
        actions={
            "Send_reminder_email": {
                "runAfter": {},
                "metadata": {"flowSystemMetadata": {"swaggerOperationId": "SendEmailV2"}},
                "type": "ApiConnection",
                "inputs": {
                    "host": {
                        "connection": {
                            "name": "@parameters('$connections')['shared_office365']['connectionId']"
                        }
                    },
                    "method": "post",
                    "body": {
                        "To": _join_recipients(recipients),
                        "Subject": f"Reminder: update the {tracker_name}",
                        "Body": body,
                        "Importance": "Normal",
                    },
                    "path": "/v2/Mail",
                    "authentication": "@parameters('$authentication')",
                },
            }
        },
    )


def build_digest_flow_definition(
    *,
    tracker_name: str,
    tracker_url: str,
    site_url: str,
    list_id: str,
    recipients: tuple[str, ...],
    digest_day: str,
    digest_hour: int,
    digest_minute: int,
    time_zone: str,
) -> dict[str, Any]:
    return _flow_definition_envelope(
        description=f"Send a weekly digest summarizing updates from {tracker_name}.",
        triggers=_flow_recurrence(digest_day, digest_hour, digest_minute, time_zone),
        actions={
            "Get_tracker_items": {
                "runAfter": {},
                "metadata": {"flowSystemMetadata": {"swaggerOperationId": "GetItems"}},
                "type": "ApiConnection",
                "inputs": {
                    "host": {
                        "connection": {
                            "name": "@parameters('$connections')['shared_sharepointonline']['connectionId']"
                        }
                    },
                    "method": "get",
                    "path": (
                        "/datasets/@{encodeURIComponent(encodeURIComponent('"
                        f"{site_url}"
                        "'))}/tables/@{encodeURIComponent(encodeURIComponent('"
                        f"{list_id}"
                        "'))}/items"
                    ),
                    "authentication": "@parameters('$authentication')",
                },
            },
            "Create_HTML_table": {
                "runAfter": {"Get_tracker_items": ["Succeeded"]},
                "type": "Table",
                "inputs": {
                    "from": "@body('Get_tracker_items')?['value']",
                    "format": "HTML",
                },
            },
            "Send_digest_email": {
                "runAfter": {"Create_HTML_table": ["Succeeded"]},
                "metadata": {"flowSystemMetadata": {"swaggerOperationId": "SendEmailV2"}},
                "type": "ApiConnection",
                "inputs": {
                    "host": {
                        "connection": {
                            "name": "@parameters('$connections')['shared_office365']['connectionId']"
                        }
                    },
                    "method": "post",
                    "body": {
                        "To": _join_recipients(recipients),
                        "Subject": f"Weekly digest: {tracker_name}",
                        "Body": (
                            _tracker_summary_html(
                                f"Weekly digest for the <a href=\"{tracker_url}\">{tracker_name}</a>"
                            )
                        ),
                        "Importance": "Normal",
                    },
                    "path": "/v2/Mail",
                    "authentication": "@parameters('$authentication')",
                },
            },
        },
    )


def _select_environment(environments: list[dict[str, Any]]) -> dict[str, Any]:
    if not environments:
        raise SmarthausError("powerplatform_environment_unavailable")
    default_env = next(
        (item for item in environments if _is_default_environment(item)),
        None,
    )
    return default_env or environments[0]


def _find_existing_list(
    sharepoint_client: GraphClient,
    *,
    site_id: str,
    tracker_list_name: str,
) -> dict[str, Any] | None:
    lists = sharepoint_client.list_site_lists(site_id)
    for entry in lists:
        if str(entry.get("displayName") or "").strip().lower() == tracker_list_name.lower():
            return sharepoint_client.get_list(site_id, str(entry["id"]))
    return None


def _ensure_tracker_list(
    sharepoint_client: GraphClient,
    *,
    site_id: str,
    tracker_list_name: str,
) -> tuple[dict[str, Any], str]:
    existing = _find_existing_list(
        sharepoint_client,
        site_id=site_id,
        tracker_list_name=tracker_list_name,
    )
    if existing:
        return existing, "reused"
    created = sharepoint_client.create_list(
        site_id,
        tracker_list_name,
        columns=default_tracker_columns(),
    )
    return created, "created"


def _build_recurrence_payload(
    meeting_start: dict[str, Any],
    *,
    time_zone: str,
) -> dict[str, Any]:
    parsed_start = _parse_datetime(meeting_start)
    return {
        "pattern": {
            "type": "weekly",
            "interval": 1,
            "daysOfWeek": [_GRAPH_DAY_NAMES[parsed_start.weekday()]],
        },
        "range": {
            "type": "noEnd",
            "startDate": parsed_start.date().isoformat(),
        },
    }


def _find_existing_meeting(
    messaging_client: GraphClient,
    *,
    organizer_user_id_or_upn: str,
    meeting_subject: str,
    meeting_start: dict[str, Any],
) -> dict[str, Any] | None:
    events = messaging_client.list_events(user_id_or_upn=organizer_user_id_or_upn, top=100).get(
        "value", []
    )
    target_start = str(meeting_start.get("dateTime") or "").strip()
    for event in events:
        if str(event.get("subject") or "").strip() != meeting_subject:
            continue
        event_start = event.get("start", {})
        if str(event_start.get("dateTime") or "").strip() == target_start:
            return event
    return None


def _ensure_recurring_meeting(
    messaging_client: GraphClient,
    *,
    organizer_user_id_or_upn: str,
    meeting_subject: str,
    meeting_start: dict[str, Any],
    meeting_end: dict[str, Any],
    time_zone: str,
    attendees: tuple[str, ...],
    tracker_url: str,
) -> tuple[dict[str, Any], str]:
    existing = _find_existing_meeting(
        messaging_client,
        organizer_user_id_or_upn=organizer_user_id_or_upn,
        meeting_subject=meeting_subject,
        meeting_start=meeting_start,
    )
    if existing:
        return existing, "reused"
    body = {
        "subject": meeting_subject,
        "body": {
            "contentType": "HTML",
            "content": (
                f"<p>Weekly team status meeting.</p><p>Progress tracker: "
                f"<a href=\"{tracker_url}\">{tracker_url}</a></p>"
            ),
        },
        "start": meeting_start,
        "end": meeting_end,
        "location": {"displayName": "Microsoft Teams"},
        "attendees": [
            {"emailAddress": {"address": address}, "type": "required"} for address in attendees
        ],
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",
        "recurrence": _build_recurrence_payload(meeting_start, time_zone=time_zone),
    }
    created = messaging_client.create_event(body, user_id_or_upn=organizer_user_id_or_upn)
    return created, "created"


def _find_existing_flow_by_display_name(
    power_automate_client: PowerAutomateClient,
    *,
    environment_name: str,
    display_name: str,
) -> dict[str, Any] | None:
    for flow in power_automate_client.list_flows_operator(environment_name):
        properties = flow.get("properties", {})
        if str(properties.get("displayName") or "").strip() == display_name:
            return flow
    return None


def _resolve_connection_references(
    power_automate_client: PowerAutomateClient,
    *,
    environment_name: str,
) -> dict[str, Any]:
    for flow in power_automate_client.list_flows_operator(environment_name):
        flow_name = str(flow.get("name") or "").strip()
        if not flow_name:
            continue
        detailed = power_automate_client.get_flow_operator(environment_name, flow_name)
        refs = detailed.get("properties", {}).get("connectionReferences", {})
        if not isinstance(refs, dict):
            continue
        api_names = {str(ref.get("apiName") or "").strip() for ref in refs.values()}
        if {"sharepointonline", "office365"}.issubset(api_names):
            return {
                key: value
                for key, value in refs.items()
                if key in {"shared_sharepointonline", "shared_office365"}
            }
    raise SmarthausError("power_automate_connection_references_unavailable")


def _ensure_flow(
    power_automate_client: PowerAutomateClient,
    *,
    environment_name: str,
    display_name: str,
    definition: dict[str, Any],
    connection_references: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    existing = _find_existing_flow_by_display_name(
        power_automate_client,
        environment_name=environment_name,
        display_name=display_name,
    )
    if existing:
        return existing, "reused"
    created = power_automate_client.create_flow_operator(
        environment_name,
        display_name=display_name,
        definition=definition,
        connection_references=connection_references,
    )
    return created, "created"


def provision_team_status_workflow(
    *,
    sharepoint_client: GraphClient,
    messaging_client: GraphClient,
    power_apps_client: PowerAppsClient,
    power_automate_client: PowerAutomateClient,
    request: TeamStatusWorkflowRequest,
) -> dict[str, Any]:
    site = sharepoint_client.get_site(request.site_id)
    site_url = request.site_url or str(site.get("webUrl") or "").strip()
    if not site_url:
        raise SmarthausError("team_status_workflow_site_url_unavailable")

    environment = _select_environment(power_apps_client.list_powerapp_environments())
    environment_name = _environment_name(environment)
    if not environment_name:
        raise SmarthausError("powerplatform_environment_name_unavailable")

    tracker_list, tracker_status = _ensure_tracker_list(
        sharepoint_client,
        site_id=request.site_id,
        tracker_list_name=request.tracker_list_name,
    )
    tracker_list_id = str(tracker_list.get("id") or "").strip()
    tracker_url = str(tracker_list.get("webUrl") or "").strip()
    if not tracker_list_id or not tracker_url:
        raise SmarthausError("team_status_tracker_creation_incomplete")

    meeting, meeting_status = _ensure_recurring_meeting(
        messaging_client,
        organizer_user_id_or_upn=request.organizer_user_id_or_upn,
        meeting_subject=request.meeting_subject,
        meeting_start=request.meeting_start,
        meeting_end=request.meeting_end,
        time_zone=request.time_zone,
        attendees=request.meeting_attendees,
        tracker_url=tracker_url,
    )
    meeting_link = (
        str(
            (meeting.get("onlineMeeting") or {}).get("joinUrl")
            or meeting.get("webLink")
            or ""
        ).strip()
        or None
    )

    connection_references = _resolve_connection_references(
        power_automate_client,
        environment_name=environment_name,
    )
    if {"shared_sharepointonline", "shared_office365"} - set(connection_references):
        raise SmarthausError("power_automate_connection_references_incomplete")

    reminder_flow_name = f"{request.workflow_name} - Friday reminder"
    digest_flow_name = f"{request.workflow_name} - Weekly digest"

    reminder_flow, reminder_status = _ensure_flow(
        power_automate_client,
        environment_name=environment_name,
        display_name=reminder_flow_name,
        definition=build_reminder_flow_definition(
            tracker_name=request.tracker_list_name,
            tracker_url=tracker_url,
            meeting_subject=request.meeting_subject,
            meeting_link=meeting_link,
            recipients=request.recipients,
            reminder_day=request.reminder_day,
            reminder_hour=request.reminder_hour,
            reminder_minute=request.reminder_minute,
            time_zone=request.time_zone,
        ),
        connection_references=connection_references,
    )
    digest_flow, digest_status = _ensure_flow(
        power_automate_client,
        environment_name=environment_name,
        display_name=digest_flow_name,
        definition=build_digest_flow_definition(
            tracker_name=request.tracker_list_name,
            tracker_url=tracker_url,
            site_url=site_url,
            list_id=tracker_list_id,
            recipients=request.recipients,
            digest_day=request.digest_day,
            digest_hour=request.digest_hour,
            digest_minute=request.digest_minute,
            time_zone=request.time_zone,
        ),
        connection_references=connection_references,
    )

    return {
        "status": "provisioned",
        "environment": {
            "name": environment_name,
            "display_name": _environment_display_name(environment),
        },
        "site": {
            "id": request.site_id,
            "display_name": site.get("displayName"),
            "web_url": site_url,
        },
        "tracker_list": {
            "status": tracker_status,
            "id": tracker_list_id,
            "display_name": tracker_list.get("displayName"),
            "web_url": tracker_url,
        },
        "meeting": {
            "status": meeting_status,
            "id": meeting.get("id"),
            "subject": meeting.get("subject"),
            "web_link": meeting_link,
        },
        "reminder_flow": {
            "status": reminder_status,
            "id": reminder_flow.get("name"),
            "display_name": (
                reminder_flow.get("properties", {}).get("displayName")
                or reminder_flow_name
            ),
        },
        "digest_flow": {
            "status": digest_status,
            "id": digest_flow.get("name"),
            "display_name": (
                digest_flow.get("properties", {}).get("displayName")
                or digest_flow_name
            ),
        },
    }
