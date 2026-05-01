"""Tests for B2 Calendar reads coverage.

plan:m365-cps-trkB-p2-calendar-reads / L104
"""

from __future__ import annotations

from m365_runtime.graph.registry import READ_ONLY_REGISTRY
from ucp_m365_pack.client import map_legacy_action_to_runtime


B2_NEW_ACTIONS = [
    "graph.calendar.list",
    "graph.calendar.get",
    "graph.events.list",
    "graph.calendar.availability",
]

B2_NEW_ALIASES = {
    "calendar.list": "graph.calendar.list",
    "calendar.get": "graph.calendar.get",
    "events.list": "graph.events.list",
    "availability.check": "graph.calendar.availability",
}


def test_b2_new_entries_registered() -> None:
    for action_id in B2_NEW_ACTIONS:
        assert action_id in READ_ONLY_REGISTRY
        spec = READ_ONLY_REGISTRY[action_id]
        assert spec.rw == "read"
        assert spec.workload == "exchange"
        assert "Calendars.Read" in spec.scopes


def test_b2_aliases_resolve() -> None:
    for legacy, runtime in B2_NEW_ALIASES.items():
        assert map_legacy_action_to_runtime(legacy) == runtime


def test_b2_calendar_list_supports_device_code() -> None:
    """Delegated calendar.list must accept device_code (the operator's normal flow)."""
    spec = READ_ONLY_REGISTRY["graph.calendar.list"]
    assert "device_code" in spec.auth_modes
    assert "auth_code_pkce" in spec.auth_modes


def test_b2_events_list_excludes_device_code() -> None:
    """Cross-user /users/{id}/events requires app-only or PKCE (delegated /me/events for device-code)."""
    spec = READ_ONLY_REGISTRY["graph.events.list"]
    assert "device_code" not in spec.auth_modes
