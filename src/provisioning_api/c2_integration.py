"""
C2 secure cloud platform integration
- Secure document sharing
- Infrastructure monitoring
- Security alerts and compliance
"""

from __future__ import annotations

from provisioning_api.schemas import C2Compliance, C2Documents, C2Infrastructure, C2Security
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_security(entry: C2Security) -> str:
    rec = _store.append("c2_security", entry.model_dump())
    return rec["id"]


def add_infrastructure(entry: C2Infrastructure) -> str:
    rec = _store.append("c2_infrastructure", entry.model_dump())
    return rec["id"]


def add_compliance(entry: C2Compliance) -> str:
    rec = _store.append("c2_compliance", entry.model_dump())
    return rec["id"]


def add_document(entry: C2Documents) -> str:
    rec = _store.append("c2_documents", entry.model_dump())
    return rec["id"]
