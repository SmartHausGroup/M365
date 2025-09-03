from __future__ import annotations

from fastapi import APIRouter

from provisioning_api.schemas import (
    Ack,
    MarketingAnalytics,
    MarketingBusiness,
    MarketingCampaigns,
    MarketingLeads,
)
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/marketing", tags=["marketing"])
store = JsonStore()


@router.post("/leads", response_model=Ack)
def marketing_leads(body: MarketingLeads) -> Ack:
    rec = store.append("marketing_leads", body.model_dump())
    return Ack(id=rec["id"], collection="marketing_leads")


@router.post("/campaigns", response_model=Ack)
def marketing_campaigns(body: MarketingCampaigns) -> Ack:
    rec = store.append("marketing_campaigns", body.model_dump())
    return Ack(id=rec["id"], collection="marketing_campaigns")


@router.post("/analytics", response_model=Ack)
def marketing_analytics(body: MarketingAnalytics) -> Ack:
    rec = store.append("marketing_analytics", body.model_dump())
    return Ack(id=rec["id"], collection="marketing_analytics")


@router.post("/business", response_model=Ack)
def marketing_business(body: MarketingBusiness) -> Ack:
    rec = store.append("marketing_business", body.model_dump())
    return Ack(id=rec["id"], collection="marketing_business")
