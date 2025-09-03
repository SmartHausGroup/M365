from __future__ import annotations

from fastapi import APIRouter, HTTPException

from provisioning_api.audit import log_event
from provisioning_api.m365_provision import provision_group_site, provision_teams_workspace
from provisioning_api.metrics import inc_sites_created, inc_teams_created

router = APIRouter(prefix="/api/m365/provision", tags=["m365"])


@router.post("/tai")
def provision_tai() -> dict:
    try:
        result = provision_group_site(
            display_name="TAI Research Hub",
            mail_nickname="tai-research",
            description="TAI research collaboration site",
            libraries=[
                "Research Papers",
                "Holographic Memory",
                "AI Orchestration",
                "Performance Metrics",
                "Project Management",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_tai", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/lattice")
def provision_lattice() -> dict:
    try:
        result = provision_group_site(
            display_name="LATTICE Research Hub",
            mail_nickname="lattice-research",
            description="LATTICE research collaboration site",
            libraries=[
                "Architecture Documentation",
                "AIOS Development",
                "LQL Language",
                "LEF Execution",
                "Mathematical Proofs",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_lattice", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/business")
def provision_business() -> dict:
    try:
        result = provision_group_site(
            display_name="SmartHaus Group Business Hub",
            mail_nickname="business-hub",
            description="Business operations hub",
            libraries=[
                "Website Updates",
                "Business Development",
                "Client Projects",
                "Strategic Planning",
            ],
        )
        inc_sites_created(1 if result.get("group_created") else 0)
        log_event("provision_site_business", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/teams/tai")
def create_tai_team() -> dict:
    try:
        channels = [
            "General",
            "Holographic Memory",
            "AI Orchestration",
            "Performance Metrics",
            "Research Updates",
        ]
        result = provision_teams_workspace("tai-research", channels)
        inc_teams_created()
        log_event("provision_team_tai", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/teams/lattice")
def create_lattice_team() -> dict:
    try:
        channels = [
            "General",
            "AIOS Development",
            "LQL Language",
            "LEF Execution",
            "Architecture Updates",
        ]
        result = provision_teams_workspace("lattice-research", channels)
        inc_teams_created()
        log_event("provision_team_lattice", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/teams/business")
def create_business_team() -> dict:
    try:
        channels = [
            "General",
            "Website Development",
            "Business Development",
            "Client Projects",
            "Strategic Planning",
        ]
        result = provision_teams_workspace("business-hub", channels)
        inc_teams_created()
        log_event("provision_team_business", result)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
