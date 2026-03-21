from __future__ import annotations

from collections.abc import Generator
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
from smarthaus_common.forms_approvals_connectors_client import FormsApprovalsConnectorsClient
from smarthaus_common.tenant_config import AuthConfig, AzureConfig, TenantConfig


@pytest.fixture(autouse=True)
def _reload_registries() -> Generator[None, None, None]:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()
    yield
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def test_e3d_instruction_schema_includes_forms_approvals_connectors_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}

    assert {
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
    }.issubset(supported)


def test_e3d_actions_route_and_auth_to_expected_domains() -> None:
    approval_actions = {
        "get_approval_solution",
        "list_approval_items",
        "get_approval_item",
        "create_approval_item",
        "list_approval_item_requests",
        "respond_to_approval_item",
    }
    connector_actions = {
        "list_external_connections",
        "get_external_connection",
        "create_external_connection",
        "register_external_connection_schema",
        "get_external_item",
        "upsert_external_item",
        "create_external_group",
        "add_external_group_member",
    }

    for action in approval_actions:
        assert executor_route_for_action(None, action) == "powerplatform"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "powerplatform"
        assert resolution.auth_class == "delegated"

    for action in connector_actions:
        assert executor_route_for_action(None, action) == "knowledge"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "knowledge"
        assert resolution.auth_class == "app_only"


def test_e3d_risk_profiles_match_expected_posture() -> None:
    create_approval = resolve_action_approval_risk(
        "m365-administrator", "create_approval_item", {}
    )
    respond_approval = resolve_action_approval_risk(
        "m365-administrator", "respond_to_approval_item", {}
    )
    create_connection = resolve_action_approval_risk(
        "m365-administrator", "create_external_connection", {}
    )

    assert create_approval.risk_class == "medium"
    assert create_approval.approval_profile == "medium-operational"
    assert create_approval.approval_required is False

    assert respond_approval.risk_class == "high"
    assert respond_approval.approval_profile == "high-impact"
    assert respond_approval.approval_required is False

    assert create_connection.risk_class == "high"
    assert create_connection.approval_profile == "high-impact"
    assert create_connection.approval_required is True


def test_e3d_instruction_contract_executes_approval_and_connector_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def get_approval_solution(self) -> dict[str, Any]:
            return {"state": "provisioned"}

        def create_approval_item(
            self,
            *,
            display_name: str,
            description: str,
            approver_user_ids: list[str],
            approver_group_ids: list[str] | None = None,
            approval_type: str = "basic",
            allow_email_notification: bool = True,
        ) -> dict[str, Any]:
            assert display_name == "Approve spend"
            assert description == "Need approval"
            assert approver_user_ids == ["user-1"]
            assert approver_group_ids == []
            assert approval_type == "basic"
            assert allow_email_notification is True
            return {"status": "accepted", "displayName": display_name}

        def list_external_connections(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 25
            return [{"id": "conn-1"}]

        def upsert_external_item(
            self,
            connection_id: str,
            item_id: str,
            *,
            acl: list[dict[str, Any]],
            properties: dict[str, Any],
            content: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            assert connection_id == "conn-1"
            assert item_id == "item-1"
            assert acl == [{"type": "everyone", "value": "everyone", "accessType": "grant"}]
            assert properties == {"title": "Ticket"}
            assert content == {"value": "Body", "type": "text"}
            return {"itemId": item_id, "status": "upserted"}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(
        m365_router,
        "_forms_approvals_connectors_client",
        lambda action=None: _FakeClient(),
    )

    solution_payload = m365_router.execute_instruction_contract(
        action="get_approval_solution",
        params_payload={},
        trace_id="trace-approval-solution",
    )
    create_payload = m365_router.execute_instruction_contract(
        action="create_approval_item",
        params_payload={
            "displayName": "Approve spend",
            "description": "Need approval",
            "approverUserIds": ["user-1"],
        },
        trace_id="trace-create-approval",
    )
    list_connections_payload = m365_router.execute_instruction_contract(
        action="list_external_connections",
        params_payload={"top": 25},
        trace_id="trace-list-connections",
    )
    upsert_item_payload = m365_router.execute_instruction_contract(
        action="upsert_external_item",
        params_payload={
            "connectionId": "conn-1",
            "itemId": "item-1",
            "acl": [{"type": "everyone", "value": "everyone", "accessType": "grant"}],
            "properties": {"title": "Ticket"},
            "content": {"value": "Body", "type": "text"},
        },
        trace_id="trace-upsert-item",
    )

    assert solution_payload["ok"] is True
    assert solution_payload["result"] == {"solution": {"state": "provisioned"}}
    assert create_payload["ok"] is True
    assert create_payload["result"] == {"status": "accepted", "displayName": "Approve spend"}
    assert list_connections_payload["ok"] is True
    assert list_connections_payload["result"] == {"connections": [{"id": "conn-1"}], "count": 1}
    assert upsert_item_payload["ok"] is True
    assert upsert_item_payload["result"] == {"itemId": "item-1", "status": "upserted"}


def test_e3d_approval_actions_fail_closed_without_delegated_mode() -> None:
    client = FormsApprovalsConnectorsClient(
        tenant_config=TenantConfig(
            azure=AzureConfig(tenant_id="tenant-id", client_id="client-id", client_secret="secret"),
            auth=AuthConfig(mode="app_only"),
        )
    )

    with pytest.raises(Exception, match="delegated or hybrid auth mode"):
        client.get_approval_solution()
