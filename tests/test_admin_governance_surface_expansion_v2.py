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


def test_e4e_instruction_schema_includes_admin_governance_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}
    assert {
        "get_report",
        "get_usage_reports",
        "get_activity_reports",
        "list_access_reviews",
        "get_access_review",
        "create_access_review",
        "list_access_review_decisions",
        "record_access_review_decision",
    }.issubset(supported)


def test_e4e_actions_route_auth_and_risk_to_expected_domains() -> None:
    for action in {"get_report", "get_usage_reports", "get_activity_reports"}:
        assert executor_route_for_action(None, action) == "reports"
        auth = resolve_action_auth("admin-governance", action, {})
        assert auth.executor_domain == "reports"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("admin-governance", action, {})
        assert approval.approval_profile == "low-observe-create"
        assert approval.approval_required is False

    for action in {
        "list_access_reviews",
        "get_access_review",
        "list_access_review_decisions",
    }:
        assert executor_route_for_action(None, action) == "access_reviews"
        auth = resolve_action_auth("admin-governance", action, {})
        assert auth.executor_domain == "access_reviews"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("admin-governance", action, {})
        assert approval.approval_profile == "low-observe-create"
        assert approval.approval_required is False

    for action in {"create_access_review", "record_access_review_decision"}:
        auth = resolve_action_auth("admin-governance", action, {})
        assert auth.executor_domain == "access_reviews"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("admin-governance", action, {})
        assert approval.approval_profile == "high-impact"
        assert approval.approval_required is True


def test_e4e_instruction_contract_executes_admin_governance_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def get_report(
            self,
            report_name: str,
            *,
            period: str | None = None,
            category: str | None = None,
        ) -> dict[str, Any]:
            assert report_name == "office365_active_user_detail"
            assert period == "D30"
            assert category == "usage"
            return {
                "name": report_name,
                "category": "usage",
                "period": period,
                "format": "csv",
                "rows": [],
                "count": 0,
            }

        def get_usage_reports(
            self,
            report_name: str | None = None,
            *,
            period: str | None = None,
        ) -> dict[str, Any]:
            assert report_name == "office365_active_user_detail"
            assert period == "D7"
            return {
                "name": report_name,
                "category": "usage",
                "period": period,
                "format": "csv",
                "rows": [],
                "count": 0,
            }

        def get_activity_reports(
            self,
            report_name: str | None = None,
            *,
            period: str | None = None,
        ) -> dict[str, Any]:
            assert report_name == "email_activity_user_detail"
            assert period == "D90"
            return {
                "name": report_name,
                "category": "activity",
                "period": period,
                "format": "csv",
                "rows": [],
                "count": 0,
            }

        def list_access_reviews(self, *, top: int = 50) -> list[dict[str, Any]]:
            assert top == 12
            return [{"id": "review-1"}]

        def get_access_review(self, review_id: str) -> dict[str, Any]:
            assert review_id == "review-1"
            return {"id": review_id}

        def create_access_review(self, *, body: dict[str, Any]) -> dict[str, Any]:
            assert body == {"displayName": "Quarterly Guest Review"}
            return {"id": "review-1", **body}

        def list_access_review_decisions(
            self,
            review_id: str,
            instance_id: str,
            *,
            top: int = 50,
        ) -> list[dict[str, Any]]:
            assert review_id == "review-1"
            assert instance_id == "instance-1"
            assert top == 7
            return [{"id": "decision-1"}]

        def record_access_review_decision(
            self,
            review_id: str,
            instance_id: str,
            decision_id: str,
            *,
            body: dict[str, Any],
        ) -> dict[str, Any]:
            assert review_id == "review-1"
            assert instance_id == "instance-1"
            assert decision_id == "decision-1"
            assert body == {"decision": "Approve"}
            return {
                "updated": True,
                "reviewId": review_id,
                "instanceId": instance_id,
                "decisionId": decision_id,
            }

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_admin_governance_client", lambda action=None: _FakeClient())

    get_report_payload = m365_router.execute_instruction_contract(
        action="get_report",
        params_payload={
            "reportName": "office365_active_user_detail",
            "period": "D30",
            "category": "usage",
        },
        trace_id="trace-get-report",
    )
    usage_payload = m365_router.execute_instruction_contract(
        action="get_usage_reports",
        params_payload={"reportName": "office365_active_user_detail", "period": "D7"},
        trace_id="trace-get-usage-reports",
    )
    activity_payload = m365_router.execute_instruction_contract(
        action="get_activity_reports",
        params_payload={"reportName": "email_activity_user_detail", "period": "D90"},
        trace_id="trace-get-activity-reports",
    )
    list_reviews_payload = m365_router.execute_instruction_contract(
        action="list_access_reviews",
        params_payload={"top": 12},
        trace_id="trace-list-access-reviews",
    )
    get_review_payload = m365_router.execute_instruction_contract(
        action="get_access_review",
        params_payload={"reviewId": "review-1"},
        trace_id="trace-get-access-review",
    )
    create_review_payload = m365_router.execute_instruction_contract(
        action="create_access_review",
        params_payload={"body": {"displayName": "Quarterly Guest Review"}},
        trace_id="trace-create-access-review",
    )
    list_decisions_payload = m365_router.execute_instruction_contract(
        action="list_access_review_decisions",
        params_payload={"reviewId": "review-1", "instanceId": "instance-1", "top": 7},
        trace_id="trace-list-access-review-decisions",
    )
    record_decision_payload = m365_router.execute_instruction_contract(
        action="record_access_review_decision",
        params_payload={
            "reviewId": "review-1",
            "instanceId": "instance-1",
            "decisionId": "decision-1",
            "body": {"decision": "Approve"},
        },
        trace_id="trace-record-access-review-decision",
    )

    assert get_report_payload["result"] == {
        "report": {
            "name": "office365_active_user_detail",
            "category": "usage",
            "period": "D30",
            "format": "csv",
            "rows": [],
            "count": 0,
        }
    }
    assert usage_payload["result"] == {
        "report": {
            "name": "office365_active_user_detail",
            "category": "usage",
            "period": "D7",
            "format": "csv",
            "rows": [],
            "count": 0,
        }
    }
    assert activity_payload["result"] == {
        "report": {
            "name": "email_activity_user_detail",
            "category": "activity",
            "period": "D90",
            "format": "csv",
            "rows": [],
            "count": 0,
        }
    }
    assert list_reviews_payload["result"] == {"reviews": [{"id": "review-1"}], "count": 1}
    assert get_review_payload["result"] == {"review": {"id": "review-1"}}
    assert create_review_payload["result"] == {
        "review": {"id": "review-1", "displayName": "Quarterly Guest Review"},
        "status": "created",
    }
    assert list_decisions_payload["result"] == {
        "decisions": [{"id": "decision-1"}],
        "count": 1,
    }
    assert record_decision_payload["result"] == {
        "updated": True,
        "reviewId": "review-1",
        "instanceId": "instance-1",
        "decisionId": "decision-1",
    }
