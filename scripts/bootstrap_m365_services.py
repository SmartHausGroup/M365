#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from typing import Any

from provisioning_api.m365_provision import provision_group_site
from provisioning_api.orchestrator import (
    CONFIG_PATH,
    ServiceConfig,
    _ensure_plan_and_buckets,
    _ensure_team_and_channels,
)
from smarthaus_common.errors import SmarthausError
from smarthaus_common.logging import configure_logging, get_logger
from smarthaus_graph.client import GraphClient

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
        service_config = ServiceConfig.from_dict(svc)
        key = service_config.key
        log.info("\n=== Provisioning service: %s (%s) ===", key, service_config.display_name)

        try:
            if _enabled():
                # Ensure group-connected site exists (and libraries) – use default doc library creation only
                provision_group_site(
                    display_name=service_config.display_name,
                    mail_nickname=service_config.mail_nickname,
                    libraries=["Documents"],
                    description=f"Service workspace for {service_config.display_name}",
                    wait_secs=60,
                )

            # Ensure Team + Channels
            team_id, channel_map = _ensure_team_and_channels(client, service_config)
            svc["team_id"] = team_id
            svc["channel_ids"] = channel_map

            # Ensure Planner Plan + Buckets
            plan_id, buckets = _ensure_plan_and_buckets(client, team_id, service_config.plan_title)
            svc["plan_id"] = plan_id
            # Buckets are standard; we don't persist here beyond plan

            log.info(
                "Provisioned: team_id=%s plan_id=%s channels=%d", team_id, plan_id, len(channel_map)
            )
        except SmarthausError as e:
            log.error("Service %s failed: %s", key, e)

    # Write back updated IDs
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    print(f"Updated {CONFIG_PATH} with IDs.")


if __name__ == "__main__":
    main()
