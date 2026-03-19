#!/usr/bin/env python3
"""
Build full capability_registry.yaml from M365_CAPABILITIES_UNIVERSE.md (MA master calculus).
Keeps existing implemented entries; adds all universe actions as planned with domain/mutating.
Run from repo root: python scripts/ci/build_capability_registry.py
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_PATH = REPO_ROOT / "docs" / "contracts" / "M365_CAPABILITIES_UNIVERSE.md"
REGISTRY_PATH = REPO_ROOT / "registry" / "capability_registry.yaml"

# Section header -> domain (registry value)
SECTION_TO_DOMAIN = {
    "Identity & directory": "identity",
    "Mail (Outlook)": "mail",
    "Calendar": "calendar",
    "Contacts (Outlook)": "contacts",
    "Drive & files (OneDrive / SharePoint libraries)": "files",
    "SharePoint (sites, lists, pages)": "sharepoint",
    "Teams": "teams",
    "Planner & tasks": "planner",
    "OneNote": "onenote",
    "To Do / tasks (Microsoft To Do)": "todo",
    "Subscriptions & webhooks": "subscriptions",
    "Search": "search",
    "Reports & analytics": "reports",
    "Access reviews & governance": "access_reviews",
    "Security & compliance (where exposed via Graph)": "security",
    "Provisioning / composite (our conveniences)": "provisioning",
}

# Action name prefix/suffix -> mutating
MUTATING_VERBS = (
    "create",
    "update",
    "delete",
    "add",
    "remove",
    "send",
    "assign",
    "set",
    "copy",
    "move",
    "archive",
    "unarchive",
    "install",
    "uninstall",
    "upgrade",
    "restore",
    "publish",
    "reply",
    "cancel",
    "accept",
    "decline",
    "tentatively_accept",
    "revoke",
    "follow",
    "unfollow",
    "check_out",
    "check_in",
    "complete",
    "record",
    "provision",
    "offboard",
)


def is_mutating(action: str) -> bool:
    for verb in MUTATING_VERBS:
        if action.startswith(verb + "_") or action == verb or action.endswith("_" + verb):
            return True
    return False


def action_to_resource(action: str, domain: str) -> str:
    """Infer Graph resource from action name and domain."""
    if "user" in action and domain == "identity":
        return "user"
    if "group" in action and domain == "identity":
        return "group"
    if "device" in action:
        return "device"
    if "application" in action:
        return "application"
    if "service_principal" in action:
        return "servicePrincipal"
    if "directory_role" in action:
        return "directoryRole"
    if "administrative_unit" in action:
        return "administrativeUnit"
    if "contact" in action and domain == "identity":
        return "orgContact"
    if domain == "mail":
        if "folder" in action:
            return "mailFolder"
        if "attachment" in action:
            return "attachment"
        if "mailbox" in action:
            return "mailboxSettings"
        return "message"
    if domain == "calendar":
        if "event" in action:
            return "event"
        if "group" in action:
            return "calendarGroup"
        if "schedule" in action:
            return "schedule"
        return "calendar"
    if domain == "contacts":
        return "contactFolder" if "folder" in action else "contact"
    if domain == "files":
        return (
            "driveItem"
            if "drive_item" in action or "file" in action or "folder" in action
            else "drive"
        )
    if domain == "sharepoint":
        if "site" in action and "page" not in action and "list" not in action:
            return "site"
        if "list_item" in action or "list_item" in action:
            return "listItem"
        if "list" in action and "list_item" not in action:
            return "list"
        if "page" in action:
            return "sitePage"
        return "site"
    if domain == "teams":
        if (
            "channel" in action
            and "message" not in action
            and "tab" not in action
            and "member" not in action
        ):
            return "channel"
        if "channel_message" in action or "channel_message" in action:
            return "chatMessage"
        if "tab" in action:
            return "teamsTab"
        if "chat" in action and "message" not in action:
            return "chat"
        if "member" in action or "owner" in action:
            return "teamMember"
        if "app" in action:
            return "teamsAppInstallation"
        return "team"
    if domain == "planner":
        if "task" in action:
            return "plannerTask"
        if "bucket" in action:
            return "plannerBucket"
        return "plan"
    if domain == "onenote":
        if "section" in action:
            return "section"
        if "page" in action:
            return "page"
        return "notebook"
    if domain == "todo":
        return "taskList" if "list" in action else "task"
    if domain == "subscriptions":
        return "subscription"
    if domain == "search":
        return "search"
    if domain == "reports":
        return "report"
    if domain == "access_reviews":
        return "accessReview"
    if domain == "security":
        return "secureScore" if "score" in action else "riskDetection"
    if domain == "provisioning":
        return "composite"
    return "unknown"


def parse_universe(path: Path) -> list[tuple[str, str]]:
    """Return [(action, domain), ...] from universe markdown."""
    text = path.read_text()
    lines = text.splitlines()
    current_domain = "identity"
    out = []
    for line in lines:
        if line.startswith("## "):
            section = line[3:].strip()
            current_domain = SECTION_TO_DOMAIN.get(section, "other")
            continue
        m = re.match(r"^\- ([a-z][a-z0-9_]+)$", line.strip())
        if m:
            out.append((m.group(1), current_domain))
    return out


def main() -> None:
    universe_actions = parse_universe(UNIVERSE_PATH)
    # Load existing registry to preserve implemented + result_shape_keys
    import yaml

    existing = yaml.safe_load(REGISTRY_PATH.read_text())

    actions = []
    seen = set()
    # First: all existing (to keep order and implemented status)
    for a in existing["actions"]:
        actions.append(a)
        seen.add(a["action"])
    # Then: any from universe not yet in registry
    for action, domain in universe_actions:
        if action in seen:
            continue
        seen.add(action)
        entry = {
            "action": action,
            "resource": action_to_resource(action, domain),
            "domain": domain,
            "required_permissions": ["See permissions reference"],
            "mutating": is_mutating(action),
            "status": "planned",
        }
        actions.append(entry)

    out = {
        "schema_version": "1.0",
        "source": [
            "docs/contracts/M365_CAPABILITIES_UNIVERSE.md",
            "docs/contracts/caio-m365/ACTION_SPECIFICATION.md",
            "docs/contracts/M365_MASTER_CALCULUS_FULL.md",
        ],
        "actions": actions,
    }
    REGISTRY_PATH.write_text(
        "# M365 Capability Registry — full O (master calculus)\n"
        "# Generated from M365_CAPABILITIES_UNIVERSE.md. Do not edit by hand; run scripts/ci/build_capability_registry.py\n"
        "# Verification: scripts/ci/verify_capability_registry.py\n\n"
        + yaml.dump(out, default_flow_style=False, sort_keys=False, allow_unicode=True)
    )
    print("Wrote", REGISTRY_PATH, "with", len(actions), "actions.")


if __name__ == "__main__":
    main()
