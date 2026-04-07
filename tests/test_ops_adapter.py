from __future__ import annotations

import asyncio
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import jwt
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from ops_adapter import actions as actions_module
from ops_adapter.approvals import ApprovalsStore
from ops_adapter.audit import Auditor
from ops_adapter.main import app
from ops_adapter.personas import build_persona_registry
from smarthaus_common import permission_enforcer as permission_enforcer_module
from smarthaus_common import tenant_config as tenant_config_module
from smarthaus_common.permission_enforcer import check_user_permission
from smarthaus_common.tenant_config import reload_tenant_config

# Load environment variables for testing
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def test_health() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


class _DummyRate:
    def allow(self, _key: str) -> bool:
        return True


class _DummyAuditor:
    async def log(self, *_args: Any, **_kwargs: Any) -> None:
        return None


class _DummyOPA:
    def __init__(self, allowed: bool, approval_required: bool) -> None:
        self.allowed = allowed
        self.approval_required = approval_required

    async def check(
        self,
        _agent: str,
        _action: str,
        _data: dict[str, Any],
        _rate_allowed: bool,
        _corr: str,
    ) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "approval_required": self.approval_required,
            "reason": "" if self.allowed else "policy_denied",
        }


def _auth_headers(
    user_email: str, secret: str = "test-secret", groups: list[str] | None = None
) -> dict[str, str]:
    claims: dict[str, Any] = {
        "sub": f"{user_email}-sub",
        "preferred_username": user_email,
    }
    if groups is not None:
        claims["groups"] = groups
    token = jwt.encode(
        claims,
        secret,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def _invalid_actor_headers(secret: str = "test-secret") -> dict[str, str]:
    token = jwt.encode({"sub": "no-upn"}, secret, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def tenant_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-alpha.yaml").write_text(
        """
tenant:
  id: tenant-alpha
azure:
  tenant_id: tenant-guid-alpha
  client_id: client-alpha
auth:
  mode: app_only
permission_tiers:
  default_tier: standard_user
  users:
    admin@example.com: global_admin
  groups:
    entra-global-admins: global_admin
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "tenant-alpha")
    monkeypatch.setenv("LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("JWT_REQUIRED", "1")
    monkeypatch.setenv("JWT_HS256_SECRET", "test-secret")
    monkeypatch.delenv("M365_PERMISSION_FAIL_OPEN", raising=False)
    monkeypatch.delenv("M365_ACTOR_HEADER_FALLBACK", raising=False)
    reload_tenant_config()
    yield
    reload_tenant_config()


@pytest.fixture
def patched_runtime(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    import ops_adapter.main as ops_main

    registry = {
        "agents": {
            "m365-administrator": {
                "allowed_actions": [
                    "users.disable",
                    "groups.list",
                    "sites.get",
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
            },
            "website-manager": {
                "allowed_actions": ["sites.get"],
                "approval_rules": [],
            },
        }
    }
    personas = build_persona_registry(
        registry,
        {
            "departments": {
                "operations": [
                    {
                        "agent": "m365-administrator",
                        "name": "Marcus Chen",
                        "role": "Senior IT Administrator",
                    },
                    {
                        "agent": "website-manager",
                        "name": "Elena Rodriguez",
                        "role": "Website Manager",
                    },
                ]
            }
        },
    )
    monkeypatch.setattr(ops_main, "REGISTRY", registry)
    monkeypatch.setattr(ops_main, "PERSONAS", personas)
    monkeypatch.setattr(ops_main, "RATE", _DummyRate())
    monkeypatch.setattr(ops_main, "AUDITOR", _DummyAuditor())
    monkeypatch.setattr(ops_main, "APPROVALS", ApprovalsStore(registry, personas))
    return ops_main


@pytest.fixture
def multi_executor_tenant_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-multi.yaml").write_text(
        """
tenant:
  id: tenant-multi
azure:
  tenant_id: root-tenant
  client_id: root-client
auth:
  mode: app_only
executors:
  collaboration:
    domain: collaboration
    azure:
      tenant_id: collab-tenant
      client_id: collab-client
  directory:
    domain: directory
    azure:
      tenant_id: directory-tenant
      client_id: directory-client
  sharepoint:
    domain: sharepoint
    azure:
      tenant_id: sharepoint-tenant
      client_id: sharepoint-client
executor_registry:
  default_executor: directory
  routes:
    approvals: sharepoint
    collaboration: collaboration
    directory: directory
    sharepoint: sharepoint
permission_tiers:
  default_tier: standard_user
  users:
    admin@example.com: global_admin
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "tenant-multi")
    monkeypatch.setenv("LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("JWT_REQUIRED", "1")
    monkeypatch.setenv("JWT_HS256_SECRET", "test-secret")
    monkeypatch.delenv("M365_PERMISSION_FAIL_OPEN", raising=False)
    monkeypatch.delenv("M365_ACTOR_HEADER_FALLBACK", raising=False)
    reload_tenant_config()
    yield
    reload_tenant_config()


def test_check_user_permission_denies_without_identity(tenant_env: None) -> None:
    allowed, reason = check_user_permission("", "users.disable")
    assert allowed is False
    assert reason == "user_identity_missing"


def test_check_user_permission_allows_group_mapped_actor(tenant_env: None) -> None:
    allowed, reason = check_user_permission(
        "group-admin@example.com",
        "users.disable",
        actor_groups=["entra-global-admins"],
    )
    assert allowed is True
    assert reason == ""


def test_check_user_permission_normalizes_planner_aliases(tenant_env: None) -> None:
    allowed, reason = check_user_permission("admin@example.com", "create_plan")
    assert allowed is True
    assert reason == ""


def test_check_user_permission_normalizes_calendar_aliases(tenant_env: None) -> None:
    allowed, reason = check_user_permission("admin@example.com", "email.schedule")
    assert allowed is True
    assert reason == ""


def test_check_user_permission_normalizes_hr_aliases(tenant_env: None) -> None:
    allowed, reason = check_user_permission("admin@example.com", "employee.offboard")
    assert allowed is True
    assert reason == ""


def test_check_user_permission_denies_without_tiers_file(
    tenant_env: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("M365_PERMISSION_TIERS_PATH", str(tmp_path / "missing.yaml"))
    monkeypatch.setattr(permission_enforcer_module, "_TIERS", None)
    monkeypatch.setattr(permission_enforcer_module, "_TIERS_PATH", None)
    monkeypatch.setattr(permission_enforcer_module, "_TIERS_MTIME", 0.0)

    allowed, reason = check_user_permission("admin@example.com", "users.disable")

    assert allowed is False
    assert reason == "permission_tiers_missing"


def test_actions_denies_when_identity_missing(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/users.disable",
        json={"params": {"userPrincipalName": "jdoe@example.com"}},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "missing_bearer_token"


def test_actions_denies_when_actor_claim_missing(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/users.disable",
        headers=_invalid_actor_headers(),
        json={"params": {"userPrincipalName": "jdoe@example.com"}},
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "entra_actor_identity_required"


def test_actions_denies_when_tier_not_allowed(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/users.disable",
        headers=_auth_headers("user@example.com"),
        json={"params": {"userPrincipalName": "jdoe@example.com"}},
    )
    assert r.status_code == 403
    assert "tier_" in r.json()["detail"]
    assert "users.disable" in r.json()["detail"]


def test_actions_returns_pending_approval_for_high_risk_admin_action(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=True))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/sites.provision",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"displayName": "Operations Site"}},
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_approval"
    assert isinstance(data["approval_id"], str) and data["approval_id"]


def test_e1d_matrix_forces_pending_approval_when_opa_surface_is_incomplete(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/sites.provision",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"displayName": "Operations Site"}},
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_approval"
    approval = patched_runtime.APPROVALS.get(data["approval_id"])
    assert approval is not None
    assert approval["params"]["risk_class"] == "high"
    assert approval["params"]["approval_profile"] == "high-impact"
    assert approval["approvers"] == ["global_admin"]


def test_group_mapped_actor_binding_is_preserved_in_pending_approval(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=True))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/sites.provision",
        headers=_auth_headers("group-admin@example.com", groups=["entra-global-admins"]),
        json={"params": {"displayName": "Operations Site"}},
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_approval"
    approval = patched_runtime.APPROVALS.get(data["approval_id"])
    assert approval is not None
    assert approval["requestor"] == "group-admin@example.com"
    assert approval["requestor_tier"] == "global_admin"
    assert approval["requestor_groups"] == ["entra-global-admins"]
    assert approval["tenant"] == "tenant-alpha"
    assert approval["executor"]["mode"] == "app_only"
    assert approval["executor"]["client_id"] == "client-alpha"
    assert approval["persona"]["canonical_agent"] == "m365-administrator"
    assert approval["persona"]["display_name"] == "Marcus Chen"
    assert approval["persona_target"] == "m365-administrator"


def test_b7c_resolves_humanized_persona_target_to_canonical_agent(
    multi_executor_tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    async def _capture_execute(
        agent: str,
        _action: str,
        params: dict[str, Any],
        _correlation_id: str,
        executor_name: str | None = None,
    ) -> dict[str, Any]:
        return {
            "canonical_agent": agent,
            "executor_name": executor_name,
            "persona": params["persona"],
            "persona_target": params["persona_target"],
        }

    monkeypatch.setattr(patched_runtime, "execute", _capture_execute)

    client = TestClient(app)
    r = client.post(
        "/actions/Elena%20Rodriguez/sites.get",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"siteId": "site-123"}},
    )

    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "success"
    assert payload["result"]["canonical_agent"] == "website-manager"
    assert payload["result"]["executor_name"] == "sharepoint"
    assert payload["result"]["persona"]["display_name"] == "Elena Rodriguez"
    assert payload["result"]["persona"]["canonical_agent"] == "website-manager"
    assert payload["result"]["persona_target"] == "Elena Rodriguez"


def test_b7c_denies_inactive_persona_targets(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        patched_runtime,
        "PERSONAS",
        {
            **patched_runtime.PERSONAS,
            "legacy-analyst": {
                "persona_id": "legacy-analyst",
                "canonical_agent": "legacy-analyst",
                "display_name": "Legacy Analyst",
                "slug": "legacy-analyst",
                "department": "operations",
                "title": "Legacy Analyst",
                "manager": "unassigned",
                "responsibilities": [],
                "allowed_domains": [],
                "approval_owner": "unassigned",
                "status": "inactive",
                "external_presence_policy": "internal_only",
                "aliases": ["legacy-analyst", "legacy analyst"],
            },
        },
    )
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/legacy-analyst/sites.get",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"siteId": "site-123"}},
    )

    assert r.status_code == 403
    assert r.json()["detail"] == "persona_inactive:legacy-analyst"


def test_b7c_fails_closed_on_persona_domain_mismatch(
    multi_executor_tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))
    mismatched = {
        **patched_runtime.PERSONAS,
        "website-manager": {
            **patched_runtime.PERSONAS["website-manager"],
            "allowed_domains": ["directory"],
        },
    }
    monkeypatch.setattr(patched_runtime, "PERSONAS", mismatched)

    client = TestClient(app)
    r = client.post(
        "/actions/website-manager/sites.get",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"siteId": "site-123"}},
    )

    assert r.status_code == 403
    assert r.json()["detail"] == "persona_domain_mismatch:website-manager:sharepoint"


