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


@pytest.fixture(autouse=True)
def _reload_registries() -> Generator[None, None, None]:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()
    yield
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def test_e4d_instruction_schema_includes_identity_security_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}
    assert {
        "list_conditional_access_policies",
        "get_conditional_access_policy",
        "create_conditional_access_policy",
        "update_conditional_access_policy",
        "delete_conditional_access_policy",
        "list_named_locations",
        "list_risk_detections",
    }.issubset(supported)


def test_e4d_actions_route_auth_and_risk_to_identity_security_domain() -> None:
    for action in {
        "list_conditional_access_policies",
        "get_conditional_access_policy",
        "list_named_locations",
        "list_risk_detections",
    }:
        assert executor_route_for_action(None, action) == "identity_security"
        auth = resolve_action_auth("identity-security", action, {})
        assert auth.executor_domain == "identity_security"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("identity-security", action, {})
        assert approval.approval_profile == "low-observe-create"
        assert approval.approval_required is False

    for action in {
        "create_conditional_access_policy",
        "update_conditional_access_policy",
        "delete_conditional_access_policy",
    }:
        auth = resolve_action_auth("identity-security", action, {})
        assert auth.executor_domain == "identity_security"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("identity-security", action, {})
        assert approval.approval_profile == "high-impact"
        assert approval.approval_required is True


def test_e4d_instruction_contract_executes_identity_security_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def list_conditional_access_policies(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 15
            return [{"id": "policy-1"}]

        def get_conditional_access_policy(self, policy_id: str) -> dict[str, Any]:
            assert policy_id == "policy-1"
            return {"id": policy_id}

        def create_conditional_access_policy(self, *, body: dict[str, Any]) -> dict[str, Any]:
            assert body == {"displayName": "Policy One"}
            return {"id": "policy-1", **body}

        def update_conditional_access_policy(
            self, policy_id: str, *, body: dict[str, Any]
        ) -> dict[str, Any]:
            assert policy_id == "policy-1"
            assert body == {"state": "enabled"}
            return {"updated": True, "policyId": policy_id}

        def delete_conditional_access_policy(self, policy_id: str) -> dict[str, Any]:
            assert policy_id == "policy-1"
            return {"deleted": True, "policyId": policy_id}

        def list_named_locations(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 10
            return [{"id": "location-1"}]

        def list_risk_detections(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 5
            return [{"id": "risk-1"}]

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_identity_security_client", lambda action=None: _FakeClient())

    list_payload = m365_router.execute_instruction_contract(
        action="list_conditional_access_policies",
        params_payload={"top": 15},
        trace_id="trace-list-conditional-access-policies",
    )
    get_payload = m365_router.execute_instruction_contract(
        action="get_conditional_access_policy",
        params_payload={"policyId": "policy-1"},
        trace_id="trace-get-conditional-access-policy",
    )
    create_payload = m365_router.execute_instruction_contract(
        action="create_conditional_access_policy",
        params_payload={"body": {"displayName": "Policy One"}},
        trace_id="trace-create-conditional-access-policy",
    )
    update_payload = m365_router.execute_instruction_contract(
        action="update_conditional_access_policy",
        params_payload={"policyId": "policy-1", "body": {"state": "enabled"}},
        trace_id="trace-update-conditional-access-policy",
    )
    delete_payload = m365_router.execute_instruction_contract(
        action="delete_conditional_access_policy",
        params_payload={"policyId": "policy-1"},
        trace_id="trace-delete-conditional-access-policy",
    )
    named_locations_payload = m365_router.execute_instruction_contract(
        action="list_named_locations",
        params_payload={"top": 10},
        trace_id="trace-list-named-locations",
    )
    risk_detections_payload = m365_router.execute_instruction_contract(
        action="list_risk_detections",
        params_payload={"top": 5},
        trace_id="trace-list-risk-detections",
    )

    assert list_payload["result"] == {"policies": [{"id": "policy-1"}], "count": 1}
    assert get_payload["result"] == {"policy": {"id": "policy-1"}}
    assert create_payload["result"] == {
        "policy": {"id": "policy-1", "displayName": "Policy One"},
        "status": "created",
    }
    assert update_payload["result"] == {"updated": True, "policyId": "policy-1"}
    assert delete_payload["result"] == {"deleted": True, "policyId": "policy-1"}
    assert named_locations_payload["result"] == {
        "namedLocations": [{"id": "location-1"}],
        "count": 1,
    }
    assert risk_detections_payload["result"] == {
        "riskDetections": [{"id": "risk-1"}],
        "count": 1,
    }
