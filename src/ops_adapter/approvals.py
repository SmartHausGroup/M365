from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

import httpx
from smarthaus_common.tenant_config import TenantConfig, get_tenant_config

from .personas import load_persona_registry, project_persona_context

ApprovalUpdateResult = dict[str, list[str]]


def _parse_site_url(site_url: str) -> tuple[str, str]:
    # Returns (hostname, path)
    # e.g., https://contoso.sharepoint.com/sites/ops -> (contoso.sharepoint.com, /sites/ops)
    from urllib.parse import urlparse

    p = urlparse(site_url)
    return p.netloc, p.path


def _selected_tenant_config() -> TenantConfig | None:
    try:
        return get_tenant_config()
    except Exception:
        return None


def _approval_tenant_config() -> TenantConfig | None:
    tenant_cfg = _selected_tenant_config()
    if tenant_cfg is None:
        return None
    try:
        executor_name = tenant_cfg.resolve_executor_name(
            "approvals",
            fallback_keys=["sharepoint"],
        )
        return tenant_cfg.project_executor(executor_name)
    except ValueError:
        return tenant_cfg


def _resolve_approval_setting(
    tenant_field: str,
    env_keys: tuple[str, ...],
    *,
    default: str = "",
) -> str:
    tenant_cfg = _selected_tenant_config()
    if tenant_cfg is not None:
        tenant_value = getattr(tenant_cfg.governance, tenant_field, "")
        if isinstance(tenant_value, str) and tenant_value.strip():
            return tenant_value.strip()

    for key in env_keys:
        value = os.getenv(key)
        if value:
            return value

    return default


def _build_graph_token_provider() -> Any:
    from smarthaus_graph.client import GraphTokenProvider

    return GraphTokenProvider(tenant_config=_approval_tenant_config())


