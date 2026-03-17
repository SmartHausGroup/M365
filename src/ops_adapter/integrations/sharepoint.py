from __future__ import annotations

from typing import Any

from smarthaus_graph.client import GraphClient


def create_approval_item(site_id: str, list_id: str, data: dict[str, Any]) -> str:
    """Create a simplified approval item in a SharePoint list.

    This is a placeholder; implement field mapping per your list schema.
    """
    gc = GraphClient()
    # Minimal item with title and status fields (adjust to your schema)
    body = {
        "fields": {
            "Title": f"{data.get('agent')}::{data.get('action')}::{data.get('id')}",
            "Status": data.get("status", "pending"),
        }
    }
    # POST /sites/{site-id}/lists/{list-id}/items
    r = gc._request("POST", f"/sites/{site_id}/lists/{list_id}/items", json=body)  # type: ignore[attr-defined]
    return r.json().get("id", "")

