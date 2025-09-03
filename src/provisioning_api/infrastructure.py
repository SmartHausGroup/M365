"""
Infrastructure automation
- CI/CD pipeline management
- Deployment automation
- Performance monitoring
"""

from __future__ import annotations

from provisioning_api.schemas import InfraCiCd, InfraDeployments, InfraMonitoring, InfraOptimization
from provisioning_api.storage import JsonStore

_store = JsonStore()


def add_cicd(entry: InfraCiCd) -> str:
    rec = _store.append("infra_cicd", entry.model_dump())
    return rec["id"]


def add_deployment(entry: InfraDeployments) -> str:
    rec = _store.append("infra_deployments", entry.model_dump())
    return rec["id"]


def add_monitoring(entry: InfraMonitoring) -> str:
    rec = _store.append("infra_monitoring", entry.model_dump())
    return rec["id"]


def add_optimization(entry: InfraOptimization) -> str:
    rec = _store.append("infra_optimization", entry.model_dump())
    return rec["id"]
