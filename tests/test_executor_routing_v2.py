from __future__ import annotations

from collections.abc import Iterator

import pytest
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


def test_executor_routing_v2_fails_closed_for_unknown_action() -> None:
    with pytest.raises(ValueError, match="executor_route_unknown"):
        executor_route_for_action("m365-administrator", "totally.unknown.action")
