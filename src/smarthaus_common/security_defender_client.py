from __future__ import annotations

from typing import Any

from smarthaus_graph.client import GraphClient

from smarthaus_common.config import AppConfig
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config


class SecurityDefenderClient:
    """Bounded Microsoft 365 security / Defender client."""

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

    def list_security_alerts(self, *, top: int = 50) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/security/alerts_v2",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)

    def get_security_alert(self, alert_id: str) -> dict[str, Any]:
        payload = self._graph._request("GET", f"/security/alerts_v2/{alert_id}").json()
        return self._normalize_object(payload)

    def list_security_incidents(self, *, top: int = 50) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/security/incidents",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)

    def get_security_incident(self, incident_id: str) -> dict[str, Any]:
        payload = self._graph._request("GET", f"/security/incidents/{incident_id}").json()
        return self._normalize_object(payload)

    def list_secure_scores(self, *, top: int = 25) -> list[dict[str, Any]]:
        payload = self._graph._request(
            "GET",
            "/security/secureScores",
            params={"$top": min(max(1, top), 999)},
        ).json()
        return self._normalize_list(payload)

    def get_secure_score_profile(self, profile_id: str) -> dict[str, Any]:
        payload = self._graph._request(
            "GET",
            f"/security/secureScoreControlProfiles/{profile_id}",
        ).json()
        return self._normalize_object(payload)

    def update_security_incident(
        self,
        incident_id: str,
        *,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        self._graph._request("PATCH", f"/security/incidents/{incident_id}", json=body)
        return {"updated": True, "incidentId": incident_id}
