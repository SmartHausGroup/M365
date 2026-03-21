from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


def has_selected_tenant() -> bool:
    return bool(os.getenv("UCP_TENANT", "").strip())


def load_bootstrap_env(*paths: str | Path) -> str | None:
    """Load the first available dotenv file as bootstrap-only input."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return None

    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if path.exists():
            load_dotenv(path, override=False)
            return str(path)
    return None


def _selected_tenant_config() -> Any | None:
    if not has_selected_tenant():
        return None
    try:
        from smarthaus_common.tenant_config import get_tenant_config

        return get_tenant_config()
    except Exception:
        return None


def _resolve_graph_value(field_name: str, env_keys: tuple[str, ...]) -> str:
    tenant_cfg = _selected_tenant_config()
    if tenant_cfg is not None:
        tenant_value = getattr(tenant_cfg.azure, field_name, "")
        if tenant_value:
            return tenant_value

    for key in env_keys:
        value = os.getenv(key)
        if value:
            return value
    return ""


def _resolve_graph_scope() -> str:
    tenant_cfg = _selected_tenant_config()
    if tenant_cfg is not None and tenant_cfg.auth.app_only.scope:
        return tenant_cfg.auth.app_only.scope
    return "https://graph.microsoft.com/.default"


def resolve_sharepoint_hostname(default: str = "smarthausgroup.sharepoint.com") -> str:
    tenant_cfg = _selected_tenant_config()
    if tenant_cfg is not None and tenant_cfg.org.sharepoint_hostname:
        return tenant_cfg.org.sharepoint_hostname
    return os.getenv("SHAREPOINT_HOSTNAME") or os.getenv("SP_HOSTNAME") or default


class GraphAuthConfig(BaseModel):
    tenant_id: str = Field(
        default_factory=lambda: _resolve_graph_value(
            "tenant_id",
            ("GRAPH_TENANT_ID", "AZURE_TENANT_ID", "MICROSOFT_TENANT_ID"),
        )
    )
    client_id: str = Field(
        default_factory=lambda: _resolve_graph_value(
            "client_id",
            (
                "AZURE_APP_CLIENT_ID_TAI",
                "GRAPH_CLIENT_ID",
                "AZURE_CLIENT_ID",
                "MICROSOFT_CLIENT_ID",
            ),
        )
    )
    client_secret: str = Field(
        default_factory=lambda: _resolve_graph_value(
            "client_secret",
            (
                "AZURE_APP_CLIENT_SECRET_TAI",
                "GRAPH_CLIENT_SECRET",
                "AZURE_CLIENT_SECRET",
                "MICROSOFT_CLIENT_SECRET",
            ),
        )
    )
    scope: str = Field(default_factory=_resolve_graph_scope)


class AppConfig(BaseModel):
    environment: str = Field(default_factory=lambda: os.getenv("APP_ENV", "dev"))
    graph: GraphAuthConfig = Field(default_factory=GraphAuthConfig)


class EnterpriseConfig(BaseModel):
    projects: dict[str, str] = {
        "tai": "TAI Research - Holographic Memory & AI Orchestration",
        "lattice": "LATTICE Architecture - AIOS, LQL, LEF Development",
        "sigma": "SIGMA Trading - Algorithm Development & Performance",
        "c2": "C2 Cloud Platform - Secure Infrastructure",
        "aidf": "AIDF Framework - AI Development & Integration",
        "website": "SmartHaus Group - Business & Client Operations",
    }

    teams_config: dict[str, list[str]] = {
        "tai": [
            "General",
            "Holographic Memory",
            "AI Orchestration",
            "Performance Metrics",
            "Research Updates",
        ],
        "lattice": [
            "General",
            "AIOS Development",
            "LQL Language",
            "LEF Execution",
            "Architecture Updates",
        ],
        "sigma": [
            "General",
            "Algorithm Development",
            "Performance Metrics",
            "Risk Management",
            "Trading Updates",
        ],
        "c2": [
            "General",
            "Infrastructure",
            "Security",
            "Compliance",
            "Platform Updates",
        ],
        "aidf": [
            "General",
            "Framework Development",
            "Integration",
            "Testing",
            "Documentation",
        ],
        "website": [
            "General",
            "Website Development",
            "Business Development",
            "Client Projects",
            "Strategic Planning",
        ],
    }

    sharepoint_config: dict[str, list[str]] = {
        "tai": [
            "Research Papers",
            "Holographic Memory",
            "AI Orchestration",
            "Performance Metrics",
            "Project Management",
        ],
        "lattice": [
            "Architecture Documentation",
            "AIOS Development",
            "LQL Language",
            "LEF Execution",
            "Mathematical Proofs",
        ],
        "sigma": [
            "Trading Algorithms",
            "Performance Data",
            "Risk Analysis",
            "Backtesting Results",
            "Research Papers",
        ],
        "c2": [
            "Infrastructure Docs",
            "Security Policies",
            "Compliance Reports",
            "Platform Architecture",
            "Operations Manuals",
        ],
        "aidf": [
            "Framework Docs",
            "Integration Guides",
            "Testing Results",
            "API Documentation",
            "Implementation Examples",
        ],
        "website": [
            "Website Updates",
            "Business Development",
            "Client Projects",
            "Strategic Planning",
            "Marketing Materials",
        ],
    }
