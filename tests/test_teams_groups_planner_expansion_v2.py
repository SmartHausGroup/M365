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


def test_e2d_instruction_schema_includes_collaboration_and_planner_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}

    assert {
        "get_team",
        "list_channels",
        "create_channel",
        "list_plans",
        "create_plan",
        "list_plan_buckets",
        "create_plan_bucket",
        "create_plan_task",
    }.issubset(supported)


def test_e2d_actions_route_to_collaboration_and_use_app_only_auth() -> None:
    for action in (
        "get_team",
        "list_channels",
        "create_channel",
        "list_plans",
        "create_plan",
        "list_plan_buckets",
        "create_plan_bucket",
        "create_plan_task",
    ):
        assert executor_route_for_action(None, action) == "collaboration"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "collaboration"
        assert resolution.auth_class == "app_only"


def test_e2d_collaboration_and_planner_actions_resolve_expected_approval_profiles() -> None:
    read_resolution = resolve_action_approval_risk("m365-administrator", "get_team", {})
    channel_resolution = resolve_action_approval_risk("m365-administrator", "create_channel", {})
    planner_resolution = resolve_action_approval_risk("m365-administrator", "create_plan_task", {})

    assert read_resolution.risk_class == "low"
    assert read_resolution.approval_profile == "low-observe-create"
    assert read_resolution.approval_required is False

    assert channel_resolution.risk_class == "high"
    assert channel_resolution.approval_profile == "high-impact"
    assert channel_resolution.approval_required is True

    assert planner_resolution.risk_class == "medium"
    assert planner_resolution.approval_profile == "medium-operational"
    assert planner_resolution.approval_required is False


def test_e2d_instruction_contract_executes_team_and_channel_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def get_team(
            self,
            team_id: str | None = None,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> dict[str, Any]:
            assert team_id is None
            assert group_id is None
            assert mail_nickname == "ops"
            return {"id": "team-123", "displayName": "Operations"}

        def list_channels(
            self,
            team_id: str | None = None,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> list[dict[str, Any]]:
            assert team_id == "team-123"
            assert group_id is None
            assert mail_nickname is None
            return [
                {"id": "chan-1", "displayName": "General"},
                {"id": "chan-2", "displayName": "Planning"},
            ]

        def create_channel(
            self,
            display_name: str,
            *,
            team_id: str | None = None,
            group_id: str | None = None,
            mail_nickname: str | None = None,
            description: str | None = None,
        ) -> dict[str, Any]:
            assert display_name == "Escalations"
            assert team_id is None
            assert group_id == "group-ops"
            assert mail_nickname is None
            assert description == "High priority work"
            return {"id": "chan-3", "displayName": display_name}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: _FakeClient())

    team_payload = m365_router.execute_instruction_contract(
        action="get_team",
        params_payload={"mail_nickname": "ops"},
        trace_id="trace-team",
    )
    channels_payload = m365_router.execute_instruction_contract(
        action="list_channels",
        params_payload={"teamId": "team-123", "top": 1},
        trace_id="trace-channels",
    )
    create_channel_payload = m365_router.execute_instruction_contract(
        action="create_channel",
        params_payload={
            "groupId": "group-ops",
            "channel_name": "Escalations",
            "description": "High priority work",
        },
        trace_id="trace-create-channel",
    )

    assert team_payload["ok"] is True
    assert team_payload["result"] == {"team": {"id": "team-123", "displayName": "Operations"}}

    assert channels_payload["ok"] is True
    assert channels_payload["result"] == {
        "channels": [{"id": "chan-1", "displayName": "General"}],
        "count": 1,
    }

    assert create_channel_payload["ok"] is True
    assert create_channel_payload["result"] == {
        "channel": {"id": "chan-3", "displayName": "Escalations"},
        "status": "created",
    }


def test_e2d_instruction_contract_executes_planner_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def list_plans(
            self,
            *,
            group_id: str | None = None,
            mail_nickname: str | None = None,
        ) -> list[dict[str, Any]]:
            assert group_id is None
            assert mail_nickname == "ops"
            return [{"id": "plan-1", "title": "Operations Plan"}]

        def create_plan(
            self,
            group_id: str | None,
            title: str,
            *,
            mail_nickname: str | None = None,
        ) -> dict[str, Any]:
            assert group_id == "group-ops"
            assert title == "Launch Plan"
            assert mail_nickname is None
            return {"id": "plan-2", "title": title}

        def list_plan_buckets(self, plan_id: str) -> list[dict[str, Any]]:
            assert plan_id == "plan-2"
            return [{"id": "bucket-1", "name": "Backlog"}]

        def create_plan_bucket(
            self, plan_id: str, name: str, order_hint: str = " !"
        ) -> dict[str, Any]:
            assert plan_id == "plan-2"
            assert name == "In Progress"
            assert order_hint == " !"
            return {"id": "bucket-2", "name": name}

        def create_plan_task(
            self,
            plan_id: str,
            bucket_id: str,
            title: str,
            *,
            description: str | None = None,
            reference_url: str | None = None,
            percent_complete: int | None = None,
        ) -> dict[str, Any]:
            assert plan_id == "plan-2"
            assert bucket_id == "bucket-2"
            assert title == "Draft rollout"
            assert description == "Prepare launch checklist"
            assert reference_url == "https://example.com/rollout"
            assert percent_complete == 25
            return {"id": "task-1", "title": title}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: _FakeClient())

    list_plans_payload = m365_router.execute_instruction_contract(
        action="list_plans",
        params_payload={"mail_nickname": "ops"},
        trace_id="trace-list-plans",
    )
    create_plan_payload = m365_router.execute_instruction_contract(
        action="create_plan",
        params_payload={"groupId": "group-ops", "title": "Launch Plan"},
        trace_id="trace-create-plan",
    )
    list_buckets_payload = m365_router.execute_instruction_contract(
        action="list_plan_buckets",
        params_payload={"planId": "plan-2"},
        trace_id="trace-list-buckets",
    )
    create_bucket_payload = m365_router.execute_instruction_contract(
        action="create_plan_bucket",
        params_payload={"planId": "plan-2", "name": "In Progress"},
        trace_id="trace-create-bucket",
    )
    create_task_payload = m365_router.execute_instruction_contract(
        action="create_plan_task",
        params_payload={
            "planId": "plan-2",
            "bucketId": "bucket-2",
            "title": "Draft rollout",
            "description": "Prepare launch checklist",
            "referenceUrl": "https://example.com/rollout",
            "percentComplete": 25,
        },
        trace_id="trace-create-task",
    )

    assert list_plans_payload["ok"] is True
    assert list_plans_payload["result"] == {
        "plans": [{"id": "plan-1", "title": "Operations Plan"}],
        "count": 1,
    }
    assert create_plan_payload["ok"] is True
    assert create_plan_payload["result"] == {
        "plan": {"id": "plan-2", "title": "Launch Plan"},
        "status": "created",
    }
    assert list_buckets_payload["ok"] is True
    assert list_buckets_payload["result"] == {
        "buckets": [{"id": "bucket-1", "name": "Backlog"}],
        "count": 1,
    }
    assert create_bucket_payload["ok"] is True
    assert create_bucket_payload["result"] == {
        "bucket": {"id": "bucket-2", "name": "In Progress"},
        "status": "created",
    }
    assert create_task_payload["ok"] is True
    assert create_task_payload["result"] == {
        "task": {"id": "task-1", "title": "Draft rollout"},
        "status": "created",
    }
