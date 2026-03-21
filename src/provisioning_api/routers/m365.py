from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field
from smarthaus_common.automation_recipe_client import AutomationRecipeClient
from smarthaus_common.config import AppConfig, has_selected_tenant
from smarthaus_common.errors import SmarthausError
from smarthaus_common.executor_routing import executor_route_for_action
from smarthaus_common.forms_approvals_connectors_client import FormsApprovalsConnectorsClient
from smarthaus_common.office_generation import (
    DOCUMENT_CONTENT_TYPE,
    PRESENTATION_CONTENT_TYPE,
    WORKBOOK_CONTENT_TYPE,
    generate_docx_bytes,
    generate_pptx_bytes,
    generate_xlsx_bytes,
)
from smarthaus_common.power_apps_client import PowerAppsClient
from smarthaus_common.power_automate_client import PowerAutomateClient
from smarthaus_common.power_bi_client import PowerBIClient
from smarthaus_common.tenant_config import get_tenant_config
from smarthaus_graph.client import GraphClient

from provisioning_api import auth as authn
from provisioning_api.audit import log_event
from provisioning_api.m365_provision import provision_group_site, provision_teams_workspace
from provisioning_api.metrics import inc_sites_created, inc_teams_created
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/m365", tags=["m365"])
_SESSION_DEPENDENCY = Depends(authn.verify_microsoft_token)

_IDEMPOTENCY_COLLECTION = "m365_instruction_idempotency"
_SUPPORTED_ACTIONS = {
    "create_site",
    "create_team",
    "add_channel",
    "get_team",
    "list_channels",
    "create_channel",
    "list_plans",
    "create_plan",
    "list_plan_buckets",
    "create_plan_bucket",
    "create_plan_task",
    "provision_service",
    "list_users",
    "list_teams",
    "list_sites",
    "get_site",
    "list_site_lists",
    "get_list",
    "list_list_items",
    "create_list_item",
    "list_drives",
    "get_drive",
    "list_drive_items",
    "get_drive_item",
    "create_folder",
    "upload_file",
    "create_document",
    "update_document",
    "create_workbook",
    "update_workbook",
    "create_presentation",
    "update_presentation",
    "list_flows_admin",
    "get_flow_admin",
    "list_http_flows",
    "list_flow_owners",
    "list_flow_runs",
    "set_flow_owner_role",
    "remove_flow_owner_role",
    "enable_flow",
    "disable_flow",
    "delete_flow",
    "restore_flow",
    "invoke_flow_callback",
    "list_powerapps_admin",
    "get_powerapp_admin",
    "list_powerapp_role_assignments",
    "set_powerapp_owner",
    "remove_powerapp_role_assignment",
    "delete_powerapp",
    "list_powerapp_environments",
    "get_powerapp_environment",
    "list_powerapp_environment_role_assignments",
    "set_powerapp_environment_role_assignment",
    "remove_powerapp_environment_role_assignment",
    "list_powerbi_workspaces",
    "get_powerbi_workspace",
    "list_powerbi_reports",
    "get_powerbi_report",
    "list_powerbi_datasets",
    "get_powerbi_dataset",
    "refresh_powerbi_dataset",
    "list_powerbi_dataset_refreshes",
    "list_powerbi_dashboards",
    "get_powerbi_dashboard",
    "get_approval_solution",
    "list_approval_items",
    "get_approval_item",
    "create_approval_item",
    "list_approval_item_requests",
    "respond_to_approval_item",
    "list_external_connections",
    "get_external_connection",
    "create_external_connection",
    "register_external_connection_schema",
    "get_external_item",
    "upsert_external_item",
    "create_external_group",
    "add_external_group_member",
    "list_automation_recipes",
    "get_automation_recipe",
    "get_user",
    "reset_user_password",
    "create_user",
    "update_user",
    "disable_user",
    "list_groups",
    "get_group",
    "create_group",
    "list_group_members",
    "add_group_member",
    "remove_group_member",
    "assign_user_license",
    "list_directory_roles",
    "list_directory_role_members",
    "list_domains",
    "get_organization",
    "list_applications",
    "get_application",
    "update_application",
    "list_service_principals",
    "list_messages",
    "get_message",
    "send_mail",
    "move_message",
    "delete_message",
    "list_mail_folders",
    "get_mailbox_settings",
    "update_mailbox_settings",
    "list_events",
    "create_event",
    "get_event",
    "update_event",
    "delete_event",
    "get_schedule",
    "list_contacts",
    "get_contact",
    "create_contact",
    "update_contact",
    "delete_contact",
    "list_contact_folders",
}
_MUTATING_ACTIONS = {
    "create_site",
    "create_team",
    "add_channel",
    "create_channel",
    "create_plan",
    "create_plan_bucket",
    "create_plan_task",
    "provision_service",
    "reset_user_password",
    "create_user",
    "update_user",
    "disable_user",
    "create_group",
    "add_group_member",
    "remove_group_member",
    "assign_user_license",
    "update_application",
    "send_mail",
    "move_message",
    "delete_message",
    "update_mailbox_settings",
    "create_event",
    "update_event",
    "delete_event",
    "create_contact",
    "update_contact",
    "delete_contact",
    "create_list_item",
    "create_folder",
    "upload_file",
    "create_document",
    "update_document",
    "create_workbook",
    "update_workbook",
    "create_presentation",
    "update_presentation",
    "set_flow_owner_role",
    "remove_flow_owner_role",
    "enable_flow",
    "disable_flow",
    "delete_flow",
    "restore_flow",
    "invoke_flow_callback",
    "set_powerapp_owner",
    "remove_powerapp_role_assignment",
    "delete_powerapp",
    "set_powerapp_environment_role_assignment",
    "remove_powerapp_environment_role_assignment",
    "refresh_powerbi_dataset",
    "create_approval_item",
    "respond_to_approval_item",
    "create_external_connection",
    "register_external_connection_schema",
    "upsert_external_item",
    "create_external_group",
    "add_external_group_member",
}


class M365InstructionRequest(BaseModel):
    action: str = Field(..., min_length=1)
    params: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None


class M365InstructionResponse(BaseModel):
    ok: bool
    result: dict[str, Any] | None = None
    error: str | None = None
    trace_id: str | None = None


def _allow_mutations() -> bool:
    return os.getenv("ALLOW_M365_MUTATIONS", "false").lower() in ("1", "true", "yes")


def _validate_caio_api_key(request: Request) -> bool:
    expected = os.getenv("CAIO_API_KEY")
    if not expected:
        return True
    provided = request.headers.get("X-CAIO-API-Key") or request.headers.get("X-CAIO-Token")
    return bool(provided and provided == expected)


def _request_hash(action: str, params: dict[str, Any]) -> str:
    payload = {"action": action, "params": params}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _get_idempotency_record(key: str) -> dict[str, Any] | None:
    store = JsonStore()
    for rec in store.list(_IDEMPOTENCY_COLLECTION):
        if rec.get("key") == key:
            return rec
    return None


def _store_idempotency_record(
    key: str, request_hash: str, response_payload: dict[str, Any]
) -> None:
    JsonStore().append(
        _IDEMPOTENCY_COLLECTION,
        {"key": key, "request_hash": request_hash, "response": response_payload},
    )


def _require_str(params: dict[str, Any], key: str) -> str:
    value = params.get(key)
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(status_code=400, detail=f"Missing or invalid '{key}'")
    return value.strip()


def _optional_str(params: dict[str, Any], key: str) -> str | None:
    value = params.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail=f"Invalid '{key}'")
    return value.strip()


