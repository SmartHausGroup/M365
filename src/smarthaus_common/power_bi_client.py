from __future__ import annotations

import time
from typing import Any

import httpx
from msal import ConfidentialClientApplication

from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError, SmarthausError
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config
from smarthaus_graph.client import _load_client_certificate_credential

_POWER_BI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
_POWER_BI_BASE_URL = "https://api.powerbi.com/v1.0/myorg"


class PowerBIClient:
    """Bounded Power BI admin/runtime client.

    E3C is intentionally limited to workspace, report, dataset, dashboard, and
    dataset-refresh surfaces. The client fails closed when service-principal
    identity is missing.
    """

    def __init__(
        self,
        *,
        tenant_config: TenantConfig | None = None,
        legacy_config: AppConfig | None = None,
    ) -> None:
        self._tenant_config = tenant_config or get_tenant_config()
        self._legacy_config = legacy_config
        self._cca: ConfidentialClientApplication | None = None
        self._cached_token: str | None = None
        self._cached_token_expires_at = 0.0

    def _resolve_identity(self) -> tuple[str, str, str | dict[str, Any]]:
        if self._legacy_config is not None:
            tenant_id = self._legacy_config.graph.tenant_id
            client_id = self._legacy_config.graph.client_id
            client_secret = self._legacy_config.graph.client_secret
            if not tenant_id or not client_id or not client_secret:
                raise AuthConfigurationError(
                    "Power BI not configured: missing tenant_id, client_id, or client_secret."
                )
            return tenant_id, client_id, client_secret

        cfg = self._tenant_config.azure
        if not cfg.tenant_id or not cfg.client_id:
            raise AuthConfigurationError(
                "Power BI not configured: missing tenant_id or client_id."
            )
        if cfg.client_certificate_path:
            return (
                cfg.tenant_id,
                cfg.client_id,
                _load_client_certificate_credential(cfg.client_certificate_path),
            )
        if cfg.client_secret:
            return cfg.tenant_id, cfg.client_id, cfg.client_secret
        raise AuthConfigurationError(
            "Power BI not configured: set client_secret or client_certificate_path."
        )

    def _ensure_cca(self) -> ConfidentialClientApplication:
        if self._cca is not None:
            return self._cca
        tenant_id, client_id, credential = self._resolve_identity()
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        self._cca = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=credential,
            authority=authority,
        )
        return self._cca

    def _get_token(self) -> str:
        if self._cached_token and time.time() < (self._cached_token_expires_at - 60):
            return self._cached_token

        cca = self._ensure_cca()
        result = cca.acquire_token_silent([_POWER_BI_SCOPE], account=None)
        if not result:
            result = cca.acquire_token_for_client(scopes=[_POWER_BI_SCOPE])
        if "access_token" not in result:
            raise AuthConfigurationError(
                f"Failed to acquire Power BI token: {result.get('error_description')}"
            )
        self._cached_token = str(result["access_token"])
        self._cached_token_expires_at = time.time() + int(result.get("expires_in", 3600))
        return self._cached_token

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any] | list[Any] | None, httpx.Response]:
        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method,
                f"{_POWER_BI_BASE_URL}{path}",
                headers=headers,
                params=params,
                json=json_body,
            )
        if response.status_code >= 400:
            detail = response.text.strip() or "unknown Power BI failure"
            raise SmarthausError(f"Power BI request failed ({response.status_code}): {detail}")
        if not response.content:
            return None, response
        try:
            return response.json(), response
        except ValueError as exc:
            raise SmarthausError(
                f"Power BI request returned non-JSON output: {response.text[:200]}"
            ) from exc

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

    def list_workspaces(self) -> list[dict[str, Any]]:
        payload, _ = self._request("GET", "/groups")
        return self._normalize_list(payload)

    def get_workspace(self, workspace_id: str) -> dict[str, Any]:
        payload, _ = self._request("GET", f"/groups/{workspace_id}")
        return self._normalize_object(payload)

    def list_reports(self, workspace_id: str) -> list[dict[str, Any]]:
        payload, _ = self._request("GET", f"/groups/{workspace_id}/reports")
        return self._normalize_list(payload)

    def get_report(self, workspace_id: str, report_id: str) -> dict[str, Any]:
        payload, _ = self._request("GET", f"/groups/{workspace_id}/reports/{report_id}")
        return self._normalize_object(payload)

    def list_datasets(self, workspace_id: str) -> list[dict[str, Any]]:
        payload, _ = self._request("GET", f"/groups/{workspace_id}/datasets")
        return self._normalize_list(payload)

    def get_dataset(self, workspace_id: str, dataset_id: str) -> dict[str, Any]:
        payload, _ = self._request("GET", f"/groups/{workspace_id}/datasets/{dataset_id}")
        return self._normalize_object(payload)

    def refresh_dataset(
        self,
        workspace_id: str,
        dataset_id: str,
        *,
        notify_option: str = "NoNotification",
    ) -> dict[str, Any]:
        _, response = self._request(
            "POST",
            f"/groups/{workspace_id}/datasets/{dataset_id}/refreshes",
            json_body={"notifyOption": notify_option},
        )
        result: dict[str, Any] = {
            "workspaceId": workspace_id,
            "datasetId": dataset_id,
            "status": "queued",
        }
        request_id = response.headers.get("RequestId") or response.headers.get("x-ms-request-id")
        location = response.headers.get("Location")
        if request_id:
            result["requestId"] = request_id
        if location:
            result["location"] = location
        return result

    def list_dataset_refreshes(self, workspace_id: str, dataset_id: str) -> list[dict[str, Any]]:
        payload, _ = self._request("GET", f"/groups/{workspace_id}/datasets/{dataset_id}/refreshes")
        return self._normalize_list(payload)

    def list_dashboards(self, workspace_id: str) -> list[dict[str, Any]]:
        payload, _ = self._request("GET", f"/groups/{workspace_id}/dashboards")
        return self._normalize_list(payload)

    def get_dashboard(self, workspace_id: str, dashboard_id: str) -> dict[str, Any]:
        payload, _ = self._request("GET", f"/groups/{workspace_id}/dashboards/{dashboard_id}")
        return self._normalize_object(payload)
