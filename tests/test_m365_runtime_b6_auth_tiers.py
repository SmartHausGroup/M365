"""Tests for B6 Auth-mode tier system. plan:m365-cps-trkB-p6-auth-mode-tiers / L108"""

from __future__ import annotations

from m365_runtime.graph.registry import (
    READ_ONLY_REGISTRY,
    ALLOWED_TIERS,
    admit,
    tier_at_or_above,
)


def test_b6_tier_default_read_only() -> None:
    """L108.L_TIER_DEFAULT_READ_ONLY — every existing ActionSpec defaults to read-only."""
    for action_id, spec in READ_ONLY_REGISTRY.items():
        assert spec.min_tier == "read-only", f"{action_id} has min_tier={spec.min_tier}"


def test_b6_allowed_tiers() -> None:
    """L108 — three tiers exactly: read-only, standard, admin."""
    assert ALLOWED_TIERS == frozenset({"read-only", "standard", "admin"})


def test_b6_tier_ordering_transitive() -> None:
    """L108.L_TIER_ORDERING_TRANSITIVE."""
    assert tier_at_or_above("admin", "read-only")
    assert tier_at_or_above("admin", "standard")
    assert tier_at_or_above("admin", "admin")
    assert tier_at_or_above("standard", "read-only")
    assert tier_at_or_above("standard", "standard")
    assert tier_at_or_above("read-only", "read-only")
    assert not tier_at_or_above("read-only", "standard")
    assert not tier_at_or_above("read-only", "admin")
    assert not tier_at_or_above("standard", "admin")


def test_b6_tier_at_or_above_rejects_unknown() -> None:
    """Unknown tier strings fail closed."""
    assert not tier_at_or_above("unknown", "read-only")
    assert not tier_at_or_above("read-only", "unknown")
    assert not tier_at_or_above(None, "read-only")
    assert not tier_at_or_above("read-only", None)


def test_b6_admit_default_tier_admits_read_only_action() -> None:
    """L108.L_ADMIT_REJECTS_INSUFFICIENT — read-only tier admits read-only action."""
    decision, reason = admit(
        "graph.me",
        frozenset({"User.Read"}),
        "device_code",
        current_tier="read-only",
    )
    assert decision == "admit"
    assert reason == "ok"


def test_b6_admit_no_tier_param_keeps_legacy_behavior() -> None:
    """No current_tier argument keeps legacy behavior (default read-only)."""
    decision, reason = admit("graph.me", frozenset({"User.Read"}), "device_code")
    assert decision == "admit"
    assert reason == "ok"


def test_b6_invalid_min_tier_raises() -> None:
    """ActionSpec rejects invalid min_tier strings."""
    import pytest
    from m365_runtime.graph.registry import ActionRegistryError, ActionSpec

    with pytest.raises(ActionRegistryError):
        ActionSpec(
            "graph.bogus",
            "test",
            "/test",
            frozenset({"device_code"}),
            frozenset({"User.Read"}),
            "low",
            "read",
            min_tier="superuser",
        )
