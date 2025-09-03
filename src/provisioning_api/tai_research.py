"""
TAI-specific research management
- Holographic memory research
- AI orchestration development
- TAI project collaboration
"""

from __future__ import annotations

from provisioning_api.schemas import TaiMemory, TaiOrchestration, TaiPerformance, TaiResearch
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_research(entry: TaiResearch) -> str:
    rec = _store.append("tai_research", entry.model_dump())
    return rec["id"]


def add_memory(entry: TaiMemory) -> str:
    rec = _store.append("tai_memory", entry.model_dump())
    return rec["id"]


def add_orchestration(entry: TaiOrchestration) -> str:
    rec = _store.append("tai_orchestration", entry.model_dump())
    return rec["id"]


def add_performance(entry: TaiPerformance) -> str:
    rec = _store.append("tai_performance", entry.model_dump())
    return rec["id"]