def _first_str(params: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = _optional_str(params, key)
        if value:
            return value
    return None


def _normalize_str_list(params: dict[str, Any], key: str, default: list[str]) -> list[str]:
    value = params.get(key, default)
    if not isinstance(value, list):
        raise HTTPException(status_code=400, detail=f"'{key}' must be a list of strings")
    cleaned = [str(x).strip() for x in value if str(x).strip()]
    if not cleaned:
        return list(default)
    return cleaned


def _normalize_top(params: dict[str, Any], default: int = 100) -> int:
    top = params.get("top")
    if top is not None:
        try:
            return min(max(1, int(top)), 999)
        except (TypeError, ValueError):
            return default
    return default


def _normalize_string_map(value: Any, field_name: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise HTTPException(status_code=400, detail=f"'{field_name}' must be an object")
    normalized = {
        str(key).strip(): str(item).strip()
        for key, item in value.items()
        if str(key).strip() and str(item).strip()
    }
    if len(normalized) != len(value):
        raise HTTPException(status_code=400, detail=f"Invalid '{field_name}' entries")
    return normalized


def _normalize_string_list_field(
    params: dict[str, Any],
    *keys: str,
    required: bool = False,
) -> list[str]:
    for key in keys:
        if key not in params:
            continue
        value = params.get(key)
        if not isinstance(value, list):
            raise HTTPException(status_code=400, detail=f"'{key}' must be a list of strings")
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if required and not cleaned:
            raise HTTPException(
                status_code=400, detail=f"'{key}' must contain at least one non-empty value"
            )
        return cleaned
    if required:
        joined = "', '".join(keys)
        raise HTTPException(status_code=400, detail=f"Missing '{joined}'")
    return []


def _normalize_dict_field(
    params: dict[str, Any],
    *keys: str,
    required: bool = False,
) -> dict[str, Any] | None:
    for key in keys:
        if key not in params:
            continue
        value = params.get(key)
        if not isinstance(value, dict):
            raise HTTPException(status_code=400, detail=f"'{key}' must be an object")
        return value
    if required:
        joined = "', '".join(keys)
        raise HTTPException(status_code=400, detail=f"Missing '{joined}'")
    return None


def _normalize_dict_list_field(
    params: dict[str, Any],
    *keys: str,
    required: bool = False,
) -> list[dict[str, Any]]:
    for key in keys:
        if key not in params:
            continue
        value = params.get(key)
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise HTTPException(status_code=400, detail=f"'{key}' must be a list of objects")
        if required and not value:
            raise HTTPException(status_code=400, detail=f"'{key}' must not be empty")
        return value
    if required:
        joined = "', '".join(keys)
        raise HTTPException(status_code=400, detail=f"Missing '{joined}'")
    return []


def _normalize_bool_field(params: dict[str, Any], *keys: str, default: bool) -> bool:
    for key in keys:
        if key in params:
            value = params.get(key)
            if not isinstance(value, bool):
                raise HTTPException(status_code=400, detail=f"'{key}' must be a boolean")
            return value
    return default


def _normalize_user_context(params: dict[str, Any]) -> str | None:
    return _first_str(params, "userId", "user_id", "userPrincipalName", "mailbox")


def _normalize_drive_target(params: dict[str, Any]) -> dict[str, Any]:
    return {
        "drive_id": _first_str(params, "driveId", "drive_id"),
        "group_id": _first_str(params, "groupId", "group_id"),
        "site_id": _first_str(params, "siteId", "site_id"),
        "user_id_or_upn": _normalize_user_context(params),
    }


def _normalize_office_remote_path(params: dict[str, Any], extension: str) -> str:
    remote_path = _first_str(params, "remotePath", "remote_path", "path", "fileName", "file_name")
    if not remote_path:
        raise HTTPException(status_code=400, detail="Missing 'remotePath' or 'fileName'")
    normalized = remote_path.strip("/")
    dotted_extension = f".{extension}"
    if "." not in Path(normalized).name:
        return f"{normalized}{dotted_extension}"
    if not normalized.lower().endswith(dotted_extension):
        raise HTTPException(
            status_code=400,
            detail=f"Remote path must end with '{dotted_extension}'",
        )
    return normalized


def _normalize_document_payload(params: dict[str, Any]) -> dict[str, Any]:
    paragraphs = params.get("paragraphs")
    if paragraphs is not None and not isinstance(paragraphs, list):
        raise HTTPException(status_code=400, detail="'paragraphs' must be a list of strings")
    return {
        "title": _first_str(params, "title", "name"),
        "paragraphs": [str(item) for item in paragraphs or [] if str(item).strip()],
        "content": _optional_str(params, "content"),
    }


def _normalize_workbook_payload(params: dict[str, Any]) -> list[dict[str, Any]]:
    raw = params.get("worksheets")
    if raw is None:
        rows = params.get("rows")
        if rows is None:
            raise HTTPException(status_code=400, detail="Missing 'worksheets' or 'rows'")
        raw = [{"name": _first_str(params, "sheetName", "sheet_name") or "Sheet1", "rows": rows}]
    if not isinstance(raw, list) or not raw:
        raise HTTPException(status_code=400, detail="'worksheets' must be a non-empty list")
    normalized: list[dict[str, Any]] = []
    for index, worksheet in enumerate(raw, start=1):
        if not isinstance(worksheet, dict):
            raise HTTPException(status_code=400, detail="Each worksheet must be an object")
        rows = worksheet.get("rows")
        if not isinstance(rows, list):
            raise HTTPException(status_code=400, detail="Each worksheet requires a 'rows' list")
        normalized_rows: list[list[Any]] = []
        for row in rows:
            if isinstance(row, list):
                normalized_rows.append(list(row))
            else:
                normalized_rows.append([row])
        normalized.append(
            {
                "name": str(worksheet.get("name") or f"Sheet{index}").strip() or f"Sheet{index}",
                "rows": normalized_rows,
            }
        )
    return normalized


def _normalize_presentation_payload(params: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    title = _first_str(params, "title", "name") or "SMARTHAUS Presentation"
    raw_slides = params.get("slides")
    if raw_slides is None:
        bullets = params.get("bullets") or params.get("items") or []
        if isinstance(bullets, str):
            bullets = [line for line in bullets.splitlines() if line.strip()]
        elif not isinstance(bullets, list):
            raise HTTPException(status_code=400, detail="'bullets' must be a list of strings")
        raw_slides = [{"title": title, "bullets": bullets}]
    if not isinstance(raw_slides, list) or not raw_slides:
        raise HTTPException(status_code=400, detail="'slides' must be a non-empty list")
    normalized: list[dict[str, Any]] = []
    for index, slide in enumerate(raw_slides, start=1):
        if not isinstance(slide, dict):
            raise HTTPException(status_code=400, detail="Each slide must be an object")
        bullets = slide.get("bullets") or slide.get("items") or []
        if isinstance(bullets, str):
            bullet_list = [line for line in bullets.splitlines() if line.strip()]
        elif isinstance(bullets, list):
            bullet_list = [str(item) for item in bullets if str(item).strip()]
        else:
            raise HTTPException(status_code=400, detail="Each slide 'bullets' value must be a list")
        normalized.append(
            {
                "title": str(slide.get("title") or f"Slide {index}").strip() or f"Slide {index}",
                "bullets": bullet_list,
            }
        )
    return title, normalized


def _normalize_email_addresses(value: Any, field_name: str) -> list[str]:
    if isinstance(value, str):
        parts = [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]
        if not parts:
            raise HTTPException(status_code=400, detail=f"Missing or invalid '{field_name}'")
        return parts
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        if not parts:
            raise HTTPException(status_code=400, detail=f"Missing or invalid '{field_name}'")
        return parts
    raise HTTPException(status_code=400, detail=f"Missing or invalid '{field_name}'")


def _normalize_datetime_value(value: Any, field_name: str) -> dict[str, Any]:
    if isinstance(value, dict) and value.get("dateTime"):
        return value
    if isinstance(value, str) and value.strip():
        return {"dateTime": value.strip(), "timeZone": "UTC"}
    raise HTTPException(status_code=400, detail=f"Missing or invalid '{field_name}'")


def _normalize_event_body(params: dict[str, Any], *, require_full: bool) -> dict[str, Any]:
    raw_body = params.get("body")
    if isinstance(raw_body, dict) and raw_body:
        return raw_body

    body: dict[str, Any] = {}
    subject = _optional_str(params, "subject")
    if subject is not None:
        body["subject"] = subject
    elif require_full:
        raise HTTPException(status_code=400, detail="Missing or invalid 'subject'")

    raw_body_content = params.get("bodyContent", params.get("body"))
    if isinstance(raw_body_content, str) and raw_body_content.strip():
        body["body"] = {
            "contentType": _optional_str(params, "contentType") or "Text",
            "content": raw_body_content.strip(),
        }
    elif isinstance(raw_body_content, dict) and raw_body_content:
        body["body"] = raw_body_content

    if "start" in params or "startTime" in params:
        body["start"] = _normalize_datetime_value(
            params.get("start", params.get("startTime")),
            "start",
        )
    elif require_full:
        raise HTTPException(status_code=400, detail="Missing or invalid 'start'")

    if "end" in params or "endTime" in params:
        body["end"] = _normalize_datetime_value(
            params.get("end", params.get("endTime")),
            "end",
        )
    elif require_full:
        raise HTTPException(status_code=400, detail="Missing or invalid 'end'")

    for field in ("location", "attendees", "isOnlineMeeting", "recurrence"):
        if field in params:
            body[field] = params[field]

    if not body:
        raise HTTPException(status_code=400, detail="Missing or invalid event payload")
    return body


def _normalize_contact_body(params: dict[str, Any], *, require_any: bool) -> dict[str, Any]:
    raw_body = params.get("body")
    if isinstance(raw_body, dict) and raw_body:
        return raw_body

    body: dict[str, Any] = {}
    for field in (
        "displayName",
        "givenName",
        "surname",
        "companyName",
        "jobTitle",
        "department",
        "mobilePhone",
        "businessPhones",
    ):
        if field in params:
            body[field] = params[field]

    email_addresses = params.get("emailAddresses")
    if email_addresses is None and params.get("email"):
        email_addresses = [
            {
                "address": _require_str(params, "email"),
                "name": _optional_str(params, "displayName")
                or _optional_str(params, "givenName")
                or "",
            }
        ]
    if email_addresses is not None:
        if not isinstance(email_addresses, list) or not email_addresses:
            raise HTTPException(status_code=400, detail="Missing or invalid 'emailAddresses'")
        body["emailAddresses"] = email_addresses

    if require_any and not body:
        raise HTTPException(status_code=400, detail="Missing or invalid contact payload")
    return body


def _slugify_mail_nickname(value: str) -> str:
    cleaned = value.strip().lower()
    slug = re.sub(r"[^a-z0-9-]+", "-", cleaned)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if not slug:
        raise HTTPException(status_code=400, detail="Missing or invalid 'mail_nickname'")
    return slug


def _normalize_params(action: str, params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise HTTPException(status_code=400, detail="params must be an object")
    if action == "create_site":
        display_name = _optional_str(params, "display_name") or _optional_str(params, "site_name")
        if not display_name:
            raise HTTPException(status_code=400, detail="Missing or invalid 'display_name'")
        mail_nickname = _optional_str(params, "mail_nickname") or _optional_str(params, "url_slug")
        if not mail_nickname:
            mail_nickname = _slugify_mail_nickname(display_name)
        else:
            mail_nickname = _slugify_mail_nickname(mail_nickname)
        libraries = _normalize_str_list(params, "libraries", ["Documents"])
        description = _optional_str(params, "description")
        return {
            "display_name": display_name,
            "mail_nickname": mail_nickname,
            "libraries": libraries,
            "description": description,
        }
    if action == "create_team":
        mail_nickname = _optional_str(params, "mail_nickname")
        if not mail_nickname:
            team_name = _optional_str(params, "team_name")
            if team_name:
                mail_nickname = _slugify_mail_nickname(team_name)
        if not mail_nickname:
            raise HTTPException(status_code=400, detail="Missing or invalid 'mail_nickname'")
        mail_nickname = _slugify_mail_nickname(mail_nickname)
        channels = _normalize_str_list(params, "channels", ["General"])
        return {"mail_nickname": mail_nickname, "channels": channels}
    if action == "add_channel":
        mail_nickname = _optional_str(params, "mail_nickname")
        if not mail_nickname:
            team_name = _optional_str(params, "team_name")
            if team_name:
                mail_nickname = _slugify_mail_nickname(team_name)
        if not mail_nickname:
            raise HTTPException(status_code=400, detail="Missing or invalid 'mail_nickname'")
        mail_nickname = _slugify_mail_nickname(mail_nickname)
        channel_name = _require_str(params, "channel_name")
        description = _optional_str(params, "description")
        return {
            "mail_nickname": mail_nickname,
            "channel_name": channel_name,
            "description": description,
        }
    if action in {"get_team", "list_channels", "create_channel"}:
        team_id = _first_str(params, "teamId", "team_id", "id")
        group_id = _first_str(params, "groupId", "group_id")
        mail_nickname = _first_str(params, "mail_nickname", "mailNickname")
        if not team_id and not group_id and not mail_nickname:
            raise HTTPException(
                status_code=400,
                detail="Missing team selector ('teamId', 'groupId', or 'mail_nickname')",
            )
        normalized: dict[str, Any] = {
            "team_id": team_id,
            "group_id": group_id,
            "mail_nickname": _slugify_mail_nickname(mail_nickname) if mail_nickname else None,
        }
        if action == "create_channel":
            channel_display_name: str | None = _first_str(
                params, "channel_name", "displayName", "name"
            )
            if not channel_display_name:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'channel_name', 'displayName', or 'name'",
                )
            normalized["channel_name"] = channel_display_name
            normalized["description"] = _optional_str(params, "description")
        elif action == "list_channels":
            normalized["top"] = _normalize_top(params)
        return normalized
    if action in {"list_plans", "create_plan"}:
        group_id = _first_str(params, "groupId", "group_id", "id")
        mail_nickname = _first_str(params, "mail_nickname", "mailNickname")
        if not group_id and not mail_nickname:
            raise HTTPException(
                status_code=400,
                detail="Missing plan owner ('groupId' or 'mail_nickname')",
            )
        normalized_plan: dict[str, Any] = {
            "group_id": group_id,
            "mail_nickname": _slugify_mail_nickname(mail_nickname) if mail_nickname else None,
        }
        if action == "create_plan":
            title = _first_str(params, "title", "name")
            if not title:
                raise HTTPException(status_code=400, detail="Missing 'title' or 'name'")
            normalized_plan["title"] = title
        return normalized_plan
    if action in {"list_plan_buckets", "create_plan_bucket", "create_plan_task"}:
        plan_id = _first_str(params, "planId", "plan_id", "id")
        if not plan_id:
            raise HTTPException(status_code=400, detail="Missing 'planId', 'plan_id', or 'id'")
        normalized_bucket: dict[str, Any] = {"plan_id": plan_id}
        if action == "list_plan_buckets":
            return normalized_bucket
        if action == "create_plan_bucket":
            bucket_name = _first_str(params, "name", "bucketName", "bucket_name")
            if not bucket_name:
                raise HTTPException(status_code=400, detail="Missing 'name' or 'bucketName'")
            normalized_bucket["name"] = bucket_name
            normalized_bucket["order_hint"] = _first_str(params, "orderHint", "order_hint") or " !"
            return normalized_bucket
        bucket_id = _first_str(params, "bucketId", "bucket_id")
        title = _first_str(params, "title", "name")
        if not bucket_id or not title:
            raise HTTPException(status_code=400, detail="Missing 'bucketId' or 'title'")
        percent_complete = params.get("percentComplete", params.get("percent_complete"))
        if percent_complete is not None:
            try:
                percent_complete = int(percent_complete)
            except (TypeError, ValueError) as exc:
                raise HTTPException(
                    status_code=400,
                    detail="percentComplete must be an integer",
                ) from exc
        normalized_bucket.update(
            {
                "bucket_id": bucket_id,
                "title": title,
                "description": _optional_str(params, "description"),
                "reference_url": _first_str(params, "referenceUrl", "reference_url", "url"),
                "percent_complete": percent_complete,
            }
        )
        return normalized_bucket
    if action == "provision_service":
        key = _optional_str(params, "key") or _optional_str(params, "service_name")
        if not key:
            raise HTTPException(status_code=400, detail="Missing or invalid 'key'")
        return {"key": key}
    if action == "list_users":
        top = _normalize_top(params)
        select = (
            _optional_str(params, "select")
            or "id,displayName,userPrincipalName,mail,jobTitle,accountEnabled"
        )
        return {"top": top, "select": select}
    if action == "list_teams":
        return {"top": _normalize_top(params)}
    if action == "list_sites":
        return {"top": _normalize_top(params)}
    if action in {"get_site", "list_site_lists"}:
        site_id = _first_str(params, "siteId", "site_id", "id")
        if not site_id:
            raise HTTPException(status_code=400, detail="Missing 'siteId', 'site_id', or 'id'")
        if action == "get_site":
            return {"site_id": site_id}
        return {"site_id": site_id, "top": _normalize_top(params)}
    if action in {"get_list", "list_list_items", "create_list_item"}:
        site_id = _first_str(params, "siteId", "site_id")
        list_id = _first_str(params, "listId", "list_id", "id")
        if not site_id or not list_id:
            raise HTTPException(status_code=400, detail="Missing 'siteId' or 'listId'")
        if action == "get_list":
            return {"site_id": site_id, "list_id": list_id}
        if action == "list_list_items":
            return {
                "site_id": site_id,
                "list_id": list_id,
                "top": _normalize_top(params, default=50),
            }
        fields = params.get("fields")
        if not isinstance(fields, dict) or not fields:
            raise HTTPException(status_code=400, detail="Missing or invalid 'fields'")
        return {"site_id": site_id, "list_id": list_id, "fields": fields}
    if action == "list_drives":
        return {
            "group_id": _first_str(params, "groupId", "group_id"),
            "site_id": _first_str(params, "siteId", "site_id"),
            "user_id_or_upn": _normalize_user_context(params),
            "top": _normalize_top(params),
        }
    if action == "get_drive":
        drive_id = _first_str(params, "driveId", "drive_id", "id")
        if not drive_id:
            raise HTTPException(status_code=400, detail="Missing 'driveId', 'drive_id', or 'id'")
        return {"drive_id": drive_id}
    if action == "list_drive_items":
        return {
            "drive_id": _first_str(params, "driveId", "drive_id"),
            "group_id": _first_str(params, "groupId", "group_id"),
            "site_id": _first_str(params, "siteId", "site_id"),
            "user_id_or_upn": _normalize_user_context(params),
            "folder_id": _first_str(params, "folderId", "folder_id"),
            "folder_path": _first_str(params, "folderPath", "folder_path", "path"),
            "top": _normalize_top(params),
        }
    if action == "get_drive_item":
        drive_id = _first_str(params, "driveId", "drive_id")
        item_id = _first_str(params, "itemId", "item_id", "id")
        if not drive_id or not item_id:
            raise HTTPException(status_code=400, detail="Missing 'driveId' or 'itemId'")
        return {"drive_id": drive_id, "item_id": item_id}
    if action == "create_folder":
        folder_name = _first_str(params, "name", "folderName", "folder_name")
        if not folder_name:
            raise HTTPException(status_code=400, detail="Missing 'name' or 'folderName'")
        return {
            "name": folder_name,
            "drive_id": _first_str(params, "driveId", "drive_id"),
            "group_id": _first_str(params, "groupId", "group_id"),
            "site_id": _first_str(params, "siteId", "site_id"),
            "user_id_or_upn": _normalize_user_context(params),
            "parent_id": _first_str(params, "parentId", "parent_id") or "root",
            "conflict_behavior": _first_str(params, "conflictBehavior", "conflict_behavior")
            or "rename",
        }
    if action == "upload_file":
        local_path = _first_str(params, "filePath", "localPath", "local_path")
        remote_path = _first_str(
            params, "remotePath", "remote_path", "path", "fileName", "file_name"
        )
        if not local_path or not remote_path:
            raise HTTPException(status_code=400, detail="Missing 'filePath' or 'remotePath'")
        return {
            "local_path": local_path,
            "remote_path": remote_path,
            "drive_id": _first_str(params, "driveId", "drive_id"),
            "group_id": _first_str(params, "groupId", "group_id"),
            "site_id": _first_str(params, "siteId", "site_id"),
            "user_id_or_upn": _normalize_user_context(params),
            "conflict_behavior": _first_str(params, "conflictBehavior", "conflict_behavior")
            or "replace",
            "content_type": _first_str(params, "contentType", "content_type"),
        }
    if action in {"create_document", "update_document"}:
        return {
            **_normalize_drive_target(params),
            "remote_path": _normalize_office_remote_path(params, "docx"),
            "payload": _normalize_document_payload(params),
            "conflict_behavior": _first_str(params, "conflictBehavior", "conflict_behavior")
            or "replace",
        }
    if action in {"create_workbook", "update_workbook"}:
        return {
            **_normalize_drive_target(params),
            "remote_path": _normalize_office_remote_path(params, "xlsx"),
            "worksheets": _normalize_workbook_payload(params),
            "conflict_behavior": _first_str(params, "conflictBehavior", "conflict_behavior")
            or "replace",
        }
    if action in {"create_presentation", "update_presentation"}:
        presentation_title, slides = _normalize_presentation_payload(params)
        return {
            **_normalize_drive_target(params),
            "remote_path": _normalize_office_remote_path(params, "pptx"),
            "title": presentation_title,
            "slides": slides,
            "conflict_behavior": _first_str(params, "conflictBehavior", "conflict_behavior")
            or "replace",
        }
    if action in {
        "list_flows_admin",
        "list_http_flows",
        "get_flow_admin",
        "list_flow_owners",
        "list_flow_runs",
        "set_flow_owner_role",
        "remove_flow_owner_role",
        "enable_flow",
        "disable_flow",
        "delete_flow",
        "restore_flow",
    }:
        environment_name = _first_str(
            params,
            "environmentName",
            "environment_name",
            "environment",
            "environmentId",
            "environment_id",
        )
        if not environment_name:
            raise HTTPException(
                status_code=400,
                detail="Missing 'environmentName', 'environment_name', or 'environment'",
            )
        normalized_flow: dict[str, Any] = {"environment_name": environment_name}
        if action in {"list_flows_admin", "list_http_flows"}:
            normalized_flow["top"] = _normalize_top(params, default=50)
            return normalized_flow
        flow_name = _first_str(params, "flowName", "flow_name", "flowId", "flow_id", "id")
        if not flow_name:
            raise HTTPException(
                status_code=400,
                detail="Missing 'flowName', 'flow_name', 'flowId', 'flow_id', or 'id'",
            )
        normalized_flow["flow_name"] = flow_name
        if action == "list_flow_owners":
            return normalized_flow
        if action == "list_flow_runs":
            normalized_flow["top"] = _normalize_top(params, default=25)
            return normalized_flow
        if action == "set_flow_owner_role":
            principal_object_id = _first_str(
                params,
                "principalObjectId",
                "principal_object_id",
                "userId",
                "user_id",
                "id",
            )
            if not principal_object_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'principalObjectId', 'principal_object_id', or 'userId'",
                )
            normalized_flow["principal_object_id"] = principal_object_id
            normalized_flow["role_name"] = _first_str(params, "roleName", "role_name") or "CanEdit"
            normalized_flow["principal_type"] = (
                _first_str(params, "principalType", "principal_type") or "User"
            )
            return normalized_flow
        if action == "remove_flow_owner_role":
            role_id = _first_str(params, "roleId", "role_id")
            if not role_id:
                raise HTTPException(status_code=400, detail="Missing 'roleId' or 'role_id'")
            normalized_flow["role_id"] = role_id
        return normalized_flow
    if action == "invoke_flow_callback":
        callback_url = _first_str(params, "callbackUrl", "callback_url", "url")
        if not callback_url:
            raise HTTPException(
                status_code=400,
                detail="Missing 'callbackUrl', 'callback_url', or 'url'",
            )
        timeout_seconds = params.get("timeoutSeconds", params.get("timeout_seconds", 30))
        try:
            normalized_timeout = max(1, int(timeout_seconds))
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail="timeoutSeconds must be an integer",
            ) from exc
        return {
            "callback_url": callback_url,
            "body": params.get("body", params.get("payload", {})),
            "headers": _normalize_string_map(params.get("headers"), "headers"),
            "timeout_seconds": normalized_timeout,
        }
    if action in {
        "list_powerapps_admin",
        "get_powerapp_admin",
        "list_powerapp_role_assignments",
        "set_powerapp_owner",
        "remove_powerapp_role_assignment",
        "delete_powerapp",
        "list_powerapp_environments",
        "get_powerapp_environment",
        "list_powerapp_environment_role_assignments",
        "set_powerapp_environment_role_assignment",
        "remove_powerapp_environment_role_assignment",
    }:
        if action == "list_powerapp_environments":
            return {"top": _normalize_top(params, default=50)}
        environment_name = _first_str(
            params,
            "environmentName",
            "environment_name",
            "environment",
            "environmentId",
            "environment_id",
            "id",
        )
        if action == "list_powerapps_admin":
            return {
                "environment_name": environment_name,
                "owner": _first_str(params, "owner", "ownerId", "owner_id", "userId", "user_id"),
                "filter_text": _first_str(params, "filter", "filterText", "filter_text"),
                "top": _normalize_top(params, default=50),
            }
        if not environment_name:
            raise HTTPException(
                status_code=400,
                detail="Missing 'environmentName', 'environment_name', 'environment', or 'id'",
            )
        if action == "get_powerapp_environment":
            return {"environment_name": environment_name}
        if action == "list_powerapp_environment_role_assignments":
            return {
                "environment_name": environment_name,
                "user_id": _first_str(params, "userId", "user_id"),
            }
        if action == "set_powerapp_environment_role_assignment":
            principal_object_id = _first_str(
                params,
                "principalObjectId",
                "principal_object_id",
                "userId",
                "user_id",
            )
            if not principal_object_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'principalObjectId', 'principal_object_id', or 'userId'",
                )
            role_name = _first_str(params, "roleName", "role_name")
            if not role_name:
                raise HTTPException(status_code=400, detail="Missing 'roleName' or 'role_name'")
            return {
                "environment_name": environment_name,
                "principal_object_id": principal_object_id,
                "role_name": role_name,
                "principal_type": _first_str(params, "principalType", "principal_type") or "User",
            }
        if action == "remove_powerapp_environment_role_assignment":
            role_id = _first_str(params, "roleId", "role_id")
            if not role_id:
                raise HTTPException(status_code=400, detail="Missing 'roleId' or 'role_id'")
            return {
                "environment_name": environment_name,
                "role_id": role_id,
            }
        app_name = _first_str(params, "appName", "app_name", "appId", "app_id", "id")
        if action == "list_powerapps_admin":
            raise AssertionError("list_powerapps_admin must return before app normalization")
        if not app_name:
            raise HTTPException(
                status_code=400,
                detail="Missing 'appName', 'app_name', 'appId', 'app_id', or 'id'",
            )
        normalized_powerapp: dict[str, Any] = {
            "environment_name": environment_name,
            "app_name": app_name,
        }
        if action == "get_powerapp_admin":
            return normalized_powerapp
        if action == "list_powerapp_role_assignments":
            normalized_powerapp["user_id"] = _first_str(params, "userId", "user_id")
            return normalized_powerapp
        if action == "set_powerapp_owner":
            owner_object_id = _first_str(
                params,
                "ownerObjectId",
                "owner_object_id",
                "principalObjectId",
                "principal_object_id",
                "userId",
                "user_id",
            )
            if not owner_object_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'ownerObjectId', 'owner_object_id', or 'principalObjectId'",
                )
            normalized_powerapp["owner_object_id"] = owner_object_id
            return normalized_powerapp
        if action == "remove_powerapp_role_assignment":
            role_id = _first_str(params, "roleId", "role_id")
            if not role_id:
                raise HTTPException(status_code=400, detail="Missing 'roleId' or 'role_id'")
            normalized_powerapp["role_id"] = role_id
        return normalized_powerapp
    if action in {
        "list_powerbi_workspaces",
        "get_powerbi_workspace",
        "list_powerbi_reports",
        "get_powerbi_report",
        "list_powerbi_datasets",
        "get_powerbi_dataset",
        "refresh_powerbi_dataset",
        "list_powerbi_dataset_refreshes",
        "list_powerbi_dashboards",
        "get_powerbi_dashboard",
    }:
        if action == "list_powerbi_workspaces":
            return {"top": _normalize_top(params, default=50)}
        workspace_id = _first_str(
            params,
            "workspaceId",
            "workspace_id",
            "groupId",
            "group_id",
            "id",
        )
        if not workspace_id:
            raise HTTPException(
                status_code=400,
                detail="Missing 'workspaceId', 'workspace_id', 'groupId', 'group_id', or 'id'",
            )
        if action == "get_powerbi_workspace":
            return {"workspace_id": workspace_id}
        if action in {
            "list_powerbi_reports",
            "list_powerbi_datasets",
            "list_powerbi_dashboards",
        }:
            return {"workspace_id": workspace_id, "top": _normalize_top(params, default=50)}
        if action == "list_powerbi_dataset_refreshes":
            dataset_id = _first_str(params, "datasetId", "dataset_id")
            if not dataset_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'datasetId' or 'dataset_id'",
                )
            return {
                "workspace_id": workspace_id,
                "dataset_id": dataset_id,
                "top": _normalize_top(params, default=50),
            }
        if action == "get_powerbi_report":
            report_id = _first_str(params, "reportId", "report_id", "id")
            if not report_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'reportId', 'report_id', or 'id'",
                )
            return {"workspace_id": workspace_id, "report_id": report_id}
        if action in {"get_powerbi_dataset", "refresh_powerbi_dataset"}:
            dataset_id = _first_str(params, "datasetId", "dataset_id", "id")
            if not dataset_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'datasetId', 'dataset_id', or 'id'",
                )
            normalized_dataset = {"workspace_id": workspace_id, "dataset_id": dataset_id}
            if action == "refresh_powerbi_dataset":
                normalized_dataset["notify_option"] = (
                    _first_str(params, "notifyOption", "notify_option") or "NoNotification"
                )
            return normalized_dataset
        if action == "get_powerbi_dashboard":
            dashboard_id = _first_str(params, "dashboardId", "dashboard_id", "id")
            if not dashboard_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'dashboardId', 'dashboard_id', or 'id'",
                )
            return {"workspace_id": workspace_id, "dashboard_id": dashboard_id}
        raise HTTPException(status_code=400, detail=f"Unknown Power BI action: {action}")
    if action in {
        "get_approval_solution",
        "list_approval_items",
        "get_approval_item",
        "create_approval_item",
        "list_approval_item_requests",
        "respond_to_approval_item",
        "list_external_connections",
        "get_external_connection",
        "create_external_connection",
        "register_external_connection_schema",
        "get_external_item",
        "upsert_external_item",
        "create_external_group",
        "add_external_group_member",
    }:
        if action == "get_approval_solution":
            return {}
        if action in {"list_approval_items", "list_external_connections"}:
            return {"top": _normalize_top(params, default=50)}
        if action == "get_approval_item":
            approval_id = _first_str(params, "approvalId", "approval_id", "id")
            if not approval_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'approvalId', 'approval_id', or 'id'",
                )
            return {"approval_id": approval_id}
        if action == "create_approval_item":
            display_name = _first_str(params, "displayName", "display_name", "title")
            description = _first_str(params, "description", "details", "body")
            if not display_name or not description:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'displayName'/'title' or 'description'/'details'",
                )
            return {
                "display_name": display_name,
                "description": description,
                "approver_user_ids": _normalize_string_list_field(
                    params,
                    "approverUserIds",
                    "approver_user_ids",
                    required=True,
                ),
                "approver_group_ids": _normalize_string_list_field(
                    params,
                    "approverGroupIds",
                    "approver_group_ids",
                ),
                "approval_type": _first_str(params, "approvalType", "approval_type") or "basic",
                "allow_email_notification": _normalize_bool_field(
                    params,
                    "allowEmailNotification",
                    "allow_email_notification",
                    default=True,
                ),
            }
        if action == "list_approval_item_requests":
            approval_id = _first_str(params, "approvalId", "approval_id", "id")
            if not approval_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'approvalId', 'approval_id', or 'id'",
                )
            return {"approval_id": approval_id, "top": _normalize_top(params, default=50)}
        if action == "respond_to_approval_item":
            approval_id = _first_str(params, "approvalId", "approval_id", "id")
            response_value = _first_str(params, "response", "decision")
            if not approval_id or not response_value:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'approvalId'/'id' or 'response'/'decision'",
                )
            return {
                "approval_id": approval_id,
                "response": response_value,
                "comments": _first_str(params, "comments", "comment"),
            }
        connection_id = _first_str(params, "connectionId", "connection_id", "id")
        if action == "get_external_connection":
            if not connection_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'connectionId', 'connection_id', or 'id'",
                )
            return {"connection_id": connection_id}
        if action == "create_external_connection":
            if not connection_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'connectionId', 'connection_id', or 'id'",
                )
            name = _first_str(params, "name", "displayName", "display_name", "title")
            if not name:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'name', 'displayName', 'display_name', or 'title'",
                )
            return {
                "connection_id": connection_id,
                "name": name,
                "description": _first_str(params, "description"),
            }
        if action == "register_external_connection_schema":
            if not connection_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'connectionId', 'connection_id', or 'id'",
                )
            schema = _normalize_dict_field(params, "schema")
            if schema is None:
                schema_properties = _normalize_dict_list_field(params, "properties", required=True)
                schema = {
                    "baseType": _first_str(params, "baseType", "base_type")
                    or "microsoft.graph.externalItem",
                    "properties": schema_properties,
                }
            return {"connection_id": connection_id, "schema": schema}
        if action == "get_external_item":
            if not connection_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'connectionId', 'connection_id'",
                )
            item_id = _first_str(params, "itemId", "item_id", "id")
            if not item_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'itemId', 'item_id', or 'id'",
                )
            return {"connection_id": connection_id, "item_id": item_id}
        if action == "upsert_external_item":
            if not connection_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'connectionId', 'connection_id'",
                )
            item_id = _first_str(params, "itemId", "item_id", "id")
            if not item_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'itemId', 'item_id', or 'id'",
                )
            properties = _normalize_dict_field(params, "properties", required=True)
            return {
                "connection_id": connection_id,
                "item_id": item_id,
                "acl": _normalize_dict_list_field(params, "acl", required=True),
                "properties": properties or {},
                "content": _normalize_dict_field(params, "content"),
            }
        if action == "create_external_group":
            if not connection_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'connectionId', 'connection_id'",
                )
            group_id = _first_str(params, "groupId", "group_id", "id")
            if not group_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'groupId', 'group_id', or 'id'",
                )
            return {
                "connection_id": connection_id,
                "group_id": group_id,
                "display_name": _first_str(params, "displayName", "display_name", "name"),
                "description": _first_str(params, "description"),
            }
        if action == "add_external_group_member":
            if not connection_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'connectionId', 'connection_id'",
                )
            group_id = _first_str(params, "groupId", "group_id")
            member_id = _first_str(params, "memberId", "member_id", "id")
            if not group_id or not member_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'groupId'/'group_id' or 'memberId'/'member_id'/'id'",
                )
            return {
                "connection_id": connection_id,
                "group_id": group_id,
                "member_id": member_id,
                "member_type": _first_str(params, "memberType", "member_type") or "user",
                "identity_source": _first_str(
                    params,
                    "identitySource",
                    "identity_source",
                )
                or "azureActiveDirectory",
            }
        raise HTTPException(
            status_code=400,
            detail=f"Unknown Forms/Approvals/Connectors action: {action}",
        )
    if action == "list_automation_recipes":
        return {
            "department": _first_str(params, "department"),
            "persona": _first_str(params, "persona"),
            "workload": _first_str(params, "workload"),
            "top": _normalize_top(params, default=50),
        }
    if action == "get_automation_recipe":
        recipe_id = _first_str(params, "recipeId", "recipe_id", "id")
        if not recipe_id:
            raise HTTPException(status_code=400, detail="Missing 'recipeId', 'recipe_id', or 'id'")
        return {"recipe_id": recipe_id}
    if action == "get_user":
        user_id_or_upn = _first_str(params, "userPrincipalName", "user_id", "id")
        if not user_id_or_upn:
            raise HTTPException(
                status_code=400, detail="Missing 'userPrincipalName', 'user_id', or 'id'"
            )
        return {"user_id_or_upn": user_id_or_upn}
    if action == "reset_user_password":
        user_id_or_upn = _first_str(params, "userPrincipalName", "user_id", "id")
        if not user_id_or_upn:
            raise HTTPException(
                status_code=400, detail="Missing 'userPrincipalName', 'user_id', or 'id'"
            )
        pwd = _optional_str(params, "temporary_password") or _optional_str(params, "password")
        if not pwd:
            raise HTTPException(
                status_code=400, detail="Missing 'temporary_password' or 'password'"
            )
        return {
            "user_id_or_upn": user_id_or_upn,
            "temporary_password": pwd,
            "force_change_next_sign_in": params.get("force_change_next_sign_in", True),
        }
    if action == "create_user":
        user_principal_name = _first_str(params, "userPrincipalName", "user_principal_name")
        password = _first_str(params, "password", "temporary_password")
        if not user_principal_name or not password:
            raise HTTPException(status_code=400, detail="Missing 'userPrincipalName' or 'password'")
        account_enabled = params.get("accountEnabled", True)
        if not isinstance(account_enabled, bool):
            raise HTTPException(status_code=400, detail="accountEnabled must be a boolean")
        return {
            "user_principal_name": user_principal_name,
            "display_name": _first_str(params, "displayName", "display_name"),
            "mail_nickname": _first_str(params, "mailNickname", "mail_nickname"),
            "password": password,
            "account_enabled": account_enabled,
            "job_title": _first_str(params, "jobTitle", "job_title"),
            "department": _optional_str(params, "department"),
        }
    if action == "update_user":
        user_id_or_upn = _first_str(params, "userPrincipalName", "user_id", "id")
        if not user_id_or_upn:
            raise HTTPException(
                status_code=400, detail="Missing 'userPrincipalName', 'user_id', or 'id'"
            )
        patch: dict[str, Any] = {}
        display_name = _first_str(params, "displayName", "display_name")
        job_title = _first_str(params, "jobTitle", "job_title")
        department = _optional_str(params, "department")
        account_enabled = params.get("accountEnabled")
        if display_name is not None:
            patch["displayName"] = display_name
        if job_title is not None:
            patch["jobTitle"] = job_title
        if department is not None:
            patch["department"] = department
        if account_enabled is not None:
            if not isinstance(account_enabled, bool):
                raise HTTPException(status_code=400, detail="accountEnabled must be a boolean")
            patch["accountEnabled"] = account_enabled
        if not patch:
            raise HTTPException(status_code=400, detail="No user fields provided for update")
        return {"user_id_or_upn": user_id_or_upn, "patch": patch}
    if action == "disable_user":
        user_id_or_upn = _first_str(params, "userPrincipalName", "user_id", "id")
        if not user_id_or_upn:
            raise HTTPException(
                status_code=400, detail="Missing 'userPrincipalName', 'user_id', or 'id'"
            )
        return {"user_id_or_upn": user_id_or_upn}
    if action == "list_groups":
        return {"top": _normalize_top(params)}
    if action == "get_group":
        group_id = _first_str(params, "group_id", "groupId", "id")
        mail_nickname = _first_str(params, "mail_nickname", "mailNickname")
        if not group_id and not mail_nickname:
            raise HTTPException(
                status_code=400, detail="Missing 'group_id', 'id', or 'mail_nickname'"
            )
        return {"group_id": group_id, "mail_nickname": mail_nickname}
    if action == "create_group":
        display_name = _first_str(params, "display_name", "displayName")
        mail_nickname = _first_str(params, "mail_nickname", "mailNickname")
        if not display_name or not mail_nickname:
            raise HTTPException(status_code=400, detail="Missing 'display_name' or 'mail_nickname'")
        mail_enabled = params.get("mail_enabled", params.get("mailEnabled", True))
        security_enabled = params.get("security_enabled", params.get("securityEnabled", False))
        if not isinstance(mail_enabled, bool) or not isinstance(security_enabled, bool):
            raise HTTPException(
                status_code=400, detail="mailEnabled/securityEnabled must be booleans"
            )
        return {
            "display_name": display_name,
            "mail_nickname": _slugify_mail_nickname(mail_nickname),
            "description": _optional_str(params, "description"),
            "mail_enabled": mail_enabled,
            "security_enabled": security_enabled,
        }
    if action == "list_group_members":
        group_id = _first_str(params, "group_id", "groupId", "id")
        if not group_id:
            raise HTTPException(status_code=400, detail="Missing 'group_id' or 'id'")
        return {"group_id": group_id}
    if action in {"add_group_member", "remove_group_member"}:
        group_id = _first_str(params, "group_id", "groupId", "id")
        member_id = _first_str(params, "member_id", "memberId", "user_id", "userId")
        if not group_id or not member_id:
            raise HTTPException(status_code=400, detail="Missing 'group_id' or 'member_id'")
        return {"group_id": group_id, "member_id": member_id}
    if action == "assign_user_license":
        user_id_or_upn = _first_str(params, "userPrincipalName", "user_id", "id")
        licenses = params.get("licenses")
        disabled_plans = params.get("disabled_plans", params.get("disabledPlans", {}))
        if not user_id_or_upn:
            raise HTTPException(
                status_code=400, detail="Missing 'userPrincipalName', 'user_id', or 'id'"
            )
        if not isinstance(licenses, list) or not licenses:
            raise HTTPException(status_code=400, detail="'licenses' must be a non-empty list")
        if disabled_plans is not None and not isinstance(disabled_plans, dict):
            raise HTTPException(status_code=400, detail="'disabled_plans' must be an object")
        return {
            "user_id_or_upn": user_id_or_upn,
            "licenses": [str(item).strip() for item in licenses if str(item).strip()],
            "disabled_plans": disabled_plans or {},
        }
    if action in {"list_directory_roles", "list_applications", "list_service_principals"}:
        return {"top": _normalize_top(params)}
    if action == "list_directory_role_members":
        role_id = _first_str(params, "role_id", "roleId", "id")
        if not role_id:
            raise HTTPException(status_code=400, detail="Missing 'role_id', 'roleId', or 'id'")
        return {"role_id": role_id}
    if action in {"list_domains", "get_organization"}:
        return {}
    if action in {"get_application", "update_application"}:
        app_id = _first_str(params, "app_id", "appId", "id")
        if not app_id:
            raise HTTPException(status_code=400, detail="Missing 'app_id', 'appId', or 'id'")
        if action == "get_application":
            return {"app_id": app_id}
        body = params.get("body")
        if not isinstance(body, dict) or not body:
            raise HTTPException(status_code=400, detail="Missing or invalid 'body'")
        return {"app_id": app_id, "body": body}
    if action == "list_messages":
        return {
            "user_id_or_upn": _normalize_user_context(params),
            "top": _normalize_top(params, default=25),
            "select": _optional_str(params, "select") or "id,subject,from,receivedDateTime,isRead",
        }
    if action in {"get_message", "delete_message"}:
        message_id = _first_str(params, "messageId", "message_id", "id")
        if not message_id:
            raise HTTPException(
                status_code=400, detail="Missing 'messageId', 'message_id', or 'id'"
            )
        return {"message_id": message_id, "user_id_or_upn": _normalize_user_context(params)}
    if action == "send_mail":
        recipients = params.get("recipient_or_to", params.get("to", params.get("recipient")))
        subject = _optional_str(params, "subject")
        body = params.get("body", params.get("content"))
        if recipients is None or not subject or body is None:
            raise HTTPException(status_code=400, detail="Missing recipient, subject, or body")
        save_to_sent_items = params.get("saveToSentItems", params.get("save_to_sent_items", True))
        if not isinstance(save_to_sent_items, bool):
            raise HTTPException(status_code=400, detail="saveToSentItems must be a boolean")
        return {
            "recipient_or_to": _normalize_email_addresses(recipients, "recipient_or_to"),
            "subject": subject,
            "body": body,
            "content_type": _optional_str(params, "contentType") or "Text",
            "save_to_sent_items": save_to_sent_items,
            "user_id_or_upn": _normalize_user_context(params) or _first_str(params, "from"),
        }
    if action == "move_message":
        message_id = _first_str(params, "messageId", "message_id", "id")
        destination_id = _first_str(params, "destinationId", "folderId", "destination_id")
        if not message_id or not destination_id:
            raise HTTPException(status_code=400, detail="Missing messageId or destinationId")
        return {
            "message_id": message_id,
            "destination_id": destination_id,
            "user_id_or_upn": _normalize_user_context(params),
        }
    if action == "list_mail_folders":
        return {
            "user_id_or_upn": _normalize_user_context(params),
            "top": _normalize_top(params),
        }
    if action == "get_mailbox_settings":
        return {"user_id_or_upn": _normalize_user_context(params)}
    if action == "update_mailbox_settings":
        body = params.get("body")
        if not isinstance(body, dict) or not body:
            raise HTTPException(status_code=400, detail="Missing or invalid 'body'")
        return {"user_id_or_upn": _normalize_user_context(params), "body": body}
    if action == "list_events":
        return {
            "user_id_or_upn": _normalize_user_context(params),
            "top": _normalize_top(params, default=25),
        }
    if action == "create_event":
        return {
            "user_id_or_upn": _normalize_user_context(params),
            "body": _normalize_event_body(params, require_full=True),
        }
    if action in {"get_event", "delete_event"}:
        event_id = _first_str(params, "eventId", "event_id", "id")
        if not event_id:
            raise HTTPException(status_code=400, detail="Missing 'eventId', 'event_id', or 'id'")
        return {"event_id": event_id, "user_id_or_upn": _normalize_user_context(params)}
    if action == "update_event":
        event_id = _first_str(params, "eventId", "event_id", "id")
        if not event_id:
            raise HTTPException(status_code=400, detail="Missing 'eventId', 'event_id', or 'id'")
        return {
            "event_id": event_id,
            "user_id_or_upn": _normalize_user_context(params),
            "patch": _normalize_event_body(params, require_full=False),
        }
    if action == "get_schedule":
        schedules = params.get("schedules")
        scoped_user = _normalize_user_context(params)
        if schedules is None:
            schedules = [scoped_user] if scoped_user else []
        if not isinstance(schedules, list) or not schedules:
            raise HTTPException(status_code=400, detail="Missing or invalid 'schedules'")
        return {
            "user_id_or_upn": scoped_user,
            "schedules": [str(item).strip() for item in schedules if str(item).strip()],
            "start_time": _normalize_datetime_value(
                params.get("startTime", params.get("start")),
                "startTime",
            ),
            "end_time": _normalize_datetime_value(
                params.get("endTime", params.get("end")),
                "endTime",
            ),
            "availability_view_interval": int(params.get("availabilityViewInterval", 30)),
        }
    if action in {"list_contacts", "list_contact_folders"}:
        return {
            "user_id_or_upn": _normalize_user_context(params),
            "top": _normalize_top(params),
        }
    if action in {"get_contact", "delete_contact"}:
        contact_id = _first_str(params, "contactId", "contact_id", "id")
        if not contact_id:
            raise HTTPException(
                status_code=400, detail="Missing 'contactId', 'contact_id', or 'id'"
            )
        return {"contact_id": contact_id, "user_id_or_upn": _normalize_user_context(params)}
    if action == "create_contact":
        return {
            "user_id_or_upn": _normalize_user_context(params),
            "body": _normalize_contact_body(params, require_any=True),
        }
    if action == "update_contact":
        contact_id = _first_str(params, "contactId", "contact_id", "id")
        if not contact_id:
            raise HTTPException(
                status_code=400, detail="Missing 'contactId', 'contact_id', or 'id'"
            )
        return {
            "contact_id": contact_id,
            "user_id_or_upn": _normalize_user_context(params),
            "patch": _normalize_contact_body(params, require_any=True),
        }
    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


