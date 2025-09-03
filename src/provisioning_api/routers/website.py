from __future__ import annotations

from fastapi import APIRouter

from provisioning_api.schemas import (
    Ack,
    WebsiteBusiness,
    WebsiteContent,
    WebsiteDeployment,
    WebsiteUpdate,
)
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/website", tags=["website"])
store = JsonStore()


@router.post("/updates", response_model=Ack)
def website_updates(body: WebsiteUpdate) -> Ack:
    rec = store.append("website_updates", body.model_dump())
    return Ack(id=rec["id"], collection="website_updates")


@router.post("/deployments", response_model=Ack)
def website_deployments(body: WebsiteDeployment) -> Ack:
    rec = store.append("website_deployments", body.model_dump())
    return Ack(id=rec["id"], collection="website_deployments")


@router.post("/content", response_model=Ack)
def website_content(body: WebsiteContent) -> Ack:
    rec = store.append("website_content", body.model_dump())
    return Ack(id=rec["id"], collection="website_content")


@router.post("/business", response_model=Ack)
def website_business(body: WebsiteBusiness) -> Ack:
    rec = store.append("website_business", body.model_dump())
    return Ack(id=rec["id"], collection="website_business")
