from __future__ import annotations

from fastapi import APIRouter, Query

from provisioning_api.schemas import Ack, TaiMemory, TaiOrchestration, TaiPerformance, TaiResearch
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/tai", tags=["tai"])
store = JsonStore()


@router.post("/research", response_model=Ack)
def create_tai_research(body: TaiResearch) -> Ack:
    rec = store.append("tai_research", body.model_dump())
    return Ack(id=rec["id"], collection="tai_research")


@router.post("/memory", response_model=Ack)
def track_tai_memory(body: TaiMemory) -> Ack:
    rec = store.append("tai_memory", body.model_dump())
    return Ack(id=rec["id"], collection="tai_memory")


@router.post("/orchestration", response_model=Ack)
def track_tai_orchestration(body: TaiOrchestration) -> Ack:
    rec = store.append("tai_orchestration", body.model_dump())
    return Ack(id=rec["id"], collection="tai_orchestration")


@router.post("/performance", response_model=Ack)
def track_tai_performance(body: TaiPerformance) -> Ack:
    rec = store.append("tai_performance", body.model_dump())
    return Ack(id=rec["id"], collection="tai_performance")


@router.get("/research")
def list_tai_research() -> list[dict]:
    return store.list("tai_research")


@router.get("/search")
def search_tai(q: str = Query(default=""), tags: str = Query(default="")) -> list[dict]:
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    return store.search("tai_research", q=q, tags=tag_list)
