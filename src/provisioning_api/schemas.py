from __future__ import annotations

from pydantic import BaseModel, Field


# Common
class Ack(BaseModel):
    id: str
    collection: str
    status: str = "accepted"


# TAI
class TaiResearch(BaseModel):
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)


class TaiMemory(BaseModel):
    experiment: str
    dataset: str
    notes: str | None = None
    metrics: dict = Field(default_factory=dict)


class TaiOrchestration(BaseModel):
    component: str
    change: str
    status: str
    notes: str | None = None


class TaiPerformance(BaseModel):
    benchmark: str
    value: float
    unit: str
    context: dict = Field(default_factory=dict)


# LATTICE
class LatticeResearch(BaseModel):
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)


class LatticeAIOS(BaseModel):
    feature: str
    status: str
    notes: str | None = None


class LatticeLQL(BaseModel):
    query: str
    description: str | None = None
    status: str | None = None


class LatticeLEF(BaseModel):
    component: str
    update: str
    status: str


class LatticeArchitecture(BaseModel):
    decision: str
    rationale: str
    impact: list[str] = Field(default_factory=list)


# Website
class WebsiteUpdate(BaseModel):
    change: str
    repo: str
    pr: int | None = None
    author: str | None = None


class WebsiteDeployment(BaseModel):
    environment: str
    version: str
    status: str


class WebsiteContent(BaseModel):
    path: str
    action: str
    owner: str | None = None


class WebsiteBusiness(BaseModel):
    topic: str
    details: str


# Cross-Project Research
class ResearchCollaboration(BaseModel):
    topic: str
    summary: str
    participants: list[str] = Field(default_factory=list)


class ResearchResources(BaseModel):
    name: str
    link: str
    category: str


class ResearchSynthesis(BaseModel):
    theme: str
    inputs: list[str]
    outcome: str


class ResearchPerformance(BaseModel):
    project: str
    metric: str
    value: float
    unit: str


# SIGMA
class SigmaPerformance(BaseModel):
    strategy: str
    sharpe: float
    pnl: float
    period: str


class SigmaSignals(BaseModel):
    name: str
    signal: str
    strength: float


class SigmaBacktesting(BaseModel):
    strategy: str
    window: str
    result: dict = Field(default_factory=dict)


class SigmaRisk(BaseModel):
    strategy: str
    var: float
    drawdown: float


# C2
class C2Security(BaseModel):
    status: str
    details: str


class C2Infrastructure(BaseModel):
    component: str
    health: str
    metrics: dict = Field(default_factory=dict)


class C2Compliance(BaseModel):
    area: str
    status: str
    notes: str | None = None


class C2Documents(BaseModel):
    doc_id: str
    action: str
    recipient: str | None = None


# Marketing
class MarketingLeads(BaseModel):
    source: str
    contact: str
    notes: str | None = None


class MarketingCampaigns(BaseModel):
    name: str
    channel: str
    status: str


class MarketingAnalytics(BaseModel):
    metric: str
    value: float
    unit: str


class MarketingBusiness(BaseModel):
    initiative: str
    status: str


# Patents
class PatentsApplications(BaseModel):
    title: str
    jurisdiction: str
    status: str


class PatentsPortfolio(BaseModel):
    asset: str
    stage: str


class PatentsAutopsy(BaseModel):
    paper: str
    result: str


class PatentsCompliance(BaseModel):
    area: str
    status: str


# Infrastructure
class InfraCiCd(BaseModel):
    pipeline: str
    status: str
    change: str


class InfraDeployments(BaseModel):
    service: str
    version: str
    status: str


class InfraMonitoring(BaseModel):
    component: str
    metric: str
    value: float


class InfraOptimization(BaseModel):
    area: str
    improvement: str


# Clients
class ClientsProjects(BaseModel):
    client: str
    project: str
    description: str


class ClientsShowcase(BaseModel):
    client: str
    topic: str
    summary: str


class ClientsAutomation(BaseModel):
    client: str
    process: str
    status: str


class ClientsCommunication(BaseModel):
    client: str
    message: str
