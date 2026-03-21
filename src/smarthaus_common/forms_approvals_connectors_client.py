from __future__ import annotations

from typing import Any

from smarthaus_graph.client import GraphClient

from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError, SmarthausError
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config

_GRAPH_V1 = "https://graph.microsoft.com/v1.0"
_GRAPH_BETA = "https://graph.microsoft.com/beta"


class FormsApprovalsConnectorsClient:
    """Bounded Forms / Approvals / Connectors client.

    E3D intentionally implements the programmable surfaces Microsoft exposes
    cleanly today:
    - Approvals app APIs through Microsoft Graph beta with delegated auth.
    - Microsoft 365 Copilot connector APIs through Graph v1/beta.

    Direct Microsoft Forms authoring/response APIs are not exposed here because
    the pack still relies on connector/workbook-backed ingestion rather than a
    stable first-party Forms runtime API.
    """

    def __init__(
        self,
        *,
        tenant_config: TenantConfig | None = None,
        legacy_config: AppConfig | None = None,
    ) -> None:
        self._tenant_config = tenant_config or get_tenant_config()
        self._legacy_config = legacy_config
        self._graph_v1 = GraphClient(
            tenant_config=self._tenant_config,
            config=self._legacy_config,
            base_url=_GRAPH_V1,
        )
        self._graph_beta = GraphClient(
            tenant_config=self._tenant_config,
            config=self._legacy_config,
            base_url=_GRAPH_BETA,
        )

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

    def _require_delegated_approvals(self) -> None:
        if self._tenant_config.auth.mode not in {"delegated", "hybrid"}:
            raise AuthConfigurationError(
                "Approvals app actions require delegated or hybrid auth mode."
            )

    def _graph_request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        beta: bool = False,
        prefer_delegated: bool = False,
    ) -> tuple[dict[str, Any] | list[Any] | None, dict[str, str]]:
        client = self._graph_beta if beta else self._graph_v1
        response = client._request(  # noqa: SLF001 - bounded internal runtime reuse
            method,
            path,
            json=json_body,
            params=params,
            prefer_delegated=prefer_delegated,
        )
        if not response.content:
            return None, dict(response.headers)
        try:
            return response.json(), dict(response.headers)
        except ValueError as exc:  # pragma: no cover - fail closed
            raise SmarthausError(
                f"Forms/Approvals/Connectors request returned non-JSON output: {response.text[:200]}"
            ) from exc

    @staticmethod
    def _extract_operation_result(
        headers: dict[str, str],
        *,
        status: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {"status": status}
        if extra:
            result.update(extra)
        location = headers.get("Location") or headers.get("location")
        if location:
            result["location"] = location
            result["operationId"] = location.rstrip("/").rsplit("/", 1)[-1]
        request_id = (
            headers.get("request-id") or headers.get("Request-Id") or headers.get("x-ms-request-id")
        )
        if request_id:
            result["requestId"] = request_id
        return result

    def get_approval_solution(self) -> dict[str, Any]:
        self._require_delegated_approvals()
        payload, _ = self._graph_request(
            "GET",
            "/solutions/approval",
            beta=True,
            prefer_delegated=True,
        )
        return self._normalize_object(payload)

    def list_approval_items(self, *, top: int = 50) -> list[dict[str, Any]]:
        self._require_delegated_approvals()
        payload, _ = self._graph_request(
            "GET",
            "/solutions/approval/approvalItems",
            params={"$top": min(max(1, top), 999)},
            beta=True,
            prefer_delegated=True,
        )
        return self._normalize_list(payload)

    def get_approval_item(self, approval_id: str) -> dict[str, Any]:
        self._require_delegated_approvals()
        payload, _ = self._graph_request(
            "GET",
            f"/solutions/approval/approvalItems/{approval_id}",
            beta=True,
            prefer_delegated=True,
        )
        return self._normalize_object(payload)

    def create_approval_item(
        self,
        *,
        display_name: str,
        description: str,
        approver_user_ids: list[str],
        approver_group_ids: list[str] | None = None,
        approval_type: str = "basic",
        allow_email_notification: bool = True,
    ) -> dict[str, Any]:
        self._require_delegated_approvals()
        approvers: list[dict[str, Any]] = []
        for user_id in approver_user_ids:
            approvers.append({"user": {"id": user_id}})
        for group_id in approver_group_ids or []:
            approvers.append({"group": {"id": group_id}})
        if not approvers:
            raise SmarthausError("Approvals create requires at least one approver.")
        _, headers = self._graph_request(
            "POST",
            "/solutions/approval/approvalItems",
            json_body={
                "approvers": approvers,
                "displayName": display_name,
                "description": description,
                "approvalType": approval_type,
                "allowEmailNotification": allow_email_notification,
            },
            beta=True,
            prefer_delegated=True,
        )
        return self._extract_operation_result(
            headers,
            status="accepted",
            extra={"displayName": display_name},
        )

    def list_approval_item_requests(
        self, approval_id: str, *, top: int = 50
    ) -> list[dict[str, Any]]:
        self._require_delegated_approvals()
        payload, _ = self._graph_request(
            "GET",
            f"/solutions/approval/approvalItems/{approval_id}/requests",
            params={"$top": min(max(1, top), 999)},
            beta=True,
            prefer_delegated=True,
        )
        return self._normalize_list(payload)

    def respond_to_approval_item(
        self,
        approval_id: str,
        *,
        response: str,
        comments: str | None = None,
    ) -> dict[str, Any]:
        self._require_delegated_approvals()
        body: dict[str, Any] = {"response": response}
        if comments:
            body["comments"] = comments
        _, headers = self._graph_request(
            "POST",
            f"/solutions/approval/approvalItems/{approval_id}/responses",
            json_body=body,
            beta=True,
            prefer_delegated=True,
        )
        return self._extract_operation_result(
            headers,
            status="accepted",
            extra={"approvalId": approval_id, "response": response},
        )

    def list_external_connections(self, *, top: int = 50) -> list[dict[str, Any]]:
        payload, _ = self._graph_request(
            "GET",
            "/external/connections",
            params={"$top": min(max(1, top), 999)},
        )
        return self._normalize_list(payload)

    def get_external_connection(self, connection_id: str) -> dict[str, Any]:
        payload, _ = self._graph_request("GET", f"/external/connections/{connection_id}")
        return self._normalize_object(payload)

    def create_external_connection(
        self,
        *,
        connection_id: str,
        name: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"id": connection_id, "name": name}
        if description:
            body["description"] = description
        payload, _ = self._graph_request("POST", "/external/connections", json_body=body)
        result = self._normalize_object(payload)
        if not result:
            result = body
        return result

    def register_external_connection_schema(
        self,
        connection_id: str,
        *,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        payload, _ = self._graph_request(
            "PATCH",
            f"/external/connections/{connection_id}/schema",
            json_body=schema,
        )
        result = self._normalize_object(payload)
        if not result:
            result = {"connectionId": connection_id, "status": "registered"}
        result.setdefault("connectionId", connection_id)
        result.setdefault("status", "registered")
        return result

    def get_external_item(self, connection_id: str, item_id: str) -> dict[str, Any]:
        payload, _ = self._graph_request(
            "GET",
            f"/external/connections/{connection_id}/items/{item_id}",
        )
        return self._normalize_object(payload)

    def upsert_external_item(
        self,
        connection_id: str,
        item_id: str,
        *,
        acl: list[dict[str, Any]],
        properties: dict[str, Any],
        content: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"acl": acl, "properties": properties}
        if content:
            body["content"] = content
        payload, _ = self._graph_request(
            "PUT",
            f"/external/connections/{connection_id}/items/{item_id}",
            json_body=body,
        )
        result = self._normalize_object(payload)
        if not result:
            result = {"itemId": item_id, "status": "upserted"}
        result.setdefault("itemId", item_id)
        result.setdefault("status", "upserted")
        return result

    def create_external_group(
        self,
        connection_id: str,
        *,
        group_id: str,
        display_name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"id": group_id}
        if display_name:
            body["displayName"] = display_name
        if description:
            body["description"] = description
        payload, _ = self._graph_request(
            "POST",
            f"/external/connections/{connection_id}/groups",
            json_body=body,
            beta=True,
        )
        result = self._normalize_object(payload)
        if not result:
            result = body
        return result

    def add_external_group_member(
        self,
        connection_id: str,
        group_id: str,
        *,
        member_id: str,
        member_type: str = "user",
        identity_source: str = "azureActiveDirectory",
    ) -> dict[str, Any]:
        self._graph_request(
            "POST",
            f"/external/connections/{connection_id}/groups/{group_id}/members",
            json_body={
                "id": member_id,
                "type": member_type,
                "identitySource": identity_source,
            },
            beta=True,
        )
        return {"groupId": group_id, "memberId": member_id, "status": "added"}
