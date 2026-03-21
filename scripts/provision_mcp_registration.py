#!/usr/bin/env python3
"""Provision MCP Registration and Investor Leads SharePoint Lists.

Lists are provisioned to separate sites matching org structure:
  - MCP_Registrations → Product site (MCP_REGISTRATION_SITE_PATH or --mcp-site-path)
  - Investor_Leads    → Investor Relations site (INVESTOR_LEADS_SITE_PATH or --investor-site-path)

Usage:
    # From M365 repo root (loads .env automatically):
    python scripts/provision_mcp_registration.py

    # Override sites:
    python scripts/provision_mcp_registration.py --mcp-site-path product2 --investor-site-path investor

    # Dry run (show what would be created):
    python scripts/provision_mcp_registration.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv

if TYPE_CHECKING:
    from smarthaus_common.config import AppConfig
    from smarthaus_common.errors import GraphRequestError
    from smarthaus_graph.client import GraphClient
else:
    AppConfig = Any
    GraphClient = Any
    GraphRequestError = Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

load_dotenv(REPO_ROOT / ".env", override=False)


def _load_runtime_dependencies() -> (
    tuple[type[AppConfig], type[GraphRequestError], type[GraphClient]]
):
    from smarthaus_common.config import AppConfig as RuntimeAppConfig
    from smarthaus_common.errors import GraphRequestError as RuntimeGraphRequestError
    from smarthaus_graph.client import GraphClient as RuntimeGraphClient

    return RuntimeAppConfig, RuntimeGraphRequestError, RuntimeGraphClient


AppConfigType, GraphRequestErrorType, GraphClientType = _load_runtime_dependencies()


MCP_REGISTRATIONS_DISPLAY_NAME = "MCP_Registrations"
INVESTOR_LEADS_DISPLAY_NAME = "Investor_Leads"


MCP_REGISTRATIONS_COLUMNS: list[dict[str, Any]] = [
    {"name": "FirstName", "text": {}},
    {"name": "LastName", "text": {}},
    {"name": "Email", "text": {}},
    {"name": "Company", "text": {}},
    {"name": "Role", "text": {}},
    {
        "name": "OrganizationSize",
        "choice": {"choices": ["Individual", "1-10", "11-50", "51-200", "200+"]},
    },
    {
        "name": "UseCase",
        "choice": {
            "choices": [
                "AI research",
                "Internal tooling",
                "Enterprise deployment",
                "Evaluation",
                "Integration testing",
                "Other",
            ]
        },
    },
    {
        "name": "TechnicalRole",
        "choice": {
            "choices": [
                "Developer",
                "Architect",
                "CTO",
                "Product",
                "Researcher",
                "Other",
            ]
        },
    },
    {
        "name": "DeploymentTimeline",
        "choice": {"choices": ["Immediate", "30 Days", "90 Days", "Exploring"]},
    },
    {
        "name": "ExpectedScale",
        "choice": {
            "choices": [
                "Personal use",
                "Team use",
                "Production system",
                "Enterprise-wide",
            ]
        },
    },
    {
        "name": "LeadStatus",
        "choice": {
            "choices": ["New", "Contacted", "Approved", "Activated", "Closed"],
            "defaultValue": {"value": "New"},
        },
    },
    {"name": "ActivationSent", "boolean": {"defaultValue": {"value": False}}},
    {"name": "CertificateSerial", "text": {}},
]


INVESTOR_LEADS_COLUMNS: list[dict[str, Any]] = [
    {"name": "FirstName", "text": {}},
    {"name": "LastName", "text": {}},
    {"name": "Email", "text": {}},
    {"name": "Firm", "text": {}},
    {"name": "InvestorTitle", "text": {}},
    {"name": "Accredited", "choice": {"choices": ["Yes", "No"]}},
    {
        "name": "CheckSize",
        "choice": {
            "choices": ["<$25k", "$25k-$100k", "$100k-$500k", "$500k+"],
        },
    },
    {
        "name": "StagePreference",
        "choice": {"choices": ["Pre-Seed", "Seed", "Series A", "Flexible"]},
    },
    {
        "name": "InvestmentTimeline",
        "choice": {
            "choices": ["Active Now", "Next 6 Months", "Evaluating"],
        },
    },
    {
        "name": "InterestArea",
        "choice": {
            "choices": [
                "RFS",
                "Enterprise AI (AIVA)",
                "Deterministic Infrastructure",
                "Advisory Model",
                "Platform Economics",
            ]
        },
    },
    {
        "name": "LeadStatus",
        "choice": {
            "choices": [
                "New",
                "Intro Call",
                "Deck Sent",
                "Meeting Held",
                "DD",
                "Committed",
                "Passed",
            ],
            "defaultValue": {"value": "New"},
        },
    },
    {"name": "EstimatedInvestmentValue", "number": {}},
    {"name": "LastContacted", "dateTime": {}},
]


def _hostname() -> str:
    hostname = (os.getenv("SHAREPOINT_HOSTNAME") or os.getenv("SP_HOSTNAME") or "").strip()
    if not hostname:
        raise SystemExit(
            "SHAREPOINT_HOSTNAME is required in .env (e.g. smarthausgroup.sharepoint.com)"
        )
    return hostname


def _normalize_site_path(site_path: str) -> str:
    path = site_path.strip().strip("/")
    if path.lower().startswith("sites/"):
        path = path[6:].strip("/")
    return path


def _resolve_site(client: GraphClient, hostname: str, site_path: str) -> tuple[str, str]:
    normalized = _normalize_site_path(site_path)
    if not normalized:
        raise SystemExit(f"Site path is empty after normalization: {site_path!r}")
    site = client.get_site_by_path(hostname, normalized)
    if not site.get("id"):
        raise SystemExit(f"Site not found: {hostname}/sites/{normalized}")
    label = site.get("displayName") or normalized
    return site["id"], label


def _find_list(lists: list[dict[str, Any]], display_name: str) -> dict[str, Any] | None:
    target = display_name.lower()
    for item in lists:
        if item.get("displayName", "").lower() == target:
            return item
    return None


def _ensure_list(
    client: GraphClient,
    site_id: str,
    site_label: str,
    display_name: str,
    columns: list[dict[str, Any]],
    dry_run: bool,
) -> tuple[bool, str | None]:
    existing = _find_list(client.list_site_lists(site_id), display_name)
    if existing:
        print(f"  [skip] {display_name} already exists on {site_label}")
        return False, existing.get("id")

    if dry_run:
        print(f"  [dry-run] would create {display_name} on {site_label} ({len(columns)} columns)")
        return True, None

    try:
        created = client.create_list(site_id, display_name, columns=columns)
        print(f"  [create] {display_name} on {site_label} (inline columns)")
        return True, created.get("id")
    except GraphRequestErrorType as err:
        print(f"  [fallback] inline columns failed for {display_name}; adding columns sequentially")
        created = client.create_list(site_id, display_name)
        list_id = created.get("id")
        if not list_id:
            raise SystemExit(f"Created list without id: {display_name}") from err

        for column in columns:
            client.add_column_to_list(site_id, list_id, column)
        print(f"  [create] {display_name} on {site_label} (sequential columns)")
        return True, list_id


def _seed_items(
    client: GraphClient,
    mcp_site_id: str,
    mcp_list_id: str,
    investor_site_id: str,
    investor_list_id: str,
) -> None:
    client.create_list_item(
        mcp_site_id,
        mcp_list_id,
        {
            "FirstName": "Demo",
            "LastName": "User",
            "Email": "demo@example.com",
            "Role": "Architect",
            "LeadStatus": "New",
        },
    )
    print("  [seed] demo item → MCP_Registrations")

    client.create_list_item(
        investor_site_id,
        investor_list_id,
        {
            "FirstName": "Sample",
            "LastName": "Investor",
            "Email": "investor@example.com",
            "LeadStatus": "New",
            "InterestArea": "RFS",
        },
    )
    print("  [seed] demo item → Investor_Leads")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Provision MCP_Registrations and Investor_Leads SharePoint lists"
    )
    parser.add_argument(
        "--mcp-site-path",
        default=None,
        help="Site path for MCP_Registrations (default: MCP_REGISTRATION_SITE_PATH env)",
    )
    parser.add_argument(
        "--investor-site-path",
        default=None,
        help="Site path for Investor_Leads (default: INVESTOR_LEADS_SITE_PATH env)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed-test-data", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed_test_data and args.dry_run:
        raise SystemExit("--seed-test-data is not available with --dry-run")

    hostname = _hostname()
    config = AppConfigType()
    client: GraphClient = GraphClientType(config)

    mcp_path = args.mcp_site_path or os.getenv("MCP_REGISTRATION_SITE_PATH", "").strip()
    investor_path = args.investor_site_path or os.getenv("INVESTOR_LEADS_SITE_PATH", "").strip()

    if not mcp_path:
        raise SystemExit(
            "MCP site path required. Set MCP_REGISTRATION_SITE_PATH in .env or pass --mcp-site-path"
        )
    if not investor_path:
        raise SystemExit(
            "Investor site path required. Set INVESTOR_LEADS_SITE_PATH in .env "
            "or pass --investor-site-path"
        )

    mcp_site_id, mcp_label = _resolve_site(client, hostname, mcp_path)
    investor_site_id, investor_label = _resolve_site(client, hostname, investor_path)

    print(f"MCP_Registrations  → {mcp_label} ({hostname}/sites/{_normalize_site_path(mcp_path)})")
    print(
        f"Investor_Leads     → {investor_label} ({hostname}/sites/{_normalize_site_path(investor_path)})"
    )
    print()

    mcp_created, mcp_list_id = _ensure_list(
        client,
        mcp_site_id,
        mcp_label,
        MCP_REGISTRATIONS_DISPLAY_NAME,
        MCP_REGISTRATIONS_COLUMNS,
        args.dry_run,
    )

    inv_created, inv_list_id = _ensure_list(
        client,
        investor_site_id,
        investor_label,
        INVESTOR_LEADS_DISPLAY_NAME,
        INVESTOR_LEADS_COLUMNS,
        args.dry_run,
    )

    if args.seed_test_data and not args.dry_run:
        if not mcp_list_id:
            raise SystemExit("Cannot seed MCP_Registrations: list id unavailable")
        if not inv_list_id:
            raise SystemExit("Cannot seed Investor_Leads: list id unavailable")
        _seed_items(client, mcp_site_id, mcp_list_id, investor_site_id, inv_list_id)

    print()
    print("Summary:")
    for name, created, dry in [
        (MCP_REGISTRATIONS_DISPLAY_NAME, mcp_created, args.dry_run),
        (INVESTOR_LEADS_DISPLAY_NAME, inv_created, args.dry_run),
    ]:
        if created and dry:
            status = "would create"
        elif created:
            status = "created"
        else:
            status = "exists (skipped)"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()
