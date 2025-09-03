from __future__ import annotations

from fastapi import APIRouter

from provisioning_api.schemas import (
    Ack,
    ClientsAutomation,
    ClientsCommunication,
    ClientsProjects,
    ClientsShowcase,
)
from provisioning_api.storage import JsonStore

router = APIRouter(prefix="/api/clients", tags=["clients"])
store = JsonStore()


@router.post("/projects", response_model=Ack)
def clients_projects(body: ClientsProjects) -> Ack:
    rec = store.append("clients_projects", body.model_dump())
    return Ack(id=rec["id"], collection="clients_projects")


@router.post("/showcase", response_model=Ack)
def clients_showcase(body: ClientsShowcase) -> Ack:
    rec = store.append("clients_showcase", body.model_dump())
    return Ack(id=rec["id"], collection="clients_showcase")


@router.post("/automation", response_model=Ack)
def clients_automation(body: ClientsAutomation) -> Ack:
    rec = store.append("clients_automation", body.model_dump())
    return Ack(id=rec["id"], collection="clients_automation")


@router.post("/communication", response_model=Ack)
def clients_communication(body: ClientsCommunication) -> Ack:
    rec = store.append("clients_communication", body.model_dump())
    return Ack(id=rec["id"], collection="clients_communication")
