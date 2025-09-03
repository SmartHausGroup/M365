from __future__ import annotations

from fastapi import APIRouter, Query

from provisioning_api.schemas import (
    Ack,
    LatticeAIOS,
    LatticeArchitecture,
    LatticeLEF,
    LatticeLQL,
    LatticeResearch,
)
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/lattice", tags=["lattice"])
store = JsonStore()


@router.post("/research", response_model=Ack)
def create_lattice_research(body: LatticeResearch) -> Ack:
    rec = store.append("lattice_research", body.model_dump())
    return Ack(id=rec["id"], collection="lattice_research")


@router.post("/aios", response_model=Ack)
def track_lattice_aios(body: LatticeAIOS) -> Ack:
    rec = store.append("lattice_aios", body.model_dump())
    return Ack(id=rec["id"], collection="lattice_aios")


@router.post("/lql", response_model=Ack)
def track_lattice_lql(body: LatticeLQL) -> Ack:
    rec = store.append("lattice_lql", body.model_dump())
    return Ack(id=rec["id"], collection="lattice_lql")


@router.post("/lef", response_model=Ack)
def track_lattice_lef(body: LatticeLEF) -> Ack:
    rec = store.append("lattice_lef", body.model_dump())
    return Ack(id=rec["id"], collection="lattice_lef")


@router.post("/architecture", response_model=Ack)
def track_lattice_architecture(body: LatticeArchitecture) -> Ack:
    rec = store.append("lattice_architecture", body.model_dump())
    return Ack(id=rec["id"], collection="lattice_architecture")


@router.get("/research")
def list_lattice_research() -> list[dict]:
    return store.list("lattice_research")


@router.get("/search")
def search_lattice(q: str = Query(default=""), tags: str = Query(default="")) -> list[dict]:
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    return store.search("lattice_research", q=q, tags=tag_list)
