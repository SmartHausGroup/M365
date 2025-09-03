"""
TAI GitHub repository integration
- Build status notifications
- Research updates and collaboration
- TAI development workflow automation
"""

from __future__ import annotations

from typing import Any

from provisioning_api.storage import JsonStore

_store = JsonStore()


def record_event(event: dict[str, Any]) -> str:
    rec = _store.append("github_tai_events", event)
    return rec["id"]
