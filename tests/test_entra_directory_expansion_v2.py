from __future__ import annotations

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
def _reload_registries() -> None:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()
    yield
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def test_e2a_directory_instruction_schema_includes_expanded_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}

    assert {
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
    }.issubset(supported)


def test_e2a_directory_legacy_aliases_route_and_auth_to_directory() -> None:
    for action in (
        "create_user",
        "list_groups",
        "assign_user_license",
        "list_applications",
        "list_service_principals",
    ):
        assert executor_route_for_action(None, action) == "directory"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "directory"
        assert resolution.auth_class == "app_only"


def test_e2a_directory_high_risk_mutations_require_approval() -> None:
    for action in (
        "create_user",
        "remove_group_member",
        "assign_user_license",
        "update_application",
    ):
        resolution = resolve_action_approval_risk("m365-administrator", action, {})
        assert resolution.risk_class == "high"
        assert resolution.approval_profile == "high-impact"
        assert resolution.approval_required is True


def test_e2a_directory_instruction_contract_executes_create_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def create_user(
            self,
            user_principal_name: str,
            *,
            display_name: str | None = None,
            mail_nickname: str | None = None,
            password: str,
            account_enabled: bool = True,
            job_title: str | None = None,
            department: str | None = None,
        ) -> dict[str, Any]:
            assert user_principal_name == "new.user@smarthausgroup.com"
            assert display_name == "New User"
            assert mail_nickname == "new.user"
            assert password == "Temp#123456"
            assert account_enabled is True
            assert job_title == "Operator"
            assert department == "Operations"
            return {"id": "user-123", "userPrincipalName": user_principal_name}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: _FakeClient())

    payload = m365_router.execute_instruction_contract(
        action="create_user",
        params_payload={
            "userPrincipalName": "new.user@smarthausgroup.com",
            "displayName": "New User",
            "mailNickname": "new.user",
            "password": "Temp#123456",
            "jobTitle": "Operator",
            "department": "Operations",
        },
        trace_id="trace-create-user",
    )

    assert payload["ok"] is True
    assert payload["result"] == {
        "user": {"id": "user-123", "userPrincipalName": "new.user@smarthausgroup.com"},
        "temporaryPassword": "Temp#123456",
    }


def test_e2a_directory_instruction_contract_executes_license_and_app_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def assign_user_license(
            self,
            user_id_or_upn: str,
            licenses: list[str],
            *,
            disabled_plans: dict[str, list[str]] | None = None,
        ) -> dict[str, Any]:
            assert user_id_or_upn == "new.user@smarthausgroup.com"
            assert licenses == ["E3"]
            assert disabled_plans == {"ENTERPRISEPACK": ["plan-a"]}
            return {"user": user_id_or_upn, "assigned": ["sku-1"], "skipped": []}

        def list_applications(self, top: int = 100) -> dict[str, Any]:
            assert top == 25
            return {"value": [{"id": "app-1", "displayName": "Executor"}]}

        def list_service_principals(self, top: int = 100) -> dict[str, Any]:
            assert top == 10
            return {"value": [{"id": "sp-1", "displayName": "Executor SP"}]}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: _FakeClient())

    license_payload = m365_router.execute_instruction_contract(
        action="assign_user_license",
        params_payload={
            "userPrincipalName": "new.user@smarthausgroup.com",
            "licenses": ["E3"],
            "disabled_plans": {"ENTERPRISEPACK": ["plan-a"]},
        },
        trace_id="trace-license",
    )
    applications_payload = m365_router.execute_instruction_contract(
        action="list_applications",
        params_payload={"top": 25},
        trace_id="trace-apps",
    )
    service_principals_payload = m365_router.execute_instruction_contract(
        action="list_service_principals",
        params_payload={"top": 10},
        trace_id="trace-sps",
    )

    assert license_payload["ok"] is True
    assert license_payload["result"] == {
        "user": "new.user@smarthausgroup.com",
        "assigned": ["sku-1"],
        "skipped": [],
    }
    assert applications_payload["ok"] is True
    assert applications_payload["result"] == {
        "applications": [{"id": "app-1", "displayName": "Executor"}],
        "count": 1,
    }
    assert service_principals_payload["ok"] is True
    assert service_principals_payload["result"] == {
        "service_principals": [{"id": "sp-1", "displayName": "Executor SP"}],
        "count": 1,
    }
