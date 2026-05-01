"""Tests for B5 Directory & Teams reads coverage. plan:m365-cps-trkB-p5-directory-and-teams / L107"""

from __future__ import annotations

from m365_runtime.graph.registry import READ_ONLY_REGISTRY
from ucp_m365_pack.client import map_legacy_action_to_runtime


B5_NEW_ACTIONS = [
    "graph.directory.domains",
    "graph.directory.roles",
    "graph.teams.get",
    "graph.channels.list",
    "graph.channels.get",
]

B5_NEW_ALIASES = {
    "directory.domains": "graph.directory.domains",
    "directory.roles": "graph.directory.roles",
    "teams.get": "graph.teams.get",
    "channels.list": "graph.channels.list",
    "channels.get": "graph.channels.get",
}


def test_b5_new_entries_registered() -> None:
    for action_id in B5_NEW_ACTIONS:
        assert action_id in READ_ONLY_REGISTRY
        spec = READ_ONLY_REGISTRY[action_id]
        assert spec.rw == "read"
        assert spec.risk == "low"


def test_b5_aliases_resolve() -> None:
    for legacy, runtime in B5_NEW_ALIASES.items():
        assert map_legacy_action_to_runtime(legacy) == runtime


def test_b5_directory_actions_workload() -> None:
    assert READ_ONLY_REGISTRY["graph.directory.domains"].workload == "directory"
    assert READ_ONLY_REGISTRY["graph.directory.roles"].workload == "directory"


def test_b5_teams_actions_workload() -> None:
    for a in ["graph.teams.get", "graph.channels.list", "graph.channels.get"]:
        assert READ_ONLY_REGISTRY[a].workload == "teams"