class GraphApprovalsStore:
    def __init__(
        self,
        registry: dict[str, Any] | None = None,
        personas: dict[str, dict[str, Any]] | None = None,
    ):
        self.registry = registry or {}
        self.personas = personas or load_persona_registry(self.registry)
        self.teams_webhook = os.getenv("TEAMS_APPROVALS_WEBHOOK")
        self.site_url = _resolve_approval_setting("approvals_site_url", ("APPROVALS_SITE_URL",))
        self.site_id = _resolve_approval_setting("approvals_site_id", ("APPROVALS_SITE_ID",))
        self.list_id = _resolve_approval_setting("approvals_list_id", ("APPROVALS_LIST_ID",))
        self.list_name = _resolve_approval_setting(
            "approvals_list_name",
            ("APPROVALS_LIST_NAME",),
            default="Approvals",
        )
        if not self.site_id:
            if not self.site_url:
                raise RuntimeError("Set APPROVALS_SITE_URL or APPROVALS_SITE_ID for approvals")
            self.site_id = self._resolve_site_id(self.site_url)
        if not self.list_id:
            self.list_id = self._resolve_list_id(self.site_id, self.list_name)

    def _graph_token(self) -> str:
        provider = _build_graph_token_provider()
        return provider.get_app_token()

    def _graph(self) -> httpx.Client:
        token = self._graph_token()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        return httpx.Client(timeout=15.0, headers=headers)

    def _resolve_site_id(self, site_url: str) -> str:
        host, path = _parse_site_url(site_url)
        with self._graph() as client:
            resp = client.get(f"https://graph.microsoft.com/v1.0/sites/{host}:{path}")
            resp.raise_for_status()
            return resp.json()["id"]

    def _resolve_list_id(self, site_id: str, list_name: str) -> str:
        with self._graph() as client:
            resp = client.get(
                f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists",
                params={"$select": "id,displayName"},
            )
            resp.raise_for_status()
            for item in resp.json().get("value", []):
                if item.get("displayName") == list_name:
                    return item["id"]
            raise RuntimeError(f"Approvals list '{list_name}' not found in site {site_id}")

    def _default_approvers(self, agent: str, action: str) -> list[str]:
        try:
            agent_def = (self.registry or {}).get("agents", {}).get(agent, {})
            for rule in agent_def.get("approval_rules", []) or []:
                if rule.get("action") == action:
                    return rule.get("approvers", []) or []
        except Exception:
            pass
        return []

    def create(self, agent: str, action: str, params: dict[str, Any]) -> str:
        approval_id = str(uuid.uuid4())
        fields = {
            "Title": f"{agent}/{action}",
            "Agent": agent,
            "Action": action,
            "Requestor": params.get("requestor") or "system",
            "Status": "pending",
            "Approvers": ", ".join(self._default_approvers(agent, action)),
            "Params": json.dumps(params),
            "ApprovalId": approval_id,
        }
        body = {"fields": fields}
        with self._graph() as client:
            resp = client.post(
                f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/lists/{self.list_id}/items",
                json=body,
            )
            resp.raise_for_status()
            item = resp.json()
            sp_item_id = item.get("id")
        # Send Teams card
        self._notify_teams(approval_id, agent, action, params)
        return approval_id or sp_item_id

    def get(self, approval_id: str) -> dict[str, Any] | None:
        # Lookup by filtering on field ApprovalId eq approval_id
        with self._graph() as client:
            resp = client.get(
                f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/lists/{self.list_id}/items",
                params={
                    "$expand": "fields",
                    "$filter": f"fields/ApprovalId eq '{approval_id}'",
                    "$select": "id,fields",
                },
            )
            resp.raise_for_status()
            val = resp.json().get("value", [])
            if not val:
                return None
            item = val[0]
            f = item.get("fields", {})
            params = json.loads(f.get("Params") or "{}")
            return {
                "id": f.get("ApprovalId") or item.get("id"),
                "agent": f.get("Agent"),
                "action": f.get("Action"),
                "params": params,
                "persona": params.get("persona"),
                "persona_target": params.get("persona_target"),
                "status": (f.get("Status") or "").lower(),
                "requested_at": f.get("Created"),
                "updated_at": f.get("Modified"),
                "approvers": (f.get("Approvers") or "").split(", ") if f.get("Approvers") else [],
                "requestor": params.get("requestor") or f.get("Requestor"),
                "requestor_tier": params.get("requestor_tier"),
                "requestor_groups": params.get("requestor_groups") or [],
                "executor": params.get("executor_identity"),
                "tenant": params.get("tenant"),
            }

    def set_status(self, approval_id: str, status: str, reason: str | None = None) -> bool:
        # Find list item id
        with self._graph() as client:
            resp = client.get(
                f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/lists/{self.list_id}/items",
                params={
                    "$expand": "fields",
                    "$filter": f"fields/ApprovalId eq '{approval_id}'",
                    "$select": "id",
                },
            )
            resp.raise_for_status()
            val = resp.json().get("value", [])
            if not val:
                return False
            item_id = val[0].get("id")
            patch_fields = {"Status": status}
            if reason:
                patch_fields["Reason"] = reason
            resp2 = client.patch(
                f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/lists/{self.list_id}/items/{item_id}/fields",
                json=patch_fields,
            )
            resp2.raise_for_status()
            return True

    def bulk_set_status(
        self, ids: list[str], status: str, reason: str | None = None
    ) -> ApprovalUpdateResult:
        results: ApprovalUpdateResult = {"updated": [], "not_found": []}
        for i in ids:
            ok = self.set_status(i, status, reason)
            (results["updated"] if ok else results["not_found"]).append(i)
        return results

    def query(
        self,
        agent: str | None = None,
        action: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        filters: list[str] = []
        if agent:
            filters.append(f"fields/Agent eq '{agent}'")
        if action:
            filters.append(f"fields/Action eq '{action}'")
        if status:
            filters.append(f"fields/Status eq '{status}'")
        if start_date:
            filters.append(f"createdDateTime ge {start_date.astimezone(UTC).isoformat()}")
        if end_date:
            filters.append(f"createdDateTime le {end_date.astimezone(UTC).isoformat()}")
        odata_filter = " and ".join(filters) if filters else None

        params = {
            "$expand": "fields($select=ApprovalId,Agent,Action,Status,Approvers,Requestor,Params)",
            "$select": "id,createdDateTime,lastModifiedDateTime",
            "$orderby": "createdDateTime desc",
            "$top": str(max(1, min(limit, 200))),
        }
        if odata_filter:
            params["$filter"] = odata_filter

        with self._graph() as client:
            resp = client.get(
                f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/lists/{self.list_id}/items",
                params=params,
            )
            resp.raise_for_status()
            items = []
            for it in resp.json().get("value", []):
                f = it.get("fields", {})
                params_json = json.loads(f.get("Params") or "{}")
                items.append(
                    {
                        "id": f.get("ApprovalId") or it.get("id"),
                        "agent": f.get("Agent"),
                        "action": f.get("Action"),
                        "persona": params_json.get("persona"),
                        "persona_target": params_json.get("persona_target"),
                        "status": (f.get("Status") or "").lower(),
                        "approvers": (
                            (f.get("Approvers") or "").split(", ") if f.get("Approvers") else []
                        ),
                        "requestor": params_json.get("requestor") or f.get("Requestor"),
                        "requestor_tier": params_json.get("requestor_tier"),
                        "requestor_groups": params_json.get("requestor_groups") or [],
                        "executor": params_json.get("executor_identity"),
                        "tenant": params_json.get("tenant"),
                        "requested_at": it.get("createdDateTime"),
                        "updated_at": it.get("lastModifiedDateTime"),
                    }
                )
            return items

    def _notify_teams(
        self, approval_id: str, agent: str, action: str, params: dict[str, Any]
    ) -> None:
        if not self.teams_webhook:
            return
        persona_payload = params.get("persona")
        if isinstance(persona_payload, dict):
            persona = project_persona_context(persona_payload)
        else:
            persona = project_persona_context(self.personas.get(agent, {}))
        title = f"Approval Required: {agent}/{action}"
        display_name = str(persona.get("display_name") or agent)
        display_title = str(persona.get("title") or agent)
        text_title = f"{display_name} ({display_title})"
        # Signed action URLs
        base = os.getenv("OPS_ADAPTER_PUBLIC_URL", "http://localhost:8080")
        ts = str(int(datetime.now(UTC).timestamp()))
        approve_url = self._signed_action_url(base, approval_id, "approve", ts)
        deny_url = self._signed_action_url(base, approval_id, "deny", ts)
        card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.5",
                        "body": [
                            {"type": "TextBlock", "text": title, "weight": "Bolder", "wrap": True},
                            {
                                "type": "FactSet",
                                "facts": [
                                    {"title": "Agent", "value": text_title},
                                    {"title": "Action", "value": action},
                                    {
                                        "title": "Requestor",
                                        "value": params.get("requestor", "system"),
                                    },
                                    {
                                        "title": "Tier",
                                        "value": params.get("requestor_tier", "unknown"),
                                    },
                                ],
                            },
                            {
                                "type": "Input.Text",
                                "id": "reason",
                                "placeholder": "Optional reason",
                                "isMultiline": True,
                            },
                        ],
                        "actions": [
                            {
                                "type": "Action.Http",
                                "title": "Approve",
                                "method": "POST",
                                "url": approve_url,
                                "body": '{"params":{"reason":"{{reason.value}}"}}',
                            },
                            {
                                "type": "Action.Http",
                                "title": "Deny",
                                "method": "POST",
                                "url": deny_url,
                                "body": '{"params":{"reason":"{{reason.value}}"}}',
                            },
                        ],
                    },
                }
            ],
        }
        try:
            with httpx.Client(timeout=5.0) as client:
                client.post(self.teams_webhook, json=card)
        except Exception:
            pass

    def _signed_action_url(self, base: str, approval_id: str, verb: str, ts: str) -> str:
        secret = os.getenv("TEAMS_CARD_SIGNING_SECRET")
        if not secret:
            return f"{base}/approvals/{approval_id}/{verb}"
        msg = f"{approval_id}|{verb}|{ts}".encode()
        sig = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        qs = urlencode({"ts": ts, "sig": sig})
        return f"{base}/approvals/{approval_id}/{verb}?{qs}"

    @staticmethod
    def verify_signature(approval_id: str, verb: str, ts: str | None, sig: str | None) -> bool:
        secret = os.getenv("TEAMS_CARD_SIGNING_SECRET")
        if not secret:
            # Fail-open if not configured
            return True
        if not ts or not sig:
            return False
        # Check expiration (default 10 minutes)
        max_skew = int(os.getenv("TEAMS_CARD_MAX_SKEW", "600"))
        try:
            ts_int = int(ts)
        except ValueError:
            return False
        now = int(datetime.now(UTC).timestamp())
        if abs(now - ts_int) > max_skew:
            return False
        msg = f"{approval_id}|{verb}|{ts}".encode()
        expected = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig)


