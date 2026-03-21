from __future__ import annotations

from typing import Any

from smarthaus_common.config import AppConfig
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config
from smarthaus_graph.client import GraphClient


class IntuneDevicesClient:
    """Bounded Intune / managed-devices client."""

    def __init__(
        self,
        *,
        tenant_config: TenantConfig | None = None,
        legacy_config: AppConfig | None = None,
    ) -> None:
        self._tenant_config = tenant_config or get_tenant_config()
        self._legacy_config = legacy_config
        self._graph = GraphClient(tenant_config=self._tenant_config, config=self._legacy_config)

    @staticmethod
    def _normalize_list(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict) and isinstance(payload.get("value"), list):
            return [item for item in payload["value"] if isinstance(item, dict)]
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    @staticmethod
    def _normalize_object(payload: Any) -> dict[str, Any]:
        if isinstance(payload, dict):
            return payload
        return {}

    def list_devices(self, *, top: int = 50) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/deviceManagement/managedDevices",
            params={
                "$top": min(max(1, top), 999),
                "$select": "id,deviceName,operatingSystem,osVersion,complianceState,userPrincipalName",
            },
        ).json()
        return self._normalize_list(payload)

    def get_device(self, device_id: str) -> dict[str, Any]:
        payload = self._graph._request(
            "GET",
            f"/deviceManagement/managedDevices/{device_id}",
            params={
                "$select": "id,deviceName,operatingSystem,osVersion,complianceState,userPrincipalName",
            },
        ).json()
        return self._normalize_object(payload)

    def list_device_compliance_summaries(self) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/deviceManagement/deviceCompliancePolicySettingStateSummaries",
        ).json()
        return self._normalize_list(payload)

    def execute_device_action(self, device_id: str, *, action: str) -> dict[str, Any]:
        self._graph._request("POST", f"/deviceManagement/managedDevices/{device_id}/{action}")
        return {"executed": True, "deviceId": device_id, "action": action}
