from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from ops_adapter.approvals import ApprovalsStore
from ops_adapter.main import app
from smarthaus_common import permission_enforcer as permission_enforcer_module
from smarthaus_common.permission_enforcer import check_user_permission
from smarthaus_common.tenant_config import reload_tenant_config

# Load environment variables for testing
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


class _DummyRate:
    def allow(self, _key: str) -> bool:
        return True


class _DummyAuditor:
    async def log(self, *_args, **_kwargs) -> None:
        return None


class _DummyOPA:
    def __init__(self, allowed: bool, approval_required: bool):
        self.allowed = allowed
        self.approval_required = approval_required

    async def check(
        self, _agent: str, _action: str, _data: dict, _rate_allowed: bool, _corr: str
    ) -> dict:
        return {
            "allowed": self.allowed,
            "approval_required": self.approval_required,
            "reason": "" if self.allowed else "policy_denied",
        }


@pytest.fixture
def tenant_env(tmp_path, monkeypatch):
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-alpha.yaml").write_text(
        """
tenant:
  id: tenant-alpha
permission_tiers:
  default_tier: standard_user
  users:
    admin@example.com: global_admin
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "tenant-alpha")
    monkeypatch.setenv("LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.delenv("M365_PERMISSION_FAIL_OPEN", raising=False)
    reload_tenant_config()
    yield
    reload_tenant_config()


@pytest.fixture
def patched_runtime(monkeypatch):
    import ops_adapter.main as ops_main

    registry = {
        "agents": {
            "m365-administrator": {
                "allowed_actions": [
                    "users.disable",
                    "sites.provision",
                    "admin.set_user_tier",
                    "admin.get_tenant_config",
                    "admin.reload_config",
                    "admin.audit_log",
                ],
                "approval_rules": [
                    {"action": "users.disable", "approvers": ["global_admin"]},
                    {"action": "sites.provision", "approvers": ["global_admin"]},
                    {"action": "admin.set_user_tier", "approvers": ["global_admin"]},
                ],
            }
        }
    }
    monkeypatch.setattr(ops_main, "REGISTRY", registry)
    monkeypatch.setattr(ops_main, "RATE", _DummyRate())
    monkeypatch.setattr(ops_main, "AUDITOR", _DummyAuditor())
    monkeypatch.setattr(ops_main, "APPROVALS", ApprovalsStore(registry))
    return ops_main


def test_check_user_permission_denies_without_identity(tenant_env):
    allowed, reason = check_user_permission("", "users.disable")
    assert allowed is False
    assert reason == "user_identity_missing"


def test_check_user_permission_denies_without_tiers_file(tenant_env, tmp_path, monkeypatch):
    monkeypatch.setenv("M365_PERMISSION_TIERS_PATH", str(tmp_path / "missing.yaml"))
    monkeypatch.setattr(permission_enforcer_module, "_TIERS", None)
    monkeypatch.setattr(permission_enforcer_module, "_TIERS_PATH", None)
    monkeypatch.setattr(permission_enforcer_module, "_TIERS_MTIME", 0.0)

    allowed, reason = check_user_permission("admin@example.com", "users.disable")

    assert allowed is False
    assert reason == "permission_tiers_missing"


def test_actions_denies_when_identity_missing(tenant_env, patched_runtime, monkeypatch):
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/users.disable",
        json={"params": {"userPrincipalName": "jdoe@example.com"}},
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "user_identity_missing"


def test_actions_denies_when_tier_not_allowed(tenant_env, patched_runtime, monkeypatch):
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/users.disable",
        headers={"X-User-Email": "user@example.com"},
        json={"params": {"userPrincipalName": "jdoe@example.com"}},
    )
    assert r.status_code == 403
    assert "tier_" in r.json()["detail"]
    assert "users.disable" in r.json()["detail"]


def test_actions_returns_pending_approval_for_high_risk_admin_action(
    tenant_env, patched_runtime, monkeypatch
):
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=True))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/sites.provision",
        headers={"X-User-Email": "admin@example.com"},
        json={"params": {"displayName": "Operations Site"}},
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_approval"
    assert isinstance(data["approval_id"], str) and data["approval_id"]


def test_admin_set_user_tier_records_append_only_audit_event(
    tenant_env, patched_runtime, monkeypatch
):
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/admin.set_user_tier",
        headers={"X-User-Email": "admin@example.com"},
        json={"params": {"email": "user@example.com", "tier": "power_user"}},
    )

    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "success"
    assert payload["result"]["status"] == "updated"

    audit = client.post(
        "/actions/m365-administrator/admin.audit_log",
        headers={"X-User-Email": "admin@example.com"},
        json={"params": {"action": "admin.set_user_tier", "limit": 5}},
    )

    assert audit.status_code == 200
    audit_payload = audit.json()
    assert audit_payload["status"] == "success"
    audit_result = audit_payload["result"]
    assert audit_result["status"] == "event_log"
    assert audit_result["count"] >= 1

    event = audit_result["events"][0]
    assert event["surface"] == "ops_adapter_admin"
    assert event["event_class"] == "permission_tier_update"
    assert event["action"] == "admin.set_user_tier"
    assert event["actor"] == "admin@example.com"
    assert event["tenant"] == "tenant-alpha"
    assert event["before"] == {"tier": "standard_user"}
    assert event["after"] == {"tier": "power_user"}
    assert event["details"]["email"] == "user@example.com"


def test_admin_audit_log_can_return_snapshot_context(tenant_env, patched_runtime, monkeypatch):
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    client.post(
        "/actions/m365-administrator/admin.get_tenant_config",
        headers={"X-User-Email": "admin@example.com"},
        json={"params": {}},
    )

    audit = client.post(
        "/actions/m365-administrator/admin.audit_log",
        headers={"X-User-Email": "admin@example.com"},
        json={"params": {"event_class": "tenant_config_read", "include_snapshot": True}},
    )

    assert audit.status_code == 200
    audit_payload = audit.json()
    assert audit_payload["status"] == "success"
    audit_result = audit_payload["result"]
    assert audit_result["status"] == "event_log"
    assert audit_result["count"] >= 1
    assert audit_result["snapshot"]["default_tier"] == "standard_user"
    assert audit_result["snapshot"]["user_count"] >= 1
    event = audit_result["events"][0]
    assert event["event_class"] == "tenant_config_read"
    assert event["details"]["redacted"] is True
