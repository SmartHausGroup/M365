from __future__ import annotations

from fastapi import APIRouter

from provisioning_api.schemas import Ack, C2Compliance, C2Documents, C2Infrastructure, C2Security
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/c2", tags=["c2"])
store = JsonStore()


@router.post("/security", response_model=Ack)
def c2_security(body: C2Security) -> Ack:
    rec = store.append("c2_security", body.model_dump())
    return Ack(id=rec["id"], collection="c2_security")


@router.post("/infrastructure", response_model=Ack)
def c2_infrastructure(body: C2Infrastructure) -> Ack:
    rec = store.append("c2_infrastructure", body.model_dump())
    return Ack(id=rec["id"], collection="c2_infrastructure")


@router.post("/compliance", response_model=Ack)
def c2_compliance(body: C2Compliance) -> Ack:
    rec = store.append("c2_compliance", body.model_dump())
    return Ack(id=rec["id"], collection="c2_compliance")


@router.post("/documents", response_model=Ack)
def c2_documents(body: C2Documents) -> Ack:
    rec = store.append("c2_documents", body.model_dump())
    return Ack(id=rec["id"], collection="c2_documents")
