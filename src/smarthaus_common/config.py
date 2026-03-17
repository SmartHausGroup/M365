from __future__ import annotations

import os

from pydantic import BaseModel, Field


class GraphAuthConfig(BaseModel):
    tenant_id: str = Field(
        default_factory=lambda: (
            os.getenv("GRAPH_TENANT_ID")
            or os.getenv("AZURE_TENANT_ID")
            or os.getenv("MICROSOFT_TENANT_ID")
            or ""
        )
    )
    client_id: str = Field(
        default_factory=lambda: (
            os.getenv("AZURE_APP_CLIENT_ID_TAI")
            or os.getenv("GRAPH_CLIENT_ID")
            or os.getenv("AZURE_CLIENT_ID")
            or os.getenv("MICROSOFT_CLIENT_ID")
            or ""
        )
    )
    client_secret: str = Field(
        default_factory=lambda: (
            os.getenv("AZURE_APP_CLIENT_SECRET_TAI")
            or os.getenv("GRAPH_CLIENT_SECRET")
            or os.getenv("AZURE_CLIENT_SECRET")
            or os.getenv("MICROSOFT_CLIENT_SECRET")
            or ""
        )
    )
    scope: str = Field(default="https://graph.microsoft.com/.default")


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
