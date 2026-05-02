"""Tests for C1 Coverage-Status Contract. plan:m365-cps-trkC-p1-coverage-status-contract / L109"""

from __future__ import annotations

from m365_runtime.graph.actions import _denial_to_status
from m365_runtime.graph.registry import COVERAGE_STATUS_VALUES


def test_c1_coverage_status_enum_complete() -> None:
    """L109.L_ENUM_COMPLETE — exactly the four values."""
    assert COVERAGE_STATUS_VALUES == frozenset(
        {"implemented", "aliased", "planned", "deprecated"}
    )


def test_c1_not_yet_implemented_distinct() -> None:
    """L109.L_NOT_YET_IMPLEMENTED_DISTINCT — not_yet_implemented does not collide."""
    assert _denial_to_status("planned_action") == "not_yet_implemented"
    assert _denial_to_status("planned_action") != _denial_to_status("unknown_action")
    assert _denial_to_status("planned_action") != _denial_to_status("mutation_fence")
    assert _denial_to_status("planned_action") != _denial_to_status("permission_missing")
    assert _denial_to_status("planned_action") != _denial_to_status("auth_mode_mismatch")
    assert _denial_to_status("planned_action") != _denial_to_status("tier_insufficient")


def test_c1_existing_status_codes_preserved() -> None:
    """L109.L_NO_REGRESSION — five existing branches still resolve correctly."""
    assert _denial_to_status("permission_missing") == "permission_missing"
    assert _denial_to_status("auth_mode_mismatch") == "auth_required"
    assert _denial_to_status("unknown_action") == "unknown_action"
    assert _denial_to_status("mutation_fence") == "mutation_fence"
    assert _denial_to_status("tier_insufficient") == "tier_insufficient"
    assert _denial_to_status("anything_else") == "policy_denied"
