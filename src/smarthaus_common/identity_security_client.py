from __future__ import annotations

from typing import Any

from smarthaus_graph.client import GraphClient

from smarthaus_common.config import AppConfig
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config


class IdentitySecurityClient:
    """Bounded Conditional Access / Identity Protection client."""

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

    def list_conditional_access_policies(self, *, top: int = 50) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/identity/conditionalAccess/policies",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)

    def get_conditional_access_policy(self, policy_id: str) -> dict[str, Any]:
        payload = self._graph._request(
            "GET",
            f"/identity/conditionalAccess/policies/{policy_id}",
        ).json()
        return self._normalize_object(payload)

    def create_conditional_access_policy(self, *, body: dict[str, Any]) -> dict[str, Any]:
        payload = self._graph._request(
            "POST",
            "/identity/conditionalAccess/policies",
            json=body,
        ).json()
        return self._normalize_object(payload)

    def update_conditional_access_policy(
        self,
        policy_id: str,
        *,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        self._graph._request(
            "PATCH",
            f"/identity/conditionalAccess/policies/{policy_id}",
            json=body,
        )
        return {"updated": True, "policyId": policy_id}

    def delete_conditional_access_policy(self, policy_id: str) -> dict[str, Any]:
        self._graph._request(
            "DELETE",
            f"/identity/conditionalAccess/policies/{policy_id}",
        )
        return {"deleted": True, "policyId": policy_id}

    def list_named_locations(self, *, top: int = 50) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/identity/conditionalAccess/namedLocations",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)

    def list_risk_detections(self, *, top: int = 50) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/identityProtection/riskDetections",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)
