"""
Client project management
- Research showcase integration
- Project automation workflows
- Client communication
"""

from __future__ import annotations

from provisioning_api.schemas import (
    ClientsAutomation,
    ClientsCommunication,
    ClientsProjects,
    ClientsShowcase,
)
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_project(entry: ClientsProjects) -> str:
    rec = _store.append("clients_projects", entry.model_dump())
    return rec["id"]


def add_showcase(entry: ClientsShowcase) -> str:
    rec = _store.append("clients_showcase", entry.model_dump())
    return rec["id"]


def add_automation(entry: ClientsAutomation) -> str:
    rec = _store.append("clients_automation", entry.model_dump())
    return rec["id"]


def add_communication(entry: ClientsCommunication) -> str:
    rec = _store.append("clients_communication", entry.model_dump())
    return rec["id"]
