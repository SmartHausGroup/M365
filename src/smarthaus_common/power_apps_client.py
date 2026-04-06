from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError, SmarthausError
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config

_ADMIN_MODULE = "Microsoft.PowerApps.Administration.PowerShell"
_PW_TENANT_ENV = "SMARTHAUS_PP_TENANT_ID"
_PW_CLIENT_ID_ENV = "SMARTHAUS_PP_CLIENT_ID"
_PW_CLIENT_SECRET_ENV = "SMARTHAUS_PP_CLIENT_SECRET"


def _ps_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _load_json_payload(stdout: str) -> Any:
    payload = stdout.strip()
    if not payload:
        return None
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        lines = [line.strip() for line in payload.splitlines() if line.strip()]
        if not lines:
            return None
        return json.loads(lines[-1])


class PowerAppsClient:
    """Bounded Power Apps admin client.

    The supported service-principal path is intentionally limited to the
    official Power Apps administration PowerShell module. If the required
    module or client-secret credentials are missing, the client fails closed.
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
                "Power Apps admin not configured: missing tenant_id or client_id."
            )
        if not client_secret:
            raise AuthConfigurationError(
                "Power Apps admin not configured: client_secret is required for "
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

    def _run_powershell_json(self, script_body: str) -> Any:
        pwsh = shutil.which("pwsh")
        if not pwsh:
            raise SmarthausError("Power Apps admin runtime not configured: pwsh not found")

        script = "\n".join(
            [
                "$ErrorActionPreference = 'Stop'",
                f"Import-Module {_ADMIN_MODULE} -DisableNameChecking -ErrorAction Stop",
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
            raise SmarthausError(f"Power Apps admin command failed: {stderr}")

        stdout = proc.stdout.strip()
        if not stdout:
            return None
        try:
            return _load_json_payload(stdout)
        except json.JSONDecodeError as exc:
            raise SmarthausError(
                f"Power Apps admin command returned non-JSON output: {stdout}"
            ) from exc

    @staticmethod
    def _normalize_list(payload: Any) -> list[Any]:
        if payload is None:
            return []
        if isinstance(payload, list):
            return payload
        return [payload]

    def list_powerapps_admin(
        self,
        *,
        environment_name: str | None = None,
        owner: str | None = None,
        filter_text: str | None = None,
    ) -> list[dict[str, Any]]:
        command = "Get-AdminPowerApp"
        if environment_name:
            command += f" -EnvironmentName {_ps_string(environment_name)}"
        if owner:
            command += f" -Owner {_ps_string(owner)}"
        if filter_text:
            command += f" -Filter {_ps_string(filter_text)}"
        payload = self._run_powershell_json(
            f"$result = {command}\n$result | ConvertTo-Json -Depth 25 -Compress"
        )
        return [item for item in self._normalize_list(payload) if isinstance(item, dict)]

    def get_powerapp_admin(self, environment_name: str, app_name: str) -> dict[str, Any]:
        payload = self._run_powershell_json(
            "$result = Get-AdminPowerApp "
            f"-EnvironmentName {_ps_string(environment_name)} "
            f"-AppName {_ps_string(app_name)}\n"
            "$result | ConvertTo-Json -Depth 25 -Compress"
        )
        if isinstance(payload, dict):
            return payload
        items = self._normalize_list(payload)
        return items[0] if items and isinstance(items[0], dict) else {}

    def list_powerapp_role_assignments(
        self,
        environment_name: str,
        app_name: str,
        *,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        command = (
            "Get-AdminPowerAppRoleAssignment "
            f"-EnvironmentName {_ps_string(environment_name)} "
            f"-AppName {_ps_string(app_name)}"
        )
        if user_id:
            command += f" -UserId {_ps_string(user_id)}"
        payload = self._run_powershell_json(
            f"$result = {command}\n$result | ConvertTo-Json -Depth 25 -Compress"
        )
        return [item for item in self._normalize_list(payload) if isinstance(item, dict)]

    def set_powerapp_owner(
        self,
        environment_name: str,
        app_name: str,
        owner_object_id: str,
    ) -> dict[str, Any]:
        return self._run_powershell_json(
            "Set-AdminPowerAppOwner "
            f"-EnvironmentName {_ps_string(environment_name)} "
            f"-AppName {_ps_string(app_name)} "
            f"-AppOwner {_ps_string(owner_object_id)} | Out-Null\n"
            "$result = @{"
            f"appName = {_ps_string(app_name)};"
            f"ownerObjectId = {_ps_string(owner_object_id)};"
            "status = 'updated'"
            "}\n"
            "$result | ConvertTo-Json -Depth 10 -Compress"
        )

    def remove_powerapp_role_assignment(
        self,
        environment_name: str,
        app_name: str,
        role_id: str,
    ) -> dict[str, Any]:
        return self._run_powershell_json(
            "Remove-AdminPowerAppRoleAssignment "
            f"-EnvironmentName {_ps_string(environment_name)} "
            f"-AppName {_ps_string(app_name)} "
            f"-RoleId {_ps_string(role_id)} | Out-Null\n"
            "$result = @{"
            f"appName = {_ps_string(app_name)};"
            f"roleId = {_ps_string(role_id)};"
            "removed = $true"
            "}\n"
            "$result | ConvertTo-Json -Depth 10 -Compress"
        )

    def delete_powerapp(self, environment_name: str, app_name: str) -> dict[str, Any]:
        return self._run_powershell_json(
            "Remove-AdminPowerApp "
            f"-EnvironmentName {_ps_string(environment_name)} "
            f"-AppName {_ps_string(app_name)} | Out-Null\n"
            "$result = @{"
            f"appName = {_ps_string(app_name)};"
            "status = 'deleted'"
            "}\n"
            "$result | ConvertTo-Json -Depth 10 -Compress"
        )

    def list_powerapp_environments(self) -> list[dict[str, Any]]:
        payload = self._run_powershell_json(
            "$result = Get-AdminPowerAppEnvironment\n$result | ConvertTo-Json -Depth 25 -Compress"
        )
        return [item for item in self._normalize_list(payload) if isinstance(item, dict)]

    def get_powerapp_environment(self, environment_name: str) -> dict[str, Any]:
        payload = self._run_powershell_json(
            "$result = Get-AdminPowerAppEnvironment "
            f"-EnvironmentName {_ps_string(environment_name)}\n"
            "$result | ConvertTo-Json -Depth 25 -Compress"
        )
        if isinstance(payload, dict):
            return payload
        items = self._normalize_list(payload)
        return items[0] if items and isinstance(items[0], dict) else {}

    def list_powerapp_environment_role_assignments(
        self,
        environment_name: str,
        *,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        command = (
            "Get-AdminPowerAppEnvironmentRoleAssignment "
            f"-EnvironmentName {_ps_string(environment_name)}"
        )
        if user_id:
            command += f" -UserId {_ps_string(user_id)}"
        payload = self._run_powershell_json(
            f"$result = {command}\n$result | ConvertTo-Json -Depth 25 -Compress"
        )
        return [item for item in self._normalize_list(payload) if isinstance(item, dict)]

    def set_powerapp_environment_role_assignment(
        self,
        environment_name: str,
        principal_object_id: str,
        *,
        role_name: str,
        principal_type: str = "User",
    ) -> dict[str, Any]:
        return self._run_powershell_json(
            "Set-AdminPowerAppEnvironmentRoleAssignment "
            f"-EnvironmentName {_ps_string(environment_name)} "
            f"-RoleName {_ps_string(role_name)} "
            f"-PrincipalType {_ps_string(principal_type)} "
            f"-PrincipalObjectId {_ps_string(principal_object_id)} | Out-Null\n"
            "$result = @{"
            f"environmentName = {_ps_string(environment_name)};"
            f"principalObjectId = {_ps_string(principal_object_id)};"
            f"roleName = {_ps_string(role_name)};"
            "status = 'updated'"
            "}\n"
            "$result | ConvertTo-Json -Depth 10 -Compress"
        )

    def remove_powerapp_environment_role_assignment(
        self,
        environment_name: str,
        role_id: str,
    ) -> dict[str, Any]:
        return self._run_powershell_json(
            "Remove-AdminPowerAppEnvironmentRoleAssignment "
            f"-EnvironmentName {_ps_string(environment_name)} "
            f"-RoleId {_ps_string(role_id)} | Out-Null\n"
            "$result = @{"
            f"environmentName = {_ps_string(environment_name)};"
            f"roleId = {_ps_string(role_id)};"
            "removed = $true"
            "}\n"
            "$result | ConvertTo-Json -Depth 10 -Compress"
        )
