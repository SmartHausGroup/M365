from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

import httpx
from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError, SmarthausError
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config

_ADMIN_MODULE = "Microsoft.PowerApps.Administration.PowerShell"
_MAKER_MODULE = "Microsoft.PowerApps.PowerShell"
_PW_TENANT_ENV = "SMARTHAUS_PP_TENANT_ID"
_PW_CLIENT_ID_ENV = "SMARTHAUS_PP_CLIENT_ID"
_PW_CLIENT_SECRET_ENV = "SMARTHAUS_PP_CLIENT_SECRET"


def _ps_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class PowerAutomateClient:
    """Bounded Power Automate admin client.

    The supported service-principal path is intentionally bounded to the
    Power Apps / Power Automate PowerShell administration modules. If the
    required modules or client-secret credentials are not present, the client
    fails closed with a deterministic error.
    """

    def __init__(
        self,
        *,
        tenant_config: TenantConfig | None = None,
        legacy_config: AppConfig | None = None,
    ) -> None:
        self._legacy_config = legacy_config
        if tenant_config is not None:
            self._tenant_config = tenant_config
        elif legacy_config is not None:
            self._tenant_config = TenantConfig()
        else:
            self._tenant_config = get_tenant_config()

    def _resolve_credentials(self) -> tuple[str, str, str]:
        if self._legacy_config is not None:
            tenant_id = self._legacy_config.graph.tenant_id
            client_id = self._legacy_config.graph.client_id
            client_secret = self._legacy_config.graph.client_secret
        else:
            cfg = self._tenant_config.azure
            tenant_id = cfg.tenant_id
            client_id = cfg.client_id
            client_secret = cfg.client_secret

        if not tenant_id or not client_id:
            raise AuthConfigurationError(
                "Power Automate admin not configured: missing tenant_id or client_id."
            )
        if not client_secret:
            raise AuthConfigurationError(
                "Power Automate admin not configured: client_secret is required for "
                "Add-PowerAppsAccount service-principal auth."
            )
        return tenant_id, client_id, client_secret

    def _command_env(self) -> dict[str, str]:
        tenant_id, client_id, client_secret = self._resolve_credentials()
        env = os.environ.copy()
        env[_PW_TENANT_ENV] = tenant_id
        env[_PW_CLIENT_ID_ENV] = client_id
        env[_PW_CLIENT_SECRET_ENV] = client_secret
        return env

    def _run_powershell_json(self, script_body: str, *, modules: tuple[str, ...]) -> Any:
        pwsh = shutil.which("pwsh")
        if not pwsh:
            raise SmarthausError("Power Automate admin runtime not configured: pwsh not found")

        import_lines = [f"Import-Module {module} -ErrorAction Stop" for module in modules]
        script = "\n".join(
            [
                "$ErrorActionPreference = 'Stop'",
                *import_lines,
                (
                    "Add-PowerAppsAccount -Endpoint prod "
                    f"-TenantID $env:{_PW_TENANT_ENV} "
                    f"-ApplicationId $env:{_PW_CLIENT_ID_ENV} "
                    f"-ClientSecret $env:{_PW_CLIENT_SECRET_ENV} | Out-Null"
                ),
                script_body,
            ]
        )
        proc = subprocess.run(
            [pwsh, "-NoLogo", "-NoProfile", "-Command", script],
            check=False,
            capture_output=True,
            text=True,
            env=self._command_env(),
        )
        if proc.returncode != 0:
            stderr = proc.stderr.strip() or proc.stdout.strip() or "unknown PowerShell failure"
            raise SmarthausError(f"Power Automate admin command failed: {stderr}")

        stdout = proc.stdout.strip()
        if not stdout:
            return None
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise SmarthausError(
                f"Power Automate admin command returned non-JSON output: {stdout}"
            ) from exc

    @staticmethod
    def _normalize_list(payload: Any) -> list[Any]:
        if payload is None:
            return []
        if isinstance(payload, list):
            return payload
        return [payload]

    def list_flows_admin(self, environment_name: str) -> list[dict[str, Any]]:
        payload = self._run_powershell_json(
            (
                f"$result = Get-AdminFlow -EnvironmentName {_ps_string(environment_name)}\n"
                "$result | ConvertTo-Json -Depth 25 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )
        return [item for item in self._normalize_list(payload) if isinstance(item, dict)]

    def get_flow_admin(self, environment_name: str, flow_name: str) -> dict[str, Any]:
        payload = self._run_powershell_json(
            (
                "$result = Get-AdminFlow "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)}\n"
                "$result | ConvertTo-Json -Depth 25 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )
        if isinstance(payload, dict):
            return payload
        items = self._normalize_list(payload)
        return items[0] if items and isinstance(items[0], dict) else {}

    def list_http_flows(self, environment_name: str) -> list[dict[str, Any]]:
        payload = self._run_powershell_json(
            (
                "$result = Get-AdminFlowWithHttpAction "
                f"-EnvironmentName {_ps_string(environment_name)}\n"
                "$result | ConvertTo-Json -Depth 25 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )
        return [item for item in self._normalize_list(payload) if isinstance(item, dict)]

    def list_flow_owners(self, environment_name: str, flow_name: str) -> list[dict[str, Any]]:
        payload = self._run_powershell_json(
            (
                "$result = Get-AdminFlowOwnerRole "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)}\n"
                "$result | ConvertTo-Json -Depth 25 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )
        return [item for item in self._normalize_list(payload) if isinstance(item, dict)]

    def list_flow_runs(self, environment_name: str, flow_name: str) -> list[dict[str, Any]]:
        payload = self._run_powershell_json(
            (
                "$result = Get-FlowRun "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)}\n"
                "$result | ConvertTo-Json -Depth 25 -Compress"
            ),
            modules=(_MAKER_MODULE,),
        )
        return [item for item in self._normalize_list(payload) if isinstance(item, dict)]

    def set_flow_owner_role(
        self,
        environment_name: str,
        flow_name: str,
        principal_object_id: str,
        *,
        role_name: str = "CanEdit",
        principal_type: str = "User",
    ) -> dict[str, Any]:
        return self._run_powershell_json(
            (
                "Set-AdminFlowOwnerRole "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)} "
                f"-PrincipalType {_ps_string(principal_type)} "
                f"-RoleName {_ps_string(role_name)} "
                f"-PrincipalObjectId {_ps_string(principal_object_id)} | Out-Null\n"
                "$result = @{"
                f"flowName = {_ps_string(flow_name)};"
                f"principalObjectId = {_ps_string(principal_object_id)};"
                f"roleName = {_ps_string(role_name)};"
                "status = 'updated'"
                "}\n"
                "$result | ConvertTo-Json -Depth 10 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )

    def remove_flow_owner_role(
        self,
        environment_name: str,
        flow_name: str,
        role_id: str,
    ) -> dict[str, Any]:
        return self._run_powershell_json(
            (
                "Remove-AdminFlowOwnerRole "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)} "
                f"-RoleId {_ps_string(role_id)} | Out-Null\n"
                "$result = @{"
                f"flowName = {_ps_string(flow_name)};"
                f"roleId = {_ps_string(role_id)};"
                "removed = $true"
                "}\n"
                "$result | ConvertTo-Json -Depth 10 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )

    def enable_flow(self, environment_name: str, flow_name: str) -> dict[str, Any]:
        return self._run_powershell_json(
            (
                "Enable-AdminFlow "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)} | Out-Null\n"
                "$result = @{"
                f"flowName = {_ps_string(flow_name)};"
                "status = 'enabled'"
                "}\n"
                "$result | ConvertTo-Json -Depth 10 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )

    def disable_flow(self, environment_name: str, flow_name: str) -> dict[str, Any]:
        return self._run_powershell_json(
            (
                "Disable-AdminFlow "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)} | Out-Null\n"
                "$result = @{"
                f"flowName = {_ps_string(flow_name)};"
                "status = 'disabled'"
                "}\n"
                "$result | ConvertTo-Json -Depth 10 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )

    def delete_flow(self, environment_name: str, flow_name: str) -> dict[str, Any]:
        return self._run_powershell_json(
            (
                "Remove-AdminFlow "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)} | Out-Null\n"
                "$result = @{"
                f"flowName = {_ps_string(flow_name)};"
                "status = 'deleted'"
                "}\n"
                "$result | ConvertTo-Json -Depth 10 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )

    def restore_flow(self, environment_name: str, flow_name: str) -> dict[str, Any]:
        return self._run_powershell_json(
            (
                "Restore-AdminFlow "
                f"-EnvironmentName {_ps_string(environment_name)} "
                f"-FlowName {_ps_string(flow_name)} | Out-Null\n"
                "$result = @{"
                f"flowName = {_ps_string(flow_name)};"
                "status = 'restored'"
                "}\n"
                "$result | ConvertTo-Json -Depth 10 -Compress"
            ),
            modules=(_ADMIN_MODULE,),
        )

    def invoke_flow_callback(
        self,
        callback_url: str,
        body: Any,
        *,
        headers: dict[str, str] | None = None,
        timeout_seconds: int = 30,
    ) -> dict[str, Any]:
        request_headers = {str(key): str(value) for key, value in (headers or {}).items()}
        kwargs: dict[str, Any]
        if isinstance(body, str):
            kwargs = {"content": body}
        else:
            kwargs = {"json": body}
        response = httpx.post(
            callback_url,
            headers=request_headers or None,
            timeout=max(1, timeout_seconds),
            **kwargs,
        )
        response.raise_for_status()
        try:
            response_payload: Any = response.json()
        except ValueError:
            response_payload = response.text
        return {
            "invoked": True,
            "status_code": response.status_code,
            "response": response_payload,
        }