def _graph_client(action: str | None = None) -> GraphClient:
    if has_selected_tenant():
        tenant_cfg = get_tenant_config()
        if action:
            route_key = executor_route_for_action(None, action)
            if route_key and len(getattr(tenant_cfg, "executors", {}) or {}) > 1:
                executor_name = tenant_cfg.resolve_executor_name(
                    route_key,
                    fallback_keys=[route_key],
                )
                tenant_cfg = tenant_cfg.project_executor(executor_name)
        has_identity = bool(tenant_cfg.azure.tenant_id and tenant_cfg.azure.client_id)
        has_credential = bool(
            tenant_cfg.azure.client_secret or tenant_cfg.azure.client_certificate_path
        )
        if not has_identity:
            raise SmarthausError(
                "Graph not configured: set UCP_TENANT to a tenant with azure.tenant_id "
                "and azure.client_id"
            )
        if tenant_cfg.auth.mode != "delegated" and not has_credential:
            raise SmarthausError(
                "Graph not configured: selected tenant is missing app-only credentials "
                "(azure.client_secret or azure.client_certificate_path)"
            )
        return GraphClient(tenant_config=tenant_cfg)

    config = AppConfig()
    if not (config.graph.tenant_id and config.graph.client_id and config.graph.client_secret):
        raise SmarthausError(
            "Graph not configured: either select UCP_TENANT or set "
            "GRAPH_TENANT_ID, GRAPH_CLIENT_ID, and GRAPH_CLIENT_SECRET"
        )
    return GraphClient(config=config)


