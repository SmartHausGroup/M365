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


def test_e2b_instruction_schema_includes_outlook_exchange_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}

    assert {
        "list_messages",
        "get_message",
        "send_mail",
        "move_message",
        "delete_message",
        "list_mail_folders",
        "get_mailbox_settings",
        "update_mailbox_settings",
        "list_events",
        "create_event",
        "get_event",
        "update_event",
        "delete_event",
        "get_schedule",
        "list_contacts",
        "get_contact",
        "create_contact",
        "update_contact",
        "delete_contact",
        "list_contact_folders",
    }.issubset(supported)


def test_e2b_actions_route_and_auth_to_messaging() -> None:
    for action in (
        "list_messages",
        "send_mail",
        "get_schedule",
        "create_contact",
        "update_mailbox_settings",
    ):
        assert executor_route_for_action(None, action) == "messaging"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "messaging"
        assert resolution.auth_class == "hybrid"


def test_e2b_reads_and_mutations_resolve_expected_approval_profiles() -> None:
    read_resolution = resolve_action_approval_risk("m365-administrator", "get_schedule", {})
    mutation_resolution = resolve_action_approval_risk("m365-administrator", "send_mail", {})

    assert read_resolution.risk_class == "low"
    assert read_resolution.approval_profile == "low-observe-create"
    assert read_resolution.approval_required is False

    assert mutation_resolution.risk_class == "medium"
    assert mutation_resolution.approval_profile == "medium-operational"
    assert mutation_resolution.approval_required is False


def test_e2b_instruction_contract_executes_messaging_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def send_mail(
            self,
            recipient_or_to: list[str] | str,
            subject: str,
            body: str | dict[str, Any],
            *,
            user_id_or_upn: str | None = None,
            content_type: str = "Text",
            save_to_sent_items: bool = True,
        ) -> dict[str, Any]:
            assert recipient_or_to == ["ops@smarthausgroup.com"]
            assert subject == "Status update"
            assert body == "Approved"
            assert user_id_or_upn == "shared@smarthausgroup.com"
            assert content_type == "Text"
            assert save_to_sent_items is True
            return {
                "sent": True,
                "to": recipient_or_to,
                "subject": subject,
                "from": user_id_or_upn,
                "saveToSentItems": save_to_sent_items,
            }

        def get_schedule(
            self,
            schedules: list[str],
            start_time: dict[str, Any],
            end_time: dict[str, Any],
            *,
            user_id_or_upn: str | None = None,
            availability_view_interval: int = 30,
        ) -> dict[str, Any]:
            assert schedules == ["shared@smarthausgroup.com"]
            assert start_time["dateTime"] == "2026-03-21T09:00:00"
            assert end_time["dateTime"] == "2026-03-21T10:00:00"
            assert user_id_or_upn == "shared@smarthausgroup.com"
            assert availability_view_interval == 30
            return {"value": [{"scheduleId": "shared@smarthausgroup.com"}]}

        def create_contact(
            self, body: dict[str, Any], *, user_id_or_upn: str | None = None
        ) -> dict[str, Any]:
            assert body["displayName"] == "Alex Rivera"
            assert body["emailAddresses"][0]["address"] == "alex@smarthausgroup.com"
            assert user_id_or_upn == "shared@smarthausgroup.com"
            return {"id": "contact-1", **body}

        def update_mailbox_settings(
            self, body: dict[str, Any], *, user_id_or_upn: str | None = None
        ) -> dict[str, Any]:
            assert body == {"timeZone": "Eastern Standard Time"}
            assert user_id_or_upn == "shared@smarthausgroup.com"
            return {"timeZone": "Eastern Standard Time"}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: _FakeClient())

    send_payload = m365_router.execute_instruction_contract(
        action="send_mail",
        params_payload={
            "to": ["ops@smarthausgroup.com"],
            "subject": "Status update",
            "body": "Approved",
            "mailbox": "shared@smarthausgroup.com",
        },
        trace_id="trace-send-mail",
    )
    schedule_payload = m365_router.execute_instruction_contract(
        action="get_schedule",
        params_payload={
            "schedules": ["shared@smarthausgroup.com"],
            "start": {"dateTime": "2026-03-21T09:00:00", "timeZone": "UTC"},
            "end": {"dateTime": "2026-03-21T10:00:00", "timeZone": "UTC"},
            "mailbox": "shared@smarthausgroup.com",
        },
        trace_id="trace-schedule",
    )
    create_contact_payload = m365_router.execute_instruction_contract(
        action="create_contact",
        params_payload={
            "displayName": "Alex Rivera",
            "email": "alex@smarthausgroup.com",
            "mailbox": "shared@smarthausgroup.com",
        },
        trace_id="trace-create-contact",
    )
    mailbox_payload = m365_router.execute_instruction_contract(
        action="update_mailbox_settings",
        params_payload={
            "body": {"timeZone": "Eastern Standard Time"},
            "mailbox": "shared@smarthausgroup.com",
        },
        trace_id="trace-mailbox-settings",
    )

    assert send_payload["ok"] is True
    assert send_payload["result"] == {
        "sent": True,
        "to": ["ops@smarthausgroup.com"],
        "subject": "Status update",
        "from": "shared@smarthausgroup.com",
        "saveToSentItems": True,
    }
    assert schedule_payload["ok"] is True
    assert schedule_payload["result"] == {
        "schedules": [{"scheduleId": "shared@smarthausgroup.com"}],
        "count": 1,
    }
    assert create_contact_payload["ok"] is True
    assert create_contact_payload["result"] == {
        "contact": {
            "id": "contact-1",
            "displayName": "Alex Rivera",
            "emailAddresses": [
                {
                    "name": "Alex Rivera",
                    "address": "alex@smarthausgroup.com",
                }
            ],
        },
        "status": "created",
    }
    assert mailbox_payload["ok"] is True
    assert mailbox_payload["result"] == {
        "updated": True,
        "settings": {"timeZone": "Eastern Standard Time"},
    }
