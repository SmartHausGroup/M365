from __future__ import annotations

import os
from typing import Any

import httpx


def is_enabled() -> bool:
    return os.getenv("ENABLE_VERCEL_LIVE_DATA", "false").lower() in ("1", "true", "yes")


def _token() -> str | None:
    return os.getenv("VERCEL_TOKEN")


def _team() -> str | None:
    return os.getenv("VERCEL_TEAM_ID")


def _client() -> httpx.Client:
    tok = _token()
    if not tok:
        raise RuntimeError("VERCEL_TOKEN not set")
    headers = {"Authorization": f"Bearer {tok}"}
    return httpx.Client(base_url="https://api.vercel.com", headers=headers, timeout=10)


def list_projects() -> dict[str, Any]:
    if not is_enabled():
        return {"enabled": False, "reason": "ENABLE_VERCEL_LIVE_DATA=false"}
    try:
        params: dict[str, Any] = {}
        if _team():
            params["teamId"] = _team()
        with _client() as c:
            r = c.get("/v9/projects", params=params)
            if r.status_code != 200:
                return {"enabled": True, "error": r.text}
            data = r.json()
            return {"enabled": True, "projects": data.get("projects") or data.get("items") or data}
    except Exception as e:
        return {"enabled": True, "error": str(e)}


def list_deployments(project_id: str | None = None, limit: int = 20) -> dict[str, Any]:
    if not is_enabled():
        return {"enabled": False, "reason": "ENABLE_VERCEL_LIVE_DATA=false"}
    try:
        params: dict[str, Any] = {"limit": limit}
        if _team():
            params["teamId"] = _team()
        if project_id:
            params["projectId"] = project_id
        with _client() as c:
            r = c.get("/v13/deployments", params=params)
            if r.status_code != 200:
                return {"enabled": True, "error": r.text}
            return {
                "enabled": True,
                "deployments": r.json().get("deployments") or r.json().get("items") or r.json(),
            }
    except Exception as e:
        return {"enabled": True, "error": str(e)}


def list_domains() -> dict[str, Any]:
    if not is_enabled():
        return {"enabled": False, "reason": "ENABLE_VERCEL_LIVE_DATA=false"}
    try:
        params: dict[str, Any] = {}
        if _team():
            params["teamId"] = _team()
        with _client() as c:
            r = c.get("/v6/domains", params=params)
            if r.status_code != 200:
                return {"enabled": True, "error": r.text}
            data = r.json()
            return {"enabled": True, "domains": data.get("domains") or data.get("items") or data}
    except Exception as e:
        return {"enabled": True, "error": str(e)}
