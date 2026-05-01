"""Tests for B1 SharePoint reads coverage.

plan:m365-cps-trkB-p1-sharepoint-reads / L103
"""

from __future__ import annotations

from typing import Any

import httpx

from m365_runtime.graph.actions import _substitute_path_params, invoke
from m365_runtime.graph.registry import READ_ONLY_REGISTRY
from ucp_m365_pack.client import LEGACY_ACTION_TO_RUNTIME_ACTION, map_legacy_action_to_runtime


B1_NEW_ACTIONS = [
    "graph.sites.get",
    "graph.lists.list",
    "graph.lists.get",
    "graph.lists.items",
    "graph.drives.children",
]

B1_NEW_ALIASES = {
    "sites.list": "graph.sites.search",
    "sites.get": "graph.sites.get",
    "lists.list": "graph.lists.list",
    "lists.get": "graph.lists.get",
    "lists.items": "graph.lists.items",
    "files.list": "graph.drives.children",
}


def test_b1_new_entries_registered() -> None:
    """L103.L_NEW_ENTRIES_REGISTERED — five SharePoint actions in registry."""
    for action_id in B1_NEW_ACTIONS:
        assert action_id in READ_ONLY_REGISTRY, f"{action_id} missing from registry"
        spec = READ_ONLY_REGISTRY[action_id]
        assert spec.rw == "read"
        assert spec.risk == "low"


def test_b1_aliases_resolve() -> None:
    """L103.L_ALIASES_RESOLVE — legacy names map to runtime action ids."""
    for legacy, runtime in B1_NEW_ALIASES.items():
        assert map_legacy_action_to_runtime(legacy) == runtime
        assert LEGACY_ACTION_TO_RUNTIME_ACTION[legacy] == runtime


def test_b1_path_subst_substitutes_placeholders() -> None:
    """L103.L_PATH_SUBST_CORRECT — placeholders are replaced from params."""
    rendered, missing = _substitute_path_params(
        "/sites/{siteId}/lists/{listId}", {"siteId": "S1", "listId": "L1"}
    )
    assert rendered == "/sites/S1/lists/L1"
    assert missing == []


def test_b1_path_subst_reports_missing() -> None:
    """L103.L_PATH_SUBST_CORRECT — missing placeholders are reported."""
    rendered, missing = _substitute_path_params("/sites/{siteId}", {})
    assert missing == ["siteId"]


def test_b1_path_subst_no_placeholders_passthrough() -> None:
    """No placeholders -> endpoint unchanged."""
    rendered, missing = _substitute_path_params("/me", {"foo": "bar"})
    assert rendered == "/me"
    assert missing == []


def test_b1_invoke_unknown_path_param_returns_internal_error() -> None:
    """invoke() with missing path params returns internal_error / endpoint_param_missing."""
    result = invoke(
        action_id="graph.sites.get",
        actor="ops@acme.com",
        granted_scopes=frozenset({"Sites.Read.All"}),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
        params={},
    )
    assert result.status_class == "internal_error"
    assert result.audit["extra_redacted"]["reason"] == "endpoint_param_missing"
    assert result.audit["extra_redacted"]["missing"] == ["siteId"]


def test_b1_invoke_substitutes_path_param_and_calls_graph() -> None:
    """invoke() with siteId in params hits Graph at /sites/SITE_ID."""
    captured: dict[str, Any] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["url"] = str(req.url)
        return httpx.Response(200, json={"id": "SITE_ID", "displayName": "Test Site"})

    result = invoke(
        action_id="graph.sites.get",
        actor="ops@acme.com",
        granted_scopes=frozenset({"Sites.Read.All"}),
        current_auth_mode="auth_code_pkce",
        access_token="AT",
        params={"siteId": "SITE_ID"},
        transport=httpx.MockTransport(handler),
    )
    assert result.status_class == "success", result.audit
    assert "/sites/SITE_ID" in captured["url"]


def test_b1_no_regression_existing_entries() -> None:
    """L103.L_NO_REGRESSION — pre-B1 entries still resolve."""
    pre_b1 = [
        "graph.org_profile",
        "graph.me",
        "graph.users.list",
        "graph.groups.list",
        "graph.sites.root",
        "graph.sites.search",
        "graph.teams.list",
        "graph.drives.list",
        "graph.mail.health",
        "graph.calendar.health",
        "graph.servicehealth",
    ]
    for a in pre_b1:
        assert a in READ_ONLY_REGISTRY
