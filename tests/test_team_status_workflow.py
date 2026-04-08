from __future__ import annotations

from typing import Any

import pytest
from provisioning_api.routers import m365 as m365_router
from smarthaus_common.team_status_workflow import (
    TeamStatusWorkflowRequest,
    _build_recurrence_payload,
    build_digest_flow_definition,
    build_reminder_flow_definition,
    provision_team_status_workflow,
)


def test_team_status_workflow_builders_include_expected_actions() -> None:
    reminder = build_reminder_flow_definition(
        tracker_name="Weekly Status Tracker",
        tracker_url="https://example.test/tracker",
        meeting_subject="Weekly Status Meeting",
        meeting_link="https://example.test/meeting",
        recipients=("team@example.com",),
        reminder_day="Friday",
        reminder_hour=9,
        reminder_minute=0,
        time_zone="Eastern Standard Time",
    )
    digest = build_digest_flow_definition(
        tracker_name="Weekly Status Tracker",
        tracker_url="https://example.test/tracker",
        site_url="https://example.test/sites/foundingteam",
        list_id="list-123",
        recipients=("team@example.com",),
        digest_day="Friday",
        digest_hour=16,
        digest_minute=0,
        time_zone="Eastern Standard Time",
    )

    assert reminder["triggers"]["Recurrence"]["type"] == "Recurrence"
    assert reminder["$schema"].endswith("/workflowdefinition.json#")
    assert reminder["contentVersion"] == "1.0.0.0"
    assert reminder["outputs"] == {}
    assert "Send_reminder_email" in reminder["actions"]
    assert (
        "shared_office365"
        in reminder["actions"]["Send_reminder_email"]["inputs"]["host"]["connection"]["name"]
    )

    assert digest["triggers"]["Recurrence"]["type"] == "Recurrence"
    assert digest["$schema"].endswith("/workflowdefinition.json#")
    assert digest["contentVersion"] == "1.0.0.0"
    assert digest["outputs"] == {}
    assert {"Get_tracker_items", "Create_HTML_table", "Send_digest_email"} == set(digest["actions"])
    assert (
        "shared_sharepointonline"
        in digest["actions"]["Get_tracker_items"]["inputs"]["host"]["connection"]["name"]
    )


def test_team_status_recurrence_payload_matches_graph_create_shape() -> None:
    payload = _build_recurrence_payload(
        {"dateTime": "2026-04-13T14:00:00", "timeZone": "Eastern Standard Time"},
        time_zone="Eastern Standard Time",
    )

    assert payload["pattern"] == {
        "type": "weekly",
        "interval": 1,
        "daysOfWeek": ["Monday"],
    }
    assert payload["range"] == {
        "type": "noEnd",
        "startDate": "2026-04-13",
    }


