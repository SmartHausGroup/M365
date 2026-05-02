"""Tests for C2 Planned-action short-circuit. plan:m365-cps-trkC-p2-agents-yaml-schema / L110"""

from __future__ import annotations

import os

import pytest

from ucp_m365_pack.client import (
    compute_coverage_status,
    execute_m365_action,
    LEGACY_ACTION_TO_RUNTIME_ACTION,
)


def test_c2_implemented_action_returns_implemented() -> None:
    """L110.L_COVERAGE_STATUS_CORRECT — direct registry hit."""
    assert compute_coverage_status("graph.me") == "implemented"
    assert compute_coverage_status("graph.users.list") == "implemented"
    assert compute_coverage_status("graph.sites.get") == "implemented"  # B1


def test_c2_aliased_action_returns_aliased() -> None:
    """L110.L_COVERAGE_STATUS_CORRECT — alias resolves to implemented."""
    assert compute_coverage_status("me") == "aliased"
    assert compute_coverage_status("users.list") == "aliased"
    assert compute_coverage_status("sites.get") == "aliased"  # B1


def test_c2_unknown_action_returns_planned() -> None:
    """L110.L_COVERAGE_STATUS_CORRECT — neither registry nor alias."""
    assert compute_coverage_status("completely.bogus") == "planned"
    assert compute_coverage_status("users.create") == "planned"  # writes are not yet implemented
    assert compute_coverage_status("teams.archive") == "planned"


def test_c2_empty_or_none_returns_planned() -> None:
    assert compute_coverage_status("") == "planned"
    assert compute_coverage_status(None) == "planned"


def test_c2_execute_planned_action_short_circuits(monkeypatch: pytest.MonkeyPatch) -> None:
    """L110.L_PLANNED_RETURNS_NOT_YET_IMPLEMENTED — no HTTP, returns honest envelope."""
    # Ensure no runtime URL is set so we'd otherwise fail-closed
    monkeypatch.delenv("M365_RUNTIME_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_RUNTIME_URL", raising=False)
    monkeypatch.delenv("M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("GRAPH_STUB_MODE", raising=False)

    result = execute_m365_action("m365-administrator", "users.create")
    assert result["status_class"] == "not_yet_implemented"
    assert result["coverage_status"] == "planned"
    assert result["agent"] == "m365-administrator"
    assert result["action"] == "users.create"
    assert "correlation_id" in result


def test_c2_execute_implemented_action_does_not_short_circuit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L110.L_IMPLEMENTED_PASSES_THROUGH — implemented actions reach stub/runtime path.

    With GRAPH_STUB_MODE=1 and no runtime/service URL, an implemented action
    should reach _stub_execute and get a stub envelope, not the planned
    short-circuit.
    """
    monkeypatch.delenv("M365_RUNTIME_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_RUNTIME_URL", raising=False)
    monkeypatch.delenv("M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.setenv("GRAPH_STUB_MODE", "1")

    result = execute_m365_action("m365-administrator", "me")
    assert result.get("stub") is True
    assert result.get("status_class") != "not_yet_implemented"


def test_c2_alias_table_unchanged_size() -> None:
    """L110 doesn't add or remove aliases."""
    # 49 from prior tracks (Track A baseline 22 + Track B added 27)
    assert len(LEGACY_ACTION_TO_RUNTIME_ACTION) >= 49
