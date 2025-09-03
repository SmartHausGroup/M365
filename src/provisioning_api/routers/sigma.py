from __future__ import annotations

from fastapi import APIRouter

from provisioning_api.schemas import (
    Ack,
    SigmaBacktesting,
    SigmaPerformance,
    SigmaRisk,
    SigmaSignals,
)
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/sigma", tags=["sigma"])
store = JsonStore()


@router.post("/performance", response_model=Ack)
def sigma_performance(body: SigmaPerformance) -> Ack:
    rec = store.append("sigma_performance", body.model_dump())
    return Ack(id=rec["id"], collection="sigma_performance")


@router.post("/signals", response_model=Ack)
def sigma_signals(body: SigmaSignals) -> Ack:
    rec = store.append("sigma_signals", body.model_dump())
    return Ack(id=rec["id"], collection="sigma_signals")


@router.post("/backtesting", response_model=Ack)
def sigma_backtesting(body: SigmaBacktesting) -> Ack:
    rec = store.append("sigma_backtesting", body.model_dump())
    return Ack(id=rec["id"], collection="sigma_backtesting")


@router.post("/risk", response_model=Ack)
def sigma_risk(body: SigmaRisk) -> Ack:
    rec = store.append("sigma_risk", body.model_dump())
    return Ack(id=rec["id"], collection="sigma_risk")
