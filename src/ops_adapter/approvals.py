from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
import hmac
import hashlib
from urllib.parse import urlencode

import httpx


def _parse_site_url(site_url: str) -> tuple[str, str]:
    # Returns (hostname, path)
    # e.g., https://contoso.sharepoint.com/sites/ops -> (contoso.sharepoint.com, /sites/ops)
    from urllib.parse import urlparse

    p = urlparse(site_url)
    return p.netloc, p.path


class GraphApprovalsStore:
    def __init__(self, registry: Dict[str, Any] | None = None):
        self.registry = registry or {}
        self.teams_webhook = os.getenv("TEAMS_APPROVALS_WEBHOOK")
        self.site_url = os.getenv("APPROVALS_SITE_URL")
        self.site_id = os.getenv("APPROVALS_SITE_ID")
        self.list_id = os.getenv("APPROVALS_LIST_ID")
        self.list_name = os.getenv("APPROVALS_LIST_NAME", "Approvals")
        if not self.site_id:
            if not self.site_url:
                raise RuntimeError("Set APPROVALS_SITE_URL or APPROVALS_SITE_ID for approvals")
            self.site_id = self._resolve_site_id(self.site_url)
        if not self.list_id:
            self.list_id = self._resolve_list_id(self.site_id, self.list_name)

        # Minimal persona mapping for Teams cards
        self.personas = {
            "m365-administrator": {"name": "Marcus Chen", "title": "Senior IT Administrator"},
            "website-manager": {"name": "Elena Rodriguez", "title": "Website Manager"},
            "hr-generalist": {"name": "Sarah Williams", "title": "HR Director"},
            "outreach-coordinator": {"name": "David Park", "title": "Communications Manager"},
        }

    def _graph_token(self) -> str:
        from azure.identity import ClientCertificateCredential, ClientSecretCredential

        tenant_id = os.getenv("AZURE_TENANT_ID") or os.getenv("GRAPH_TENANT_ID")
        client_id = (
            os.getenv("AZURE_CLIENT_ID")
            or os.getenv("AZURE_APP_CLIENT_ID_TAI")
            or os.getenv("MICROSOFT_CLIENT_ID")
            or os.getenv("GRAPH_CLIENT_ID")
        )
        cert_path = os.getenv("AZURE_CLIENT_CERTIFICATE_PATH")
        if tenant_id and client_id and cert_path and os.path.exists(cert_path):
            cred = ClientCertificateCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                certificate_path=cert_path,
            )
            token = cred.get_token("https://graph.microsoft.com/.default")
            return token.token

        client_secret = (
            os.getenv("AZURE_CLIENT_SECRET")
            or os.getenv("AZURE_APP_CLIENT_SECRET_TAI")
            or os.getenv("MICROSOFT_CLIENT_SECRET")
            or os.getenv("GRAPH_CLIENT_SECRET")
        )
        if tenant_id and client_id and client_secret:
            cred = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
            token = cred.get_token("https://graph.microsoft.com/.default")
            return token.token

        raise RuntimeError("Graph credentials not configured for approvals")

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

    def _default_approvers(self, agent: str, action: str) -> List[str]:
        try:
            agent_def = (self.registry or {}).get("agents", {}).get(agent, {})
            for rule in agent_def.get("approval_rules", []) or []:
                if rule.get("action") == action:
                    return rule.get("approvers", []) or []
        except Exception:
            pass
        return []

    def create(self, agent: str, action: str, params: Dict[str, Any]) -> str:
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

    def get(self, approval_id: str) -> Optional[Dict[str, Any]]:
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
            return {
                "id": f.get("ApprovalId") or item.get("id"),
                "agent": f.get("Agent"),
                "action": f.get("Action"),
                "params": json.loads(f.get("Params") or "{}"),
                "status": (f.get("Status") or "").lower(),
                "requested_at": f.get("Created"),
                "updated_at": f.get("Modified"),
                "approvers": (f.get("Approvers") or "").split(", ") if f.get("Approvers") else [],
            }

    def set_status(self, approval_id: str, status: str, reason: Optional[str] = None) -> bool:
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

    def bulk_set_status(self, ids: List[str], status: str, reason: Optional[str] = None) -> Dict[str, Any]:
        results = {"updated": [], "not_found": []}
        for i in ids:
            ok = self.set_status(i, status, reason)
            (results["updated"] if ok else results["not_found"]).append(i)
        return results

    def query(
        self,
        agent: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        filters: List[str] = []
        if agent:
            filters.append(f"fields/Agent eq '{agent}'")
        if action:
            filters.append(f"fields/Action eq '{action}'")
        if status:
            filters.append(f"fields/Status eq '{status}'")
        if start_date:
            filters.append(f"createdDateTime ge {start_date.astimezone(timezone.utc).isoformat()}")
        if end_date:
            filters.append(f"createdDateTime le {end_date.astimezone(timezone.utc).isoformat()}")
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
                items.append(
                    {
                        "id": f.get("ApprovalId") or it.get("id"),
                        "agent": f.get("Agent"),
                        "action": f.get("Action"),
                        "status": (f.get("Status") or "").lower(),
                        "approvers": (f.get("Approvers") or "").split(", ") if f.get("Approvers") else [],
                        "requestor": f.get("Requestor"),
                        "requested_at": it.get("createdDateTime"),
                        "updated_at": it.get("lastModifiedDateTime"),
                    }
                )
            return items

    def _notify_teams(self, approval_id: str, agent: str, action: str, params: Dict[str, Any]):
        if not self.teams_webhook:
            return
        persona = self.personas.get(agent, {"name": agent, "title": agent})
        title = f"Approval Required: {agent}/{action}"
        text_title = f"{persona['name']} ({persona['title']})"
        # Signed action URLs
        base = os.getenv('OPS_ADAPTER_PUBLIC_URL', 'http://localhost:8080')
        ts = str(int(datetime.now(timezone.utc).timestamp()))
        approve_url = self._signed_action_url(base, approval_id, 'approve', ts)
        deny_url = self._signed_action_url(base, approval_id, 'deny', ts)
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
                                    {"title": "Requestor", "value": params.get("requestor", "system")},
                                ],
                            },
                            {
                                "type": "Input.Text",
                                "id": "reason",
                                "placeholder": "Optional reason",
                                "isMultiline": True
                            },
                        ],
                        "actions": [
                            {
                                "type": "Action.Http",
                                "title": "Approve",
                                "method": "POST",
                                "url": approve_url,
                                "body": "{\"params\":{\"reason\":\"{{reason.value}}\"}}",
                            },
                            {
                                "type": "Action.Http",
                                "title": "Deny",
                                "method": "POST",
                                "url": deny_url,
                                "body": "{\"params\":{\"reason\":\"{{reason.value}}\"}}",
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
        msg = f"{approval_id}|{verb}|{ts}".encode("utf-8")
        sig = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        qs = urlencode({"ts": ts, "sig": sig})
        return f"{base}/approvals/{approval_id}/{verb}?{qs}"

    @staticmethod
    def verify_signature(approval_id: str, verb: str, ts: Optional[str], sig: Optional[str]) -> bool:
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
        now = int(datetime.now(timezone.utc).timestamp())
        if abs(now - ts_int) > max_skew:
            return False
        msg = f"{approval_id}|{verb}|{ts}".encode("utf-8")
        expected = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig)


class EnterpriseApprovalsProxy:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create(self, agent: str, action: str, params: Dict[str, Any]) -> str:
        payload = {
            "agent": agent,
            "action": action,
            "params": params,
            "requester": params.get("requestor") or "system",
        }
        with httpx.Client(timeout=10.0) as client:
            r = client.post(f"{self.base_url}/approvals", json=payload)
            r.raise_for_status()
            return r.json().get("id")

    def get(self, approval_id: str) -> Optional[Dict[str, Any]]:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{self.base_url}/approvals/{approval_id}")
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()

    def set_status(self, approval_id: str, status: str, reason: Optional[str] = None) -> bool:
        verb = "approve" if status == "approved" else "deny"
        with httpx.Client(timeout=10.0) as client:
            r = client.post(f"{self.base_url}/approvals/{approval_id}/{verb}", json={"reason": reason or ""})
            if r.status_code == 404:
                return False
            r.raise_for_status()
            return True

    def bulk_set_status(self, ids: List[str], status: str, reason: Optional[str] = None) -> Dict[str, Any]:
        res = {"updated": [], "not_found": []}
        for i in ids:
            (res["updated"] if self.set_status(i, status, reason) else res["not_found"]).append(i)
        return res


def ApprovalsStore(registry: Dict[str, Any] | None = None):
    # Prefer Enterprise approvals service when configured
    svc_url = os.getenv("APPROVAL_SERVICE_URL") or os.getenv("APPROVALS_SERVICE_URL")
    if svc_url:
        return EnterpriseApprovalsProxy(svc_url)
    # Otherwise choose Graph-backed store
    if os.getenv("APPROVALS_SITE_URL") or os.getenv("APPROVALS_SITE_ID"):
        return GraphApprovalsStore(registry=registry)
    # Fallback to in-memory (ephemeral) minimal store if Graph not configured
    class _Memory:
        def __init__(self):
            self.db: Dict[str, Dict[str, Any]] = {}
            self.teams_webhook = os.getenv("TEAMS_APPROVALS_WEBHOOK")

        def create(self, agent: str, action: str, params: Dict[str, Any]) -> str:
            aid = str(uuid.uuid4())
            self.db[aid] = {
                "id": aid,
                "agent": agent,
                "action": action,
                "params": params,
                "status": "pending",
                "requested_at": datetime.now(timezone.utc).isoformat(),
            }
            return aid

        def get(self, approval_id: str):
            return self.db.get(approval_id)

        def set_status(self, approval_id: str, status: str, reason: Optional[str] = None) -> bool:
            if approval_id not in self.db:
                return False
            self.db[approval_id]["status"] = status
            if reason:
                self.db[approval_id]["reason"] = reason
            return True

        def bulk_set_status(self, ids: List[str], status: str, reason: Optional[str] = None):
            updated, not_found = [], []
            for i in ids:
                (updated if self.set_status(i, status, reason) else not_found).append(i)
            return {"updated": updated, "not_found": not_found}

    return _Memory()
