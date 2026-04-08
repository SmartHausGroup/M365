from __future__ import annotations

from collections.abc import Generator
from typing import Any

import httpx
import pytest
from provisioning_api.routers import m365 as m365_router
from smarthaus_common.approval_risk import (
    reload_approval_risk_registry,
    resolve_action_approval_risk,
)
from smarthaus_common.auth_model import reload_auth_model_registry, resolve_action_auth
from smarthaus_common.executor_routing import (
    executor_route_for_action,
    reload_executor_routing_registry,
)
from smarthaus_common.power_automate_client import PowerAutomateClient
from smarthaus_common.tenant_config import AzureConfig, TenantConfig, TenantIdentity


@pytest.fixture(autouse=True)
def _reload_registries() -> Generator[None, None, None]:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()
    yield
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def test_e3a_instruction_schema_includes_power_automate_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}

    assert {
        "list_flows_admin",
        "get_flow_admin",
        "list_http_flows",
        "list_flow_owners",
        "list_flow_runs",
        "set_flow_owner_role",
        "remove_flow_owner_role",
        "enable_flow",
        "disable_flow",
        "delete_flow",
        "restore_flow",
        "invoke_flow_callback",
    }.issubset(supported)


def test_e3a_actions_route_and_auth_to_powerplatform() -> None:
    for action in (
        "list_flows_admin",
        "get_flow_admin",
        "list_http_flows",
        "list_flow_owners",
        "list_flow_runs",
        "set_flow_owner_role",
        "invoke_flow_callback",
    ):
        assert executor_route_for_action(None, action) == "powerplatform"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "powerplatform"
        assert resolution.auth_class == "app_only"


def test_e3a_reads_and_mutations_resolve_expected_approval_profiles() -> None:
    read_resolution = resolve_action_approval_risk("m365-administrator", "list_flows_admin", {})
    mutation_resolution = resolve_action_approval_risk("m365-administrator", "enable_flow", {})

    assert read_resolution.risk_class == "low"
    assert read_resolution.approval_profile == "low-observe-create"
    assert read_resolution.approval_required is False

    assert mutation_resolution.risk_class == "high"
    assert mutation_resolution.approval_profile == "high-impact"
    assert mutation_resolution.approval_required is True


def test_e3a_instruction_contract_executes_power_automate_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeClient:
        def list_flows_admin(self, environment_name: str) -> list[dict[str, Any]]:
            assert environment_name == "Default-Env"
            return [{"name": "flow-1"}]

        def set_flow_owner_role(
            self,
            environment_name: str,
            flow_name: str,
            principal_object_id: str,
            *,
            role_name: str = "CanEdit",
            principal_type: str = "User",
        ) -> dict[str, Any]:
            assert environment_name == "Default-Env"
            assert flow_name == "flow-1"
            assert principal_object_id == "user-1"
            assert role_name == "CanEdit"
            assert principal_type == "User"
            return {
                "flowName": flow_name,
                "principalObjectId": principal_object_id,
                "roleName": role_name,
                "status": "updated",
            }

        def invoke_flow_callback(
            self,
            callback_url: str,
            body: Any,
            *,
            headers: dict[str, str] | None = None,
            timeout_seconds: int = 30,
        ) -> dict[str, Any]:
            assert callback_url == "https://example.test/flow"
            assert body == {"ticket": "123"}
            assert headers == {"x-test": "1"}
            assert timeout_seconds == 45
            return {"invoked": True, "status_code": 202, "response": {"ok": True}}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_power_automate_client", lambda action=None: _FakeClient())

    list_payload = m365_router.execute_instruction_contract(
        action="list_flows_admin",
        params_payload={"environmentName": "Default-Env"},
        trace_id="trace-list-flows",
    )
    owner_payload = m365_router.execute_instruction_contract(
        action="set_flow_owner_role",
        params_payload={
            "environmentName": "Default-Env",
            "flowName": "flow-1",
            "principalObjectId": "user-1",
        },
        trace_id="trace-set-owner",
    )
    invoke_payload = m365_router.execute_instruction_contract(
        action="invoke_flow_callback",
        params_payload={
            "callbackUrl": "https://example.test/flow",
            "body": {"ticket": "123"},
            "headers": {"x-test": "1"},
            "timeoutSeconds": 45,
        },
        trace_id="trace-invoke-flow",
    )

    assert list_payload["ok"] is True
    assert list_payload["result"] == {"flows": [{"name": "flow-1"}], "count": 1}
    assert owner_payload["ok"] is True
    assert owner_payload["result"] == {
        "flowName": "flow-1",
        "principalObjectId": "user-1",
        "roleName": "CanEdit",
        "status": "updated",
    }
    assert invoke_payload["ok"] is True
    assert invoke_payload["result"] == {
        "invoked": True,
        "status_code": 202,
        "response": {"ok": True},
    }


