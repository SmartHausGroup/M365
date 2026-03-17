from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os
import time

from smarthaus_common.errors import SmarthausError
from smarthaus_common.logging import get_logger
from smarthaus_graph.client import GraphClient

log = get_logger(__name__)


CONFIG_PATH = Path("config/services.json")
DEFAULT_BUCKETS = ["Backlog", "In Progress", "Code Review", "Done"]


@dataclass
class ServiceConfig:
    key: str
    display_name: str
    mail_nickname: str
    github_repo: str
    plan_title: str
    channels: list[str]
    team_id: str | None = None
    plan_id: str | None = None
    channel_ids: dict[str, str] | None = None

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "ServiceConfig":
        return ServiceConfig(
            key=d["key"],
            display_name=d["display_name"],
            mail_nickname=d["mail_nickname"],
            github_repo=d["github_repo"],
            plan_title=d["plan_title"],
            channels=list(d.get("channels", [])),
            team_id=(d.get("team_id") or "") or None,
            plan_id=(d.get("plan_id") or "") or None,
            channel_ids=d.get("channel_ids") or {},
        )


def _read_services() -> list[ServiceConfig]:
    if not CONFIG_PATH.exists():
        raise SmarthausError(f"Missing config file: {CONFIG_PATH}")
    data = json.loads(CONFIG_PATH.read_text())
    return [ServiceConfig.from_dict(x) for x in data.get("services", [])]


def _find_service_by_key_or_repo(project: str) -> ServiceConfig | None:
    services = _read_services()
    prj = project.lower()
    for s in services:
        if s.key.lower() == prj:
            return s
        if s.github_repo.lower().endswith(f"/{prj}"):
            return s
        if s.github_repo.lower() == prj:
            return s
    return None


def _env_enabled() -> bool:
    return os.getenv("ENABLE_M365_AUTOMATION", "false").lower() in ("1", "true", "yes")


