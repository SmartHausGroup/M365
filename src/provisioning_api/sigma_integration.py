"""
SIGMA trading algorithm monitoring
- Performance metrics and backtesting
- Signal processing and alerts
- Trading workflow automation
"""

from __future__ import annotations

from provisioning_api.schemas import SigmaBacktesting, SigmaPerformance, SigmaRisk, SigmaSignals
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_performance(entry: SigmaPerformance) -> str:
    rec = _store.append("sigma_performance", entry.model_dump())
    return rec["id"]


def add_signal(entry: SigmaSignals) -> str:
    rec = _store.append("sigma_signals", entry.model_dump())
    return rec["id"]


def add_backtesting(entry: SigmaBacktesting) -> str:
    rec = _store.append("sigma_backtesting", entry.model_dump())
    return rec["id"]


def add_risk(entry: SigmaRisk) -> str:
    rec = _store.append("sigma_risk", entry.model_dump())
    return rec["id"]