def test_provision_team_status_workflow_reuses_existing_assets() -> None:
    class _SharePointClient:
        def get_site(self, site_id: str) -> dict[str, Any]:
            assert site_id == "site-123"
            return {
                "id": site_id,
                "displayName": "Founding Team",
                "webUrl": "https://example.test/sites/foundingteam",
            }

        def list_site_lists(self, site_id: str) -> list[dict[str, Any]]:
            assert site_id == "site-123"
            return [{"id": "list-123", "displayName": "Weekly Status Tracker"}]

        def get_list(self, site_id: str, list_id: str) -> dict[str, Any]:
            assert site_id == "site-123"
            assert list_id == "list-123"
            return {
                "id": list_id,
                "displayName": "Weekly Status Tracker",
                "webUrl": "https://example.test/sites/foundingteam/lists/tracker",
            }

        def create_list(
            self,
            site_id: str,
            display_name: str,
            *,
            columns: list[dict[str, Any]] | None = None,
        ) -> dict[str, Any]:
            raise AssertionError("create_list should not run when the tracker already exists")

    class _MessagingClient:
        def list_events(
            self, *, user_id_or_upn: str | None = None, top: int = 25, select: str = ""
        ) -> dict[str, Any]:
            assert user_id_or_upn == "owner@example.com"
            return {
                "value": [
                    {
                        "id": "event-123",
                        "subject": "Weekly Status Meeting",
                        "start": {"dateTime": "2026-04-13T14:00:00"},
                        "webLink": "https://example.test/event",
                    }
                ]
            }

        def create_event(
            self,
            body: dict[str, Any],
            *,
            user_id_or_upn: str | None = None,
        ) -> dict[str, Any]:
            raise AssertionError("create_event should not run when the meeting already exists")

    class _PowerAppsClient:
        def list_powerapp_environments(self) -> list[dict[str, Any]]:
            return [
                {
                    "EnvironmentName": "Default-tenant",
                    "DisplayName": "Default",
                    "IsDefault": True,
                    "Internal": {
                        "name": "Default-tenant",
                        "properties": {"displayName": "Default"},
                    },
                }
            ]

    class _PowerAutomateClient:
        def list_flows_operator(self, environment_name: str) -> list[dict[str, Any]]:
            assert environment_name == "Default-tenant"
            return [
                {"name": "seed-flow", "properties": {"displayName": "Seed"}},
                {
                    "name": "reminder-flow",
                    "properties": {"displayName": "Weekly Status - Friday reminder"},
                },
                {
                    "name": "digest-flow",
                    "properties": {"displayName": "Weekly Status - Weekly digest"},
                },
            ]

        def get_flow_operator(self, environment_name: str, flow_name: str) -> dict[str, Any]:
            assert environment_name == "Default-tenant"
            if flow_name == "seed-flow":
                return {
                    "name": flow_name,
                    "properties": {
                        "displayName": "Seed",
                        "connectionReferences": {
                            "shared_sharepointonline": {"apiName": "sharepointonline"},
                            "shared_office365": {"apiName": "office365"},
                        },
                    },
                }
            if flow_name == "reminder-flow":
                return {
                    "name": flow_name,
                    "properties": {"displayName": "Weekly Status - Friday reminder"},
                }
            return {
                "name": flow_name,
                "properties": {"displayName": "Weekly Status - Weekly digest"},
            }

        def create_flow_operator(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_flow_operator should not run when flows already exist")

    result = provision_team_status_workflow(
        sharepoint_client=_SharePointClient(),
        messaging_client=_MessagingClient(),
        power_apps_client=_PowerAppsClient(),
        power_automate_client=_PowerAutomateClient(),
        request=TeamStatusWorkflowRequest(
            site_id="site-123",
            organizer_user_id_or_upn="owner@example.com",
            recipients=("team@example.com",),
            meeting_start={"dateTime": "2026-04-13T14:00:00", "timeZone": "Eastern Standard Time"},
            meeting_end={"dateTime": "2026-04-13T14:30:00", "timeZone": "Eastern Standard Time"},
            meeting_subject="Weekly Status Meeting",
            workflow_name="Weekly Status",
            tracker_list_name="Weekly Status Tracker",
            time_zone="Eastern Standard Time",
            reminder_day="Friday",
            reminder_hour=9,
            reminder_minute=0,
            digest_day="Friday",
            digest_hour=16,
            digest_minute=0,
            meeting_attendees=("team@example.com",),
        ),
    )

    assert result["tracker_list"]["status"] == "reused"
    assert result["meeting"]["status"] == "reused"
    assert result["reminder_flow"]["status"] == "reused"
    assert result["digest_flow"]["status"] == "reused"


def test_instruction_contract_executes_provision_team_status_workflow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}
    assert "provision_team_status_workflow" in supported

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: object())
    monkeypatch.setattr(m365_router, "_power_apps_client", lambda action=None: object())
    monkeypatch.setattr(m365_router, "_power_automate_client", lambda action=None: object())

    def _fake_provision(**kwargs: Any) -> dict[str, Any]:
        request = kwargs["request"]
        assert request.site_id == "site-123"
        assert request.organizer_user_id_or_upn == "owner@example.com"
        assert request.recipients == ("team@example.com",)
        return {
            "status": "provisioned",
            "environment": {"name": "Default-tenant"},
            "site": {"id": "site-123"},
            "tracker_list": {"id": "list-123", "status": "created"},
            "meeting": {"id": "event-123", "status": "created"},
            "reminder_flow": {"id": "flow-reminder", "status": "created"},
            "digest_flow": {"id": "flow-digest", "status": "created"},
        }

    monkeypatch.setattr(m365_router, "provision_team_status_workflow", _fake_provision)

    payload = m365_router.execute_instruction_contract(
        action="provision_team_status_workflow",
        params_payload={
            "siteId": "site-123",
            "userPrincipalName": "owner@example.com",
            "recipients": ["team@example.com"],
            "meetingStart": {
                "dateTime": "2026-04-13T14:00:00",
                "timeZone": "Eastern Standard Time",
            },
            "meetingEnd": {"dateTime": "2026-04-13T14:30:00", "timeZone": "Eastern Standard Time"},
            "workflowName": "Weekly Status",
        },
        trace_id="trace-team-status",
    )

    assert payload["ok"] is True
    assert payload["result"]["status"] == "provisioned"
