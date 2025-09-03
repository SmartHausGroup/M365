from __future__ import annotations

from fastapi import APIRouter

from provisioning_api.schemas import (
    Ack,
    PatentsApplications,
    PatentsAutopsy,
    PatentsCompliance,
    PatentsPortfolio,
)
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/patents", tags=["patents"])
store = JsonStore()


@router.post("/applications", response_model=Ack)
def patents_applications(body: PatentsApplications) -> Ack:
    rec = store.append("patents_applications", body.model_dump())
    return Ack(id=rec["id"], collection="patents_applications")


@router.post("/portfolio", response_model=Ack)
def patents_portfolio(body: PatentsPortfolio) -> Ack:
    rec = store.append("patents_portfolio", body.model_dump())
    return Ack(id=rec["id"], collection="patents_portfolio")


@router.post("/autopsy", response_model=Ack)
def patents_autopsy(body: PatentsAutopsy) -> Ack:
    rec = store.append("patents_autopsy", body.model_dump())
    return Ack(id=rec["id"], collection="patents_autopsy")


@router.post("/compliance", response_model=Ack)
def patents_compliance(body: PatentsCompliance) -> Ack:
    rec = store.append("patents_compliance", body.model_dump())
    return Ack(id=rec["id"], collection="patents_compliance")