def _power_automate_client(action: str | None = None) -> PowerAutomateClient:
    if has_selected_tenant():
        tenant_cfg = get_tenant_config()
        if action:
            route_key = executor_route_for_action(None, action)
            if route_key and len(getattr(tenant_cfg, "executors", {}) or {}) > 1:
                executor_name = tenant_cfg.resolve_executor_name(
                    route_key,
                    fallback_keys=[route_key],
                )
                tenant_cfg = tenant_cfg.project_executor(executor_name)
        return PowerAutomateClient(tenant_config=tenant_cfg)

    config = AppConfig()
    return PowerAutomateClient(legacy_config=config)


def _power_apps_client(action: str | None = None) -> PowerAppsClient:
    if has_selected_tenant():
        tenant_cfg = get_tenant_config()
        if action:
            route_key = executor_route_for_action(None, action)
            if route_key and len(getattr(tenant_cfg, "executors", {}) or {}) > 1:
                executor_name = tenant_cfg.resolve_executor_name(
                    route_key,
                    fallback_keys=[route_key],
                )
                tenant_cfg = tenant_cfg.project_executor(executor_name)
        return PowerAppsClient(tenant_config=tenant_cfg)

    config = AppConfig()
    return PowerAppsClient(legacy_config=config)


def _power_bi_client(action: str | None = None) -> PowerBIClient:
    if has_selected_tenant():
        tenant_cfg = get_tenant_config()
        if action:
            route_key = executor_route_for_action(None, action)
            if route_key and len(getattr(tenant_cfg, "executors", {}) or {}) > 1:
                executor_name = tenant_cfg.resolve_executor_name(
                    route_key,
                    fallback_keys=[route_key],
                )
                tenant_cfg = tenant_cfg.project_executor(executor_name)
        return PowerBIClient(tenant_config=tenant_cfg)

    config = AppConfig()
    return PowerBIClient(legacy_config=config)


def _forms_approvals_connectors_client(
    action: str | None = None,
) -> FormsApprovalsConnectorsClient:
    if has_selected_tenant():
        tenant_cfg = get_tenant_config()
        if action:
            route_key = executor_route_for_action(None, action)
            if route_key and len(getattr(tenant_cfg, "executors", {}) or {}) > 1:
                executor_name = tenant_cfg.resolve_executor_name(
                    route_key,
                    fallback_keys=[route_key],
                )
                tenant_cfg = tenant_cfg.project_executor(executor_name)
        return FormsApprovalsConnectorsClient(tenant_config=tenant_cfg)

    config = AppConfig()
    return FormsApprovalsConnectorsClient(legacy_config=config)


def _automation_recipe_client() -> AutomationRecipeClient:
    return AutomationRecipeClient()