def _ensure_team_and_channels(client: GraphClient, svc: ServiceConfig) -> tuple[str, dict[str, str]]:
    # Resolve group by mailNickname and ensure team exists; return teamId and channel name->id
    grp = client.find_group_by_mailnickname(svc.mail_nickname)
    if not grp or not grp.get("id"):
        raise SmarthausError(f"Group not found for mailNickname={svc.mail_nickname}. Provision first.")
    group_id = grp["id"]

    try:
        client.teamify_group(group_id)
    except Exception:
        pass

    # Wait for team provisioning to complete before listing/creating channels
    wait_total = int(os.getenv("TEAM_READY_WAIT_SECS", "300"))
    existing = []
    for _ in range(max(1, wait_total // 3)):
        try:
            existing = client.list_team_channels(group_id)
            if isinstance(existing, list):
                break
        except Exception:
            pass
        time.sleep(3)

    # Channels
    existing_names = {c.get("displayName", ""): c.get("id") for c in existing}
    # Create missing channels (skip General)
    for ch in svc.channels:
        if ch.lower() == "general":
            continue
        if ch in existing_names:
            continue
        try:
            created = client.create_team_channel(group_id, ch, description=f"Channel for {svc.display_name} - {ch}")
            existing_names[ch] = created.get("id")
        except Exception as e:
            log.warning("Failed to create channel %s (will retry on next run): %s", ch, e)
    return group_id, {k: v for k, v in existing_names.items() if v}


def _ensure_plan_and_buckets(client: GraphClient, group_id: str, plan_title: str) -> tuple[str | None, dict[str, str]]:
    # Find or create plan
    plan_id = None
    try:
        plans = client.list_group_plans(group_id)
    except Exception as e:
        log.warning("Planner list plans failed (permissions?). Skipping plan creation: %s", e)
        return None, {}
    for p in plans:
        if (p.get("title") or "").lower() == plan_title.lower():
            plan_id = p.get("id")
            break
    if not plan_id:
        try:
            plan = client.create_plan(group_id, plan_title)
            plan_id = plan.get("id")
        except Exception as e:
            log.warning("Planner create plan failed (permissions?). Skipping buckets: %s", e)
            return None, {}
    if not plan_id:
        raise SmarthausError("Unable to find or create planner plan")

    # Ensure buckets
    try:
        buckets = client.list_plan_buckets(plan_id)
    except Exception as e:
        log.warning("Planner list buckets failed (permissions?). Skipping buckets: %s", e)
        return plan_id, {}
    name_to_id = {b.get("name", ""): b.get("id") for b in buckets}
    if not name_to_id:
        # create in standard order with simple order hints
        for i, b in enumerate(DEFAULT_BUCKETS):
            if b in name_to_id:
                continue
            hint = " !" + ("!" * i)
            try:
                created = client.create_bucket(plan_id, b, order_hint=hint)
                name_to_id[b] = created.get("id")
            except Exception as e:
                log.warning("Planner create bucket '%s' failed: %s", b, e)
                continue
    return plan_id, {k: v for k, v in name_to_id.items() if v}


def _summarize_github_event(payload: dict) -> tuple[str, str | None]:
    # Returns (event_type, human_title)
    if "pull_request" in payload:
        pr = payload["pull_request"]
        action = payload.get("action", "")
        title = f"PR {action}: #{pr.get('number')} {pr.get('title')}"
        return "pull_request", title
    if "issue" in payload:
        issue = payload["issue"]
        action = payload.get("action", "")
        title = f"Issue {action}: #{issue.get('number')} {issue.get('title')}"
        return "issues", title
    if payload.get("ref") and payload.get("head_commit"):
        commit = payload.get("head_commit", {})
        msg = commit.get("message") or "Commit pushed"
        return "push", msg
    if payload.get("release"):
        rel = payload["release"]
        return "release", f"Release {payload.get('action')}: {rel.get('tag_name')}"
    if payload.get("milestone"):
        ms = payload["milestone"]
        return "milestone", f"Milestone {payload.get('action')}: {ms.get('title')}"
    return payload.get("action") or "event", None


def _build_reference_url(payload: dict) -> str | None:
    if "pull_request" in payload:
        return payload["pull_request"].get("html_url")
    if "issue" in payload:
        return payload["issue"].get("html_url")
    if payload.get("head_commit"):
        return payload.get("head_commit", {}).get("url")
    if payload.get("release"):
        return payload["release"].get("html_url")
    return None


def _bucket_for_event(event_type: str) -> str:
    table = {
        "pull_request": "Code Review",
        "issues": "Backlog",
        "release": "Done",
        "milestone": "Backlog",
        "push": "In Progress",
    }
    return table.get(event_type, "Backlog")


def handle_github_event(project: str, payload: dict) -> dict:
    """Create Teams notifications and Planner tasks for GitHub events.

    Controlled by env ENABLE_M365_AUTOMATION. When disabled, returns dry-run summary.
    """
    svc = _find_service_by_key_or_repo(project)
    if not svc:
        raise SmarthausError(f"Unknown service mapping for project={project}")

    event_type, title = _summarize_github_event(payload)
    ref_url = _build_reference_url(payload)
    repo = (payload.get("repository") or {}).get("full_name")

    summary = {
        "service": svc.key,
        "event_type": event_type,
        "title": title,
        "repo": repo,
        "ref_url": ref_url,
    }

    if not _env_enabled():
        return {"dry_run": True, "notified": False, "planner": False, "summary": summary}

    client = GraphClient()

    # Ensure Team + Channels and Planner Plan + Buckets
    team_id, channel_map = _ensure_team_and_channels(client, svc)
    plan_id, buckets = _ensure_plan_and_buckets(client, team_id, svc.plan_title)

    # Create Planner task for issue/pr/release; push -> just Teams notification
    planner_result: dict[str, Any] | None = None
    bucket_name = _bucket_for_event(event_type)
    bucket_id = buckets.get(bucket_name)
    if bucket_id and event_type in ("pull_request", "issues", "release", "milestone"):
        task_title = title or f"GitHub {event_type}"
        description = f"Auto-created from GitHub event for {repo}."
        planner_result = client.create_task(
            plan_id=plan_id,
            bucket_id=bucket_id,
            title=task_title,
            description=description,
            reference_url=ref_url,
        )

    # Teams message to General (or Code Review for PR)
    channel_name = "Code Review" if event_type == "pull_request" and "Code Review" in channel_map else "General"
    ch_id = channel_map.get(channel_name) or channel_map.get("General")
    html = f"<div><b>{svc.display_name}</b> • GitHub <i>{event_type}</i><br/><a href='{ref_url or '#'}'>{title or 'Update'}</a></div>"
    teams_result: dict[str, Any] | None = None
    if ch_id:
        try:
            teams_result = client.post_channel_message_html(team_id, ch_id, html)
        except Exception as e:
            log.warning("Failed to post Teams message: %s", e)

    return {
        "dry_run": False,
        "notified": bool(teams_result),
        "planner": bool(planner_result),
        "summary": summary,
        "plan_id": plan_id,
        "team_id": team_id,
        "bucket": bucket_name,
    }
