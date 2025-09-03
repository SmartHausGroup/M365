"""
TAI + LATTICE collaboration workflows
- Shared research resources
- Cross-project documentation sync
- Research collaboration automation
"""

from __future__ import annotations

from provisioning_api.schemas import (
    ResearchCollaboration,
    ResearchPerformance,
    ResearchResources,
    ResearchSynthesis,
)
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_collaboration(entry: ResearchCollaboration) -> str:
    rec = _store.append("research_collaboration", entry.model_dump())
    return rec["id"]


def add_resource(entry: ResearchResources) -> str:
    rec = _store.append("research_resources", entry.model_dump())
    return rec["id"]


def add_synthesis(entry: ResearchSynthesis) -> str:
    rec = _store.append("research_synthesis", entry.model_dump())
    return rec["id"]


def add_performance(entry: ResearchPerformance) -> str:
    rec = _store.append("research_performance", entry.model_dump())
    return rec["id"]
