from __future__ import annotations

from fastapi import APIRouter

from provisioning_api.schemas import (
    Ack,
    ResearchCollaboration,
    ResearchPerformance,
    ResearchResources,
    ResearchSynthesis,
)
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/research", tags=["research"])
store = JsonStore()


@router.post("/collaboration", response_model=Ack)
def research_collaboration(body: ResearchCollaboration) -> Ack:
    rec = store.append("research_collaboration", body.model_dump())
    return Ack(id=rec["id"], collection="research_collaboration")


@router.post("/resources", response_model=Ack)
def research_resources(body: ResearchResources) -> Ack:
    rec = store.append("research_resources", body.model_dump())
    return Ack(id=rec["id"], collection="research_resources")


@router.post("/synthesis", response_model=Ack)
def research_synthesis(body: ResearchSynthesis) -> Ack:
    rec = store.append("research_synthesis", body.model_dump())
    return Ack(id=rec["id"], collection="research_synthesis")


@router.post("/performance", response_model=Ack)
def research_performance(body: ResearchPerformance) -> Ack:
    rec = store.append("research_performance", body.model_dump())
    return Ack(id=rec["id"], collection="research_performance")
