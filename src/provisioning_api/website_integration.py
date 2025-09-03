"""
SmartHaus Group website repository integration
- Website updates and deployments
- Content management workflows
- Business development integration
"""

from __future__ import annotations

from provisioning_api.schemas import (
    WebsiteBusiness,
    WebsiteContent,
    WebsiteDeployment,
    WebsiteUpdate,
)
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_update(entry: WebsiteUpdate) -> str:
    rec = _store.append("website_updates", entry.model_dump())
    return rec["id"]


def add_deployment(entry: WebsiteDeployment) -> str:
    rec = _store.append("website_deployments", entry.model_dump())
    return rec["id"]


def add_content(entry: WebsiteContent) -> str:
    rec = _store.append("website_content", entry.model_dump())
    return rec["id"]


def add_business(entry: WebsiteBusiness) -> str:
    rec = _store.append("website_business", entry.model_dump())
    return rec["id"]
