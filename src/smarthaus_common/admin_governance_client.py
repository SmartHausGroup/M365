from __future__ import annotations

import csv
from io import StringIO
from typing import Any

from smarthaus_graph.client import GraphClient

from smarthaus_common.config import AppConfig
from smarthaus_common.errors import GraphRequestError
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config

_REPORT_DEFINITIONS: dict[str, dict[str, str]] = {
    "office365_active_user_detail": {
        "category": "usage",
        "function": "getOffice365ActiveUserDetail",
    },
    "email_activity_user_detail": {
        "category": "activity",
        "function": "getEmailActivityUserDetail",
    },
    "teams_user_activity_user_detail": {
        "category": "activity",
        "function": "getTeamsUserActivityUserDetail",
    },
    "sharepoint_activity_user_detail": {
        "category": "activity",
        "function": "getSharePointActivityUserDetail",
    },
    "onedrive_activity_user_detail": {
        "category": "activity",
        "function": "getOneDriveActivityUserDetail",
    },
}
_REPORT_CATEGORY_DEFAULTS = {
    "usage": "office365_active_user_detail",
    "activity": "email_activity_user_detail",
}
_ALLOWED_REPORT_PERIODS = {"D7", "D30", "D90", "D180"}


class AdminGovernanceClient:
    """Bounded E4E runtime for admin reports and access-review governance."""

    def __init__(
        self,
        tenant_config: TenantConfig | None = None,
        legacy_config: AppConfig | None = None,
    ):
        self._tenant_config = tenant_config or get_tenant_config()
        self._graph = GraphClient(
            tenant_config=self._tenant_config,
            config=legacy_config,
        )

    def _resolve_report_name(self, report_name: str | None, category: str | None) -> str:
        normalized_category = (category or "").strip().lower() or None
        normalized_report = (report_name or "").strip().lower() or None
        if not normalized_report and normalized_category:
            normalized_report = _REPORT_CATEGORY_DEFAULTS.get(normalized_category)
        if not normalized_report or normalized_report not in _REPORT_DEFINITIONS:
            raise GraphRequestError(
                "Unsupported reportName. Expected one of: " + ", ".join(sorted(_REPORT_DEFINITIONS))
            )
        if normalized_category:
            report_category = _REPORT_DEFINITIONS[normalized_report]["category"]
            if report_category != normalized_category:
                raise GraphRequestError(
                    f"Report '{normalized_report}' does not belong to category '{normalized_category}'."
                )
        return normalized_report

    def _normalize_period(self, period: str | None) -> str:
        normalized = (period or "D7").strip().upper()
        if normalized not in _ALLOWED_REPORT_PERIODS:
            raise GraphRequestError(
                "Unsupported period. Expected one of: " + ", ".join(sorted(_ALLOWED_REPORT_PERIODS))
            )
        return normalized

    def _read_csv_rows(self, csv_payload: str) -> list[dict[str, str]]:
        if not csv_payload.strip():
            return []
        return list(csv.DictReader(StringIO(csv_payload)))

    def get_report(
        self,
        report_name: str,
        *,
        period: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        resolved_report = self._resolve_report_name(report_name, category)
        resolved_period = self._normalize_period(period)
        definition = _REPORT_DEFINITIONS[resolved_report]
        response = self._graph._request(
            "GET",
            f"/reports/{definition['function']}(period='{resolved_period}')",
            headers={"Accept": "text/csv"},
            follow_redirects=True,
        )
        rows = self._read_csv_rows(response.text)
        return {
            "name": resolved_report,
            "category": definition["category"],
            "period": resolved_period,
            "format": "csv",
            "rows": rows,
            "count": len(rows),
        }

    def get_usage_reports(
        self,
        report_name: str | None = None,
        *,
        period: str | None = None,
    ) -> dict[str, Any]:
        resolved_report = self._resolve_report_name(report_name, "usage")
        return self.get_report(resolved_report, period=period, category="usage")

    def get_activity_reports(
        self,
        report_name: str | None = None,
        *,
        period: str | None = None,
    ) -> dict[str, Any]:
        resolved_report = self._resolve_report_name(report_name, "activity")
        return self.get_report(resolved_report, period=period, category="activity")

    def list_access_reviews(self, *, top: int = 50) -> list[dict[str, Any]]:
        response = self._graph._request(
            "GET",
            "/identityGovernance/accessReviews/definitions",
            params={"$top": top},
        )
        payload = response.json()
        return list(payload.get("value", []))

    def get_access_review(self, review_id: str) -> dict[str, Any]:
        response = self._graph._request(
            "GET",
            f"/identityGovernance/accessReviews/definitions/{review_id}",
        )
        return response.json()

    def create_access_review(self, *, body: dict[str, Any]) -> dict[str, Any]:
        response = self._graph._request(
            "POST",
            "/identityGovernance/accessReviews/definitions",
            json=body,
        )
        return response.json()

    def list_access_review_decisions(
        self,
        review_id: str,
        instance_id: str,
        *,
        top: int = 50,
    ) -> list[dict[str, Any]]:
        response = self._graph._request(
            "GET",
            f"/identityGovernance/accessReviews/definitions/{review_id}/instances/{instance_id}/decisions",
            params={"$top": top},
        )
        payload = response.json()
        return list(payload.get("value", []))

    def record_access_review_decision(
        self,
        review_id: str,
        instance_id: str,
        decision_id: str,
        *,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        self._graph._request(
            "PATCH",
            (
                "/identityGovernance/accessReviews/definitions/"
                f"{review_id}/instances/{instance_id}/decisions/{decision_id}"
            ),
            json=body,
        )
        return {
            "updated": True,
            "reviewId": review_id,
            "instanceId": instance_id,
            "decisionId": decision_id,
        }
