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
from smarthaus_common.power_bi_client import PowerBIClient
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


def test_e3c_instruction_schema_includes_power_bi_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}

    assert {
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
    }.issubset(supported)


def test_e3c_actions_route_and_auth_to_powerplatform() -> None:
    for action in (
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
    ):
        assert executor_route_for_action(None, action) == "powerplatform"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "powerplatform"
        assert resolution.auth_class == "app_only"


def test_e3c_reads_and_refresh_resolve_expected_approval_profiles() -> None:
    read_resolution = resolve_action_approval_risk(
        "m365-administrator", "list_powerbi_workspaces", {}
    )
    refresh_resolution = resolve_action_approval_risk(
        "m365-administrator", "refresh_powerbi_dataset", {}
    )

    assert read_resolution.risk_class == "low"
    assert read_resolution.approval_profile == "low-observe-create"
    assert read_resolution.approval_required is False

    assert refresh_resolution.risk_class == "high"
    assert refresh_resolution.approval_profile == "high-impact"
    assert refresh_resolution.approval_required is True


def test_e3c_instruction_contract_executes_power_bi_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def list_workspaces(self) -> list[dict[str, Any]]:
            return [{"id": "w1"}]

        def get_report(self, workspace_id: str, report_id: str) -> dict[str, Any]:
            assert workspace_id == "w1"
            assert report_id == "r1"
            return {"id": report_id, "name": "Revenue"}

        def refresh_dataset(
            self,
            workspace_id: str,
            dataset_id: str,
            *,
            notify_option: str = "NoNotification",
        ) -> dict[str, Any]:
            assert workspace_id == "w1"
            assert dataset_id == "d1"
            assert notify_option == "NoNotification"
            return {
                "workspaceId": workspace_id,
                "datasetId": dataset_id,
                "status": "queued",
            }

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_power_bi_client", lambda action=None: _FakeClient())

    list_payload = m365_router.execute_instruction_contract(
        action="list_powerbi_workspaces",
        params_payload={"top": 25},
        trace_id="trace-list-workspaces",
    )
    get_payload = m365_router.execute_instruction_contract(
        action="get_powerbi_report",
        params_payload={"workspaceId": "w1", "reportId": "r1"},
        trace_id="trace-get-report",
    )
    refresh_payload = m365_router.execute_instruction_contract(
        action="refresh_powerbi_dataset",
        params_payload={"workspaceId": "w1", "datasetId": "d1"},
        trace_id="trace-refresh-dataset",
    )

    assert list_payload["ok"] is True
    assert list_payload["result"] == {"workspaces": [{"id": "w1"}], "count": 1}
    assert get_payload["ok"] is True
    assert get_payload["result"] == {"report": {"id": "r1", "name": "Revenue"}}
    assert refresh_payload["ok"] is True
    assert refresh_payload["result"] == {
        "workspaceId": "w1",
        "datasetId": "d1",
        "status": "queued",
    }


def test_e3c_power_bi_client_fails_closed_without_credential() -> None:
    client = PowerBIClient(
        tenant_config=TenantConfig(
            azure=AzureConfig(
                tenant_id="tenant-id",
                client_id="client-id",
            )
        )
    )

    with pytest.raises(Exception, match="client_secret or client_certificate_path"):
        client.list_workspaces()
