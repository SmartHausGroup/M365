from __future__ import annotations

from typing import Any

import httpx


def notify_approval(webhook_url: str, approval: dict[str, Any]) -> None:
    title = f"Approval Required: {approval.get('agent')} → {approval.get('action')}"
    text = f"Approval ID: {approval.get('id')}\nStatus: {approval.get('status')}"
    payload = {
        "title": title,
        "text": text,
    }
    with httpx.Client(timeout=5) as client:
        client.post(webhook_url, json=payload)
