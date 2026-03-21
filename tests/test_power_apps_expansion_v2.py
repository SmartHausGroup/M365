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
from smarthaus_common.power_apps_client import PowerAppsClient
from smarthaus_common.tenant_config import AzureConfig, TenantConfig


@pytest.fixture(autouse=True)
def _reload_registries() -> Generator[None, None, None]:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()
    yield
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def test_e3b_instruction_schema_includes_power_apps_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}

    assert {
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
    }.issubset(supported)


def test_e3b_actions_route_and_auth_to_powerplatform() -> None:
    for action in (
        "list_powerapps_admin",
        "get_powerapp_admin",
        "list_powerapp_role_assignments",
        "set_powerapp_owner",
        "list_powerapp_environments",
        "set_powerapp_environment_role_assignment",
    ):
        assert executor_route_for_action(None, action) == "powerplatform"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "powerplatform"
        assert resolution.auth_class == "app_only"


def test_e3b_reads_and_mutations_resolve_expected_approval_profiles() -> None:
    read_resolution = resolve_action_approval_risk("m365-administrator", "list_powerapps_admin", {})
    mutation_resolution = resolve_action_approval_risk(
        "m365-administrator", "set_powerapp_owner", {}
    )

    assert read_resolution.risk_class == "low"
    assert read_resolution.approval_profile == "low-observe-create"
    assert read_resolution.approval_required is False

    assert mutation_resolution.risk_class == "high"
    assert mutation_resolution.approval_profile == "high-impact"
    assert mutation_resolution.approval_required is True


def test_e3b_instruction_contract_executes_power_apps_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def list_powerapps_admin(
            self,
            *,
            environment_name: str | None = None,
            owner: str | None = None,
            filter_text: str | None = None,
        ) -> list[dict[str, Any]]:
            assert environment_name == "Default-Env"
            assert owner == "owner-1"
            assert filter_text == "ticket"
            return [{"name": "app-1"}]

        def set_powerapp_owner(
            self,
            environment_name: str,
            app_name: str,
            owner_object_id: str,
        ) -> dict[str, Any]:
            assert environment_name == "Default-Env"
            assert app_name == "app-1"
            assert owner_object_id == "owner-1"
            return {
                "appName": app_name,
                "ownerObjectId": owner_object_id,
                "status": "updated",
            }

        def list_powerapp_environments(self) -> list[dict[str, Any]]:
            return [{"name": "Default-Env"}]

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_power_apps_client", lambda action=None: _FakeClient())

    list_payload = m365_router.execute_instruction_contract(
        action="list_powerapps_admin",
        params_payload={"environmentName": "Default-Env", "owner": "owner-1", "filter": "ticket"},
        trace_id="trace-list-apps",
    )
    owner_payload = m365_router.execute_instruction_contract(
        action="set_powerapp_owner",
        params_payload={
            "environmentName": "Default-Env",
            "appName": "app-1",
            "ownerObjectId": "owner-1",
        },
        trace_id="trace-set-owner",
    )
    env_payload = m365_router.execute_instruction_contract(
        action="list_powerapp_environments",
        params_payload={},
        trace_id="trace-list-envs",
    )

    assert list_payload["ok"] is True
    assert list_payload["result"] == {"apps": [{"name": "app-1"}], "count": 1}
    assert owner_payload["ok"] is True
    assert owner_payload["result"] == {
        "appName": "app-1",
        "ownerObjectId": "owner-1",
        "status": "updated",
    }
    assert env_payload["ok"] is True
    assert env_payload["result"] == {"environments": [{"name": "Default-Env"}], "count": 1}


def test_e3b_power_apps_client_fails_closed_without_client_secret() -> None:
    client = PowerAppsClient(
        tenant_config=TenantConfig(
            azure=AzureConfig(
                tenant_id="tenant-id",
                client_id="client-id",
            )
        )
    )

    with pytest.raises(Exception, match="client_secret is required"):
        client.list_powerapps_admin()
