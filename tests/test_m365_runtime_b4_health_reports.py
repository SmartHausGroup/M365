"""Tests for B4 Service Health & Reports coverage. plan:m365-cps-trkB-p4-health-and-reports / L106"""

from __future__ import annotations

from m365_runtime.graph.registry import READ_ONLY_REGISTRY
from ucp_m365_pack.client import map_legacy_action_to_runtime


B4_NEW_ACTIONS = [
    "graph.health.overview",
    "graph.health.issues",
    "graph.health.messages",
    "graph.reports.users_active",
    "graph.reports.email_activity",
    "graph.reports.teams_activity",
    "graph.reports.sharepoint_usage",
    "graph.reports.onedrive_usage",
]

B4_NEW_ALIASES = {
    "health.overview": "graph.health.overview",
    "health.issues": "graph.health.issues",
    "health.messages": "graph.health.messages",
    "reports.users_active": "graph.reports.users_active",
    "reports.email_activity": "graph.reports.email_activity",
    "reports.teams_activity": "graph.reports.teams_activity",
    "reports.sharepoint_usage": "graph.reports.sharepoint_usage",
    "reports.onedrive_usage": "graph.reports.onedrive_usage",
}


def test_b4_new_entries_registered() -> None:
    for action_id in B4_NEW_ACTIONS:
        assert action_id in READ_ONLY_REGISTRY
        spec = READ_ONLY_REGISTRY[action_id]
        assert spec.rw == "read"
        # All B4 are app-only (admin tenant scope)
        assert "app_only_secret" in spec.auth_modes


def test_b4_aliases_resolve() -> None:
    for legacy, runtime in B4_NEW_ALIASES.items():
        assert map_legacy_action_to_runtime(legacy) == runtime


def test_b4_health_endpoints_use_modern_path() -> None:
    """L106 uses /admin/serviceAnnouncement/* (modern) not /admin/serviceHealth/* (legacy)."""
    spec = READ_ONLY_REGISTRY["graph.health.overview"]
    assert spec.endpoint.startswith("/admin/serviceAnnouncement/")


def test_b4_reports_use_period_d7() -> None:
    """L106 reports default to D7 period in the endpoint path."""
    for action_id in ["graph.reports.users_active", "graph.reports.email_activity"]:
        spec = READ_ONLY_REGISTRY[action_id]
        assert "period='D7'" in spec.endpoint
