from __future__ import annotations

from collections.abc import Generator
from typing import Any

import pytest
from provisioning_api.routers import m365 as m365_router
from smarthaus_common.approval_risk import reload_approval_risk_registry, resolve_action_approval_risk
from smarthaus_common.auth_model import reload_auth_model_registry, resolve_action_auth
from smarthaus_common.executor_routing import executor_route_for_action, reload_executor_routing_registry


@pytest.fixture(autouse=True)
def _reload_registries() -> Generator[None, None, None]:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()
    yield
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def test_e4a_instruction_schema_includes_device_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}
    assert {
        "list_devices",
        "get_device",
        "list_device_compliance_summaries",
        "execute_device_action",
    }.issubset(supported)


def test_e4a_actions_route_auth_and_risk_to_devices_domain() -> None:
    for action in {"list_devices", "get_device", "list_device_compliance_summaries"}:
        assert executor_route_for_action(None, action) == "devices"
        auth = resolve_action_auth("m365-administrator", action, {})
        assert auth.executor_domain == "devices"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("m365-administrator", action, {})
        assert approval.approval_profile == "low-observe-create"
        assert approval.approval_required is False

    mutation_auth = resolve_action_auth("m365-administrator", "execute_device_action", {})
    assert mutation_auth.executor_domain == "devices"
    assert mutation_auth.auth_class == "app_only"
    mutation_approval = resolve_action_approval_risk(
        "m365-administrator", "execute_device_action", {}
    )
    assert mutation_approval.approval_profile == "high-impact"
    assert mutation_approval.approval_required is True


def test_e4a_instruction_contract_executes_device_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def list_devices(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 25
            return [{"id": "device-1"}]

        def get_device(self, device_id: str) -> dict[str, Any]:
            assert device_id == "device-1"
            return {"id": device_id}

        def list_device_compliance_summaries(self) -> list[dict[str, Any]]:
            return [{"id": "summary-1"}]

        def execute_device_action(self, device_id: str, *, action: str) -> dict[str, Any]:
            assert device_id == "device-1"
            assert action == "syncDevice"
            return {"executed": True, "deviceId": device_id, "action": action}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_intune_devices_client", lambda action=None: _FakeClient())

    list_payload = m365_router.execute_instruction_contract(
        action="list_devices",
        params_payload={"top": 25},
        trace_id="trace-list-devices",
    )
    get_payload = m365_router.execute_instruction_contract(
        action="get_device",
        params_payload={"deviceId": "device-1"},
        trace_id="trace-get-device",
    )
    compliance_payload = m365_router.execute_instruction_contract(
        action="list_device_compliance_summaries",
        params_payload={},
        trace_id="trace-list-device-compliance",
    )
    action_payload = m365_router.execute_instruction_contract(
        action="execute_device_action",
        params_payload={"deviceId": "device-1", "action": "syncDevice"},
        trace_id="trace-execute-device-action",
    )

    assert list_payload["ok"] is True
    assert list_payload["result"] == {"devices": [{"id": "device-1"}], "count": 1}
    assert get_payload["ok"] is True
    assert get_payload["result"] == {"device": {"id": "device-1"}}
    assert compliance_payload["ok"] is True
    assert compliance_payload["result"] == {"summaries": [{"id": "summary-1"}], "count": 1}
    assert action_payload["ok"] is True
    assert action_payload["result"] == {
        "executed": True,
        "deviceId": "device-1",
        "action": "syncDevice",
    }