def _execute_action(action: str, params: dict[str, Any]) -> dict[str, Any]:
    if action == "create_site":
        result = provision_group_site(
            display_name=params["display_name"],
            mail_nickname=params["mail_nickname"],
            libraries=params["libraries"],
            description=params.get("description"),
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        return result
    if action == "create_team":
        result = provision_teams_workspace(params["mail_nickname"], params["channels"])
        inc_teams_created()
        return result
    if action == "add_channel":
        result = provision_teams_workspace(params["mail_nickname"], [params["channel_name"]])
        if params.get("description"):
            result["description"] = params["description"]
        return {"team": result, "channel": params["channel_name"]}
    if action == "get_team":
        client = _graph_client(action)
        return {
            "team": client.get_team(
                params.get("team_id"),
                group_id=params.get("group_id"),
                mail_nickname=params.get("mail_nickname"),
            )
        }
    if action == "list_channels":
        client = _graph_client(action)
        value = client.list_channels(
            params.get("team_id"),
            group_id=params.get("group_id"),
            mail_nickname=params.get("mail_nickname"),
        )[: params.get("top", 100)]
        return {"channels": value, "count": len(value)}
    if action == "create_channel":
        client = _graph_client(action)
        return {
            "channel": client.create_channel(
                params["channel_name"],
                team_id=params.get("team_id"),
                group_id=params.get("group_id"),
                mail_nickname=params.get("mail_nickname"),
                description=params.get("description"),
            ),
            "status": "created",
        }
    if action == "list_plans":
        client = _graph_client(action)
        value = client.list_plans(
            group_id=params.get("group_id"),
            mail_nickname=params.get("mail_nickname"),
        )
        return {"plans": value, "count": len(value)}
    if action == "create_plan":
        client = _graph_client(action)
        return {
            "plan": client.create_plan(
                params.get("group_id"),
                params["title"],
                mail_nickname=params.get("mail_nickname"),
            ),
            "status": "created",
        }
    if action == "list_plan_buckets":
        client = _graph_client(action)
        value = client.list_plan_buckets(params["plan_id"])
        return {"buckets": value, "count": len(value)}
    if action == "create_plan_bucket":
        client = _graph_client(action)
        return {
            "bucket": client.create_plan_bucket(
                params["plan_id"],
                params["name"],
                order_hint=params.get("order_hint", " !"),
            ),
            "status": "created",
        }
    if action == "create_plan_task":
        client = _graph_client(action)
        return {
            "task": client.create_plan_task(
                params["plan_id"],
                params["bucket_id"],
                params["title"],
                description=params.get("description"),
                reference_url=params.get("reference_url"),
                percent_complete=params.get("percent_complete"),
            ),
            "status": "created",
        }
    if action == "provision_service":
        return provision_service(params["key"])
    if action == "list_users":
        client = _graph_client(action)
        data = client.list_users(top=params["top"], select=params.get("select"))
        return {"users": data.get("value", []), "count": len(data.get("value", []))}
    if action == "list_teams":
        client = _graph_client(action)
        data = client.list_teams()
        value = data.get("value", [])[: params.get("top", 100)]
        return {"teams": value, "count": len(value)}
    if action == "list_sites":
        client = _graph_client(action)
        data = client.list_sites(top=params["top"])
        value = data.get("value", [])
        return {"sites": value, "count": len(value)}
    if action == "get_site":
        client = _graph_client(action)
        return {"site": client.get_site(params["site_id"])}
    if action == "list_site_lists":
        client = _graph_client(action)
        value = client.list_site_lists(params["site_id"], top=params["top"])
        return {"lists": value, "count": len(value)}
    if action == "get_list":
        client = _graph_client(action)
        return {"list": client.get_list(params["site_id"], params["list_id"])}
    if action == "list_list_items":
        client = _graph_client(action)
        data = client.list_list_items(params["site_id"], params["list_id"], top=params["top"])
        value = data.get("value", [])
        return {"items": value, "count": len(value)}
    if action == "create_list_item":
        client = _graph_client(action)
        return {
            "item": client.create_list_item(params["site_id"], params["list_id"], params["fields"]),
            "status": "created",
        }
    if action == "list_drives":
        client = _graph_client(action)
        data = client.list_drives(
            group_id=params.get("group_id"),
            site_id=params.get("site_id"),
            user_id_or_upn=params.get("user_id_or_upn"),
            top=params["top"],
        )
        value = data.get("value", [])
        return {"drives": value, "count": len(value)}
    if action == "get_drive":
        client = _graph_client(action)
        return {"drive": client.get_drive(params["drive_id"])}
    if action == "list_drive_items":
        client = _graph_client(action)
        data = client.list_drive_items(
            drive_id=params.get("drive_id"),
            group_id=params.get("group_id"),
            site_id=params.get("site_id"),
            user_id_or_upn=params.get("user_id_or_upn"),
            folder_id=params.get("folder_id"),
            folder_path=params.get("folder_path"),
            top=params["top"],
        )
        value = data.get("value", [])
        return {"items": value, "count": len(value)}
    if action == "get_drive_item":
        client = _graph_client(action)
        return {"item": client.get_drive_item(params["drive_id"], params["item_id"])}
    if action == "create_folder":
        client = _graph_client(action)
        return {
            "folder": client.create_folder(
                params["name"],
                drive_id=params.get("drive_id"),
                group_id=params.get("group_id"),
                site_id=params.get("site_id"),
                user_id_or_upn=params.get("user_id_or_upn"),
                parent_id=params.get("parent_id", "root"),
                conflict_behavior=params.get("conflict_behavior", "rename"),
            ),
            "status": "created",
        }
    if action == "upload_file":
        client = _graph_client(action)
        return {
            "file": client.upload_file(
                params["local_path"],
                params["remote_path"],
                drive_id=params.get("drive_id"),
                group_id=params.get("group_id"),
                site_id=params.get("site_id"),
                user_id_or_upn=params.get("user_id_or_upn"),
                conflict_behavior=params.get("conflict_behavior", "replace"),
                content_type=params.get("content_type"),
            ),
            "status": "uploaded",
        }
    if action in {"create_document", "update_document"}:
        client = _graph_client(action)
        document = client.upload_bytes(
            file_bytes=generate_docx_bytes(**params["payload"]),
            remote_path=params["remote_path"],
            drive_id=params.get("drive_id"),
            group_id=params.get("group_id"),
            site_id=params.get("site_id"),
            user_id_or_upn=params.get("user_id_or_upn"),
            conflict_behavior=params.get("conflict_behavior", "replace"),
            content_type=DOCUMENT_CONTENT_TYPE,
            source_name=Path(params["remote_path"]).name,
        )
        return {
            "document": document,
            "status": "created" if action == "create_document" else "updated",
        }
    if action in {"create_workbook", "update_workbook"}:
        client = _graph_client(action)
        workbook = client.upload_bytes(
            file_bytes=generate_xlsx_bytes(params["worksheets"]),
            remote_path=params["remote_path"],
            drive_id=params.get("drive_id"),
            group_id=params.get("group_id"),
            site_id=params.get("site_id"),
            user_id_or_upn=params.get("user_id_or_upn"),
            conflict_behavior=params.get("conflict_behavior", "replace"),
            content_type=WORKBOOK_CONTENT_TYPE,
            source_name=Path(params["remote_path"]).name,
        )
        return {
            "workbook": workbook,
            "status": "created" if action == "create_workbook" else "updated",
        }
    if action in {"create_presentation", "update_presentation"}:
        client = _graph_client(action)
        presentation = client.upload_bytes(
            file_bytes=generate_pptx_bytes(title=params["title"], slides=params["slides"]),
            remote_path=params["remote_path"],
            drive_id=params.get("drive_id"),
            group_id=params.get("group_id"),
            site_id=params.get("site_id"),
            user_id_or_upn=params.get("user_id_or_upn"),
            conflict_behavior=params.get("conflict_behavior", "replace"),
            content_type=PRESENTATION_CONTENT_TYPE,
            source_name=Path(params["remote_path"]).name,
        )
        return {
            "presentation": presentation,
            "status": "created" if action == "create_presentation" else "updated",
        }
    if action == "list_flows_admin":
        pa_client = _power_automate_client(action)
        value = pa_client.list_flows_admin(params["environment_name"])[: params["top"]]
        return {"flows": value, "count": len(value)}
    if action == "get_flow_admin":
        pa_client = _power_automate_client(action)
        return {
            "flow": pa_client.get_flow_admin(
                params["environment_name"],
                params["flow_name"],
            )
        }
    if action == "list_http_flows":
        pa_client = _power_automate_client(action)
        value = pa_client.list_http_flows(params["environment_name"])[: params["top"]]
        return {"flows": value, "count": len(value)}
    if action == "list_flow_owners":
        pa_client = _power_automate_client(action)
        value = pa_client.list_flow_owners(
            params["environment_name"],
            params["flow_name"],
        )
        return {"owners": value, "count": len(value)}
    if action == "list_flow_runs":
        pa_client = _power_automate_client(action)
        value = pa_client.list_flow_runs(
            params["environment_name"],
            params["flow_name"],
        )[: params["top"]]
        return {"runs": value, "count": len(value)}
    if action == "set_flow_owner_role":
        pa_client = _power_automate_client(action)
        return pa_client.set_flow_owner_role(
            params["environment_name"],
            params["flow_name"],
            params["principal_object_id"],
            role_name=params.get("role_name", "CanEdit"),
            principal_type=params.get("principal_type", "User"),
        )
    if action == "remove_flow_owner_role":
        pa_client = _power_automate_client(action)
        return pa_client.remove_flow_owner_role(
            params["environment_name"],
            params["flow_name"],
            params["role_id"],
        )
    if action == "enable_flow":
        pa_client = _power_automate_client(action)
        return pa_client.enable_flow(params["environment_name"], params["flow_name"])
    if action == "disable_flow":
        pa_client = _power_automate_client(action)
        return pa_client.disable_flow(params["environment_name"], params["flow_name"])
    if action == "delete_flow":
        pa_client = _power_automate_client(action)
        return pa_client.delete_flow(params["environment_name"], params["flow_name"])
    if action == "restore_flow":
        pa_client = _power_automate_client(action)
        return pa_client.restore_flow(params["environment_name"], params["flow_name"])
    if action == "invoke_flow_callback":
        pa_client = _power_automate_client(action)
        return pa_client.invoke_flow_callback(
            params["callback_url"],
            params.get("body", {}),
            headers=params.get("headers"),
            timeout_seconds=params.get("timeout_seconds", 30),
        )
    if action == "list_powerapps_admin":
        power_apps_client = _power_apps_client(action)
        value = power_apps_client.list_powerapps_admin(
            environment_name=params.get("environment_name"),
            owner=params.get("owner"),
            filter_text=params.get("filter_text"),
        )[: params["top"]]
        return {"apps": value, "count": len(value)}
    if action == "get_powerapp_admin":
        power_apps_client = _power_apps_client(action)
        return {
            "app": power_apps_client.get_powerapp_admin(
                params["environment_name"],
                params["app_name"],
            )
        }
    if action == "list_powerapp_role_assignments":
        power_apps_client = _power_apps_client(action)
        value = power_apps_client.list_powerapp_role_assignments(
            params["environment_name"],
            params["app_name"],
            user_id=params.get("user_id"),
        )
        return {"roles": value, "count": len(value)}
    if action == "set_powerapp_owner":
        power_apps_client = _power_apps_client(action)
        return power_apps_client.set_powerapp_owner(
            params["environment_name"],
            params["app_name"],
            params["owner_object_id"],
        )
    if action == "remove_powerapp_role_assignment":
        power_apps_client = _power_apps_client(action)
        return power_apps_client.remove_powerapp_role_assignment(
            params["environment_name"],
            params["app_name"],
            params["role_id"],
        )
    if action == "delete_powerapp":
        power_apps_client = _power_apps_client(action)
        return power_apps_client.delete_powerapp(
            params["environment_name"],
            params["app_name"],
        )
    if action == "list_powerapp_environments":
        power_apps_client = _power_apps_client(action)
        value = power_apps_client.list_powerapp_environments()[: params["top"]]
        return {"environments": value, "count": len(value)}
    if action == "get_powerapp_environment":
        power_apps_client = _power_apps_client(action)
        return {
            "environment": power_apps_client.get_powerapp_environment(params["environment_name"])
        }
    if action == "list_powerapp_environment_role_assignments":
        power_apps_client = _power_apps_client(action)
        value = power_apps_client.list_powerapp_environment_role_assignments(
            params["environment_name"],
            user_id=params.get("user_id"),
        )
        return {"roles": value, "count": len(value)}
    if action == "set_powerapp_environment_role_assignment":
        power_apps_client = _power_apps_client(action)
        return power_apps_client.set_powerapp_environment_role_assignment(
            params["environment_name"],
            params["principal_object_id"],
            role_name=params["role_name"],
            principal_type=params.get("principal_type", "User"),
        )
    if action == "remove_powerapp_environment_role_assignment":
        power_apps_client = _power_apps_client(action)
        return power_apps_client.remove_powerapp_environment_role_assignment(
            params["environment_name"],
            params["role_id"],
        )
    if action == "list_powerbi_workspaces":
        power_bi_client = _power_bi_client(action)
        value = power_bi_client.list_workspaces()[: params["top"]]
        return {"workspaces": value, "count": len(value)}
    if action == "get_powerbi_workspace":
        power_bi_client = _power_bi_client(action)
        return {"workspace": power_bi_client.get_workspace(params["workspace_id"])}
    if action == "list_powerbi_reports":
        power_bi_client = _power_bi_client(action)
        value = power_bi_client.list_reports(params["workspace_id"])[: params["top"]]
        return {"reports": value, "count": len(value)}
    if action == "get_powerbi_report":
        power_bi_client = _power_bi_client(action)
        return {
            "report": power_bi_client.get_report(
                params["workspace_id"],
                params["report_id"],
            )
        }
    if action == "list_powerbi_datasets":
        power_bi_client = _power_bi_client(action)
        value = power_bi_client.list_datasets(params["workspace_id"])[: params["top"]]
        return {"datasets": value, "count": len(value)}
    if action == "get_powerbi_dataset":
        power_bi_client = _power_bi_client(action)
        return {
            "dataset": power_bi_client.get_dataset(
                params["workspace_id"],
                params["dataset_id"],
            )
        }
    if action == "refresh_powerbi_dataset":
        power_bi_client = _power_bi_client(action)
        return power_bi_client.refresh_dataset(
            params["workspace_id"],
            params["dataset_id"],
            notify_option=params.get("notify_option", "NoNotification"),
        )
    if action == "list_powerbi_dataset_refreshes":
        power_bi_client = _power_bi_client(action)
        value = power_bi_client.list_dataset_refreshes(
            params["workspace_id"],
            params["dataset_id"],
        )[: params["top"]]
        return {"refreshes": value, "count": len(value)}
    if action == "list_powerbi_dashboards":
        power_bi_client = _power_bi_client(action)
        value = power_bi_client.list_dashboards(params["workspace_id"])[: params["top"]]
        return {"dashboards": value, "count": len(value)}
    if action == "get_powerbi_dashboard":
        power_bi_client = _power_bi_client(action)
        return {
            "dashboard": power_bi_client.get_dashboard(
                params["workspace_id"],
                params["dashboard_id"],
            )
        }
    if action == "get_approval_solution":
        fac_client = _forms_approvals_connectors_client(action)
        return {"solution": fac_client.get_approval_solution()}
    if action == "list_approval_items":
        fac_client = _forms_approvals_connectors_client(action)
        value = fac_client.list_approval_items(top=params["top"])
        return {"approvals": value, "count": len(value)}
    if action == "get_approval_item":
        fac_client = _forms_approvals_connectors_client(action)
        return {"approval": fac_client.get_approval_item(params["approval_id"])}
    if action == "create_approval_item":
        fac_client = _forms_approvals_connectors_client(action)
        return fac_client.create_approval_item(
            display_name=params["display_name"],
            description=params["description"],
            approver_user_ids=params["approver_user_ids"],
            approver_group_ids=params.get("approver_group_ids") or [],
            approval_type=params.get("approval_type", "basic"),
            allow_email_notification=params.get("allow_email_notification", True),
        )
    if action == "list_approval_item_requests":
        fac_client = _forms_approvals_connectors_client(action)
        value = fac_client.list_approval_item_requests(
            params["approval_id"],
            top=params["top"],
        )
        return {"requests": value, "count": len(value)}
    if action == "respond_to_approval_item":
        fac_client = _forms_approvals_connectors_client(action)
        return fac_client.respond_to_approval_item(
            params["approval_id"],
            response=params["response"],
            comments=params.get("comments"),
        )
    if action == "list_external_connections":
        fac_client = _forms_approvals_connectors_client(action)
        value = fac_client.list_external_connections(top=params["top"])
        return {"connections": value, "count": len(value)}
    if action == "get_external_connection":
        fac_client = _forms_approvals_connectors_client(action)
        return {"connection": fac_client.get_external_connection(params["connection_id"])}
    if action == "create_external_connection":
        fac_client = _forms_approvals_connectors_client(action)
        return {
            "connection": fac_client.create_external_connection(
                connection_id=params["connection_id"],
                name=params["name"],
                description=params.get("description"),
            )
        }
    if action == "register_external_connection_schema":
        fac_client = _forms_approvals_connectors_client(action)
        return fac_client.register_external_connection_schema(
            params["connection_id"],
            schema=params["schema"],
        )
    if action == "get_external_item":
        fac_client = _forms_approvals_connectors_client(action)
        return {
            "item": fac_client.get_external_item(
                params["connection_id"],
                params["item_id"],
            )
        }
    if action == "upsert_external_item":
        fac_client = _forms_approvals_connectors_client(action)
        return fac_client.upsert_external_item(
            params["connection_id"],
            params["item_id"],
            acl=params["acl"],
            properties=params["properties"],
            content=params.get("content"),
        )
    if action == "create_external_group":
        fac_client = _forms_approvals_connectors_client(action)
        group = fac_client.create_external_group(
            params["connection_id"],
            group_id=params["group_id"],
            display_name=params.get("display_name"),
            description=params.get("description"),
        )
        return {"group": group, "status": "created"}
    if action == "add_external_group_member":
        fac_client = _forms_approvals_connectors_client(action)
        return fac_client.add_external_group_member(
            params["connection_id"],
            params["group_id"],
            member_id=params["member_id"],
            member_type=params.get("member_type", "user"),
            identity_source=params.get("identity_source", "azureActiveDirectory"),
        )
    if action == "list_automation_recipes":
        recipe_client = _automation_recipe_client()
        value = recipe_client.list_recipes(
            department=params.get("department"),
            persona=params.get("persona"),
            workload=params.get("workload"),
            top=params["top"],
        )
        return {"recipes": value, "count": len(value)}
    if action == "get_automation_recipe":
        recipe_client = _automation_recipe_client()
        return {"recipe": recipe_client.get_recipe(params["recipe_id"])}
    if action == "get_user":
        client = _graph_client(action)
        user = client.get_user(params["user_id_or_upn"])
        return {"user": user}
    if action == "reset_user_password":
        client = _graph_client(action)
        return client.reset_user_password(
            params["user_id_or_upn"],
            params["temporary_password"],
            force_change_next_sign_in=params.get("force_change_next_sign_in", True),
        )
    if action == "create_user":
        client = _graph_client(action)
        user = client.create_user(
            params["user_principal_name"],
            display_name=params.get("display_name"),
            mail_nickname=params.get("mail_nickname"),
            password=params["password"],
            account_enabled=params.get("account_enabled", True),
            job_title=params.get("job_title"),
            department=params.get("department"),
        )
        return {"user": user, "temporaryPassword": params["password"]}
    if action == "update_user":
        client = _graph_client(action)
        return {"user": client.update_user(params["user_id_or_upn"], params["patch"])}
    if action == "disable_user":
        client = _graph_client(action)
        return client.disable_user(params["user_id_or_upn"])
    if action == "list_groups":
        client = _graph_client(action)
        data = client.list_groups(top=params["top"])
        value = data.get("value", [])
        return {"groups": value, "count": len(value)}
    if action == "get_group":
        client = _graph_client(action)
        group = client.get_group(
            group_id=params.get("group_id"), mail_nickname=params.get("mail_nickname")
        )
        return {"group": group}
    if action == "create_group":
        client = _graph_client(action)
        group = client.create_group(
            params["display_name"],
            params["mail_nickname"],
            description=params.get("description"),
            mail_enabled=params.get("mail_enabled", True),
            security_enabled=params.get("security_enabled", False),
        )
        return {
            "group_id": group.get("id"),
            "display_name": group.get("displayName"),
            "mail_nickname": group.get("mailNickname"),
        }
    if action == "list_group_members":
        client = _graph_client(action)
        data = client.list_group_members(params["group_id"])
        value = data.get("value", [])
        return {"members": value, "count": len(value)}
    if action == "add_group_member":
        client = _graph_client(action)
        client.add_group_member(params["group_id"], params["member_id"])
        return {"group_id": params["group_id"], "member_id": params["member_id"], "added": True}
    if action == "remove_group_member":
        client = _graph_client(action)
        client.remove_group_member(params["group_id"], params["member_id"])
        return {
            "group_id": params["group_id"],
            "member_id": params["member_id"],
            "removed": True,
        }
    if action == "assign_user_license":
        client = _graph_client(action)
        return client.assign_user_license(
            params["user_id_or_upn"],
            params["licenses"],
            disabled_plans=params.get("disabled_plans"),
        )
    if action == "list_directory_roles":
        client = _graph_client(action)
        data = client.list_directory_roles(top=params["top"])
        value = data.get("value", [])
        return {"roles": value, "count": len(value)}
    if action == "list_directory_role_members":
        client = _graph_client(action)
        data = client.list_directory_role_members(params["role_id"])
        value = data.get("value", [])
        return {"members": value, "count": len(value)}
    if action == "list_domains":
        client = _graph_client(action)
        data = client.list_domains()
        value = data.get("value", [])
        return {"domains": value, "count": len(value)}
    if action == "get_organization":
        client = _graph_client(action)
        data = client.get_organization()
        value = data.get("value", [])
        return {"organization": value[0] if value else None}
    if action == "list_applications":
        client = _graph_client(action)
        data = client.list_applications(top=params["top"])
        value = data.get("value", [])
        return {"applications": value, "count": len(value)}
    if action == "get_application":
        client = _graph_client(action)
        return {"application": client.get_application(params["app_id"])}
    if action == "update_application":
        client = _graph_client(action)
        client.update_application(params["app_id"], params["body"])
        return {"app_id": params["app_id"], "status": "updated"}
    if action == "list_service_principals":
        client = _graph_client(action)
        data = client.list_service_principals(top=params["top"])
        value = data.get("value", [])
        return {"service_principals": value, "count": len(value)}
    if action == "list_messages":
        client = _graph_client(action)
        select = _optional_str(params, "select")
        data = client.list_messages(
            user_id_or_upn=params.get("user_id_or_upn"),
            top=params["top"],
            select=select,
        )
        value = data.get("value", [])
        return {"messages": value, "count": len(value)}
    if action == "get_message":
        client = _graph_client(action)
        return {
            "message": client.get_message(
                params["message_id"], user_id_or_upn=params.get("user_id_or_upn")
            )
        }
    if action == "send_mail":
        client = _graph_client(action)
        return client.send_mail(
            params["recipient_or_to"],
            params["subject"],
            params["body"],
            user_id_or_upn=params.get("user_id_or_upn"),
            content_type=params.get("content_type", "Text"),
            save_to_sent_items=params.get("save_to_sent_items", True),
        )
    if action == "move_message":
        client = _graph_client(action)
        return client.move_message(
            params["message_id"],
            params["destination_id"],
            user_id_or_upn=params.get("user_id_or_upn"),
        )
    if action == "delete_message":
        client = _graph_client(action)
        return client.delete_message(
            params["message_id"], user_id_or_upn=params.get("user_id_or_upn")
        )
    if action == "list_mail_folders":
        client = _graph_client(action)
        data = client.list_mail_folders(
            user_id_or_upn=params.get("user_id_or_upn"),
            top=params["top"],
        )
        value = data.get("value", [])
        return {"folders": value, "count": len(value)}
    if action == "get_mailbox_settings":
        client = _graph_client(action)
        return {
            "settings": client.get_mailbox_settings(user_id_or_upn=params.get("user_id_or_upn"))
        }
    if action == "update_mailbox_settings":
        client = _graph_client(action)
        return {
            "updated": True,
            "settings": client.update_mailbox_settings(
                params["body"], user_id_or_upn=params.get("user_id_or_upn")
            ),
        }
    if action == "list_events":
        client = _graph_client(action)
        data = client.list_events(user_id_or_upn=params.get("user_id_or_upn"), top=params["top"])
        value = data.get("value", [])
        return {"events": value, "count": len(value)}
    if action == "create_event":
        client = _graph_client(action)
        return {
            "event": client.create_event(
                params["body"], user_id_or_upn=params.get("user_id_or_upn")
            ),
            "status": "created",
        }
    if action == "get_event":
        client = _graph_client(action)
        return {
            "event": client.get_event(
                params["event_id"], user_id_or_upn=params.get("user_id_or_upn")
            )
        }
    if action == "update_event":
        client = _graph_client(action)
        client.update_event(
            params["event_id"],
            params["patch"],
            user_id_or_upn=params.get("user_id_or_upn"),
        )
        return {"updated": True, "eventId": params["event_id"]}
    if action == "delete_event":
        client = _graph_client(action)
        return client.delete_event(params["event_id"], user_id_or_upn=params.get("user_id_or_upn"))
    if action == "get_schedule":
        client = _graph_client(action)
        data = client.get_schedule(
            params["schedules"],
            params["start_time"],
            params["end_time"],
            user_id_or_upn=params.get("user_id_or_upn"),
            availability_view_interval=params.get("availability_view_interval", 30),
        )
        value = data.get("value", [])
        return {"schedules": value, "count": len(value)}
    if action == "list_contacts":
        client = _graph_client(action)
        data = client.list_contacts(
            user_id_or_upn=params.get("user_id_or_upn"),
            top=params["top"],
        )
        value = data.get("value", [])
        return {"contacts": value, "count": len(value)}
    if action == "get_contact":
        client = _graph_client(action)
        return {
            "contact": client.get_contact(
                params["contact_id"], user_id_or_upn=params.get("user_id_or_upn")
            )
        }
    if action == "create_contact":
        client = _graph_client(action)
        return {
            "contact": client.create_contact(
                params["body"], user_id_or_upn=params.get("user_id_or_upn")
            ),
            "status": "created",
        }
    if action == "update_contact":
        client = _graph_client(action)
        client.update_contact(
            params["contact_id"],
            params["patch"],
            user_id_or_upn=params.get("user_id_or_upn"),
        )
        return {"updated": True, "contactId": params["contact_id"]}
    if action == "delete_contact":
        client = _graph_client(action)
        return client.delete_contact(
            params["contact_id"], user_id_or_upn=params.get("user_id_or_upn")
        )
    if action == "list_contact_folders":
        client = _graph_client(action)
        data = client.list_contact_folders(
            user_id_or_upn=params.get("user_id_or_upn"),
            top=params["top"],
        )
        value = data.get("value", [])
        return {"folders": value, "count": len(value)}
    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


def _audit_instruction(
    action: str,
    params: dict[str, Any],
    response_payload: dict[str, Any],
    user_info: dict[str, Any] | None,
    *,
    blocked: bool = False,
    idempotent_replay: bool = False,
) -> None:
    log_event(
        "m365_instruction",
        {
            "action": action,
            "params": params,
            "ok": response_payload.get("ok"),
            "result": response_payload.get("result"),
            "error": response_payload.get("error"),
            "trace_id": response_payload.get("trace_id"),
            "blocked": blocked,
            "idempotent_replay": idempotent_replay,
        },
        user_info=user_info or {},
    )


def execute_instruction_contract(
    *,
    action: str,
    params_payload: dict[str, Any],
    trace_id: str,
    user_info: dict[str, Any] | None = None,
    idempotency_key: str | None = None,
    require_user_context: bool = False,
) -> dict[str, Any]:
    """Execute an M365 instruction with the canonical action/params contract."""
    normalized_action = action.strip().lower()
    raw_params = params_payload if isinstance(params_payload, dict) else {}

    if require_user_context and not user_info:
        payload = M365InstructionResponse(
            ok=False,
            error="auth_required",
            trace_id=trace_id,
        ).model_dump()
        _audit_instruction(
            normalized_action or "unknown", raw_params, payload, user_info, blocked=True
        )
        return payload

    if normalized_action not in _SUPPORTED_ACTIONS:
        payload = M365InstructionResponse(
            ok=False,
            error=f"Unknown action: {normalized_action}",
            trace_id=trace_id,
        ).model_dump()
        _audit_instruction(normalized_action or "unknown", raw_params, payload, user_info)
        return payload

    try:
        params = _normalize_params(normalized_action, raw_params)
    except HTTPException as exc:
        payload = M365InstructionResponse(
            ok=False,
            error=str(exc.detail),
            trace_id=trace_id,
        ).model_dump()
        _audit_instruction(normalized_action, raw_params, payload, user_info)
        return payload

    idem_key = (idempotency_key or "").strip() or None
    request_hash = _request_hash(normalized_action, params)
    if idem_key:
        record = _get_idempotency_record(idem_key)
        if record:
            if record.get("request_hash") != request_hash:
                payload = M365InstructionResponse(
                    ok=False,
                    error="idempotency_key_conflict",
                    trace_id=trace_id,
                ).model_dump()
                _audit_instruction(normalized_action, params, payload, user_info)
                return payload
            stored = record.get("response") or {}
            _audit_instruction(normalized_action, params, stored, user_info, idempotent_replay=True)
            return stored

    if normalized_action in _MUTATING_ACTIONS and not _allow_mutations():
        blocked = M365InstructionResponse(
            ok=False,
            error="m365_mutations_disabled",
            trace_id=trace_id,
        ).model_dump()
        _audit_instruction(normalized_action, params, blocked, user_info, blocked=True)
        if idem_key:
            _store_idempotency_record(idem_key, request_hash, blocked)
        return blocked

    try:
        result = _execute_action(normalized_action, params)
        payload = M365InstructionResponse(ok=True, result=result, trace_id=trace_id).model_dump()
    except HTTPException as exc:
        payload = M365InstructionResponse(
            ok=False, error=str(exc.detail), trace_id=trace_id
        ).model_dump()
    except SmarthausError as exc:
        payload = M365InstructionResponse(ok=False, error=str(exc), trace_id=trace_id).model_dump()
    except Exception as exc:  # noqa: BLE001
        payload = M365InstructionResponse(ok=False, error=str(exc), trace_id=trace_id).model_dump()

    _audit_instruction(normalized_action, params, payload, user_info)
    if idem_key:
        _store_idempotency_record(idem_key, request_hash, payload)
    return payload


@router.post("/instruction", response_model=M365InstructionResponse)
async def handle_instruction(
    body: M365InstructionRequest,
    request: Request,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    session: dict[str, Any] = _SESSION_DEPENDENCY,
) -> M365InstructionResponse:
    trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response.headers["X-Request-ID"] = trace_id

    action = body.action.strip().lower()
    user_info = session.get("user_info") if isinstance(session, dict) else None
    if not _validate_caio_api_key(request):
        payload = M365InstructionResponse(
            ok=False,
            error="invalid_caio_api_key",
            trace_id=trace_id,
        ).model_dump()
        response.status_code = 401
        _audit_instruction(action or "unknown", body.params or {}, payload, user_info, blocked=True)
        return payload

    payload = execute_instruction_contract(
        action=action,
        params_payload=body.params or {},
        trace_id=trace_id,
        user_info=user_info,
        idempotency_key=idempotency_key or body.idempotency_key,
    )
    trace = payload.get("trace_id")
    if isinstance(trace, str) and trace:
        response.headers["X-Request-ID"] = trace
    return payload


# ---------- Instruction schema and agents (for dashboard and CAIO) ----------

INSTRUCTION_ACTIONS_SCHEMA = [
    {
        "action": "create_site",
        "description": "Create a SharePoint site with group",
        "params": ["display_name", "mail_nickname?", "libraries?", "description?"],
        "mutating": True,
    },
    {
        "action": "create_team",
        "description": "Create a Teams workspace",
        "params": ["mail_nickname", "channels?"],
        "mutating": True,
    },
    {
        "action": "add_channel",
        "description": "Add a channel to a team",
        "params": ["mail_nickname", "channel_name", "description?"],
        "mutating": True,
    },
    {
        "action": "get_team",
        "description": "Get a Teams workspace by team id, backing group id, or mail nickname",
        "params": ["teamId|team_id|id|groupId|group_id|mail_nickname|mailNickname"],
        "mutating": False,
    },
    {
        "action": "list_channels",
        "description": "List channels for a Teams workspace",
        "params": ["teamId|team_id|id|groupId|group_id|mail_nickname|mailNickname", "top?"],
        "mutating": False,
    },
    {
        "action": "create_channel",
        "description": "Create a channel in a Teams workspace",
        "params": [
            "teamId|team_id|id|groupId|group_id|mail_nickname|mailNickname",
            "channel_name|displayName|name",
            "description?",
        ],
        "mutating": True,
    },
    {
        "action": "list_plans",
        "description": "List Planner plans owned by a group",
        "params": ["groupId|group_id|id|mail_nickname|mailNickname"],
        "mutating": False,
    },
    {
        "action": "create_plan",
        "description": "Create a Planner plan for a group",
        "params": ["groupId|group_id|id|mail_nickname|mailNickname", "title|name"],
        "mutating": True,
    },
    {
        "action": "list_plan_buckets",
        "description": "List buckets for a Planner plan",
        "params": ["planId|plan_id|id"],
        "mutating": False,
    },
    {
        "action": "create_plan_bucket",
        "description": "Create a bucket in a Planner plan",
        "params": ["planId|plan_id|id", "name|bucketName", "orderHint?"],
        "mutating": True,
    },
    {
        "action": "create_plan_task",
        "description": "Create a task in a Planner plan bucket",
        "params": [
            "planId|plan_id",
            "bucketId|bucket_id",
            "title|name",
            "description?",
            "referenceUrl?",
            "percentComplete?",
        ],
        "mutating": True,
    },
    {
        "action": "provision_service",
        "description": "Provision a service from config",
        "params": ["key"],
        "mutating": True,
    },
    {
        "action": "list_users",
        "description": "List M365 users",
        "params": ["top?", "select?"],
        "mutating": False,
    },
    {
        "action": "list_teams",
        "description": "List Teams workspaces",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "list_sites",
        "description": "List SharePoint site collections",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "get_site",
        "description": "Get a SharePoint site by id",
        "params": ["siteId|site_id|id"],
        "mutating": False,
    },
    {
        "action": "list_site_lists",
        "description": "List SharePoint lists for a site",
        "params": ["siteId|site_id|id", "top?"],
        "mutating": False,
    },
    {
        "action": "get_list",
        "description": "Get a SharePoint list by site and list id",
        "params": ["siteId|site_id", "listId|list_id|id"],
        "mutating": False,
    },
    {
        "action": "list_list_items",
        "description": "List SharePoint list items",
        "params": ["siteId|site_id", "listId|list_id|id", "top?"],
        "mutating": False,
    },
    {
        "action": "create_list_item",
        "description": "Create a SharePoint list item",
        "params": ["siteId|site_id", "listId|list_id|id", "fields"],
        "mutating": True,
    },
    {
        "action": "list_drives",
        "description": "List drives for a site, group, user, or delegated self context",
        "params": ["groupId?|siteId?|userId?|userPrincipalName?", "top?"],
        "mutating": False,
    },
    {
        "action": "get_drive",
        "description": "Get a drive by id",
        "params": ["driveId|drive_id|id"],
        "mutating": False,
    },
    {
        "action": "list_drive_items",
        "description": "List items in a drive, site drive, group drive, or delegated self drive",
        "params": [
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "folderId?|folderPath?|path?",
            "top?",
        ],
        "mutating": False,
    },
    {
        "action": "get_drive_item",
        "description": "Get a drive item by drive and item id",
        "params": ["driveId|drive_id", "itemId|item_id|id"],
        "mutating": False,
    },
    {
        "action": "create_folder",
        "description": "Create a folder in a drive, site drive, group drive, or delegated self drive",
        "params": [
            "name|folderName",
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "parentId?",
            "conflictBehavior?",
        ],
        "mutating": True,
    },
    {
        "action": "upload_file",
        "description": "Upload a local file into a drive, site drive, group drive, or delegated self drive",
        "params": [
            "filePath|localPath",
            "remotePath|path|fileName",
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "conflictBehavior?",
            "contentType?",
        ],
        "mutating": True,
    },
    {
        "action": "create_document",
        "description": "Generate and upload a DOCX document into a drive, site drive, group drive, or delegated self drive",
        "params": [
            "remotePath|path|fileName",
            "title?",
            "paragraphs?|content?",
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "conflictBehavior?",
        ],
        "mutating": True,
    },
    {
        "action": "update_document",
        "description": "Update a DOCX document by regenerating and uploading it into a drive, site drive, group drive, or delegated self drive",
        "params": [
            "remotePath|path|fileName",
            "title?",
            "paragraphs?|content?",
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "conflictBehavior?",
        ],
        "mutating": True,
    },
    {
        "action": "create_workbook",
        "description": "Generate and upload an XLSX workbook into a drive, site drive, group drive, or delegated self drive",
        "params": [
            "remotePath|path|fileName",
            "worksheets?|rows?",
            "sheetName?",
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "conflictBehavior?",
        ],
        "mutating": True,
    },
    {
        "action": "update_workbook",
        "description": "Update an XLSX workbook by regenerating and uploading it into a drive, site drive, group drive, or delegated self drive",
        "params": [
            "remotePath|path|fileName",
            "worksheets?|rows?",
            "sheetName?",
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "conflictBehavior?",
        ],
        "mutating": True,
    },
    {
        "action": "create_presentation",
        "description": "Generate and upload a PPTX presentation into a drive, site drive, group drive, or delegated self drive",
        "params": [
            "remotePath|path|fileName",
            "title?",
            "slides?|bullets?|items?",
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "conflictBehavior?",
        ],
        "mutating": True,
    },
    {
        "action": "update_presentation",
        "description": "Update a PPTX presentation by regenerating and uploading it into a drive, site drive, group drive, or delegated self drive",
        "params": [
            "remotePath|path|fileName",
            "title?",
            "slides?|bullets?|items?",
            "driveId?|groupId?|siteId?|userId?|userPrincipalName?",
            "conflictBehavior?",
        ],
        "mutating": True,
    },
    {
        "action": "list_flows_admin",
        "description": "List Power Automate flows as admin for an environment",
        "params": ["environmentName|environment_name|environment", "top?"],
        "mutating": False,
    },
    {
        "action": "get_flow_admin",
        "description": "Get a Power Automate flow as admin by environment and flow name",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
        ],
        "mutating": False,
    },
    {
        "action": "list_http_flows",
        "description": "List Power Automate HTTP-triggered flows for an environment",
        "params": ["environmentName|environment_name|environment", "top?"],
        "mutating": False,
    },
    {
        "action": "list_flow_owners",
        "description": "List Power Automate flow owner roles for a flow",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
        ],
        "mutating": False,
    },
    {
        "action": "list_flow_runs",
        "description": "List Power Automate runs for a flow",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
            "top?",
        ],
        "mutating": False,
    },
    {
        "action": "set_flow_owner_role",
        "description": "Grant or update a Power Automate flow owner role",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
            "principalObjectId|principal_object_id|userId|user_id",
            "roleName?",
            "principalType?",
        ],
        "mutating": True,
    },
    {
        "action": "remove_flow_owner_role",
        "description": "Remove a Power Automate flow owner role",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
            "roleId|role_id",
        ],
        "mutating": True,
    },
    {
        "action": "enable_flow",
        "description": "Enable a Power Automate flow",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
        ],
        "mutating": True,
    },
    {
        "action": "disable_flow",
        "description": "Disable a Power Automate flow",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
        ],
        "mutating": True,
    },
    {
        "action": "delete_flow",
        "description": "Soft-delete a Power Automate flow",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
        ],
        "mutating": True,
    },
    {
        "action": "restore_flow",
        "description": "Restore a soft-deleted Power Automate flow",
        "params": [
            "environmentName|environment_name|environment",
            "flowName|flow_name|flowId|flow_id|id",
        ],
        "mutating": True,
    },
    {
        "action": "invoke_flow_callback",
        "description": "Invoke a Power Automate HTTP callback URL with a bounded payload",
        "params": ["callbackUrl|callback_url|url", "body|payload?", "headers?", "timeoutSeconds?"],
        "mutating": True,
    },
    {
        "action": "list_powerapps_admin",
        "description": "List Power Apps as admin across environments or within a specific environment",
        "params": ["environmentName?|environment_name?|environment?|id?", "owner?|filter?|top?"],
        "mutating": False,
    },
    {
        "action": "get_powerapp_admin",
        "description": "Get a Power App as admin by environment and app name",
        "params": [
            "environmentName|environment_name|environment|environmentId|environment_id",
            "appName|app_name|appId|app_id|id",
        ],
        "mutating": False,
    },
    {
        "action": "list_powerapp_role_assignments",
        "description": "List Power App role assignments for an app",
        "params": [
            "environmentName|environment_name|environment|environmentId|environment_id",
            "appName|app_name|appId|app_id|id",
            "userId?|user_id?",
        ],
        "mutating": False,
    },
    {
        "action": "set_powerapp_owner",
        "description": "Transfer or set Power App ownership",
        "params": [
            "environmentName|environment_name|environment|environmentId|environment_id",
            "appName|app_name|appId|app_id|id",
            "ownerObjectId|owner_object_id|principalObjectId|principal_object_id|userId|user_id",
        ],
        "mutating": True,
    },
    {
        "action": "remove_powerapp_role_assignment",
        "description": "Remove a Power App role assignment",
        "params": [
            "environmentName|environment_name|environment|environmentId|environment_id",
            "appName|app_name|appId|app_id|id",
            "roleId|role_id",
        ],
        "mutating": True,
    },
    {
        "action": "delete_powerapp",
        "description": "Delete a Power App by environment and app name",
        "params": [
            "environmentName|environment_name|environment|environmentId|environment_id",
            "appName|app_name|appId|app_id|id",
        ],
        "mutating": True,
    },
    {
        "action": "list_powerapp_environments",
        "description": "List Power Apps environments",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "get_powerapp_environment",
        "description": "Get a Power Apps environment",
        "params": ["environmentName|environment_name|environment|environmentId|environment_id|id"],
        "mutating": False,
    },
    {
        "action": "list_powerapp_environment_role_assignments",
        "description": "List Power Apps environment role assignments",
        "params": [
            "environmentName|environment_name|environment|environmentId|environment_id|id",
            "userId?|user_id?",
        ],
        "mutating": False,
    },
    {
        "action": "set_powerapp_environment_role_assignment",
        "description": "Grant or update a Power Apps environment role assignment",
        "params": [
            "environmentName|environment_name|environment|environmentId|environment_id|id",
            "principalObjectId|principal_object_id|userId|user_id",
            "roleName|role_name",
            "principalType?",
        ],
        "mutating": True,
    },
    {
        "action": "remove_powerapp_environment_role_assignment",
        "description": "Remove a Power Apps environment role assignment",
        "params": [
            "environmentName|environment_name|environment|environmentId|environment_id|id",
            "roleId|role_id",
        ],
        "mutating": True,
    },
    {
        "action": "list_powerbi_workspaces",
        "description": "List Power BI workspaces",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "get_powerbi_workspace",
        "description": "Get a Power BI workspace",
        "params": ["workspaceId|workspace_id|groupId|group_id|id"],
        "mutating": False,
    },
    {
        "action": "list_powerbi_reports",
        "description": "List Power BI reports for a workspace",
        "params": ["workspaceId|workspace_id|groupId|group_id|id", "top?"],
        "mutating": False,
    },
    {
        "action": "get_powerbi_report",
        "description": "Get a Power BI report for a workspace",
        "params": ["workspaceId|workspace_id|groupId|group_id", "reportId|report_id|id"],
        "mutating": False,
    },
    {
        "action": "list_powerbi_datasets",
        "description": "List Power BI datasets for a workspace",
        "params": ["workspaceId|workspace_id|groupId|group_id|id", "top?"],
        "mutating": False,
    },
    {
        "action": "get_powerbi_dataset",
        "description": "Get a Power BI dataset for a workspace",
        "params": ["workspaceId|workspace_id|groupId|group_id", "datasetId|dataset_id|id"],
        "mutating": False,
    },
    {
        "action": "refresh_powerbi_dataset",
        "description": "Trigger a bounded Power BI dataset refresh",
        "params": [
            "workspaceId|workspace_id|groupId|group_id",
            "datasetId|dataset_id|id",
            "notifyOption?",
        ],
        "mutating": True,
    },
    {
        "action": "list_powerbi_dataset_refreshes",
        "description": "List Power BI dataset refresh history",
        "params": ["workspaceId|workspace_id|groupId|group_id", "datasetId|dataset_id", "top?"],
        "mutating": False,
    },
    {
        "action": "list_powerbi_dashboards",
        "description": "List Power BI dashboards for a workspace",
        "params": ["workspaceId|workspace_id|groupId|group_id|id", "top?"],
        "mutating": False,
    },
    {
        "action": "get_powerbi_dashboard",
        "description": "Get a Power BI dashboard for a workspace",
        "params": ["workspaceId|workspace_id|groupId|group_id", "dashboardId|dashboard_id|id"],
        "mutating": False,
    },
    {
        "action": "get_approval_solution",
        "description": "Get the tenant approval-solution provisioning state",
        "params": [],
        "mutating": False,
    },
    {
        "action": "list_approval_items",
        "description": "List approval items from the Teams Approvals app",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "get_approval_item",
        "description": "Get an approval item from the Teams Approvals app",
        "params": ["approvalId|approval_id|id"],
        "mutating": False,
    },
    {
        "action": "create_approval_item",
        "description": "Create an approval item in the Teams Approvals app",
        "params": [
            "displayName|display_name|title",
            "description|details|body",
            "approverUserIds|approver_user_ids",
            "approverGroupIds?|approver_group_ids?",
            "approvalType?",
            "allowEmailNotification?",
        ],
        "mutating": True,
    },
    {
        "action": "list_approval_item_requests",
        "description": "List request records associated with an approval item",
        "params": ["approvalId|approval_id|id", "top?"],
        "mutating": False,
    },
    {
        "action": "respond_to_approval_item",
        "description": "Submit an approval response for an approval item",
        "params": ["approvalId|approval_id|id", "response|decision", "comments?"],
        "mutating": True,
    },
    {
        "action": "list_external_connections",
        "description": "List Microsoft 365 Copilot connector connections",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "get_external_connection",
        "description": "Get a Microsoft 365 Copilot connector connection",
        "params": ["connectionId|connection_id|id"],
        "mutating": False,
    },
    {
        "action": "create_external_connection",
        "description": "Create a Microsoft 365 Copilot connector connection",
        "params": [
            "connectionId|connection_id|id",
            "name|displayName|display_name|title",
            "description?",
        ],
        "mutating": True,
    },
    {
        "action": "register_external_connection_schema",
        "description": "Register or update the schema for a connector connection",
        "params": ["connectionId|connection_id|id", "schema?|properties", "baseType?"],
        "mutating": True,
    },
    {
        "action": "get_external_item",
        "description": "Get an indexed external item from a connector connection",
        "params": ["connectionId|connection_id", "itemId|item_id|id"],
        "mutating": False,
    },
    {
        "action": "upsert_external_item",
        "description": "Create or update an indexed external item for a connector connection",
        "params": [
            "connectionId|connection_id",
            "itemId|item_id|id",
            "acl",
            "properties",
            "content?",
        ],
        "mutating": True,
    },
    {
        "action": "create_external_group",
        "description": "Create an external group for connector ACL management",
        "params": [
            "connectionId|connection_id",
            "groupId|group_id|id",
            "displayName?|display_name?|name?",
            "description?",
        ],
        "mutating": True,
    },
    {
        "action": "add_external_group_member",
        "description": "Add a member to an external group for connector ACL management",
        "params": [
            "connectionId|connection_id",
            "groupId|group_id",
            "memberId|member_id|id",
            "memberType?",
            "identitySource?",
        ],
        "mutating": True,
    },
    {
        "action": "list_automation_recipes",
        "description": "List the bounded cross-workload automation recipes available in the catalog",
        "params": ["department?", "persona?", "workload?", "top?"],
        "mutating": False,
    },
    {
        "action": "get_automation_recipe",
        "description": "Get one bounded cross-workload automation recipe by id",
        "params": ["recipeId|recipe_id|id"],
        "mutating": False,
    },
    {
        "action": "get_user",
        "description": "Get a single user by id or UPN",
        "params": ["userPrincipalName|user_id|id"],
        "mutating": False,
    },
    {
        "action": "reset_user_password",
        "description": "Reset user password (temporary); force change at next sign-in",
        "params": [
            "userPrincipalName|user_id",
            "temporary_password|password",
            "force_change_next_sign_in?",
        ],
        "mutating": True,
    },
    {
        "action": "create_user",
        "description": "Create an Entra user",
        "params": [
            "userPrincipalName",
            "displayName?",
            "mailNickname?",
            "password",
            "accountEnabled?",
            "jobTitle?",
            "department?",
        ],
        "mutating": True,
    },
    {
        "action": "update_user",
        "description": "Update Entra user profile fields",
        "params": [
            "userPrincipalName|user_id|id",
            "displayName?",
            "jobTitle?",
            "department?",
            "accountEnabled?",
        ],
        "mutating": True,
    },
    {
        "action": "disable_user",
        "description": "Disable an Entra user account",
        "params": ["userPrincipalName|user_id|id"],
        "mutating": True,
    },
    {
        "action": "list_groups",
        "description": "List Entra groups",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "get_group",
        "description": "Get a single group by id or mail nickname",
        "params": ["group_id|id|mail_nickname"],
        "mutating": False,
    },
    {
        "action": "create_group",
        "description": "Create an Entra group",
        "params": [
            "display_name",
            "mail_nickname",
            "description?",
            "mail_enabled?",
            "security_enabled?",
        ],
        "mutating": True,
    },
    {
        "action": "list_group_members",
        "description": "List Entra group members",
        "params": ["group_id|id"],
        "mutating": False,
    },
    {
        "action": "add_group_member",
        "description": "Add a member to an Entra group",
        "params": ["group_id|id", "member_id|memberId|user_id|userId"],
        "mutating": True,
    },
    {
        "action": "remove_group_member",
        "description": "Remove a member from an Entra group",
        "params": ["group_id|id", "member_id|memberId|user_id|userId"],
        "mutating": True,
    },
    {
        "action": "assign_user_license",
        "description": "Assign licenses to an Entra user",
        "params": ["userPrincipalName|user_id|id", "licenses", "disabled_plans?"],
        "mutating": True,
    },
    {
        "action": "list_directory_roles",
        "description": "List Entra directory roles",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "list_directory_role_members",
        "description": "List members of an Entra directory role",
        "params": ["role_id|roleId|id"],
        "mutating": False,
    },
    {
        "action": "list_domains",
        "description": "List Entra verified domains",
        "params": [],
        "mutating": False,
    },
    {
        "action": "get_organization",
        "description": "Get Entra organization metadata",
        "params": [],
        "mutating": False,
    },
    {
        "action": "list_applications",
        "description": "List Entra application registrations",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "get_application",
        "description": "Get an Entra application registration",
        "params": ["app_id|appId|id"],
        "mutating": False,
    },
    {
        "action": "update_application",
        "description": "Update an Entra application registration",
        "params": ["app_id|appId|id", "body"],
        "mutating": True,
    },
    {
        "action": "list_service_principals",
        "description": "List Entra service principals",
        "params": ["top?"],
        "mutating": False,
    },
    {
        "action": "list_messages",
        "description": "List mailbox messages for a user or shared mailbox",
        "params": ["userId|userPrincipalName|mailbox?", "top?", "select?"],
        "mutating": False,
    },
    {
        "action": "get_message",
        "description": "Get a mailbox message by id",
        "params": ["messageId|message_id|id", "userId|userPrincipalName|mailbox?"],
        "mutating": False,
    },
    {
        "action": "send_mail",
        "description": "Send mail from the current user or an explicit mailbox context",
        "params": [
            "recipient_or_to|to|recipient",
            "subject",
            "body|content",
            "userId|userPrincipalName|mailbox|from?",
            "contentType?",
            "saveToSentItems?",
        ],
        "mutating": True,
    },
    {
        "action": "move_message",
        "description": "Move a mailbox message to another folder",
        "params": [
            "messageId|message_id|id",
            "destinationId|folderId",
            "userId|userPrincipalName|mailbox?",
        ],
        "mutating": True,
    },
    {
        "action": "delete_message",
        "description": "Delete a mailbox message",
        "params": ["messageId|message_id|id", "userId|userPrincipalName|mailbox?"],
        "mutating": True,
    },
    {
        "action": "list_mail_folders",
        "description": "List mail folders for a user or shared mailbox",
        "params": ["userId|userPrincipalName|mailbox?", "top?"],
        "mutating": False,
    },
    {
        "action": "get_mailbox_settings",
        "description": "Get mailbox settings",
        "params": ["userId|userPrincipalName|mailbox?"],
        "mutating": False,
    },
    {
        "action": "update_mailbox_settings",
        "description": "Update mailbox settings",
        "params": ["body", "userId|userPrincipalName|mailbox?"],
        "mutating": True,
    },
    {
        "action": "list_events",
        "description": "List calendar events for a user or shared mailbox",
        "params": ["userId|userPrincipalName|mailbox?", "top?"],
        "mutating": False,
    },
    {
        "action": "create_event",
        "description": "Create a calendar event",
        "params": [
            "subject",
            "start",
            "end",
            "bodyContent?",
            "location?",
            "attendees?",
            "userId|userPrincipalName|mailbox?",
        ],
        "mutating": True,
    },
    {
        "action": "get_event",
        "description": "Get a calendar event by id",
        "params": ["eventId|event_id|id", "userId|userPrincipalName|mailbox?"],
        "mutating": False,
    },
    {
        "action": "update_event",
        "description": "Update a calendar event",
        "params": [
            "eventId|event_id|id",
            "body? | subject? | start? | end? | location? | attendees?",
            "userId|userPrincipalName|mailbox?",
        ],
        "mutating": True,
    },
    {
        "action": "delete_event",
        "description": "Delete a calendar event",
        "params": ["eventId|event_id|id", "userId|userPrincipalName|mailbox?"],
        "mutating": True,
    },
    {
        "action": "get_schedule",
        "description": "Get free/busy schedule for one or more mailboxes",
        "params": [
            "schedules?",
            "startTime|start",
            "endTime|end",
            "availabilityViewInterval?",
            "userId|userPrincipalName|mailbox?",
        ],
        "mutating": False,
    },
    {
        "action": "list_contacts",
        "description": "List Outlook contacts for a user or shared mailbox",
        "params": ["userId|userPrincipalName|mailbox?", "top?"],
        "mutating": False,
    },
    {
        "action": "get_contact",
        "description": "Get an Outlook contact by id",
        "params": ["contactId|contact_id|id", "userId|userPrincipalName|mailbox?"],
        "mutating": False,
    },
    {
        "action": "create_contact",
        "description": "Create an Outlook contact",
        "params": [
            "body? | displayName? | givenName? | surname? | emailAddresses? | email?",
            "userId|userPrincipalName|mailbox?",
        ],
        "mutating": True,
    },
    {
        "action": "update_contact",
        "description": "Update an Outlook contact",
        "params": [
            "contactId|contact_id|id",
            "body? | displayName? | givenName? | surname? | emailAddresses? | email?",
            "userId|userPrincipalName|mailbox?",
        ],
        "mutating": True,
    },
    {
        "action": "delete_contact",
        "description": "Delete an Outlook contact",
        "params": ["contactId|contact_id|id", "userId|userPrincipalName|mailbox?"],
        "mutating": True,
    },
    {
        "action": "list_contact_folders",
        "description": "List Outlook contact folders",
        "params": ["userId|userPrincipalName|mailbox?", "top?"],
        "mutating": False,
    },
]


