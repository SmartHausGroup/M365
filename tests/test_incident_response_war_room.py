from __future__ import annotations

from typing import Any

import pytest
from provisioning_api.routers import m365 as m365_router
from smarthaus_common.incident_response_war_room import (
    IncidentResponseWarRoomRequest,
    provision_incident_response_war_room,
)


def test_provision_incident_response_war_room_reuses_existing_assets() -> None:
    class _WorkspaceClient:
        def find_group_by_mailnickname(self, mail_nickname: str) -> dict[str, Any] | None:
            assert mail_nickname == "incident-alpha"
            return {"id": "group-123", "displayName": "Incident Alpha"}

        def create_group(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_group should not run when the workspace already exists")

        def get_group_root_site(self, group_id: str) -> dict[str, Any]:
            assert group_id == "group-123"
            return {"id": "site-123"}

        def get_site_by_path(self, hostname: str, site_path: str) -> dict[str, Any]:
            raise AssertionError("get_site_by_path should not run when the root site resolves")

        def get_site(self, site_id: str) -> dict[str, Any]:
            assert site_id == "site-123"
            return {
                "id": site_id,
                "displayName": "Incident Alpha",
                "webUrl": "https://example.test/sites/incident-alpha",
            }

    class _CollaborationClient:
        def teamify_group(self, group_id: str) -> None:
            raise AssertionError("teamify_group should not run when the Team already exists")

        def get_team(
            self,
            team_id: str | None = None,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> dict[str, Any]:
            assert team_id is None
            assert group_id == "group-123"
            assert mail_nickname is None
            return {
                "id": "group-123",
                "displayName": "Incident Alpha",
                "webUrl": "https://teams.example.test/incident-alpha",
            }

        def list_channels(
            self,
            team_id: str | None = None,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> list[dict[str, Any]]:
            assert group_id == "group-123"
            return [
                {"id": "chan-1", "displayName": "General"},
                {"id": "chan-2", "displayName": "Command"},
            ]

        def create_channel(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_channel should not run when the command channel exists")

    class _DocumentClient:
        def list_drive_items(self, **kwargs: Any) -> dict[str, Any]:
            assert kwargs["site_id"] == "site-123"
            return {
                "value": [
                    {
                        "id": "doc-1",
                        "name": "Incident Alpha Incident Runbook.docx",
                        "webUrl": "https://example.test/runbook",
                    }
                ]
            }

        def upload_bytes(self, **kwargs: Any) -> dict[str, Any]:
            assert kwargs["site_id"] == "site-123"
            assert kwargs["remote_path"] == "Incident Alpha Incident Runbook.docx"
            return {
                "id": "doc-1",
                "name": "Incident Alpha Incident Runbook.docx",
                "webUrl": "https://example.test/runbook",
            }

    class _PlannerClient:
        def list_plans(
            self,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> list[dict[str, Any]]:
            assert group_id == "group-123"
            assert mail_nickname is None
            return [{"id": "plan-123", "title": "Incident Alpha Response Plan"}]

        def create_plan(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_plan should not run when the plan exists")

        def list_plan_buckets(self, plan_id: str) -> list[dict[str, Any]]:
            assert plan_id == "plan-123"
            return [{"id": "bucket-123", "name": "Active Response"}]

        def create_plan_bucket(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_plan_bucket should not run when the bucket exists")

        def list_bucket_tasks(self, bucket_id: str) -> list[dict[str, Any]]:
            assert bucket_id == "bucket-123"
            return [{"id": "task-123", "title": "Establish incident command"}]

        def create_plan_task(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_plan_task should not run when the seed task exists")

    class _MessagingClient:
        def send_mail(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("send_mail should not run when no new assets were provisioned")

    result = provision_incident_response_war_room(
        workspace_client=_WorkspaceClient(),
        collaboration_client=_CollaborationClient(),
        document_client=_DocumentClient(),
        planner_client=_PlannerClient(),
        messaging_client=_MessagingClient(),
        request=IncidentResponseWarRoomRequest(
            incident_name="Incident Alpha",
            team_name="Incident Alpha",
            site_name="Incident Alpha",
            mail_nickname="incident-alpha",
            incident_lead_upn="lead@example.com",
            command_channel_name="Command",
            runbook_path="Incident Alpha Incident Runbook.docx",
            plan_title="Incident Alpha Response Plan",
            bucket_name="Active Response",
            seed_task_title="Establish incident command",
            seed_task_description="Start the bridge and assign owners.",
            activation_recipients=("lead@example.com",),
            activation_sender_user_id_or_upn="lead@example.com",
            activation_subject="[Incident] Incident Alpha war room activated",
            send_activation_mail=True,
        ),
    )

    assert result["team"]["status"] == "reused"
    assert result["command_channel"]["status"] == "reused"
    assert result["site"]["status"] == "reused"
    assert result["runbook_document"]["status"] == "updated"
    assert result["plan"]["status"] == "reused"
    assert result["bucket"]["status"] == "reused"
    assert result["seed_task"]["status"] == "reused"
    assert result["activation_mail"]["status"] == "skipped"


def test_instruction_contract_executes_provision_incident_response_war_room(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}
    assert "provision_incident_response_war_room" in supported

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: object())

    def _fake_provision(**kwargs: Any) -> dict[str, Any]:
        request = kwargs["request"]
        assert request.incident_name == "Incident Alpha"
        assert request.team_name == "Incident Alpha"
        assert request.site_name == "Incident Alpha"
        assert request.mail_nickname == "incident-alpha"
        assert request.incident_lead_upn == "lead@example.com"
        assert request.activation_recipients == ("lead@example.com", "ops@example.com")
        return {
            "status": "provisioned",
            "workspace": {"mail_nickname": "incident-alpha"},
            "team": {"status": "created"},
            "command_channel": {"status": "created"},
            "site": {"status": "created"},
            "runbook_document": {"status": "created"},
            "plan": {"status": "created"},
            "bucket": {"status": "created"},
            "seed_task": {"status": "created"},
            "activation_mail": {"status": "sent"},
        }

    monkeypatch.setattr(m365_router, "provision_incident_response_war_room", _fake_provision)

    payload = m365_router.execute_instruction_contract(
        action="provision_incident_response_war_room",
        params_payload={
            "incidentName": "Incident Alpha",
            "teamName": "Incident Alpha",
            "siteName": "Incident Alpha",
            "incidentLeadUpn": "lead@example.com",
            "activationRecipients": ["lead@example.com", "ops@example.com"],
        },
        trace_id="trace-incident-workflow",
    )

    assert payload["ok"] is True
    assert payload["result"]["status"] == "provisioned"
    assert payload["result"]["activation_mail"]["status"] == "sent"


def test_provision_incident_response_war_room_sends_activation_when_runbook_is_created() -> None:
    class _WorkspaceClient:
        def find_group_by_mailnickname(self, mail_nickname: str) -> dict[str, Any] | None:
            assert mail_nickname == "incident-alpha"
            return {"id": "group-123", "displayName": "Incident Alpha"}

        def create_group(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_group should not run when the workspace already exists")

        def get_group_root_site(self, group_id: str) -> dict[str, Any]:
            assert group_id == "group-123"
            return {"id": "site-123"}

        def get_site_by_path(self, hostname: str, site_path: str) -> dict[str, Any]:
            raise AssertionError("get_site_by_path should not run when the root site resolves")

        def get_site(self, site_id: str) -> dict[str, Any]:
            assert site_id == "site-123"
            return {
                "id": site_id,
                "displayName": "Incident Alpha",
                "webUrl": "https://example.test/sites/incident-alpha",
            }

    class _CollaborationClient:
        def teamify_group(self, group_id: str) -> None:
            raise AssertionError("teamify_group should not run when the Team already exists")

        def get_team(
            self,
            team_id: str | None = None,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> dict[str, Any]:
            assert team_id is None
            assert group_id == "group-123"
            assert mail_nickname is None
            return {
                "id": "group-123",
                "displayName": "Incident Alpha",
                "webUrl": "https://teams.example.test/incident-alpha",
            }

        def list_channels(
            self,
            team_id: str | None = None,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> list[dict[str, Any]]:
            assert group_id == "group-123"
            return [
                {"id": "chan-1", "displayName": "General"},
                {"id": "chan-2", "displayName": "Command"},
            ]

        def create_channel(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_channel should not run when the command channel exists")

    class _DocumentClient:
        def list_drive_items(self, **kwargs: Any) -> dict[str, Any]:
            assert kwargs["site_id"] == "site-123"
            return {"value": []}

        def upload_bytes(self, **kwargs: Any) -> dict[str, Any]:
            assert kwargs["site_id"] == "site-123"
            assert kwargs["remote_path"] == "Incident Alpha Incident Runbook.docx"
            return {
                "id": "doc-1",
                "name": "Incident Alpha Incident Runbook.docx",
                "webUrl": "https://example.test/runbook",
            }

    class _PlannerClient:
        def list_plans(
            self,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> list[dict[str, Any]]:
            assert group_id == "group-123"
            assert mail_nickname is None
            return [{"id": "plan-123", "title": "Incident Alpha Response Plan"}]

        def create_plan(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_plan should not run when the plan exists")

        def list_plan_buckets(self, plan_id: str) -> list[dict[str, Any]]:
            assert plan_id == "plan-123"
            return [{"id": "bucket-123", "name": "Active Response"}]

        def create_plan_bucket(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_plan_bucket should not run when the bucket exists")

        def list_bucket_tasks(self, bucket_id: str) -> list[dict[str, Any]]:
            assert bucket_id == "bucket-123"
            return [{"id": "task-123", "title": "Establish incident command"}]

        def create_plan_task(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            raise AssertionError("create_plan_task should not run when the seed task exists")

    class _MessagingClient:
        def send_mail(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            assert args[0] == ["lead@example.com"]
            assert args[1] == "[Incident] Incident Alpha war room activated"
            return {
                "to": ["lead@example.com"],
                "subject": "[Incident] Incident Alpha war room activated",
                "from": "lead@example.com",
            }

    result = provision_incident_response_war_room(
        workspace_client=_WorkspaceClient(),
        collaboration_client=_CollaborationClient(),
        document_client=_DocumentClient(),
        planner_client=_PlannerClient(),
        messaging_client=_MessagingClient(),
        request=IncidentResponseWarRoomRequest(
            incident_name="Incident Alpha",
            team_name="Incident Alpha",
            site_name="Incident Alpha",
            mail_nickname="incident-alpha",
            incident_lead_upn="lead@example.com",
            command_channel_name="Command",
            runbook_path="Incident Alpha Incident Runbook.docx",
            plan_title="Incident Alpha Response Plan",
            bucket_name="Active Response",
            seed_task_title="Establish incident command",
            seed_task_description="Start the bridge and assign owners.",
            activation_recipients=("lead@example.com",),
            activation_sender_user_id_or_upn="lead@example.com",
            activation_subject="[Incident] Incident Alpha war room activated",
            send_activation_mail=True,
        ),
    )

    assert result["runbook_document"]["status"] == "created"
    assert result["activation_mail"]["status"] == "sent"


def test_instruction_contract_requires_explicit_mail_nickname_for_mismatched_workspace_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")

    payload = m365_router.execute_instruction_contract(
        action="provision_incident_response_war_room",
        params_payload={
            "incidentName": "Incident Alpha",
            "teamName": "Incident Alpha",
            "siteName": "Alpha Site",
            "incidentLeadUpn": "lead@example.com",
        },
        trace_id="trace-incident-workflow-mismatch",
    )

    assert payload["ok"] is False
    assert "mailNickname" in str(payload["error"])
