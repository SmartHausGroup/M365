"""Token-vs-registry intersection for the M365 runtime.

plan:m365-cps-trkA-p3-preflight-intersection:T2
Lemma: L102_m365_cps_preflight_intersection_v1
Notebook: notebooks/m365/INV-M365-CPS-A3-preflight-intersection-v1.ipynb

Given the current session's auth_mode and granted_scopes, partition the
READ_ONLY_REGISTRY into three disjoint, complete buckets:

- invokable: session can call this action right now.
- blocked_by_auth_mode: action exists but the session's auth_mode is wrong.
- blocked_by_scopes: action and auth_mode match but session scopes are insufficient.

Pure function. No I/O, no Graph call, no state change.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .registry import READ_ONLY_REGISTRY


def compute_intersection(
    auth_mode: str | None,
    granted_scopes: Iterable[str] | None,
) -> dict[str, Any]:
    """Partition READ_ONLY_REGISTRY against the session's auth state.

    Args:
        auth_mode: the session's current auth mode, e.g. "device_code",
                   "auth_code_pkce", "app_only_secret", "app_only_certificate",
                   or None when no session is active.
        granted_scopes: the session's granted Graph scopes.

    Returns:
        dict with keys:
            invokable:            sorted list of action_ids the session can call
            blocked_by_auth_mode: sorted list whose registry entry excludes the
                                  current auth mode
            blocked_by_scopes:    sorted list where auth_mode matches but the
                                  registry entry's required scopes are not all
                                  granted
            session:              echoed {auth_mode, granted_scopes}
            registry_size:        len(READ_ONLY_REGISTRY)
    """
    granted: frozenset[str] = frozenset(granted_scopes or [])
    invokable: list[str] = []
    blocked_by_auth_mode: list[str] = []
    blocked_by_scopes: list[str] = []
    for action_id, spec in READ_ONLY_REGISTRY.items():
        if auth_mode is None or auth_mode not in spec.auth_modes:
            blocked_by_auth_mode.append(action_id)
        elif not spec.scopes.issubset(granted):
            blocked_by_scopes.append(action_id)
        else:
            invokable.append(action_id)
    return {
        "invokable": sorted(invokable),
        "blocked_by_auth_mode": sorted(blocked_by_auth_mode),
        "blocked_by_scopes": sorted(blocked_by_scopes),
        "session": {
            "auth_mode": auth_mode,
            "granted_scopes": sorted(granted),
        },
        "registry_size": len(READ_ONLY_REGISTRY),
    }
