from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from smarthaus_common.executor_routing import (
    executor_route_for_action,
    reload_executor_routing_registry,
)


@pytest.fixture(autouse=True)
def _reset_routing_registry() -> Iterator[None]:
    reload_executor_routing_registry()
    yield
    reload_executor_routing_registry()


def test_executor_routing_v2_routes_canonical_action_keys() -> None:
    assert executor_route_for_action(None, "directory.user.list") == "directory"
    assert executor_route_for_action(None, "sharepoint.site.create") == "sharepoint"
    assert executor_route_for_action(None, "collaboration.team.create") == "collaboration"


def test_executor_routing_v2_routes_legacy_aliases() -> None:
    assert executor_route_for_action(None, "list_users") == "directory"
    assert executor_route_for_action("m365-administrator", "sites.get") == "sharepoint"
    assert executor_route_for_action("outreach-coordinator", "mail.send") == "messaging"
    assert executor_route_for_action("email-processing-agent", "email.respond") == "messaging"
    assert executor_route_for_action("teams-manager", "create-workspace") == "collaboration"
    assert executor_route_for_action("service-health", "health.overview") == "reports"
    assert executor_route_for_action("identity-security", "ca.policies") == "identity_security"


def test_executor_routing_v2_covers_all_allowed_actions_in_agent_registry() -> None:
    agents_path = Path(__file__).resolve().parents[1] / "registry" / "agents.yaml"
    agents = (yaml.safe_load(agents_path.read_text(encoding="utf-8")) or {}).get("agents", {})

    missing: list[str] = []
    for agent, config in agents.items():
        for action in (config or {}).get("allowed_actions", []) or []:
            try:
                executor_route_for_action(agent, action)
            except ValueError as exc:
                missing.append(f"{agent}:{action}:{exc}")

    assert missing == []


def test_executor_routing_v2_fails_closed_for_unknown_action() -> None:
    with pytest.raises(ValueError, match="executor_route_unknown"):
        executor_route_for_action("m365-administrator", "totally.unknown.action")
