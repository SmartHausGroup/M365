"""Tests for B3 Mail reads coverage. plan:m365-cps-trkB-p3-mail-reads / L105"""

from __future__ import annotations

from m365_runtime.graph.registry import READ_ONLY_REGISTRY
from ucp_m365_pack.client import map_legacy_action_to_runtime


def test_b3_new_entries_registered() -> None:
    for action_id in ["graph.mail.list", "graph.mail.message_get", "graph.mail.attachments"]:
        assert action_id in READ_ONLY_REGISTRY
        spec = READ_ONLY_REGISTRY[action_id]
        assert spec.workload == "exchange"
        assert "Mail.Read" in spec.scopes
        assert "device_code" in spec.auth_modes


def test_b3_aliases_resolve() -> None:
    assert map_legacy_action_to_runtime("mail.list") == "graph.mail.list"
    assert map_legacy_action_to_runtime("mail.read") == "graph.mail.message_get"
    assert map_legacy_action_to_runtime("mail.attachments") == "graph.mail.attachments"
    assert map_legacy_action_to_runtime("mail.folders") == "graph.mail.health"
