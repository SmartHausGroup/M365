"""Standalone M365 pack adapter for UCP-hosted service-mode execution."""

from __future__ import annotations

import os
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from smarthaus_mcp_sdk.contracts import (
    MCPEvent,
    MCPPackContractError,
    PackAdapter,
    PackContext,
)

_M365_TOOL_PREFIX = "m365_"

_RISK_TIERS: dict[str, str] = {
    "m365-administrator": "high",
    "website-manager": "medium",
    "hr-generalist": "critical",
    "outreach-coordinator": "high",
    "project-manager": "medium",
    "platform-manager": "medium",
    "teams-manager": "medium",
    "it-operations-manager": "high",
    "website-operations-specialist": "medium",
    "email-processing-agent": "medium",
    "calendar-management-agent": "low",
    "project-coordination-agent": "medium",
    "client-relationship-agent": "medium",
    "compliance-monitoring-agent": "critical",
    "recruitment-assistance-agent": "high",
    "financial-operations-agent": "critical",
    "knowledge-management-agent": "low",
    "security-operations": "high",
    "audit-operations": "high",
    "service-health": "low",
    "identity-security": "critical",
    "reports": "low",
    "device-management": "medium",
    "ai-engineer": "medium",
    "backend-architect": "medium",
    "devops-automator": "medium",
    "frontend-developer": "low",
    "mobile-app-builder": "low",
    "rapid-prototyper": "low",
    "test-writer-fixer": "low",
    "app-store-optimizer": "low",
    "content-creator": "low",
    "growth-hacker": "medium",
    "instagram-curator": "low",
    "reddit-community-builder": "low",
    "tiktok-strategist": "low",
    "twitter-engager": "low",
    "sprint-prioritizer": "low",
    "feedback-synthesizer": "low",
    "trend-researcher": "low",
    "experiment-tracker": "low",
    "project-shipper": "low",
    "studio-producer": "low",
    "analytics-reporter": "low",
    "finance-tracker": "high",
    "infrastructure-maintainer": "medium",
    "legal-compliance-checker": "high",
    "support-responder": "low",
    "api-tester": "low",
    "performance-benchmarker": "low",
    "test-results-analyzer": "low",
    "tool-evaluator": "low",
    "workflow-optimizer": "low",
    "brand-guardian": "low",
    "ui-designer": "low",
    "ux-researcher": "low",
    "visual-storyteller": "low",
    "whimsy-injector": "low",
}

_CONFIRMATION_REQUIRED_ACTIONS: set[str] = {
    "users.disable",
    "employee.offboard",
    "deployment.production",
    "dns.update",
    "backup.restore",
    "ssl.renew",
    "violation.report",
    "email.send_bulk",
    "ca.policy_create",
    "ca.policy_update",
    "ca.policy_delete",
    "security.alert_update",
    "devices.actions",
    "teams.archive",
    "teams.remove_member",
    "groups.remove_member",
}


def risk_tier_for_agent(agent: str) -> str:
    return _RISK_TIERS.get(agent, "medium")


def requires_confirmation(agent: str, action: str) -> bool:
    if action in _CONFIRMATION_REQUIRED_ACTIONS:
        return True
    return risk_tier_for_agent(agent) == "critical"


@dataclass
class M365PackAdapter(PackAdapter):
    _context: PackContext | None = None
    _events: list[MCPEvent] = field(default_factory=list)
    _blocked_count: int = 0
    _strict_mode: bool = False

    def __post_init__(self) -> None:
        raw = os.getenv("SMARTHAUS_M365_STRICT_MODE", "false").strip().lower()
        self._strict_mode = raw in ("1", "true", "yes", "on")

    @property
    def pack_id(self) -> str:
        return "m365_pack"

    def register(self, context: PackContext) -> None:
        self._context = context

    def handle_event(self, event: MCPEvent) -> None:
        if not event.tool.startswith(_M365_TOOL_PREFIX):
            return

        self._events.append(event)

        if event.direction != "in":
            return

        agent = (event.payload or {}).get("agent", "")
        if agent and self._strict_mode and agent not in _RISK_TIERS:
            self._blocked_count += 1
            raise MCPPackContractError(f"m365_pack rejected unknown agent '{agent}' in strict mode")

    def snapshot(self) -> dict[str, Any]:
        agent_counts: Counter[str] = Counter()
        action_counts: Counter[str] = Counter()
        tier_counts: Counter[str] = Counter()
        tool_counts: Counter[str] = Counter()
        outcome_counts: Counter[str] = Counter()

        for event in self._events:
            tool_counts[event.tool] += 1
            outcome_counts[event.status] += 1
            agent = (event.payload or {}).get("agent", "unknown")
            action = (event.payload or {}).get("action", "unknown")
            agent_counts[agent] += 1
            action_counts[f"{agent}:{action}"] += 1
            tier_counts[risk_tier_for_agent(agent)] += 1

        return {
            "pack_id": self.pack_id,
            "server_id": self._context.server_id if self._context else "",
            "event_count": len(self._events),
            "blocked_count": self._blocked_count,
            "strict_mode": self._strict_mode,
            "agent_counts": dict(agent_counts),
            "action_counts": dict(action_counts),
            "tier_counts": dict(tier_counts),
            "tool_counts": dict(tool_counts),
            "outcome_counts": dict(outcome_counts),
        }


def create_pack_adapter() -> M365PackAdapter:
    return M365PackAdapter()
