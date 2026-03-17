"""UCP Permission Tier Enforcer.

Validates user actions against their assigned permission tier before execution.
This is the governance layer that sits between the MCP tools and the Graph API —
the Azure AD app has all permissions (the pipe), this module controls what each
user is actually allowed to invoke (the governance).

Architecture:
  1. Tenant config maps users → tiers (e.g., phil@smarthausgroup.com → global_admin)
  2. permission_tiers.yaml defines what each tier can and cannot do
  3. This module checks both before any action reaches the Graph API

Usage:
  from smarthaus_common.permission_enforcer import check_user_permission

  allowed, reason = check_user_permission(user_email, action)
  if not allowed:
      return {"error": reason, "status": "permission_denied"}
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Tier definitions loader (from permission_tiers.yaml)
# ---------------------------------------------------------------------------

_TIERS: dict[str, Any] | None = None
_TIERS_PATH: str | None = None
_TIERS_MTIME: float = 0.0


def _find_tiers_yaml() -> str | None:
    """Locate permission_tiers.yaml using standard search paths."""
    search_paths = [
        os.getenv("M365_PERMISSION_TIERS_PATH", ""),
        os.path.join(os.getenv("M365_REPO_ROOT", ""), "registry", "permission_tiers.yaml"),
    ]

    # Relative from this file: smarthaus_common/ -> src/ -> M365/
    this_dir = Path(__file__).parent
    search_paths.append(
        str(this_dir / ".." / ".." / "registry" / "permission_tiers.yaml")
    )
    # Also check from SMARTHAUS_MCPSERVER_core layout
    search_paths.append(
        str(this_dir / ".." / ".." / ".." / "M365" / "registry" / "permission_tiers.yaml")
    )

    for path in search_paths:
        path = os.path.expanduser(path.strip())
        if path and os.path.isfile(path):
            return os.path.normpath(path)
    return None


def _load_tiers() -> dict[str, Any]:
    """Load tier definitions with hot-reload on file change."""
    global _TIERS, _TIERS_PATH, _TIERS_MTIME

    # Hot-reload check
    if _TIERS is not None and _TIERS_PATH is not None:
        try:
            current_mtime = os.path.getmtime(_TIERS_PATH)
            if current_mtime == _TIERS_MTIME:
                return _TIERS
        except OSError:
            pass

    path = _find_tiers_yaml()
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        _TIERS = data.get("tiers", {})
        _TIERS_PATH = path
        _TIERS_MTIME = os.path.getmtime(path)
        return _TIERS

    # No tiers file found — permissive fallback (everything allowed)
    _TIERS = {}
    _TIERS_PATH = None
    _TIERS_MTIME = 0.0
    return _TIERS


def get_tier_definition(tier_name: str) -> dict[str, Any] | None:
    """Return the full tier definition dict, or None if not found."""
    tiers = _load_tiers()
    return tiers.get(tier_name)


# ---------------------------------------------------------------------------
# Action matching helpers
# ---------------------------------------------------------------------------


def _action_matches_pattern(action: str, pattern: str) -> bool:
    """Check if an action matches a pattern.

    Patterns can be:
      - Exact: "mail.send"
      - Domain wildcard: "users.*" (matches any action in the users domain)
      - Wildcard prefix: "*.create" (matches any create action)
      - Full domain: "mail" (matches all mail.* actions)
    """
    if action == pattern:
        return True

    # Wildcard patterns like "users.*" or "*.create"
    if "*" in pattern:
        return fnmatch.fnmatch(action, pattern)

    # Domain-only pattern: "mail" matches "mail.list", "mail.send", etc.
    if "." not in pattern and action.startswith(f"{pattern}."):
        return True

    return False


def _is_action_in_list(action: str, patterns: list[str]) -> bool:
    """Check if an action matches any pattern in a list."""
    for pattern in patterns:
        if _action_matches_pattern(action, pattern):
            return True
    return False


# ---------------------------------------------------------------------------
# Core enforcement
# ---------------------------------------------------------------------------


def check_user_permission(
    user_email: str,
    action: str,
    tenant_config: Any | None = None,
) -> tuple[bool, str]:
    """Check whether a user is allowed to perform an action based on their tier.

    Args:
        user_email: The user's email address (used for tier lookup).
        action: The action being attempted (e.g., "mail.send", "users.create").
        tenant_config: Optional TenantConfig instance. If None, loads from env.

    Returns:
        (True, "") if allowed.
        (False, reason) if denied, with a human-readable reason string.
    """
    # Load tier definitions
    tiers = _load_tiers()
    if not tiers:
        # No tier file — permissive mode (governance not configured)
        return True, ""

    # If no user identity is available, pass through permissively.
    # Tier enforcement requires a known identity — without one, we can't
    # determine what to allow or deny. This is expected during early setup
    # or when the session doesn't carry user context yet.
    if not user_email:
        return True, ""

    # Resolve user's tier from tenant config
    if tenant_config is None:
        try:
            from smarthaus_common.tenant_config import get_tenant_config
            tenant_config = get_tenant_config()
        except Exception:
            # Can't load tenant config — permissive fallback
            return True, ""

    tier_name = tenant_config.permission_tiers.get_user_tier(user_email)
    tier_def = get_tier_definition(tier_name)

    if tier_def is None:
        return False, f"unknown_tier:{tier_name} assigned to {user_email}"

    # Check blocked_actions first (explicit deny takes precedence)
    blocked = tier_def.get("blocked_actions", [])
    if _is_action_in_list(action, blocked):
        return False, (
            f"tier_blocked:{tier_name}/{action} — "
            f"{tier_def.get('name', tier_name)} does not have permission for '{action}'"
        )

    # Check allowed_domains (explicit allow list)
    allowed = tier_def.get("allowed_domains", [])
    if allowed and not _is_action_in_list(action, allowed):
        return False, (
            f"tier_not_allowed:{tier_name}/{action} — "
            f"'{action}' is not in the allowed actions for {tier_def.get('name', tier_name)}"
        )

    return True, ""


def get_confirmation_override(
    user_email: str,
    action: str,
    tenant_config: Any | None = None,
) -> str | None:
    """Check if a tier has a confirmation override for this action.

    Returns:
        "always" if the tier requires confirmation for this action.
        None if no override (use default confirmation rules).
    """
    tiers = _load_tiers()
    if not tiers:
        return None

    if tenant_config is None:
        try:
            from smarthaus_common.tenant_config import get_tenant_config
            tenant_config = get_tenant_config()
        except Exception:
            return None

    tier_name = tenant_config.permission_tiers.get_user_tier(user_email)
    tier_def = get_tier_definition(tier_name)

    if tier_def is None:
        return None

    overrides = tier_def.get("confirmation_overrides", {})
    return overrides.get(action)


def get_user_tier_info(
    user_email: str,
    tenant_config: Any | None = None,
) -> dict[str, Any]:
    """Return summary info about a user's tier for display/audit.

    Returns a dict with tier_name, display_name, risk_tier, and description.
    """
    if tenant_config is None:
        try:
            from smarthaus_common.tenant_config import get_tenant_config
            tenant_config = get_tenant_config()
        except Exception:
            return {"tier_name": "unknown", "error": "tenant_config_unavailable"}

    tier_name = tenant_config.permission_tiers.get_user_tier(user_email)
    tier_def = get_tier_definition(tier_name)

    if tier_def is None:
        return {"tier_name": tier_name, "error": f"tier_definition_not_found:{tier_name}"}

    return {
        "tier_name": tier_name,
        "display_name": tier_def.get("name", tier_name),
        "risk_tier": tier_def.get("risk_tier", "unknown"),
        "description": tier_def.get("description", ""),
        "user_email": user_email,
    }
