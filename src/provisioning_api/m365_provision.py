from __future__ import annotations

import os
import time
from collections.abc import Sequence

from smarthaus_common.errors import SmarthausError
from smarthaus_common.logging import get_logger
from smarthaus_graph.client import GraphClient

log = get_logger(__name__)


def _hostname() -> str:
    return os.getenv("SP_HOSTNAME", "smarthausgroup.sharepoint.com")


def provision_group_site(
    display_name: str,
    mail_nickname: str,
    libraries: Sequence[str],
    description: str | None = None,
    wait_secs: int = 60,
) -> dict:
    """Create (or ensure) a group-connected Team site with given libraries.

    Returns dict with site_id, site_url, created flags.
    Requires app permissions: Group.ReadWrite.All and Sites.ReadWrite.All (or FullControl).
    """
    client = GraphClient()
    created_group = False

    grp = client.find_group_by_mailnickname(mail_nickname)
    if not grp:
        log.info("Creating M365 group %s (%s)", display_name, mail_nickname)
        grp = client.create_group(display_name, mail_nickname, description)
        created_group = True

    hostname = _hostname()
    site_path = mail_nickname

    # The group-connected SharePoint site may take a short time to provision.
    site = None
    for attempt in range(max(1, wait_secs // 3)):
        try:
            site = client.get_site_by_path(hostname, site_path)
            if site and site.get("id"):
                break
        except SmarthausError as e:
            log.warning("Site not ready yet (%s): %s", attempt, e)
        time.sleep(3)

    if not site or not site.get("id"):
        raise SmarthausError("Site provisioning detection failed; try again shortly.")

    site_id = site["id"]
    web_url = site.get("webUrl", f"https://{hostname}/sites/{site_path}")

    # Ensure libraries
    existing = client.list_site_lists(site_id)
    existing_names = {lst.get("displayName", "") for lst in existing}
    created_libs: list[str] = []
    for lib in libraries:
        if lib in existing_names:
            continue
        try:
            client.create_document_library(site_id, lib)
            created_libs.append(lib)
        except SmarthausError as e:
            log.error("Failed to create library %s: %s", lib, e)

    return {
        "site_id": site_id,
        "site_url": web_url,
        "group_created": created_group,
        "libraries_created": created_libs,
    }


def provision_teams_workspace(
    mail_nickname: str, channels: Sequence[str], wait_secs: int = 90
) -> dict:
    """Ensure a Teams workspace exists for the M365 group and add channels.

    Requires application permissions: Team.ReadWrite.All, Channel.ReadWrite.All.
    """
    client = GraphClient()
    grp = client.find_group_by_mailnickname(mail_nickname)
    if not grp:
        raise SmarthausError(f"Group '{mail_nickname}' not found; create site/group first.")

    group_id = grp.get("id")
    if not group_id:
        raise SmarthausError("Group missing id")

    try:
        client.teamify_group(group_id)
    except SmarthausError as e:
        # Already teamified or transient; proceed to check readiness
        log.warning("Teamify warning: %s", e)

    team = None
    for _ in range(max(1, wait_secs // 3)):
        try:
            team = client.get_team(group_id)
            if team and team.get("id"):
                break
        except SmarthausError:
            pass
        time.sleep(3)

    if not team or not team.get("id"):
        raise SmarthausError("Team provisioning detection failed; try again shortly.")

    existing = client.list_team_channels(group_id)
    existing_names = {c.get("displayName", "") for c in existing}
    created_channels: list[str] = []
    for ch in channels:
        if ch.lower() == "general":
            continue
        if ch in existing_names:
            continue
        try:
            client.create_team_channel(group_id, ch, description=f"Channel for {ch}")
            created_channels.append(ch)
        except SmarthausError as e:
            log.error("Failed to create channel %s: %s", ch, e)

    team_web = team.get("webUrl") or team.get("internalId") or group_id
    return {"team_id": group_id, "team_url": team_web, "channels_created": created_channels}
