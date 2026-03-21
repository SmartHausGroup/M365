from __future__ import annotations

from collections.abc import Iterator

import pytest
from smarthaus_common.approval_risk import (
    reload_approval_risk_registry,
    resolve_action_approval_risk,
)


@pytest.fixture(autouse=True)
def _reset_registries() -> Iterator[None]:
    reload_approval_risk_registry()
    yield
    reload_approval_risk_registry()


def test_sites_provision_is_high_impact_and_requires_approval() -> None:
    resolution = resolve_action_approval_risk("m365-administrator", "sites.provision", {})

    assert resolution.risk_class == "high"
    assert resolution.approval_profile == "high-impact"
    assert resolution.approval_required is True
    assert resolution.approvers == ("global_admin",)


def test_groups_list_is_low_risk_without_approval() -> None:
    resolution = resolve_action_approval_risk("m365-administrator", "groups.list", {})

    assert resolution.risk_class == "low"
    assert resolution.approval_profile == "low-observe-create"
    assert resolution.approval_required is False


def test_email_send_bulk_only_requires_approval_above_threshold() -> None:
    blocked = resolve_action_approval_risk(
        "outreach-coordinator",
        "email.send_bulk",
        {"recipients_count": 250},
    )
    allowed = resolve_action_approval_risk(
        "outreach-coordinator",
        "email.send_bulk",
        {"recipients_count": 25},
    )

    assert blocked.approval_required is True
    assert allowed.approval_required is False
    assert blocked.approvers == ("marketing-lead",)


def test_security_domain_default_is_critical_and_approval_bearing() -> None:
    resolution = resolve_action_approval_risk("it-operations-manager", "security.alert.update", {})

    assert resolution.executor_domain == "security"
    assert resolution.risk_class == "critical"
    assert resolution.approval_profile == "critical-regulated"
    assert resolution.approval_required is True


def test_persona_profile_fallback_uses_authoritative_persona_map() -> None:
    resolution = resolve_action_approval_risk("website-manager", "content.create", {})

    assert resolution.executor_domain == "publishing"
    assert resolution.approval_profile == "medium-operational"
    assert resolution.risk_class == "medium"
    assert resolution.approval_required is False