def test_e3a_power_automate_client_fails_closed_without_client_secret() -> None:
    client = PowerAutomateClient(
        tenant_config=TenantConfig(
            azure=AzureConfig(
                tenant_id="tenant-id",
                client_id="client-id",
            )
        )
    )

    with pytest.raises(Exception, match="client_secret is required"):
        client.list_flows_admin("Default-Env")


def test_e3a_power_automate_client_ignores_warning_preamble_when_json_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Proc:
        returncode = 0
        stdout = 'WARNING: module import warning\n[{"name":"flow-1"}]'
        stderr = ""

    monkeypatch.setattr("shutil.which", lambda _name: "/usr/bin/pwsh")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: _Proc())

    client = PowerAutomateClient(
        tenant_config=TenantConfig(
            azure=AzureConfig(
                tenant_id="tenant-id",
                client_id="client-id",
                client_secret="secret",
            )
        )
    )

    payload = client.list_flows_admin("Default-Env")

    assert payload == [{"name": "flow-1"}]


def test_e3a_power_automate_client_treats_warning_only_stdout_as_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Proc:
        returncode = 0
        stdout = "WARNING: module import warning"
        stderr = ""

    monkeypatch.setattr("shutil.which", lambda _name: "/usr/bin/pwsh")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: _Proc())

    client = PowerAutomateClient(
        tenant_config=TenantConfig(
            azure=AzureConfig(
                tenant_id="tenant-id",
                client_id="client-id",
                client_secret="secret",
            )
        )
    )

    payload = client.list_flows_admin("Default-Env")

    assert payload == []


def test_e3a_operator_access_token_prefers_azure_tenant_id_over_slug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class _Proc:
        returncode = 0
        stdout = '{"accessToken":"token"}'
        stderr = ""

    def _fake_run(args: list[str], **kwargs: Any) -> _Proc:
        captured["args"] = args
        return _Proc()

    monkeypatch.setattr("shutil.which", lambda _name: "/usr/bin/az")
    monkeypatch.setattr("subprocess.run", _fake_run)

    client = PowerAutomateClient(
        tenant_config=TenantConfig(
            tenant=TenantIdentity(id="smarthaus", domain="smarthausgroup.com"),
            azure=AzureConfig(
                tenant_id="6c4cb441-342c-430f-9a9d-79c3cdb18b75",
                client_id="client-id",
                client_secret="secret",
            ),
        )
    )

    token = client._operator_access_token()

    assert token == "token"
    assert captured["args"][-2:] == ["--tenant", "6c4cb441-342c-430f-9a9d-79c3cdb18b75"]


def test_e3a_invoke_flow_callback_returns_response(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Response:
        status_code = 202
        text = "accepted"

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return {"accepted": True}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: _Response())
    client = PowerAutomateClient(
        tenant_config=TenantConfig(
            azure=AzureConfig(
                tenant_id="tenant-id",
                client_id="client-id",
                client_secret="secret",
            )
        )
    )

    payload = client.invoke_flow_callback(
        "https://example.test/flow",
        {"sample": True},
        headers={"x-test": "1"},
        timeout_seconds=10,
    )

    assert payload == {
        "invoked": True,
        "status_code": 202,
        "response": {"accepted": True},
    }
