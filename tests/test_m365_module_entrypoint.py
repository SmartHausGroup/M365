from __future__ import annotations

import uuid

import pytest
from m365.module.entrypoint import M365ConnectorModule
from m365.module.manifest import m365_connector_module_manifest


def test_m365_module_manifest_matches_tai_entrypoint_contract() -> None:
    manifest = m365_connector_module_manifest()
    assert manifest["module_id"] == "m365-connector"
    assert manifest["entrypoint"] == "m365.module.entrypoint:M365ConnectorModule"
    assert manifest["capabilities"] == ["m365.instruction.execute"]
    assert manifest["entitlements"] == ["m365_actions"]


def test_m365_module_rejects_unsupported_capability() -> None:
    module = M365ConnectorModule(require_user_context=False)
    result = module.invoke("m365.provision", {"trace_id": "trace-unsupported"})
    assert result["ok"] is False
    assert "Unsupported capability" in result["error"]
    assert result["trace_id"] == "trace-unsupported"


def test_m365_module_requires_user_context_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    module = M365ConnectorModule(require_user_context=True)
    result = module.execute(
        {
            "action": "create_team",
            "params": {"mail_nickname": "project-x", "channels": ["General"]},
            "trace_id": "trace-auth-required",
        }
    )
    assert result["ok"] is False
    assert result["error"] == "auth_required"
    assert result["trace_id"] == "trace-auth-required"


def test_m365_module_enforces_mutation_gate_and_idempotency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "false")
    module = M365ConnectorModule(require_user_context=True)
    idem_key = f"mod-idem-{uuid.uuid4()}"
    payload = {
        "action": "create_site",
        "params": {"display_name": "Project Site", "mail_nickname": "project-site"},
        "trace_id": "trace-idempotent",
        "idempotency_key": idem_key,
        "user_info": {"id": "integration-test"},
    }
    first = module.execute(payload)
    second = module.execute(payload)
    assert first["ok"] is False
    assert first["error"] == "m365_mutations_disabled"
    assert second == first


def test_m365_module_executes_instruction_contract_with_mocked_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")

    def _fake_execute_action(action: str, params: dict[str, object]) -> dict[str, object]:
        assert action == "create_team"
        assert params["mail_nickname"] == "project-x"
        return {"status": "accepted", "team_id": "team-123"}

    monkeypatch.setattr("provisioning_api.routers.m365._execute_action", _fake_execute_action)

    module = M365ConnectorModule(require_user_context=True)
    result = module.execute(
        {
            "action": "create_team",
            "params": {"mail_nickname": "project-x", "channels": ["General"]},
            "trace_id": "trace-success",
            "user_info": {"id": "integration-test"},
        }
    )
    assert result["ok"] is True
    assert result["trace_id"] == "trace-success"
    assert result["result"]["status"] == "accepted"
    assert result["result"]["team_id"] == "team-123"
