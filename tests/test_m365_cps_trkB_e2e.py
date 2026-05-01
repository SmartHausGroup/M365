"""End-to-end test of Track B coverage build-out.

plan:m365-cps-trkB-p7-end-to-end-and-repackage:T1

Verifies that the inventory endpoint and the legacy alias table cover
every action introduced across B1-B5, and that the auth-tier gate from
B6 is in place.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from m365_runtime import launcher
from m365_runtime.graph.registry import ALLOWED_TIERS, READ_ONLY_REGISTRY
from ucp_m365_pack.client import LEGACY_ACTION_TO_RUNTIME_ACTION


B_NEW_RUNTIME_ACTIONS = [
    # B1 SharePoint
    "graph.sites.get",
    "graph.lists.list",
    "graph.lists.get",
    "graph.lists.items",
    "graph.drives.children",
    # B2 Calendar
    "graph.calendar.list",
    "graph.calendar.get",
    "graph.events.list",
    "graph.calendar.availability",
    # B3 Mail
    "graph.mail.list",
    "graph.mail.message_get",
    "graph.mail.attachments",
    # B4 Health & Reports
    "graph.health.overview",
    "graph.health.issues",
    "graph.health.messages",
    "graph.reports.users_active",
    "graph.reports.email_activity",
    "graph.reports.teams_activity",
    "graph.reports.sharepoint_usage",
    "graph.reports.onedrive_usage",
    # B5 Directory & Teams
    "graph.directory.domains",
    "graph.directory.roles",
    "graph.teams.get",
    "graph.channels.list",
    "graph.channels.get",
]


B_NEW_ALIASES = {
    # B1
    "sites.list": "graph.sites.search",
    "sites.get": "graph.sites.get",
    "lists.list": "graph.lists.list",
    "lists.get": "graph.lists.get",
    "lists.items": "graph.lists.items",
    "files.list": "graph.drives.children",
    # B2
    "calendar.list": "graph.calendar.list",
    "calendar.get": "graph.calendar.get",
    "events.list": "graph.events.list",
    "availability.check": "graph.calendar.availability",
    # B3
    "mail.list": "graph.mail.list",
    "mail.read": "graph.mail.message_get",
    "mail.attachments": "graph.mail.attachments",
    "mail.folders": "graph.mail.health",
    # B4
    "health.overview": "graph.health.overview",
    "health.issues": "graph.health.issues",
    "health.messages": "graph.health.messages",
    "reports.users_active": "graph.reports.users_active",
    "reports.email_activity": "graph.reports.email_activity",
    "reports.teams_activity": "graph.reports.teams_activity",
    "reports.sharepoint_usage": "graph.reports.sharepoint_usage",
    "reports.onedrive_usage": "graph.reports.onedrive_usage",
    # B5
    "directory.domains": "graph.directory.domains",
    "directory.roles": "graph.directory.roles",
    "teams.get": "graph.teams.get",
    "channels.list": "graph.channels.list",
    "channels.get": "graph.channels.get",
}


@pytest.fixture()
def trkB_client(tmp_path: Path) -> TestClient:
    env = {
        "M365_TENANT_ID": "11111111-1111-1111-1111-111111111111",
        "M365_CLIENT_ID": "22222222-2222-2222-2222-222222222222",
        "M365_AUTH_MODE": "auth_code_pkce",
        "M365_SERVICE_ACTOR_UPN": "ops@example.com",
        "M365_REDIRECT_URI": "http://127.0.0.1:9301/callback",
        "M365_GRANTED_SCOPES": "User.Read,Sites.Read.All,Files.Read.All,Mail.Read,Calendars.Read",
        "M365_TOKEN_STORE": "memory",
    }
    plan = launcher.plan_launch(env=env)
    app = launcher.build_app(plan)
    return TestClient(app)


def test_trkB_e2e_all_new_actions_in_registry() -> None:
    """B1-B5 actions are all registered."""
    for action_id in B_NEW_RUNTIME_ACTIONS:
        assert action_id in READ_ONLY_REGISTRY, f"{action_id} missing"


def test_trkB_e2e_all_new_aliases_resolve() -> None:
    """B1-B5 aliases all map to runtime actions."""
    for legacy, runtime in B_NEW_ALIASES.items():
        assert LEGACY_ACTION_TO_RUNTIME_ACTION[legacy] == runtime


def test_trkB_e2e_inventory_reports_post_b_size(trkB_client: TestClient) -> None:
    """B coverage moved registry size from 11 to 36 and aliases from 22 to 49."""
    body = trkB_client.get("/v1/inventory").json()
    assert len(body["implemented_actions"]) == len(READ_ONLY_REGISTRY)
    assert len(body["alias_map"]) == len(LEGACY_ACTION_TO_RUNTIME_ACTION)
    assert len(READ_ONLY_REGISTRY) >= 36
    assert len(LEGACY_ACTION_TO_RUNTIME_ACTION) >= 49


def test_trkB_e2e_advertised_only_shrunk_after_aliases(trkB_client: TestClient) -> None:
    """Adding aliases moves actions out of advertised_only into the implemented/aliased path."""
    body = trkB_client.get("/v1/inventory").json()
    advertised_only = set(body["advertised_only"])
    # The legacy names we added in Track B should NOT appear in advertised_only
    for legacy in B_NEW_ALIASES.keys():
        assert legacy not in advertised_only, f"{legacy} still in advertised_only"


def test_trkB_e2e_preflight_with_pkce_admits_new_sharepoint_actions(
    trkB_client: TestClient,
) -> None:
    """Preflight with PKCE + Sites.Read.All admits the new SharePoint reads."""
    body = trkB_client.post(
        "/v1/auth/preflight",
        json={
            "auth_mode": "auth_code_pkce",
            "granted_scopes": ["Sites.Read.All", "Files.Read.All"],
        },
    ).json()
    invokable = set(body["invokable"])
    # Sites + lists actions should be invokable with PKCE + Sites.Read.All
    expected = {
        "graph.sites.root",
        "graph.sites.search",
        "graph.sites.get",
        "graph.lists.list",
        "graph.lists.get",
        "graph.lists.items",
    }
    assert expected.issubset(invokable), f"missing: {expected - invokable}"


def test_trkB_e2e_tier_system_in_place() -> None:
    """B6 — auth-tier hierarchy is exposed."""
    assert ALLOWED_TIERS == frozenset({"read-only", "standard", "admin"})
    # Every registered action defaults to read-only tier
    for spec in READ_ONLY_REGISTRY.values():
        assert spec.min_tier == "read-only"