def test_b7b_routes_sharepoint_actions_to_sharepoint_executor(
    multi_executor_tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    async def _capture_execute(
        _agent: str,
        _action: str,
        params: dict[str, Any],
        _correlation_id: str,
        executor_name: str | None = None,
    ) -> dict[str, Any]:
        return {
            "executor_name": executor_name,
            "executor_identity": params["executor_identity"],
        }

    monkeypatch.setattr(patched_runtime, "execute", _capture_execute)

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/sites.get",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"siteId": "site-123"}},
    )

    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "success"
    assert payload["result"]["executor_name"] == "sharepoint"
    assert payload["result"]["executor_identity"]["domain"] == "sharepoint"
    assert payload["result"]["executor_identity"]["client_id"] == "sharepoint-client"


def test_b7b_routes_directory_actions_to_directory_executor(
    multi_executor_tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    async def _capture_execute(
        _agent: str,
        _action: str,
        params: dict[str, Any],
        _correlation_id: str,
        executor_name: str | None = None,
    ) -> dict[str, Any]:
        return {
            "executor_name": executor_name,
            "executor_identity": params["executor_identity"],
        }

    monkeypatch.setattr(patched_runtime, "execute", _capture_execute)

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/groups.list",
        headers=_auth_headers("admin@example.com"),
        json={"params": {}},
    )

    assert r.status_code == 200
    payload = r.json()
    assert payload["result"]["executor_name"] == "directory"
    assert payload["result"]["executor_identity"]["domain"] == "directory"
    assert payload["result"]["executor_identity"]["client_id"] == "directory-client"


