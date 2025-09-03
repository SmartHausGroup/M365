"""
LATTICE architecture management
- AIOS, LQL, LEF development tracking
- Mathematical proofs and verification
- LATTICE research collaboration
"""

from __future__ import annotations

from provisioning_api.schemas import (
    LatticeAIOS,
    LatticeArchitecture,
    LatticeLEF,
    LatticeLQL,
    LatticeResearch,
)
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_research(entry: LatticeResearch) -> str:
    rec = _store.append("lattice_research", entry.model_dump())
    return rec["id"]


def add_aios(entry: LatticeAIOS) -> str:
    rec = _store.append("lattice_aios", entry.model_dump())
    return rec["id"]


def add_lql(entry: LatticeLQL) -> str:
    rec = _store.append("lattice_lql", entry.model_dump())
    return rec["id"]


def add_lef(entry: LatticeLEF) -> str:
    rec = _store.append("lattice_lef", entry.model_dump())
    return rec["id"]


def add_architecture(entry: LatticeArchitecture) -> str:
    rec = _store.append("lattice_architecture", entry.model_dump())
    return rec["id"]