class EnterpriseApprovalsProxy:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create(self, agent: str, action: str, params: dict[str, Any]) -> str:
        payload = {
            "agent": agent,
            "action": action,
            "params": params,
            "requester": params.get("requestor") or "system",
            "requester_tier": params.get("requestor_tier"),
            "requester_groups": params.get("requestor_groups") or [],
            "executor": params.get("executor_identity"),
            "tenant": params.get("tenant"),
        }
        with httpx.Client(timeout=10.0) as client:
            r = client.post(f"{self.base_url}/approvals", json=payload)
            r.raise_for_status()
            return r.json().get("id")

    def get(self, approval_id: str) -> dict[str, Any] | None:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{self.base_url}/approvals/{approval_id}")
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()

    def set_status(self, approval_id: str, status: str, reason: str | None = None) -> bool:
        verb = "approve" if status == "approved" else "deny"
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                f"{self.base_url}/approvals/{approval_id}/{verb}", json={"reason": reason or ""}
            )
            if r.status_code == 404:
                return False
            r.raise_for_status()
            return True

    def bulk_set_status(
        self, ids: list[str], status: str, reason: str | None = None
    ) -> ApprovalUpdateResult:
        res: ApprovalUpdateResult = {"updated": [], "not_found": []}
        for i in ids:
            (res["updated"] if self.set_status(i, status, reason) else res["not_found"]).append(i)
        return res