def test_b7b_preserves_logical_domain_when_executor_alias_maps_to_collaboration(
    multi_executor_tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))
    monkeypatch.setattr(
        patched_runtime,
        "REGISTRY",
        {
            "agents": {
                "email-processing-agent": {
                    "allowed_actions": ["mail.list"],
                    "approval_rules": [],
                }
            }
        },
    )
    monkeypatch.setattr(
        patched_runtime,
        "PERSONAS",
        {
            "email-processing-agent": {
                "persona_id": "email-processing-agent",
                "canonical_agent": "email-processing-agent",
                "display_name": "Hannah Kim",
                "slug": "hannah-kim",
                "department": "communication",
                "title": "Email Processing Agent",
                "manager": "unassigned",
                "responsibilities": [],
                "allowed_domains": ["messaging"],
                "approval_owner": "unassigned",
                "status": "active",
                "external_presence_policy": "internal_only",
                "aliases": ["email-processing-agent", "hannah kim"],
            }
        },
    )
    monkeypatch.setattr(
        patched_runtime,
        "APPROVALS",
        ApprovalsStore(patched_runtime.REGISTRY, patched_runtime.PERSONAS),
    )

    async def _capture_execute(
        _agent: str,
        _action: str,
        params: dict[str, Any],
        _correlation_id: str,
        executor_name: str | None = None,
    ) -> dict[str, Any]:
        return {
            "executor_name": executor_name,
            "executor_domain": params["executor_domain"],
            "executor_identity": params["executor_identity"],
        }

    monkeypatch.setattr(patched_runtime, "execute", _capture_execute)

    client = TestClient(app)
    response = client.post(
        "/actions/email-processing-agent/mail.list",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"userId": "admin@example.com", "top": 5}},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["executor_name"] == "collaboration"
    assert payload["result"]["executor_domain"] == "messaging"
    assert payload["result"]["executor_identity"]["domain"] == "messaging"
    assert payload["result"]["executor_identity"]["logical_domain"] == "messaging"
    assert payload["result"]["executor_identity"]["physical_domain"] == "collaboration"
    assert payload["result"]["executor_identity"]["client_id"] == "collab-client"


