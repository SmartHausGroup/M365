from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from smarthaus_common.config import resolve_sharepoint_hostname
from smarthaus_common.errors import SmarthausError
from smarthaus_common.office_generation import DOCUMENT_CONTENT_TYPE, generate_docx_bytes


class WorkspaceWorkflowClient(Protocol):
    def find_group_by_mailnickname(self, mail_nickname: str) -> dict[str, Any] | None: ...

    def create_group(
        self,
        display_name: str,
        mail_nickname: str,
        description: str | None = None,
        *,
        mail_enabled: bool = True,
        security_enabled: bool = False,
        group_types: list[str] | None = None,
        owners: list[str] | None = None,
        members: list[str] | None = None,
    ) -> dict[str, Any]: ...

    def get_group_root_site(self, group_id: str) -> dict[str, Any]: ...

    def get_site_by_path(self, hostname: str, site_path: str) -> dict[str, Any]: ...

    def get_site(self, site_id: str) -> dict[str, Any]: ...


class CollaborationWorkflowClient(Protocol):
    def teamify_group(self, group_id: str) -> None: ...

    def get_team(
        self,
        team_id: str | None = None,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> dict[str, Any]: ...

    def list_channels(
        self,
        team_id: str | None = None,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> list[dict[str, Any]]: ...

    def create_channel(
        self,
        display_name: str,
        *,
        team_id: str | None = None,
        group_id: str | None = None,
        mail_nickname: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]: ...


class DocumentWorkflowClient(Protocol):
    def list_drive_items(
        self,
        *,
        drive_id: str | None = None,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
        folder_id: str | None = None,
        folder_path: str | None = None,
        top: int = 100,
    ) -> dict[str, Any]: ...

    def upload_bytes(
        self,
        *,
        file_bytes: bytes,
        remote_path: str,
        drive_id: str | None = None,
        group_id: str | None = None,
        site_id: str | None = None,
        user_id_or_upn: str | None = None,
        conflict_behavior: str = "replace",
        content_type: str | None = None,
        source_name: str = "generated.bin",
    ) -> dict[str, Any]: ...


class PlannerWorkflowClient(Protocol):
    def list_plans(
        self,
        *,
        group_id: str | None = None,
        mail_nickname: str | None = None,
    ) -> list[dict[str, Any]]: ...

    def create_plan(
        self,
        group_id: str | None,
        title: str,
        *,
        mail_nickname: str | None = None,
    ) -> dict[str, Any]: ...

    def list_plan_buckets(self, plan_id: str) -> list[dict[str, Any]]: ...

    def create_plan_bucket(self, plan_id: str, name: str, order_hint: str = " !") -> dict[str, Any]: ...

    def list_bucket_tasks(self, bucket_id: str) -> list[dict[str, Any]]: ...

    def create_plan_task(
        self,
        plan_id: str,
        bucket_id: str,
        title: str,
        *,
        description: str | None = None,
        reference_url: str | None = None,
        percent_complete: int | None = None,
    ) -> dict[str, Any]: ...


class MessagingWorkflowClient(Protocol):
    def send_mail(
        self,
        recipient_or_to: list[str] | str,
        subject: str,
        body: str | dict[str, Any],
        *,
        user_id_or_upn: str | None = None,
        content_type: str = "Text",
        save_to_sent_items: bool = True,
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class IncidentResponseWarRoomRequest:
    incident_name: str
    team_name: str
    site_name: str
    mail_nickname: str
    incident_lead_upn: str
    command_channel_name: str
    runbook_path: str
    plan_title: str
    bucket_name: str
    seed_task_title: str
    seed_task_description: str
    activation_recipients: tuple[str, ...]
    activation_sender_user_id_or_upn: str
    activation_subject: str
    send_activation_mail: bool
    force_send_activation: bool = False
    workspace_wait_seconds: int = 60
    team_wait_seconds: int = 90


def _find_named_entry(
    items: list[dict[str, Any]],
    *,
    key: str,
    expected: str,
) -> dict[str, Any] | None:
    normalized_expected = expected.strip().lower()
    for item in items:
        candidate = str(item.get(key) or "").strip().lower()
        if candidate == normalized_expected:
            return item
    return None


def _resolve_site(
    workspace_client: WorkspaceWorkflowClient,
    *,
    group_id: str,
    mail_nickname: str,
    wait_seconds: int,
) -> dict[str, Any]:
    hostname = resolve_sharepoint_hostname()
    site: dict[str, Any] | None = None
    for _ in range(max(1, wait_seconds // 3)):
        try:
            site = workspace_client.get_group_root_site(group_id)
            if site.get("id"):
                break
        except Exception:  # noqa: BLE001
            site = None
        try:
            site = workspace_client.get_site_by_path(hostname, mail_nickname)
            if site.get("id"):
                break
        except Exception:  # noqa: BLE001
            pass
        time.sleep(3)
    if not site or not site.get("id"):
        raise SmarthausError("incident_response_war_room_site_unavailable")
    return site


def _ensure_workspace(
    workspace_client: WorkspaceWorkflowClient,
    *,
    display_name: str,
    mail_nickname: str,
    incident_name: str,
    wait_seconds: int,
) -> tuple[dict[str, Any], str, dict[str, Any], str]:
    group = workspace_client.find_group_by_mailnickname(mail_nickname)
    group_status = "reused"
    if not group:
        group = workspace_client.create_group(
            display_name,
            mail_nickname,
            description=f"Incident response war room for {incident_name}",
        )
        group_status = "created"
    group_id = str(group.get("id") or "").strip()
    if not group_id:
        raise SmarthausError("incident_response_war_room_group_missing_id")
    site = _resolve_site(
        workspace_client,
        group_id=group_id,
        mail_nickname=mail_nickname,
        wait_seconds=wait_seconds,
    )
    site_id = str(site.get("id") or "").strip()
    if not site_id:
        raise SmarthausError("incident_response_war_room_site_missing_id")
    site_details = workspace_client.get_site(site_id)
    site_status = "created" if group_status == "created" else "reused"
    return group, group_status, site_details, site_status


def _ensure_team(
    collaboration_client: CollaborationWorkflowClient,
    *,
    group_id: str,
    wait_seconds: int,
) -> tuple[dict[str, Any], str]:
    try:
        team = collaboration_client.get_team(group_id=group_id)
        if team.get("id"):
            return team, "reused"
    except Exception:  # noqa: BLE001
        team = {}
    try:
        collaboration_client.teamify_group(group_id)
    except Exception:  # noqa: BLE001
        pass
    for _ in range(max(1, wait_seconds // 3)):
        try:
            team = collaboration_client.get_team(group_id=group_id)
            if team.get("id"):
                return team, "created"
        except Exception:  # noqa: BLE001
            pass
        time.sleep(3)
    raise SmarthausError("incident_response_war_room_team_unavailable")


def _ensure_command_channel(
    collaboration_client: CollaborationWorkflowClient,
    *,
    group_id: str,
    command_channel_name: str,
    incident_name: str,
) -> tuple[dict[str, Any], str]:
    existing = _find_named_entry(
        collaboration_client.list_channels(group_id=group_id),
        key="displayName",
        expected=command_channel_name,
    )
    if existing:
        return existing, "reused"
    created = collaboration_client.create_channel(
        command_channel_name,
        group_id=group_id,
        description=f"Command coordination for {incident_name}",
    )
    return created, "created"


def _build_runbook_paragraphs(
    request: IncidentResponseWarRoomRequest,
    *,
    site: dict[str, Any],
    team: dict[str, Any],
    command_channel: dict[str, Any],
) -> list[str]:
    paragraphs = [
        f"Incident: {request.incident_name}",
        f"Incident lead: {request.incident_lead_upn}",
        f"Workspace mail nickname: {request.mail_nickname}",
        f"Team name: {request.team_name}",
        f"Site name: {request.site_name}",
        f"Command channel: {command_channel.get('displayName') or request.command_channel_name}",
        f"Site URL: {site.get('webUrl') or 'unavailable'}",
        f"Team URL: {team.get('webUrl') or team.get('id') or 'unavailable'}",
        f"Planner plan: {request.plan_title}",
        "Prepared by SMARTHAUS M365 incident workflow runtime.",
    ]
    return paragraphs


def _ensure_runbook_document(
    document_client: DocumentWorkflowClient,
    *,
    site_id: str,
    request: IncidentResponseWarRoomRequest,
    site: dict[str, Any],
    team: dict[str, Any],
    command_channel: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    runbook_name = Path(request.runbook_path).name
    drive_items = document_client.list_drive_items(site_id=site_id, top=999)
    existing = _find_named_entry(drive_items.get("value", []), key="name", expected=runbook_name)
    uploaded = document_client.upload_bytes(
        file_bytes=generate_docx_bytes(
            title=f"{request.incident_name} Incident Runbook",
            paragraphs=_build_runbook_paragraphs(
                request,
                site=site,
                team=team,
                command_channel=command_channel,
            ),
        ),
        remote_path=request.runbook_path,
        site_id=site_id,
        conflict_behavior="replace",
        content_type=DOCUMENT_CONTENT_TYPE,
        source_name=runbook_name,
    )
    return uploaded, "updated" if existing else "created"


def _ensure_plan(
    planner_client: PlannerWorkflowClient,
    *,
    group_id: str,
    plan_title: str,
) -> tuple[dict[str, Any], str]:
    existing = _find_named_entry(
        planner_client.list_plans(group_id=group_id),
        key="title",
        expected=plan_title,
    )
    if existing:
        return existing, "reused"
    return planner_client.create_plan(group_id, plan_title), "created"


def _ensure_bucket(
    planner_client: PlannerWorkflowClient,
    *,
    plan_id: str,
    bucket_name: str,
) -> tuple[dict[str, Any], str]:
    existing = _find_named_entry(
        planner_client.list_plan_buckets(plan_id),
        key="name",
        expected=bucket_name,
    )
    if existing:
        return existing, "reused"
    return planner_client.create_plan_bucket(plan_id, bucket_name), "created"


def _ensure_seed_task(
    planner_client: PlannerWorkflowClient,
    *,
    plan_id: str,
    bucket_id: str,
    title: str,
    description: str,
    reference_url: str | None,
) -> tuple[dict[str, Any], str]:
    existing = _find_named_entry(
        planner_client.list_bucket_tasks(bucket_id),
        key="title",
        expected=title,
    )
    if existing:
        return existing, "reused"
    return (
        planner_client.create_plan_task(
            plan_id,
            bucket_id,
            title,
            description=description,
            reference_url=reference_url,
        ),
        "created",
    )


def _build_activation_body(
    request: IncidentResponseWarRoomRequest,
    *,
    site: dict[str, Any],
    team: dict[str, Any],
    channel: dict[str, Any],
    plan: dict[str, Any],
    runbook: dict[str, Any],
) -> str:
    lines = [
        f"Incident war room activated: {request.incident_name}",
        f"Lead: {request.incident_lead_upn}",
        f"Workspace: {request.team_name}",
        f"Command channel: {channel.get('displayName') or request.command_channel_name}",
        f"Team URL: {team.get('webUrl') or team.get('id') or 'unavailable'}",
        f"Site URL: {site.get('webUrl') or 'unavailable'}",
        f"Runbook URL: {runbook.get('webUrl') or runbook.get('webUrl@odata.mediaReadLink') or 'unavailable'}",
        f"Planner plan: {plan.get('title') or request.plan_title}",
    ]
    return "\n".join(lines)


def provision_incident_response_war_room(
    *,
    workspace_client: WorkspaceWorkflowClient,
    collaboration_client: CollaborationWorkflowClient,
    document_client: DocumentWorkflowClient,
    planner_client: PlannerWorkflowClient,
    messaging_client: MessagingWorkflowClient,
    request: IncidentResponseWarRoomRequest,
) -> dict[str, Any]:
    display_name = request.team_name or request.site_name
    group, group_status, site, site_status = _ensure_workspace(
        workspace_client,
        display_name=display_name,
        mail_nickname=request.mail_nickname,
        incident_name=request.incident_name,
        wait_seconds=request.workspace_wait_seconds,
    )
    group_id = str(group.get("id") or "").strip()
    site_id = str(site.get("id") or "").strip()
    if not group_id or not site_id:
        raise SmarthausError("incident_response_war_room_workspace_incomplete")

    team, team_status = _ensure_team(
        collaboration_client,
        group_id=group_id,
        wait_seconds=request.team_wait_seconds,
    )
    command_channel, command_channel_status = _ensure_command_channel(
        collaboration_client,
        group_id=group_id,
        command_channel_name=request.command_channel_name,
        incident_name=request.incident_name,
    )
    runbook_document, runbook_status = _ensure_runbook_document(
        document_client,
        site_id=site_id,
        request=request,
        site=site,
        team=team,
        command_channel=command_channel,
    )
    plan, plan_status = _ensure_plan(
        planner_client,
        group_id=group_id,
        plan_title=request.plan_title,
    )
    plan_id = str(plan.get("id") or "").strip()
    if not plan_id:
        raise SmarthausError("incident_response_war_room_plan_missing_id")
    bucket, bucket_status = _ensure_bucket(
        planner_client,
        plan_id=plan_id,
        bucket_name=request.bucket_name,
    )
    bucket_id = str(bucket.get("id") or "").strip()
    if not bucket_id:
        raise SmarthausError("incident_response_war_room_bucket_missing_id")
    runbook_url = str(runbook_document.get("webUrl") or "").strip() or None
    seed_task, seed_task_status = _ensure_seed_task(
        planner_client,
        plan_id=plan_id,
        bucket_id=bucket_id,
        title=request.seed_task_title,
        description=request.seed_task_description,
        reference_url=runbook_url or str(site.get("webUrl") or "").strip() or None,
    )

    created_statuses = {
        group_status,
        site_status,
        team_status,
        command_channel_status,
        runbook_status,
        plan_status,
        bucket_status,
        seed_task_status,
    }
    should_send_activation = request.send_activation_mail and (
        request.force_send_activation or "created" in created_statuses
    )
    if should_send_activation:
        activation_mail = messaging_client.send_mail(
            list(request.activation_recipients),
            request.activation_subject,
            _build_activation_body(
                request,
                site=site,
                team=team,
                channel=command_channel,
                plan=plan,
                runbook=runbook_document,
            ),
            user_id_or_upn=request.activation_sender_user_id_or_upn,
        )
        activation_status = "sent"
    else:
        activation_mail = {
            "sent": False,
            "to": list(request.activation_recipients),
            "subject": request.activation_subject,
            "from": request.activation_sender_user_id_or_upn,
        }
        activation_status = "skipped"

    return {
        "status": "provisioned",
        "workspace": {
            "incident_name": request.incident_name,
            "mail_nickname": request.mail_nickname,
            "group_id": group_id,
        },
        "team": {
            "status": team_status,
            "id": team.get("id") or group_id,
            "display_name": team.get("displayName") or request.team_name,
            "web_url": team.get("webUrl"),
        },
        "command_channel": {
            "status": command_channel_status,
            "id": command_channel.get("id"),
            "display_name": command_channel.get("displayName") or request.command_channel_name,
        },
        "site": {
            "status": site_status,
            "id": site_id,
            "display_name": site.get("displayName") or request.site_name,
            "web_url": site.get("webUrl"),
        },
        "runbook_document": {
            "status": runbook_status,
            "id": runbook_document.get("id"),
            "name": runbook_document.get("name") or Path(request.runbook_path).name,
            "web_url": runbook_document.get("webUrl"),
            "path": request.runbook_path,
        },
        "plan": {
            "status": plan_status,
            "id": plan_id,
            "title": plan.get("title") or request.plan_title,
        },
        "bucket": {
            "status": bucket_status,
            "id": bucket_id,
            "name": bucket.get("name") or request.bucket_name,
        },
        "seed_task": {
            "status": seed_task_status,
            "id": seed_task.get("id"),
            "title": seed_task.get("title") or request.seed_task_title,
        },
        "activation_mail": {
            "status": activation_status,
            "to": activation_mail.get("to") or list(request.activation_recipients),
            "subject": activation_mail.get("subject") or request.activation_subject,
            "from": activation_mail.get("from") or request.activation_sender_user_id_or_upn,
        },
    }
