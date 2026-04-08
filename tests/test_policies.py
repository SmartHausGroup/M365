import json
import re
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml
from ops_adapter.personas import load_persona_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OPA_PATH = PROJECT_ROOT / "bin" / "opa"
POLICIES_PATH = PROJECT_ROOT / "policies"
REGISTRY_PATH = PROJECT_ROOT / "registry" / "agents.yaml"
ACTIONS_PATH = PROJECT_ROOT / "src" / "ops_adapter" / "actions.py"
UNSUPPORTED_PATTERN = re.compile(
    r'unsupported_m365_only_action\((?:.|\n)*?,\s*correlation_id,\s*"([a-z0-9_.-]+)"\s*\)',
    re.MULTILINE,
)


def opa_eval_query(query: str, input_obj: dict[str, Any] | None = None) -> Any:
    cmd = [str(OPA_PATH), "eval", "-f", "json", "-d", str(POLICIES_PATH), query]
    payload = None
    if input_obj is not None:
        cmd.append("--stdin-input")
        payload = json.dumps({"input": input_obj}).encode("utf-8")

    proc = subprocess.run(
        cmd,
        input=payload,
        capture_output=True,
        check=True,
        cwd=PROJECT_ROOT,
    )
    out = json.loads(proc.stdout.decode("utf-8"))
    return out["result"][0]["expressions"][0]["value"]


def opa_eval(input_obj: dict[str, Any]) -> dict[str, Any]:
    return opa_eval_query("data.ops.decision", input_obj)


def _unsupported_aliases() -> set[str]:
    text = ACTIONS_PATH.read_text(encoding="utf-8")
    return set(UNSUPPORTED_PATTERN.findall(text))


def _runtime_backed_allow_map() -> dict[str, set[str]]:
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    personas = load_persona_registry(registry)
    unsupported = _unsupported_aliases()
    allow_map: dict[str, set[str]] = {}
    for agent_id, persona in personas.items():
        if persona.get("status") != "active":
            continue
        supported = {
            str(action)
            for action in (persona.get("allowed_actions") or [])
            if str(action) not in unsupported
        }
        if supported:
            allow_map[agent_id] = supported
    return allow_map


def _runtime_backed_mandatory_approvals() -> dict[str, set[str]]:
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    allow_map = _runtime_backed_allow_map()
    mandatory: dict[str, set[str]] = {}
    for agent_id, agent in (registry.get("agents") or {}).items():
        supported = allow_map.get(str(agent_id), set())
        approvals = {
            str(rule.get("action"))
            for rule in (agent.get("approval_rules") or [])
            if str(rule.get("action")) in supported and not str(rule.get("condition") or "").strip()
        }
        if approvals:
            mandatory[str(agent_id)] = approvals
    return mandatory


def _normalize_policy_set_map(payload: dict[str, Any]) -> dict[str, set[str]]:
    normalized: dict[str, set[str]] = {}
    for agent_id, actions in payload.items():
        normalized[str(agent_id)] = {str(action) for action in actions}
    return normalized


def test_ops_allowed_actions_track_runtime_backed_active_surface() -> None:
    policy_allow_map = opa_eval_query("data.ops.allowed_actions")
    assert _normalize_policy_set_map(policy_allow_map) == _runtime_backed_allow_map()


def test_ops_mandatory_approvals_track_runtime_rules() -> None:
    policy_approvals = opa_eval_query("data.ops.mandatory_approvals")
    assert _normalize_policy_set_map(policy_approvals) == _runtime_backed_mandatory_approvals()


def test_website_manager_sites_get_allowed_without_approval() -> None:
    res = opa_eval(
        {
            "agent": "website-manager",
            "action": "sites.get",
            "data": {"siteId": "site-123"},
            "rate_allowed": True,
        }
    )
    assert res["allow"] is True
    assert res.get("approval_required") is False


def test_website_deployment_preview_is_denied_as_unsupported() -> None:
    res = opa_eval(
        {
            "agent": "website-manager",
            "action": "deployment.preview",
            "data": {},
            "rate_allowed": True,
        }
    )
    assert res["allow"] is False
    assert res["reason"] == "action_not_allowed"


def test_m365_users_create_requires_approval() -> None:
    res = opa_eval(
        {
            "agent": "m365-administrator",
            "action": "users.create",
            "data": {"userPrincipalName": "new.user@example.com"},
            "rate_allowed": True,
        }
    )
    assert res["allow"] is True
    assert res.get("approval_required") is True


def test_hr_offboard_requires_approval() -> None:
    res = opa_eval(
        {
            "agent": "hr-generalist",
            "action": "employee.offboard",
            "data": {"userPrincipalName": "x@y"},
            "rate_allowed": True,
        }
    )
    assert res["allow"] is True
    assert res.get("approval_required") is True


def test_project_coordination_create_plan_allowed_without_approval() -> None:
    res = opa_eval(
        {
            "agent": "project-coordination-agent",
            "action": "create_plan",
            "data": {"groupId": "group-123", "title": "Roadmap"},
            "rate_allowed": True,
        }
    )
    assert res["allow"] is True
    assert res.get("approval_required") is False


@pytest.mark.parametrize(
    ("agent", "action", "data"),
    [
        ("outreach-coordinator", "email.send_bulk", {"recipients_count": 250}),
        ("calendar-management-agent", "meeting.organize", {"attendees_count": 11}),
        ("calendar-management-agent", "meeting.organize", {"external_attendees": 1}),
        ("email-processing-agent", "email.respond", {"priority": "high"}),
        ("project-coordination-agent", "task.assign", {"priority": "critical"}),
        ("project-shipper", "task.assign", {"estimated_hours": 41}),
        ("support-responder", "mail.send", {"contains_sensitive_info": True}),
    ],
)
def test_conditional_policy_approvals(agent: str, action: str, data: dict[str, Any]) -> None:
    res = opa_eval(
        {
            "agent": agent,
            "action": action,
            "data": data,
            "rate_allowed": True,
        }
    )
    assert res["allow"] is True
    assert res.get("approval_required") is True
