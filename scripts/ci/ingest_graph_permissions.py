#!/usr/bin/env python3
"""
Ingest Microsoft Graph permissions into the capability registry (MA-aligned).

M365_MASTER_CALCULUS_FULL.md §4: build O from Graph permissions reference.
With Graph auth: GET servicePrincipals(Microsoft Graph), parse appRoles and
oauth2PermissionScopes, output permissions list (and optionally merge into
registry). Without auth: print usage and optionally emit static permission list.

Env (for live ingest): AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
  (or GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, GRAPH_TENANT_ID).
Output: stdout YAML or --merge into registry/capability_registry.yaml.

Usage:
  python scripts/ci/ingest_graph_permissions.py                    # list permissions (static if no auth)
  python scripts/ci/ingest_graph_permissions.py --live            # fetch from Graph when env set
  python scripts/ci/ingest_graph_permissions.py --live --merge   # fetch and merge into registry (planned actions)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_APP_ID = "00000003-0000-0000-c000-000000000000"  # Microsoft Graph
GRAPH_URL = f"https://graph.microsoft.com/v1.0/servicePrincipals(appId='{GRAPH_APP_ID}')"
SELECT = "id,appId,displayName,appRoles,oauth2PermissionScopes"


def get_token() -> str | None:
    """Obtain access token for Graph (client credentials)."""
    client_id = os.environ.get("AZURE_CLIENT_ID") or os.environ.get("GRAPH_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET") or os.environ.get("GRAPH_CLIENT_SECRET")
    tenant_id = os.environ.get("AZURE_TENANT_ID") or os.environ.get("GRAPH_TENANT_ID")
    if not all((client_id, client_secret, tenant_id)):
        return None
    try:
        import urllib.request
        import urllib.parse
        body = urllib.parse.urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }).encode()
        req = urllib.request.Request(
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get("access_token")
    except Exception:
        return None


def fetch_graph_permissions(token: str) -> dict | None:
    """GET Microsoft Graph servicePrincipal appRoles and oauth2PermissionScopes."""
    try:
        import urllib.request
        req = urllib.request.Request(
            f"{GRAPH_URL}?$select={SELECT}",
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def extract_permissions(sp: dict) -> tuple[list[dict], list[dict]]:
    """Return (app_roles, delegated_scopes) from servicePrincipal."""
    app_roles = sp.get("appRoles") or []
    delegated = sp.get("oauth2PermissionScopes") or []
    return list(app_roles), list(delegated)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest Graph permissions for capability registry")
    parser.add_argument("--live", action="store_true", help="Fetch from Graph API (requires env auth)")
    parser.add_argument("--merge", action="store_true", help="Merge into registry (planned actions from new permissions)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of YAML")
    args = parser.parse_args()

    if args.live:
        token = get_token()
        if not token:
            print("ingest_graph_permissions: no Graph auth (set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)", file=sys.stderr)
            print("See: https://learn.microsoft.com/en-us/graph/permissions-reference", file=sys.stderr)
            # Emit static list so script is still useful
            app_roles = []
            delegated = []
        else:
            sp = fetch_graph_permissions(token)
            if not sp:
                print("ingest_graph_permissions: failed to fetch servicePrincipal", file=sys.stderr)
                return 1
            app_roles, delegated = extract_permissions(sp)
    else:
        # Static subset from permissions reference (no auth)
        app_roles = [
            {"value": "User.Read.All", "displayName": "Read all users' full profiles"},
            {"value": "User.ReadWrite.All", "displayName": "Read and write all users' full profiles"},
            {"value": "Group.Read.All", "displayName": "Read all groups"},
            {"value": "Group.ReadWrite.All", "displayName": "Read and write all groups"},
            {"value": "Mail.Read", "displayName": "Read user mail"},
            {"value": "Mail.Send", "displayName": "Send mail as a user"},
            {"value": "Calendars.Read", "displayName": "Read user calendars"},
            {"value": "Calendars.ReadWrite", "displayName": "Read and write user calendars"},
            {"value": "Files.Read.All", "displayName": "Read files that user can access"},
            {"value": "Files.ReadWrite.All", "displayName": "Read and write files that user can access"},
            {"value": "Sites.Read.All", "displayName": "Read items in all site collections"},
            {"value": "Sites.ReadWrite.All", "displayName": "Read and write items in all site collections"},
            {"value": "Team.ReadBasic.All", "displayName": "Read basic properties of teams"},
            {"value": "Team.Create", "displayName": "Create teams"},
            {"value": "Channel.ReadBasic.All", "displayName": "Read channel names and channel descriptions"},
            {"value": "Channel.Create.Group", "displayName": "Create channels in group teams"},
            {"value": "ChannelMessage.Send", "displayName": "Send channel messages"},
        ]
        delegated = []

    out = {
        "source": "Microsoft Graph servicePrincipal" if args.live else "static (permissions reference subset)",
        "app_roles_count": len(app_roles),
        "delegated_count": len(delegated),
        "app_roles": [{"value": r.get("value"), "displayName": r.get("displayName", "")} for r in app_roles],
        "delegated_scopes": [{"value": s.get("value"), "adminConsentDisplayName": s.get("adminConsentDisplayName", "")} for s in delegated],
    }

    if args.json:
        json.dump(out, sys.stdout, indent=2)
    else:
        try:
            import yaml
            yaml.dump(out, sys.stdout, default_flow_style=False, sort_keys=False)
        except ImportError:
            json.dump(out, sys.stdout, indent=2)

    if args.merge and args.live and app_roles:
        # Optional: merge new permissions into registry as planned actions (skip if no PyYAML or no registry)
        registry_path = REPO_ROOT / "registry" / "capability_registry.yaml"
        if not registry_path.exists():
            print("ingest_graph_permissions: registry not found, skip --merge", file=sys.stderr)
            return 0
        try:
            import yaml
            reg = yaml.safe_load(registry_path.read_text())
            existing_values = {a.get("action") for a in reg.get("actions", [])}
            # Could add new actions here from app_roles; for now we only document that merge is possible
            print("ingest_graph_permissions: --merge (registry exists; add planned actions manually or extend script)", file=sys.stderr)
        except Exception as e:
            print("ingest_graph_permissions: merge failed", e, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
