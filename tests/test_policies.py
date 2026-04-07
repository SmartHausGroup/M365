import json
import os
import subprocess
from typing import Any


def opa_eval(input_obj: dict[str, Any]) -> dict[str, Any]:
    # Use the bin/opa wrapper from the project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    opa_path = os.path.join(project_root, "bin", "opa")
    policies_path = os.path.join(project_root, "policies")

    proc = subprocess.run(
        [opa_path, "eval", "-f", "json", "-d", policies_path, "data.ops.decision", "--stdin-input"],
        input=json.dumps({"input": input_obj}).encode("utf-8"),
        capture_output=True,
        check=True,
        cwd=project_root,
    )
    out = json.loads(proc.stdout.decode("utf-8"))
    # result[0].expressions[0].value
    return out["result"][0]["expressions"][0]["value"]


def test_m365_users_read_allowed() -> None:
    res = opa_eval(
        {
            "agent": "m365-administrator",
            "action": "users.read",
            "data": {},
            "rate_allowed": True,
        }
    )
    assert res["allow"] is True
    assert res.get("approval_required") is False


def test_website_prod_requires_approval() -> None:
    res = opa_eval(
        {
            "agent": "website-manager",
            "action": "deployment.production",
            "data": {"tests": {"passing": True}, "lighthouse_score": 95},
            "rate_allowed": True,
        }
    )
    assert res["allow"] is True
    assert res.get("approval_required") is True


def test_m365_sites_provision_requires_approval() -> None:
    res = opa_eval(
        {
            "agent": "m365-administrator",
            "action": "sites.provision",
            "data": {"displayName": "Ops Site"},
            "rate_allowed": True,
        }
    )
    assert res["allow"] is True
    assert res.get("approval_required") is True


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


def test_outreach_bulk_over_100_requires_approval() -> None:
    res = opa_eval(
        {
            "agent": "outreach-coordinator",
            "action": "email.send_bulk",
            "data": {"recipients_count": 250},
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