def test_graph_token_surfaces_missing_tenant_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_graph_client: Any = ModuleType("smarthaus_graph.client")

    class _DummyGraphTokenProvider:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            return None

    fake_graph_client.GraphTokenProvider = _DummyGraphTokenProvider

    tenant_root = tmp_path / "ucp"
    (tenant_root / "tenants").mkdir(parents=True)

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "missing-tenant")
    monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
    monkeypatch.setitem(sys.modules, "smarthaus_graph.client", fake_graph_client)
    tenant_config_module._cached_config = None
    tenant_config_module._cached_slug = None
    actions_module._token_providers.clear()

    with pytest.raises(actions_module.GraphAPIError) as excinfo:
        actions_module._graph_token()

    assert excinfo.value.code == "tenant_config_missing"
    assert "missing-tenant.yaml" in excinfo.value.message


def test_graph_token_surfaces_auth_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_graph_client: Any = ModuleType("smarthaus_graph.client")

    class _DummyGraphTokenProvider:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            return None

        def get_token(self, prefer_delegated: bool = False) -> str:
            del prefer_delegated
            raise actions_module.AuthConfigurationError(
                "Tenant config missing azure.client_secret or azure.client_certificate_path."
            )

    fake_graph_client.GraphTokenProvider = _DummyGraphTokenProvider

    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-alpha.yaml").write_text(
        """
tenant:
  id: tenant-alpha
azure:
  tenant_id: tenant-guid-alpha
  client_id: client-alpha
auth:
  mode: app_only
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "tenant-alpha")
    monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_CERTIFICATE_PATH", raising=False)
    monkeypatch.setitem(sys.modules, "smarthaus_graph.client", fake_graph_client)
    tenant_config_module._cached_config = None
    tenant_config_module._cached_slug = None
    actions_module._token_providers.clear()

    with pytest.raises(actions_module.GraphAPIError) as excinfo:
        actions_module._graph_token()

    assert excinfo.value.code == "auth_configuration_error"
    assert "client_secret" in excinfo.value.message


def test_graph_token_preserves_legacy_env_fallback_without_tenant_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _DummyClientSecretCredential:
        def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
            assert tenant_id == "legacy-tenant"
            assert client_id == "legacy-client"
            assert client_secret == "legacy-secret"

        def get_token(self, scope: str) -> SimpleNamespace:
            assert scope == actions_module.GRAPH_SCOPE
            return SimpleNamespace(token="legacy-token")

    fake_azure_identity: Any = ModuleType("azure.identity")
    fake_azure_identity.ClientSecretCredential = _DummyClientSecretCredential

    monkeypatch.delenv("UCP_TENANT", raising=False)
    monkeypatch.delenv("UCP_ROOT", raising=False)
    monkeypatch.setenv("AZURE_TENANT_ID", "legacy-tenant")
    monkeypatch.setenv("AZURE_CLIENT_ID", "legacy-client")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "legacy-secret")
    monkeypatch.setitem(sys.modules, "azure.identity", fake_azure_identity)
    monkeypatch.setattr(actions_module, "_get_token_provider", lambda: None)

    assert actions_module._graph_token() == "legacy-token"


def test_graph_token_skips_tenant_provider_without_ucp_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _DummyClientSecretCredential:
        def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
            assert tenant_id == "legacy-tenant"
            assert client_id == "legacy-client"
            assert client_secret == "legacy-secret"

        def get_token(self, scope: str) -> SimpleNamespace:
            assert scope == actions_module.GRAPH_SCOPE
            return SimpleNamespace(token="legacy-token")

    fake_azure_identity: Any = ModuleType("azure.identity")
    fake_azure_identity.ClientSecretCredential = _DummyClientSecretCredential

    monkeypatch.delenv("UCP_TENANT", raising=False)
    monkeypatch.delenv("UCP_ROOT", raising=False)
    monkeypatch.setenv("AZURE_TENANT_ID", "legacy-tenant")
    monkeypatch.setenv("AZURE_CLIENT_ID", "legacy-client")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "legacy-secret")
    monkeypatch.setitem(sys.modules, "azure.identity", fake_azure_identity)

    def _unexpected_provider() -> None:
        raise AssertionError("tenant-aware provider should be skipped without UCP_TENANT")

    monkeypatch.setattr(actions_module, "_get_token_provider", _unexpected_provider)

    assert actions_module._graph_token() == "legacy-token"


def test_b7b_preserves_routed_executor_identity_in_pending_approval(
    multi_executor_tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=True))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/sites.provision",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"displayName": "Operations Site"}},
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_approval"
    approval = patched_runtime.APPROVALS.get(data["approval_id"])
    assert approval is not None
    assert approval["executor"]["domain"] == "sharepoint"
    assert approval["executor"]["client_id"] == "sharepoint-client"


def test_b7b_fails_closed_when_multi_executor_route_is_unmapped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant_root = tmp_path / "ucp"
    tenants_dir = tenant_root / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "tenant-unmapped.yaml").write_text(
        """
