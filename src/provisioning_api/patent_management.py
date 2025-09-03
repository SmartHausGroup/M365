"""
Patent and IP management
- Mathematical autopsy workflows
- IP portfolio tracking
- Legal compliance automation
"""

from __future__ import annotations

from provisioning_api.schemas import (
    PatentsApplications,
    PatentsAutopsy,
    PatentsCompliance,
    PatentsPortfolio,
)
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_application(entry: PatentsApplications) -> str:
    rec = _store.append("patents_applications", entry.model_dump())
    return rec["id"]


def add_portfolio(entry: PatentsPortfolio) -> str:
    rec = _store.append("patents_portfolio", entry.model_dump())
    return rec["id"]


def add_autopsy(entry: PatentsAutopsy) -> str:
    rec = _store.append("patents_autopsy", entry.model_dump())
    return rec["id"]


def add_compliance(entry: PatentsCompliance) -> str:
    rec = _store.append("patents_compliance", entry.model_dump())
    return rec["id"]
