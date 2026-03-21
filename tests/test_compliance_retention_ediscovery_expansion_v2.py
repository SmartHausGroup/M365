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


def test_e4c_instruction_schema_includes_compliance_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}
    assert {
        "list_ediscovery_cases",
        "get_ediscovery_case",
        "create_ediscovery_case",
        "list_ediscovery_case_searches",
        "get_ediscovery_case_search",
        "create_ediscovery_case_search",
        "list_ediscovery_case_custodians",
        "list_ediscovery_case_legal_holds",
    }.issubset(supported)


def test_e4c_actions_route_auth_and_risk_to_compliance_domain() -> None:
    read_actions = {
        "list_ediscovery_cases",
        "get_ediscovery_case",
        "list_ediscovery_case_searches",
        "get_ediscovery_case_search",
        "list_ediscovery_case_custodians",
        "list_ediscovery_case_legal_holds",
    }
    for action in read_actions:
        assert executor_route_for_action(None, action) == "compliance"
        auth = resolve_action_auth("compliance-monitoring-agent", action, {})
        assert auth.executor_domain == "compliance"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("compliance-monitoring-agent", action, {})
        assert approval.approval_profile == "low-observe-create"
        assert approval.approval_required is False

    for action in {"create_ediscovery_case", "create_ediscovery_case_search"}:
        auth = resolve_action_auth("compliance-monitoring-agent", action, {})
        assert auth.executor_domain == "compliance"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("compliance-monitoring-agent", action, {})
        assert approval.approval_profile == "critical-regulated"
        assert approval.approval_required is True


def test_e4c_instruction_contract_executes_compliance_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def list_ediscovery_cases(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 20
            return [{"id": "case-1"}]

        def get_ediscovery_case(self, case_id: str) -> dict[str, Any]:
            assert case_id == "case-1"
            return {"id": case_id}

        def create_ediscovery_case(self, *, body: dict[str, Any]) -> dict[str, Any]:
            assert body == {"displayName": "Case Alpha"}
            return {"id": "case-2", "displayName": "Case Alpha"}

        def list_ediscovery_case_searches(
            self,
            case_id: str,
            *,
            top: int = 50,
        ) -> list[dict[str, Any]]:
            assert case_id == "case-1"
            assert top == 15
            return [{"id": "search-1"}]

        def get_ediscovery_case_search(self, case_id: str, search_id: str) -> dict[str, Any]:
            assert case_id == "case-1"
            assert search_id == "search-1"
            return {"id": search_id}

        def create_ediscovery_case_search(
            self,
            case_id: str,
            *,
            body: dict[str, Any],
        ) -> dict[str, Any]:
            assert case_id == "case-1"
            assert body == {"displayName": "Search Alpha"}
            return {"id": "search-2", "displayName": "Search Alpha"}

        def list_ediscovery_case_custodians(
            self,
            case_id: str,
            *,
            top: int = 50,
        ) -> list[dict[str, Any]]:
            assert case_id == "case-1"
            assert top == 5
            return [{"id": "custodian-1"}]

        def list_ediscovery_case_legal_holds(
            self,
            case_id: str,
            *,
            top: int = 50,
        ) -> list[dict[str, Any]]:
            assert case_id == "case-1"
            assert top == 7
            return [{"id": "hold-1"}]

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(
        m365_router, "_compliance_ediscovery_client", lambda action=None: _FakeClient()
    )

    assert m365_router.execute_instruction_contract(
        action="list_ediscovery_cases",
        params_payload={"top": 20},
        trace_id="trace-list-ediscovery-cases",
    )["result"] == {"cases": [{"id": "case-1"}], "count": 1}

    assert m365_router.execute_instruction_contract(
        action="get_ediscovery_case",
        params_payload={"caseId": "case-1"},
        trace_id="trace-get-ediscovery-case",
    )["result"] == {"case": {"id": "case-1"}}

    assert m365_router.execute_instruction_contract(
        action="create_ediscovery_case",
        params_payload={"displayName": "Case Alpha"},
        trace_id="trace-create-ediscovery-case",
    )["result"] == {"case": {"id": "case-2", "displayName": "Case Alpha"}, "status": "created"}

    assert m365_router.execute_instruction_contract(
        action="list_ediscovery_case_searches",
        params_payload={"caseId": "case-1", "top": 15},
        trace_id="trace-list-ediscovery-case-searches",
    )["result"] == {"searches": [{"id": "search-1"}], "count": 1}

    assert m365_router.execute_instruction_contract(
        action="get_ediscovery_case_search",
        params_payload={"caseId": "case-1", "searchId": "search-1"},
        trace_id="trace-get-ediscovery-case-search",
    )["result"] == {"search": {"id": "search-1"}}

    assert m365_router.execute_instruction_contract(
        action="create_ediscovery_case_search",
        params_payload={"caseId": "case-1", "displayName": "Search Alpha"},
        trace_id="trace-create-ediscovery-case-search",
    )["result"] == {
        "search": {"id": "search-2", "displayName": "Search Alpha"},
        "status": "created",
    }

    assert m365_router.execute_instruction_contract(
        action="list_ediscovery_case_custodians",
        params_payload={"caseId": "case-1", "top": 5},
        trace_id="trace-list-ediscovery-case-custodians",
    )["result"] == {"custodians": [{"id": "custodian-1"}], "count": 1}

    assert m365_router.execute_instruction_contract(
        action="list_ediscovery_case_legal_holds",
        params_payload={"caseId": "case-1", "top": 7},
        trace_id="trace-list-ediscovery-case-legal-holds",
    )["result"] == {"legalHolds": [{"id": "hold-1"}], "count": 1}
