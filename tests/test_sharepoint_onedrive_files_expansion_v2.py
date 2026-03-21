from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from provisioning_api.routers import m365 as m365_router
from smarthaus_common.approval_risk import (
    reload_approval_risk_registry,
    resolve_action_approval_risk,
)
from smarthaus_common.auth_model import reload_auth_model_registry, resolve_action_auth
from smarthaus_common.executor_routing import (
    executor_route_for_action,
    reload_executor_routing_registry,
)


@pytest.fixture(autouse=True)
def _reload_registries() -> Generator[None, None, None]:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()
    yield
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def test_e2c_instruction_schema_includes_sharepoint_files_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}

    assert {
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
    }.issubset(supported)


def test_e2c_actions_route_to_sharepoint_and_use_expected_auth() -> None:
    for action, expected_auth in (
        ("get_site", "app_only"),
        ("create_list_item", "app_only"),
        ("list_drives", "hybrid"),
        ("list_drive_items", "hybrid"),
        ("upload_file", "hybrid"),
    ):
        assert executor_route_for_action(None, action) == "sharepoint"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "sharepoint"
        assert resolution.auth_class == expected_auth


def test_e2c_reads_and_mutations_resolve_expected_approval_profiles() -> None:
    read_resolution = resolve_action_approval_risk("m365-administrator", "get_site", {})
    mutation_resolution = resolve_action_approval_risk("m365-administrator", "upload_file", {})

    assert read_resolution.risk_class == "low"
    assert read_resolution.approval_profile == "low-observe-create"
    assert read_resolution.approval_required is False

    assert mutation_resolution.risk_class == "medium"
    assert mutation_resolution.approval_profile == "medium-operational"
    assert mutation_resolution.approval_required is False


def test_e2c_instruction_contract_executes_site_and_list_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def get_site(self, site_id: str) -> dict[str, Any]:
            assert site_id == "site-123"
            return {"id": site_id, "displayName": "Operations Site"}

        def list_site_lists(self, site_id: str, top: int = 100) -> list[dict[str, Any]]:
            assert site_id == "site-123"
            assert top == 25
            return [{"id": "list-1", "displayName": "Approvals"}]

        def create_list_item(
            self, site_id: str, list_id: str, fields: dict[str, Any]
        ) -> dict[str, Any]:
            assert site_id == "site-123"
            assert list_id == "list-1"
            assert fields == {"Title": "Approval 1", "Status": "pending"}
            return {"id": "item-1", "fields": fields}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: _FakeClient())

    site_payload = m365_router.execute_instruction_contract(
        action="get_site",
        params_payload={"siteId": "site-123"},
        trace_id="trace-site",
    )
    lists_payload = m365_router.execute_instruction_contract(
        action="list_site_lists",
        params_payload={"siteId": "site-123", "top": 25},
        trace_id="trace-lists",
    )
    create_item_payload = m365_router.execute_instruction_contract(
        action="create_list_item",
        params_payload={
            "siteId": "site-123",
            "listId": "list-1",
            "fields": {"Title": "Approval 1", "Status": "pending"},
        },
        trace_id="trace-list-item",
    )

    assert site_payload["ok"] is True
    assert site_payload["result"] == {"site": {"id": "site-123", "displayName": "Operations Site"}}
    assert lists_payload["ok"] is True
    assert lists_payload["result"] == {
        "lists": [{"id": "list-1", "displayName": "Approvals"}],
        "count": 1,
    }
    assert create_item_payload["ok"] is True
    assert create_item_payload["result"] == {
        "item": {
            "id": "item-1",
            "fields": {"Title": "Approval 1", "Status": "pending"},
        },
        "status": "created",
    }


def test_e2c_instruction_contract_executes_drive_actions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    upload_path = tmp_path / "brief.txt"
    upload_path.write_text("hello", encoding="utf-8")

    class _FakeClient:
        def list_drives(
            self,
            *,
            group_id: str | None = None,
            site_id: str | None = None,
            user_id_or_upn: str | None = None,
            top: int = 100,
        ) -> dict[str, Any]:
            assert site_id == "site-123"
            assert top == 10
            assert group_id is None
            assert user_id_or_upn is None
            return {"value": [{"id": "drive-1", "name": "Documents"}]}

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
        ) -> dict[str, Any]:
            assert drive_id == "drive-1"
            assert folder_path == "General"
            assert top == 50
            assert group_id is None and site_id is None and user_id_or_upn is None
            return {"value": [{"id": "item-1", "name": "brief.txt"}]}

        def create_folder(
            self,
            name: str,
            *,
            drive_id: str | None = None,
            group_id: str | None = None,
            site_id: str | None = None,
            user_id_or_upn: str | None = None,
            parent_id: str = "root",
            conflict_behavior: str = "rename",
        ) -> dict[str, Any]:
            assert name == "Contracts"
            assert drive_id == "drive-1"
            assert parent_id == "root"
            assert conflict_behavior == "rename"
            assert group_id is None and site_id is None and user_id_or_upn is None
            return {"id": "folder-1", "name": "Contracts"}

        def upload_file(
            self,
            local_path: str,
            remote_path: str,
            *,
            drive_id: str | None = None,
            group_id: str | None = None,
            site_id: str | None = None,
            user_id_or_upn: str | None = None,
            conflict_behavior: str = "replace",
            content_type: str | None = None,
        ) -> dict[str, Any]:
            assert local_path.endswith("brief.txt")
            assert remote_path == "General/brief.txt"
            assert drive_id == "drive-1"
            assert conflict_behavior == "replace"
            assert content_type == "text/plain"
            assert group_id is None and site_id is None and user_id_or_upn is None
            return {"id": "file-1", "name": "brief.txt"}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: _FakeClient())

    drives_payload = m365_router.execute_instruction_contract(
        action="list_drives",
        params_payload={"siteId": "site-123", "top": 10},
        trace_id="trace-drives",
    )
    items_payload = m365_router.execute_instruction_contract(
        action="list_drive_items",
        params_payload={"driveId": "drive-1", "folderPath": "General", "top": 50},
        trace_id="trace-drive-items",
    )
    folder_payload = m365_router.execute_instruction_contract(
        action="create_folder",
        params_payload={"driveId": "drive-1", "name": "Contracts"},
        trace_id="trace-folder",
    )
    upload_payload = m365_router.execute_instruction_contract(
        action="upload_file",
        params_payload={
            "driveId": "drive-1",
            "filePath": str(upload_path),
            "remotePath": "General/brief.txt",
            "contentType": "text/plain",
        },
        trace_id="trace-upload",
    )

    assert drives_payload["ok"] is True
    assert drives_payload["result"] == {
        "drives": [{"id": "drive-1", "name": "Documents"}],
        "count": 1,
    }
    assert items_payload["ok"] is True
    assert items_payload["result"] == {
        "items": [{"id": "item-1", "name": "brief.txt"}],
        "count": 1,
    }
    assert folder_payload["ok"] is True
    assert folder_payload["result"] == {
        "folder": {"id": "folder-1", "name": "Contracts"},
        "status": "created",
    }
    assert upload_payload["ok"] is True
    assert upload_payload["result"] == {
        "file": {"id": "file-1", "name": "brief.txt"},
        "status": "uploaded",
    }
