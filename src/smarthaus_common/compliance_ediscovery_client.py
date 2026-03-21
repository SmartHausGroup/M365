from __future__ import annotations

from typing import Any

from smarthaus_common.config import AppConfig
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config
from smarthaus_graph.client import GraphClient


class ComplianceEDiscoveryClient:
    """Bounded Microsoft 365 compliance / eDiscovery client."""

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

    def list_ediscovery_cases(self, *, top: int = 50) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/security/cases/ediscoveryCases",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)

    def get_ediscovery_case(self, case_id: str) -> dict[str, Any]:
        payload = self._graph._request(
            "GET",
            f"/security/cases/ediscoveryCases/{case_id}",
        ).json()
        return self._normalize_object(payload)

    def create_ediscovery_case(self, *, body: dict[str, Any]) -> dict[str, Any]:
        payload = self._graph._request(
            "POST",
            "/security/cases/ediscoveryCases",
            json=body,
        ).json()
        return self._normalize_object(payload)

    def list_ediscovery_case_searches(
        self,
        case_id: str,
        *,
        top: int = 50,
    ) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            f"/security/cases/ediscoveryCases/{case_id}/searches",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)

    def get_ediscovery_case_search(self, case_id: str, search_id: str) -> dict[str, Any]:
        payload = self._graph._request(
            "GET",
            f"/security/cases/ediscoveryCases/{case_id}/searches/{search_id}",
        ).json()
        return self._normalize_object(payload)

    def create_ediscovery_case_search(
        self,
        case_id: str,
        *,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        payload = self._graph._request(
            "POST",
            f"/security/cases/ediscoveryCases/{case_id}/searches",
            json=body,
        ).json()
        return self._normalize_object(payload)

    def list_ediscovery_case_custodians(
        self,
        case_id: str,
        *,
        top: int = 50,
    ) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            f"/security/cases/ediscoveryCases/{case_id}/custodians",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)

    def list_ediscovery_case_legal_holds(
        self,
        case_id: str,
        *,
        top: int = 50,
    ) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            f"/security/cases/ediscoveryCases/{case_id}/legalHolds",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)
