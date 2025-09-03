"""
AI-powered marketing automation
- Lead generation and tracking
- Campaign management
- Business development workflows
"""

from __future__ import annotations

from provisioning_api.schemas import (
    MarketingAnalytics,
    MarketingBusiness,
    MarketingCampaigns,
    MarketingLeads,
)
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_lead(entry: MarketingLeads) -> str:
    rec = _store.append("marketing_leads", entry.model_dump())
    return rec["id"]


def add_campaign(entry: MarketingCampaigns) -> str:
    rec = _store.append("marketing_campaigns", entry.model_dump())
    return rec["id"]


def add_analytics(entry: MarketingAnalytics) -> str:
    rec = _store.append("marketing_analytics", entry.model_dump())
    return rec["id"]


def add_business(entry: MarketingBusiness) -> str:
    rec = _store.append("marketing_business", entry.model_dump())
    return rec["id"]
