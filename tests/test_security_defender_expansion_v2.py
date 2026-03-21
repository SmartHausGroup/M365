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


def test_e4b_instruction_schema_includes_security_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}
    assert {
        "list_security_alerts",
        "get_security_alert",
        "list_security_incidents",
        "get_security_incident",
        "list_secure_scores",
        "get_secure_score_profile",
        "update_security_incident",
    }.issubset(supported)


def test_e4b_actions_route_auth_and_risk_to_security_domain() -> None:
    for action in {
        "list_security_alerts",
        "get_security_alert",
        "list_security_incidents",
        "get_security_incident",
        "list_secure_scores",
        "get_secure_score_profile",
    }:
        assert executor_route_for_action(None, action) == "security"
        auth = resolve_action_auth("security-operations", action, {})
        assert auth.executor_domain == "security"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("security-operations", action, {})
        assert approval.approval_profile == "low-observe-create"
        assert approval.approval_required is False

    mutation_auth = resolve_action_auth("security-operations", "update_security_incident", {})
    assert mutation_auth.executor_domain == "security"
    assert mutation_auth.auth_class == "app_only"
    mutation_approval = resolve_action_approval_risk(
        "security-operations",
        "update_security_incident",
        {},
    )
    assert mutation_approval.approval_profile == "critical-regulated"
    assert mutation_approval.approval_required is True


def test_e4b_instruction_contract_executes_security_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def list_security_alerts(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 20
            return [{"id": "alert-1"}]

        def get_security_alert(self, alert_id: str) -> dict[str, Any]:
            assert alert_id == "alert-1"
            return {"id": alert_id}

        def list_security_incidents(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 10
            return [{"id": "incident-1"}]

        def get_security_incident(self, incident_id: str) -> dict[str, Any]:
            assert incident_id == "incident-1"
            return {"id": incident_id}

        def list_secure_scores(self, *, top: int = 25) -> list[dict[str, Any]]:
            assert top == 5
            return [{"id": "score-1"}]

        def get_secure_score_profile(self, profile_id: str) -> dict[str, Any]:
            assert profile_id == "profile-1"
            return {"id": profile_id}

        def update_security_incident(
            self, incident_id: str, *, body: dict[str, Any]
        ) -> dict[str, Any]:
            assert incident_id == "incident-1"
            assert body == {"status": "resolved"}
            return {"updated": True, "incidentId": incident_id}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_security_defender_client", lambda action=None: _FakeClient())

    list_alerts_payload = m365_router.execute_instruction_contract(
        action="list_security_alerts",
        params_payload={"top": 20},
        trace_id="trace-list-security-alerts",
    )
    get_alert_payload = m365_router.execute_instruction_contract(
        action="get_security_alert",
        params_payload={"alertId": "alert-1"},
        trace_id="trace-get-security-alert",
    )
    list_incidents_payload = m365_router.execute_instruction_contract(
        action="list_security_incidents",
        params_payload={"top": 10},
        trace_id="trace-list-security-incidents",
    )
    get_incident_payload = m365_router.execute_instruction_contract(
        action="get_security_incident",
        params_payload={"incidentId": "incident-1"},
        trace_id="trace-get-security-incident",
    )
    list_scores_payload = m365_router.execute_instruction_contract(
        action="list_secure_scores",
        params_payload={"top": 5},
        trace_id="trace-list-secure-scores",
    )
    get_profile_payload = m365_router.execute_instruction_contract(
        action="get_secure_score_profile",
        params_payload={"profileId": "profile-1"},
        trace_id="trace-get-secure-score-profile",
    )
    update_incident_payload = m365_router.execute_instruction_contract(
        action="update_security_incident",
        params_payload={"incidentId": "incident-1", "status": "resolved"},
        trace_id="trace-update-security-incident",
    )

    assert list_alerts_payload["result"] == {"alerts": [{"id": "alert-1"}], "count": 1}
    assert get_alert_payload["result"] == {"alert": {"id": "alert-1"}}
    assert list_incidents_payload["result"] == {"incidents": [{"id": "incident-1"}], "count": 1}
    assert get_incident_payload["result"] == {"incident": {"id": "incident-1"}}
    assert list_scores_payload["result"] == {"scores": [{"id": "score-1"}], "count": 1}
    assert get_profile_payload["result"] == {"profile": {"id": "profile-1"}}
    assert update_incident_payload["result"] == {"updated": True, "incidentId": "incident-1"}
