#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from provisioning_api.orchestrator import (
    CONFIG_PATH,
    _ensure_plan_and_buckets,
    _ensure_team_and_channels,
)
from smarthaus_common.errors import SmarthausError
from smarthaus_common.logging import configure_logging, get_logger
from smarthaus_graph.client import GraphClient
from provisioning_api.m365_provision import provision_group_site


log = get_logger(__name__)
configure_logging()


def _enabled() -> bool:
    return os.getenv("ALLOW_M365_MUTATIONS", "false").lower() in ("1", "true", "yes")


def main() -> None:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Config file not found: {CONFIG_PATH}")

    config = json.loads(CONFIG_PATH.read_text())
    services: list[dict[str, Any]] = config.get("services", [])
    client = GraphClient()
    if not _enabled():
        log.warning("ALLOW_M365_MUTATIONS not enabled. Running in dry-run mode.")

    for svc in services:
        key = svc.get("key")
        display = svc.get("display_name")
        nickname = svc.get("mail_nickname")
        channels = svc.get("channels", [])
        plan_title = svc.get("plan_title")
        log.info("\n=== Provisioning service: %s (%s) ===", key, display)

        try:
            if _enabled():
                # Ensure group-connected site exists (and libraries) – use default doc library creation only
                provision_group_site(
                    display_name=display,
                    mail_nickname=nickname,
                    libraries=["Documents"],
                    description=f"Service workspace for {display}",
                    wait_secs=60,
                )

            # Ensure Team + Channels
            team_id, channel_map = _ensure_team_and_channels(client, type("S", (), {
                "display_name": display,
                "mail_nickname": nickname,
                "channels": channels,
            }))
            svc["team_id"] = team_id
            svc["channel_ids"] = channel_map

            # Ensure Planner Plan + Buckets
            plan_id, buckets = _ensure_plan_and_buckets(client, team_id, plan_title)
            svc["plan_id"] = plan_id
            # Buckets are standard; we don't persist here beyond plan

            log.info("Provisioned: team_id=%s plan_id=%s channels=%d", team_id, plan_id, len(channel_map))
        except SmarthausError as e:
            log.error("Service %s failed: %s", key, e)

    # Write back updated IDs
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    print(f"Updated {CONFIG_PATH} with IDs.")


if __name__ == "__main__":
    main()

