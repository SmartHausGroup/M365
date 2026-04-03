from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UCP_SRC = REPO_ROOT.parent / "UCP" / "src"
M365_SRC = REPO_ROOT / "src"

for candidate in (str(M365_SRC), str(UCP_SRC), str(REPO_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

# These imports intentionally follow the local path bootstrap above.
from smarthaus_mcp_sdk.contracts import MCPEvent, PackContext  # noqa: E402
from ucp_m365_pack.contracts import (  # noqa: E402
    M365PackAdapter,
    create_pack_adapter,
    requires_confirmation,
    risk_tier_for_agent,
)


def _context() -> PackContext:
    return PackContext(server_id="test", server_version="1.0", config={})


def _event(
    tool: str = "m365_users",
    direction: str = "in",
    status: str = "ok",
    payload: dict | None = None,
) -> MCPEvent:
    return MCPEvent(
        trace_id="t-001",
        request_id="r-001",
        direction=direction,
        tool=tool,
        status=status,
        timestamp_utc="2026-01-01T00:00:00+00:00",
        payload=payload or {},
    )


def test_create_pack_adapter_returns_adapter() -> None:
    adapter = create_pack_adapter()
    assert isinstance(adapter, M365PackAdapter)
    assert adapter.pack_id == "m365_pack"


def test_register_sets_context() -> None:
    adapter = create_pack_adapter()
    context = _context()
    adapter.register(context)
    assert adapter._context is context


def test_snapshot_tracks_agents_and_tiers() -> None:
    adapter = create_pack_adapter()
    adapter.register(_context())
    adapter.handle_event(_event(payload={"agent": "m365-administrator", "action": "users.read"}))
    adapter.handle_event(_event(payload={"agent": "hr-generalist", "action": "employee.onboard"}))

    snapshot = adapter.snapshot()

    assert snapshot["event_count"] == 2
    assert snapshot["agent_counts"]["m365-administrator"] == 1
    assert snapshot["agent_counts"]["hr-generalist"] == 1
    assert snapshot["tier_counts"]["high"] == 1
    assert snapshot["tier_counts"]["critical"] == 1


def test_requires_confirmation_respects_critical_tier_and_explicit_actions() -> None:
    assert requires_confirmation("hr-generalist", "employee.onboard") is True
    assert requires_confirmation("m365-administrator", "users.disable") is True
    assert requires_confirmation("m365-administrator", "users.read") is False


def test_risk_tier_for_agent_defaults_medium() -> None:
    assert risk_tier_for_agent("nonexistent-agent") == "medium"