@router.get("/actions", response_model=list)
def list_instruction_actions() -> list[dict[str, Any]]:
    """Return supported instruction actions for dashboard and CAIO."""
    return INSTRUCTION_ACTIONS_SCHEMA


@router.get("/agents", response_model=dict)
def list_agents() -> dict[str, Any]:
    """Return agent registry (agents.yaml) for dashboard."""
    import yaml

    registry_path = Path(os.getenv("REGISTRY_FILE", "registry/agents.yaml"))
    if not registry_path.is_absolute():
        registry_path = Path.cwd() / registry_path
    if not registry_path.exists():
        return {"agents": {}, "error": "registry_not_found"}
    with open(registry_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {
        "agents": data.get("agents", {}),
        "version": data.get("version"),
        "metadata": data.get("metadata"),
    }


def _m365_graph_status() -> str:
    try:
        client = _graph_client()
        client.get_organization()
        return "ok"
    except (SmarthausError, HTTPException, Exception):
        return "not_configured_or_unreachable"


@router.get("/status", response_model=dict)
def m365_status() -> dict[str, Any]:
    """Status for dashboard: Graph connectivity and instruction capabilities."""
    return {
        "graph": _m365_graph_status(),
        "instruction_actions_count": len(_SUPPORTED_ACTIONS),
        "mutations_allowed": _allow_mutations(),
    }


@router.post("/provision/tai")
def provision_tai() -> dict:
    try:
        result = provision_group_site(
            display_name="TAI Research Hub",
            mail_nickname="tai-research",
            description="TAI research collaboration site",
            libraries=[
                "Research Papers",
                "Holographic Memory",
                "AI Orchestration",
                "Performance Metrics",
                "Project Management",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_tai", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/lattice")
def provision_lattice() -> dict:
    try:
        result = provision_group_site(
            display_name="LATTICE Research Hub",
            mail_nickname="lattice-research",
            description="LATTICE research collaboration site",
            libraries=[
                "Architecture Documentation",
                "AIOS Development",
                "LQL Language",
                "LEF Execution",
                "Mathematical Proofs",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_lattice", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/business")
def provision_business() -> dict:
    try:
        result = provision_group_site(
            display_name="SmartHaus Group Business Hub",
            mail_nickname="business-hub",
            description="Business operations hub",
            libraries=[
                "Website Updates",
                "Business Development",
                "Client Projects",
                "Strategic Planning",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_business", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/teams/tai")
def create_tai_team() -> dict:
    try:
        channels = [
            "General",
            "Holographic Memory",
            "AI Orchestration",
            "Performance Metrics",
            "Research Updates",
        ]
        result = provision_teams_workspace("tai-research", channels)
        inc_teams_created()
        log_event("provision_team_tai", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/teams/lattice")
def create_lattice_team() -> dict:
    try:
        channels = [
            "General",
            "AIOS Development",
            "LQL Language",
            "LEF Execution",
            "Architecture Updates",
        ]
        result = provision_teams_workspace("lattice-research", channels)
        inc_teams_created()
        log_event("provision_team_lattice", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/teams/business")
def create_business_team() -> dict:
    try:
        channels = [
            "General",
            "Website Development",
            "Business Development",
            "Client Projects",
            "Strategic Planning",
        ]
        result = provision_teams_workspace("business-hub", channels)
        inc_teams_created()
        log_event("provision_team_business", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/teams/advisory-services")
def create_advisory_services_team() -> dict:
    try:
        channels = [
            "General",
            "advisory-services",  # All advisory service notifications
            "risk-management",  # Risk assessment alerts
            "aidf-certification",  # Certification requests
            "project-management",  # Project status updates
            "client-intake",  # New client intake tracking
            "governance-updates",  # AIDF governance updates
        ]
        result = provision_teams_workspace("advisory-services", channels)
        inc_teams_created()
        log_event("provision_team_advisory_services", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/provision/service/{key}")
def provision_service(key: str) -> dict:
    cfg_path = Path("config/services.json")
    if not cfg_path.exists():
        raise HTTPException(status_code=500, detail="Missing config/services.json")
    try:
        cfg = json.loads(cfg_path.read_text())
        svc = next((s for s in cfg.get("services", []) if s.get("key") == key), None)
        if not svc:
            raise HTTPException(status_code=404, detail=f"Unknown service: {key}")
        site = provision_group_site(
            display_name=svc.get("display_name"),
            mail_nickname=svc.get("mail_nickname"),
            libraries=["Documents"],
            description=f"Service workspace for {svc.get('display_name')}",
        )
        inc_sites_created(1 if site.get("group_created") else 0)
        team = provision_teams_workspace(svc.get("mail_nickname"), svc.get("channels", []))
        inc_teams_created()
        res = {"status": "ok", "site": site, "team": team}
        log_event(f"provision_service_{key}", res)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
