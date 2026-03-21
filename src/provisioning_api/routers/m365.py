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
from smarthaus_common.config import AppConfig, has_selected_tenant
from smarthaus_common.errors import SmarthausError
from smarthaus_common.executor_routing import executor_route_for_action
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


def _normalize_user_context(params: dict[str, Any]) -> str | None:
    return _first_str(params, "userId", "user_id", "userPrincipalName", "mailbox")


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
