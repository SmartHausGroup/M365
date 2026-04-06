from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from integrations import vercel as vercel_api
from pydantic import BaseModel
from smarthaus_common.config import EnterpriseConfig, load_bootstrap_env
from smarthaus_common.logging import configure_logging
from smarthaus_graph.client import GraphClient

from provisioning_api import auth as authn
from provisioning_api import orchestrator
from provisioning_api.audit import recent_events
from provisioning_api.cache import cached
from provisioning_api.metrics import inc_requests, snapshot
from provisioning_api.routers import (
    c2,
    clients,
    infrastructure,
    lattice,
    m365,
    marketing,
    patents,
    research,
    sigma,
    tai,
    website,
)
from provisioning_api.routers.agent_dashboard import router as agent_dashboard_router
from provisioning_api.routers.email_dashboard import router as email_dashboard_router
from provisioning_api.storage import JsonStore

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STATIC_DIR = _REPO_ROOT / "static"
_TEMPLATE_DIR = _REPO_ROOT / "templates"
load_bootstrap_env(_REPO_ROOT / ".env")

configure_logging()
app = FastAPI(title="SMARTHAUS Provisioning API", version=os.getenv("APP_VERSION", "0.1.0"))
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(_TEMPLATE_DIR)) if _TEMPLATE_DIR.exists() else None
store = JsonStore()
ent = EnterpriseConfig()


class Health(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", service="provisioning")


@app.get("/metrics")
@cached(ttl=5)
def metrics() -> dict:
    snap = snapshot()
    return {
        "m365_provisioning_requests_total": snap["total_requests"],
        "m365_sites_created_total": snap["sites_created"],
        "m365_teams_created_total": snap["teams_created"],
        "instance_uptime_seconds": snap["uptime_seconds"],
    }


def _check_graph_connectivity() -> str:
    try:
        client = GraphClient()
        data = client.get_organization()
        if data.get("value"):
            return "ok"
        return "unknown"
    except Exception:
        # If credentials are missing or consent not granted
        return "not_configured_or_unreachable"


def _check_external_services() -> dict:
    return {"graph": _check_graph_connectivity()}


@app.get("/status")
@cached(ttl=5)
def detailed_status() -> dict:
    return {
        "api_status": "healthy",
        "m365_connectivity": _check_graph_connectivity(),
        "database_status": "connected",  # JSON store is local and available
        "external_services": _check_external_services(),
        "metrics": metrics(),
    }


@app.get("/")
def dashboard(request: Request) -> object:
    import json

    from provisioning_api.storage import JsonStore

    store = JsonStore()
    lattice_data = store.list("lattice_research")
    website_data = store.list("website_updates")
    if templates is None:
        return HTMLResponse(
            content="<html><body><h1>SMARTHAUS Provisioning API</h1><p>Dashboard template is not installed in this repo checkout.</p></body></html>"
        )
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "lattice_str": json.dumps(lattice_data, indent=2),
            "website_str": json.dumps(website_data, indent=2),
        },
    )


# Routers (secured when auth is enabled)
deps = [Depends(authn.verify_microsoft_token)] if authn.auth_enabled() else []
app.include_router(lattice.router, dependencies=deps)
app.include_router(tai.router, dependencies=deps)
app.include_router(website.router, dependencies=deps)
app.include_router(research.router, dependencies=deps)
app.include_router(sigma.router, dependencies=deps)
app.include_router(c2.router, dependencies=deps)
app.include_router(m365.router, dependencies=deps)
app.include_router(marketing.router, dependencies=deps)
app.include_router(patents.router, dependencies=deps)
app.include_router(infrastructure.router, dependencies=deps)
app.include_router(clients.router, dependencies=deps)
app.include_router(email_dashboard_router, dependencies=deps)
app.include_router(agent_dashboard_router, dependencies=deps)


@app.middleware("http")
async def _metrics_middleware(request, call_next):  # type: ignore[no-untyped-def]
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    try:
        inc_requests()
    except Exception:
        pass
    return response


# CORS (for Vercel-hosted frontend)
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins if o.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handlers
@app.exception_handler(Exception)
async def unhandled_exc_handler(request: Request, exc: Exception):  # type: ignore[no-untyped-def]
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    return JSONResponse(status_code=500, content={"error": "internal_error", "request_id": req_id})


# -----------------------
# Auth routes
# -----------------------


@app.get("/api/auth/login")
def auth_login(r: str | None = None) -> object:
    return authn.microsoft_login(r)


@app.get("/api/auth/callback")
def auth_callback(code: str, state: str | None = None) -> object:
    return authn.microsoft_callback(code, state)