tenant:
  id: tenant-unmapped
auth:
  mode: app_only
executors:
  collaboration:
    domain: collaboration
  directory:
    domain: directory
executor_registry:
  default_executor: directory
  routes:
    collaboration: collaboration
    directory: directory
permission_tiers:
  default_tier: standard_user
  users:
    admin@example.com: global_admin
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("UCP_ROOT", str(tenant_root))
    monkeypatch.setenv("UCP_TENANT", "tenant-unmapped")
    monkeypatch.setenv("JWT_REQUIRED", "1")
    monkeypatch.setenv("JWT_HS256_SECRET", "test-secret")
    reload_tenant_config()

    import ops_adapter.main as ops_main

    registry = {
        "agents": {
            "m365-administrator": {
                "allowed_actions": ["sites.get"],
                "approval_rules": [],
            }
        }
    }
    personas = build_persona_registry(registry)
    monkeypatch.setattr(ops_main, "REGISTRY", registry)
    monkeypatch.setattr(ops_main, "PERSONAS", personas)
    monkeypatch.setattr(ops_main, "RATE", _DummyRate())
    monkeypatch.setattr(ops_main, "AUDITOR", _DummyAuditor())
    monkeypatch.setattr(ops_main, "APPROVALS", ApprovalsStore(registry, personas))
    monkeypatch.setattr(ops_main, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/sites.get",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"siteId": "site-123"}},
    )

    assert r.status_code == 500
    assert r.json()["detail"] == "executor_route_unmapped:sharepoint"