def ApprovalsStore(
    registry: dict[str, Any] | None = None,
    personas: dict[str, dict[str, Any]] | None = None,
) -> Any:
    # Prefer Enterprise approvals service when configured
    svc_url = os.getenv("APPROVAL_SERVICE_URL") or os.getenv("APPROVALS_SERVICE_URL")
    if svc_url:
        return EnterpriseApprovalsProxy(svc_url)
    # Otherwise choose Graph-backed store
    tenant_cfg = _selected_tenant_config()
    if tenant_cfg is not None and (
        tenant_cfg.governance.approvals_site_url or tenant_cfg.governance.approvals_site_id
    ):
        return GraphApprovalsStore(registry=registry, personas=personas)
    if os.getenv("APPROVALS_SITE_URL") or os.getenv("APPROVALS_SITE_ID"):
        return GraphApprovalsStore(registry=registry, personas=personas)

    # Fallback to in-memory (ephemeral) minimal store if Graph not configured
    class _Memory:
        def __init__(self) -> None:
            self.db: dict[str, dict[str, Any]] = {}
            self.teams_webhook = os.getenv("TEAMS_APPROVALS_WEBHOOK")
            self.registry = registry or {}
            self.personas = personas or load_persona_registry(self.registry)

        def _default_approvers(self, agent: str, action: str) -> list[str]:
            try:
                agent_def = self.registry.get("agents", {}).get(agent, {})
                for rule in agent_def.get("approval_rules", []) or []:
                    if rule.get("action") == action:
                        return rule.get("approvers", []) or []
            except Exception:
                pass
            return []

        def create(self, agent: str, action: str, params: dict[str, Any]) -> str:
            aid = str(uuid.uuid4())
            self.db[aid] = {
                "id": aid,
                "agent": agent,
                "action": action,
                "params": params,
                "persona": params.get("persona"),
                "persona_target": params.get("persona_target"),
                "requestor": params.get("requestor") or "system",
                "requestor_tier": params.get("requestor_tier"),
                "requestor_groups": params.get("requestor_groups") or [],
                "executor": params.get("executor_identity"),
                "tenant": params.get("tenant"),
                "approvers": self._default_approvers(agent, action),
                "status": "pending",
                "requested_at": datetime.now(UTC).isoformat(),
            }
            return aid

        def get(self, approval_id: str) -> dict[str, Any] | None:
            return self.db.get(approval_id)

        def set_status(self, approval_id: str, status: str, reason: str | None = None) -> bool:
            if approval_id not in self.db:
                return False
            self.db[approval_id]["status"] = status
            if reason:
                self.db[approval_id]["reason"] = reason
            return True

        def bulk_set_status(
            self, ids: list[str], status: str, reason: str | None = None
        ) -> ApprovalUpdateResult:
            updated: list[str] = []
            not_found: list[str] = []
            for i in ids:
                (updated if self.set_status(i, status, reason) else not_found).append(i)
            return {"updated": updated, "not_found": not_found}

    return _Memory()