@app.get("/api/auth/me")
def auth_me(request: Request) -> dict:
    session = authn.verify_microsoft_token(request)
    return {"user": session.get("user_info"), "permissions": ["full_access"]}


# -----------------------
# Vercel Live Data
# -----------------------


@app.get("/api/vercel/projects")
def vercel_projects() -> dict:
    return vercel_api.list_projects()


@app.get("/api/vercel/deployments")
def vercel_deployments(projectId: str | None = None, limit: int = 20) -> dict:
    return vercel_api.list_deployments(projectId, limit)


@app.get("/api/vercel/domains")
def vercel_domains() -> dict:
    return vercel_api.list_domains()


# -----------------------
# GitHub Webhooks
# -----------------------


@app.post("/api/webhooks/github/{project}")
async def github_webhook(project: str, request: Request) -> dict:
    projects = {
        "lattice": "LATTICE Research Team",
        "sigma": "SIGMA Trading Team",
        "c2": "C2 Cloud Team",
        "website": "SmartHaus Business Team",
        "aidf": "AIDF Team",
    }
    if project not in projects:
        raise HTTPException(status_code=404, detail=f"Unknown project: {project}")
    team_name = projects[project]
    # Optional GitHub signature verification
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    try:
        raw = await request.body()
        if secret:
            import hashlib
            import hmac

            sig_hdr = request.headers.get("X-Hub-Signature-256", "")
            expected = "sha256=" + hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig_hdr, expected):
                raise HTTPException(status_code=401, detail="Invalid signature")
        payload = await request.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc
    return process_github_update(project, team_name, payload)


def process_github_update(project: str, team_name: str, payload: dict) -> dict:
    summary = {
        "project": project,
        "team": team_name,
        "type": payload.get("action") or payload.get("hook"),
        "ref": payload.get("ref"),
        "repo": (payload.get("repository") or {}).get("full_name"),
        "head": (payload.get("head_commit") or {}).get("id"),
        "message": (payload.get("head_commit") or {}).get("message"),
    }
    rec = store.append(f"github_events_{project}", {"payload": payload, "summary": summary})
    # Attempt automation orchestration (Teams + Planner) if enabled
    try:
        action = orchestrator.handle_github_event(project, payload)
    except Exception as e:
        action = {"error": str(e), "notified": False, "planner": False}
    return {"status": "ok", "id": rec["id"], "summary": summary, **action}


# -----------------------
# Analytics & Insights
# -----------------------


@app.get("/api/research/insights")
def research_insights() -> dict:
    lattice = store.list("lattice_research")
    sigma = store.list("sigma_performance")
    total = len(lattice)
    tags: dict[str, int] = {}
    for row in lattice:
        for t in row.get("tags", []):
            tags[t] = tags.get(t, 0) + 1
    return {
        "entries": total,
        "by_project": {"lattice": len(lattice)},
        "top_tags": sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10],
        "sigma_updates": len(sigma),
    }


@app.get("/api/bi/analytics")
def business_analytics() -> dict:
    website = store.list("website_updates")
    clients = store.list("clients_projects")
    marketing = store.list("marketing_business")
    return {
        "website_updates": len(website),
        "client_projects": len(clients),
        "business_initiatives": len(marketing),
    }


# -----------------------
# Workflow Engine
# -----------------------


@app.post("/api/workflows/auto-create")
def auto_create_workflow(workflow_type: str, data: dict) -> dict:
    table = {
        "research_approval": create_research_approval_workflow,
        "client_project": create_client_project_workflow,
        "document_review": create_document_review_workflow,
        "team_collaboration": create_team_collaboration_workflow,
        "research_synthesis": create_research_synthesis_workflow,
    }
    func = table.get(workflow_type)
    if not func:
        raise HTTPException(status_code=404, detail=f"Unknown workflow type: {workflow_type}")
    return func(data)


def _allow_mutations() -> bool:
    return os.getenv("ALLOW_M365_MUTATIONS", "false").lower() in ("1", "true", "yes")


def create_research_approval_workflow(data: dict) -> dict:
    item = {
        "title": data.get("title", "Research Approval"),
        "owner": data.get("owner"),
        "status": "pending",
        "project": data.get("project"),
    }
    rec = store.append("workflows_research_approval", item)
    return {"status": "ok", "id": rec["id"], "next_steps": ["review", "approve"]}


def create_client_project_workflow(data: dict) -> dict:
    client = data.get("client", "client")
    project = data.get("project", "project")
    mail_nickname = f"{client}-{project}".lower().replace(" ", "-")
    result = {"status": "ok", "project": project, "client": client, "mailNickname": mail_nickname}
    if _allow_mutations():
        from provisioning_api.m365_provision import provision_group_site, provision_teams_workspace

        site = provision_group_site(
            display_name=f"{client} {project}",
            mail_nickname=mail_nickname,
            libraries=["Documents", "Templates", "Archive"],
            description=f"Client project: {client} - {project}",
        )
        team = provision_teams_workspace(mail_nickname, ["General", "Updates", "Docs"])
        result.update({"site": site, "team": team})
    rec = store.append("workflows_client_project", result)
    return {"status": "ok", "id": rec["id"], **result}


