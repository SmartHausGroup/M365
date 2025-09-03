from __future__ import annotations

from fastapi import APIRouter

from provisioning_api.schemas import (
    Ack,
    InfraCiCd,
    InfraDeployments,
    InfraMonitoring,
    InfraOptimization,
)
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])
store = JsonStore()


@router.post("/cicd", response_model=Ack)
def infra_cicd(body: InfraCiCd) -> Ack:
    rec = store.append("infra_cicd", body.model_dump())
    return Ack(id=rec["id"], collection="infra_cicd")


@router.post("/deployments", response_model=Ack)
def infra_deployments(body: InfraDeployments) -> Ack:
    rec = store.append("infra_deployments", body.model_dump())
    return Ack(id=rec["id"], collection="infra_deployments")


@router.post("/monitoring", response_model=Ack)
def infra_monitoring(body: InfraMonitoring) -> Ack:
    rec = store.append("infra_monitoring", body.model_dump())
    return Ack(id=rec["id"], collection="infra_monitoring")


@router.post("/optimization", response_model=Ack)
def infra_optimization(body: InfraOptimization) -> Ack:
    rec = store.append("infra_optimization", body.model_dump())
    return Ack(id=rec["id"], collection="infra_optimization")