def test_admin_set_user_tier_records_append_only_audit_event(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/admin.set_user_tier",
        headers=_auth_headers("admin@example.com"),
        json={"params": {"email": "user@example.com", "tier": "power_user"}},
    )

    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "success"
    assert payload["result"]["status"] == "updated"

    audit = client.post(
        "/actions/m365-administrator/admin.audit_log",
        headers=_auth_headers("admin@example.com"),
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
    assert event["actor_tier"]["tier_name"] == "global_admin"
    assert event["actor_tier"]["assignment_source"] == "user"
    assert event["executor"]["mode"] == "app_only"
    assert event["executor"]["client_id"] == "client-alpha"
    assert event["tenant"] == "tenant-alpha"
    assert event["before"] == {"tier": "standard_user"}
    assert event["after"] == {"tier": "power_user"}
    assert event["details"]["email"] == "user@example.com"


def test_admin_audit_log_can_return_snapshot_context(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))

    client = TestClient(app)
    client.post(
        "/actions/m365-administrator/admin.get_tenant_config",
        headers=_auth_headers("admin@example.com"),
        json={"params": {}},
    )

    audit = client.post(
        "/actions/m365-administrator/admin.audit_log",
        headers=_auth_headers("admin@example.com"),
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
    assert event["actor_tier"]["tier_name"] == "global_admin"
    assert event["executor"]["mode"] == "app_only"


def test_success_audit_log_captures_actor_and_executor_identity(
    tenant_env: None, patched_runtime: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    audit_dir = tmp_path / "auditlogs"
    monkeypatch.setenv("LOG_DIR", str(audit_dir))
    monkeypatch.setattr(patched_runtime, "OPA", _DummyOPA(allowed=True, approval_required=False))
    monkeypatch.setattr(patched_runtime, "AUDITOR", Auditor(log_dir=str(audit_dir)))

    client = TestClient(app)
    r = client.post(
        "/actions/m365-administrator/admin.get_tenant_config",
        headers=_auth_headers("group-admin@example.com", groups=["entra-global-admins"]),
        json={"params": {}},
    )

    assert r.status_code == 200
    entries = [
        json.loads(line)
        for line in (audit_dir / "ops_audit.log").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    success_entries = [
        entry
        for entry in entries
        if entry.get("surface") == "ops_adapter"
        and entry.get("status") == "success"
        and entry.get("action") == "admin.get_tenant_config"
    ]
    assert success_entries
    entry = success_entries[-1]
    assert entry["schema_version"] == "2.0"
    assert entry["actor"] == "group-admin@example.com"
    assert entry["actor_tier"]["tier_name"] == "global_admin"
    assert entry["actor_tier"]["assignment_source"] == "group"
    assert entry["actor_groups"] == ["entra-global-admins"]
    assert entry["executor"]["mode"] == "app_only"
    assert entry["executor"]["client_id"] == "client-alpha"
    assert entry["tenant"] == "tenant-alpha"
    assert entry["result"]["outcome"] == "success"
    assert isinstance(entry["result"]["payload"], dict)


def test_execute_routes_teams_add_channel_to_channel_create(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_channels_create(params: dict[str, Any], _correlation_id: str) -> dict[str, Any]:
        return {"channel": {"teamId": params["teamId"], "displayName": params["displayName"]}}

    monkeypatch.setattr(actions_module, "channels_create", _fake_channels_create)

    result = asyncio.run(
        actions_module.execute(
            "m365-administrator",
            "teams.add_channel",
            {"teamId": "team-123", "channelName": "Operations"},
            "corr-1",
        )
    )

    assert result["channel"]["teamId"] == "team-123"
    assert result["channel"]["displayName"] == "Operations"


def test_execute_routes_create_plan_to_planner_wrapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_planner_create_plan(
        params: dict[str, Any], _correlation_id: str
    ) -> dict[str, Any]:
        return {"plan": {"id": "plan-123", "title": params["title"]}, "status": "created"}

    monkeypatch.setattr(actions_module, "planner_create_plan", _fake_planner_create_plan)

    result = asyncio.run(
        actions_module.execute(
            "project-coordination-agent",
            "create_plan",
            {"groupId": "group-123", "title": "Website Refresh"},
            "corr-2",
        )
    )

    assert result["status"] == "created"
    assert result["plan"]["title"] == "Website Refresh"


def test_execute_routes_email_schedule_to_calendar_create(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_calendar_create(params: dict[str, Any], _correlation_id: str) -> dict[str, Any]:
        return {"event": {"subject": params["subject"]}, "status": "created"}

    monkeypatch.setattr(actions_module, "calendar_create", _fake_calendar_create)

    result = asyncio.run(
        actions_module.execute(
            "outreach-coordinator",
            "email.schedule",
            {
                "userId": "admin@example.com",
                "subject": "Follow-up",
                "start": {"dateTime": "2026-04-08T10:00:00Z", "timeZone": "UTC"},
                "end": {"dateTime": "2026-04-08T10:30:00Z", "timeZone": "UTC"},
            },
            "corr-3",
        )
    )

    assert result["status"] == "created"
    assert result["event"]["subject"] == "Follow-up"


def test_execute_routes_employee_offboard_to_users_disable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_users_disable(params: dict[str, Any], _correlation_id: str) -> dict[str, Any]:
        return {"disabled": True, "userPrincipalName": params["userPrincipalName"]}

    monkeypatch.setattr(actions_module, "m365_users_disable", _fake_users_disable)

    result = asyncio.run(
        actions_module.execute(
            "hr-generalist",
            "employee.offboard",
            {"email": "departing@example.com"},
            "corr-4",
        )
    )

    assert result["disabled"] is True
    assert result["userPrincipalName"] == "departing@example.com"


@pytest.mark.parametrize(
    ("agent", "action", "params", "helper_name"),
    [
        ("website-manager", "deployment.production", {}, None),
        ("website-manager", "content.create", {"content_id": "content-1"}, None),
        ("website-manager", "content.update", {"content_id": "content-1"}, None),
        ("website-manager", "analytics.read", {}, None),
        ("website-manager", "seo.update", {"targets": ["homepage"]}, None),
        ("hr-generalist", "policy.create", {"policy_id": "policy-1"}, None),
        ("hr-generalist", "review.initiate", {"review_id": "review-1"}, None),
        ("outreach-coordinator", "followup.create", {"followup_id": "followup-1"}, None),
        ("outreach-coordinator", "campaign.create", {"campaign_id": "campaign-1"}, None),
        (
            "m365-administrator",
            "teams.add_channel",
            {"teamId": "team-1", "channelName": "Ops"},
            "channels_create",
        ),
        ("m365-administrator", "sites.provision", {"displayName": "Ops Site"}, "sites_provision"),
        (
            "outreach-coordinator",
            "email.send_bulk",
            {"recipients": ["a@example.com"]},
            "outreach_email_send_bulk",
        ),
        (
            "outreach-coordinator",
            "email.schedule",
            {"subject": "Follow-up"},
            "outreach_email_schedule",
        ),
        (
            "outreach-coordinator",
            "meeting.schedule",
            {"subject": "Meeting"},
            "outreach_meeting_schedule",
        ),
        (
            "hr-generalist",
            "employee.update_info",
            {"email": "person@example.com"},
            "m365_users_update",
        ),
        (
            "hr-generalist",
            "employee.offboard",
            {"email": "person@example.com"},
            "m365_users_disable",
        ),
        ("project-coordination-agent", "list_plans", {"groupId": "group-1"}, "planner_list_plans"),
        (
            "project-coordination-agent",
            "create_plan",
            {"groupId": "group-1", "title": "Roadmap"},
            "planner_create_plan",
        ),
        (
            "project-coordination-agent",
            "list_buckets",
            {"planId": "plan-1"},
            "planner_list_buckets",
        ),
        (
            "project-coordination-agent",
            "create_bucket",
            {"planId": "plan-1", "name": "Backlog"},
            "planner_create_bucket",
        ),
        (
            "project-coordination-agent",
            "create_task",
            {"planId": "plan-1", "bucketId": "bucket-1", "title": "Ship"},
            "planner_create_task",
        ),
    ],
)
def test_p1_dead_route_aliases_no_longer_raise(
    monkeypatch: pytest.MonkeyPatch,
    agent: str,
    action: str,
    params: dict[str, Any],
    helper_name: str | None,
) -> None:
    if helper_name is not None:

        async def _fake_helper(_params: dict[str, Any], _correlation_id: str) -> dict[str, Any]:
            return {"status": "patched", "action": action}

        monkeypatch.setattr(actions_module, helper_name, _fake_helper)

    result = asyncio.run(actions_module.execute(agent, action, params, "corr-matrix"))

    assert isinstance(result, dict)
    if helper_name is not None:
        assert result["action"] == action