def create_document_review_workflow(data: dict) -> dict:
    item = {
        "document": data.get("document"),
        "reviewers": data.get("reviewers", []),
        "status": "pending",
    }
    rec = store.append("workflows_document_review", item)
    return {"status": "ok", "id": rec["id"], "message": "Review requested"}


def create_team_collaboration_workflow(data: dict) -> dict:
    project = data.get("project", "general")
    channels = data.get("channels", ["General", "Updates"])
    result = {"status": "ok", "project": project}
    if _allow_mutations():
        from provisioning_api.m365_provision import provision_teams_workspace

        team = provision_teams_workspace(project, channels)
        result.update({"team": team})
    rec = store.append("workflows_team_collaboration", result)
    return {"status": "ok", "id": rec["id"], **result}


def create_research_synthesis_workflow(data: dict) -> dict:
    rec = store.append("workflows_research_synthesis", data)
    return {"status": "ok", "id": rec["id"], "message": "Synthesis requested"}


# -----------------------
# Empire Overview & Automation Status
# -----------------------


@app.get("/api/m365/empire-overview")
def empire_overview() -> dict:
    def _list(collection: str) -> list[dict]:
        return store.list(collection)

    return {
        "research_projects": {
            "tai": _list("tai_research"),
            "lattice": _list("lattice_research"),
            "sigma": _list("sigma_performance"),
            "c2": _list("c2_infrastructure"),
            "aidf": _list("research_collaboration"),
        },
        "business_operations": {
            "website": _list("website_updates"),
            "client_projects": _list("clients_projects"),
            "business_development": _list("marketing_business"),
        },
        "infrastructure": {
            "sharepoint_sites": [
                {"name": "tai-research"},
                {"name": "lattice-research"},
                {"name": "business-hub"},
            ],
            "teams_workspaces": [
                {"name": "TAI Research"},
                {"name": "LATTICE Research"},
                {"name": "SmartHaus Business"},
            ],
            "active_workflows": _list("workflows_research_approval")
            + _list("workflows_client_project")
            + _list("workflows_document_review")
            + _list("workflows_team_collaboration"),
            "system_health": detailed_status(),
        },
        "recent_activities": _list("research_collaboration")
        + _list("github_events_tai")
        + _list("github_events_lattice"),
        "performance_metrics": metrics(),
    }


@app.get("/api/m365/automation-status")
def automation_status() -> dict:
    return {
        "github_integrations": {
            "tai": True,
            "lattice": True,
            "sigma": False,
            "c2": False,
            "website": True,
            "aidf": False,
        },
        "workflow_automation": {
            "enabled": True,
            "pending": len(store.list("workflows_research_approval")),
        },
        "teams_notifications": {"configured": False},
        "sharepoint_automation": {"enabled": True},
        "research_tracking": {
            "entries": len(store.list("tai_research")) + len(store.list("lattice_research"))
        },
    }


@app.get("/api/security/overview")
def security_overview() -> dict:
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
    auth = {
        "enabled": authn.auth_enabled(),
        "rbac": os.getenv("ENABLE_ROLE_BASED_ACCESS", "false"),
        "allowed_upns": os.getenv("ALLOWED_UPNS", ""),
        "allowed_domains": os.getenv("ALLOWED_DOMAINS", ""),
    }
    audits = recent_events(20)
    return {"cors_origins": origins, "auth": auth, "recent_audit": audits}


# -----------------------
# Research Intelligence
# -----------------------


@app.post("/api/research/auto-track")
def auto_track_research(research_data: dict) -> dict:
    project = (research_data.get("project") or "").lower()
    entry = {k: v for k, v in research_data.items()}
    if project == "lattice":
        rec = store.append("lattice_research", entry)
    else:
        rec = store.append("tai_research", entry)
    return {"status": "ok", "id": rec["id"], "routed_project": project or "tai"}


@app.get("/api/research/synthesis")
def research_synthesis() -> dict:
    tai = store.list("tai_research")
    lattice = store.list("lattice_research")
    total = len(tai) + len(lattice)
    tags: dict[str, int] = {}
    for row in tai + lattice:
        for t in row.get("tags", []):
            tags[t] = tags.get(t, 0) + 1
    top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "total_entries": total,
        "top_tags": top_tags,
        "insights": ["Cross-project collaboration opportunities identified."],
    }
