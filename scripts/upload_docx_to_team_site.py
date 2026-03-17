#!/usr/bin/env python3
"""
Upload .docx files to any M365 drive: Teams site (group), SharePoint site (incl. communications), or OneDrive.

Requires: GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET and app permission Files.ReadWrite.All.

Usage (from M365 repo root; set PYTHONPATH=src if needed):

  # Teams site (by group display name or mail nickname)
  python scripts/upload_docx_to_team_site.py --target-type group --team "Investor Relations" /path/to/dirs
  python scripts/upload_docx_to_team_site.py --target-type group --team-nickname InvestorRelations /path/to/dirs

  # SharePoint site (communications or team site by path)
  python scripts/upload_docx_to_team_site.py --target-type site --site-path sites/MySite /path/to/dirs
  python scripts/upload_docx_to_team_site.py --target-type site --site-path sites/InvestorRelations --site-hostname contoso.sharepoint.com /path/to/dirs

  # OneDrive (user by id or UPN)
  python scripts/upload_docx_to_team_site.py --target-type user --user user@domain.com /path/to/dirs

Optional: UPLOAD_FOLDER env or --folder = subfolder path under the drive root.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from smarthaus_graph.client import GraphClient

DOCX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def resolve_target(
    client: GraphClient,
    target_type: str,
    *,
    display_name: str | None = None,
    mail_nickname: str | None = None,
    site_path: str | None = None,
    site_hostname: str | None = None,
    user: str | None = None,
) -> tuple[str, str]:
    """Return (owner_id, label) for the given target. owner_id is group id, site id, or user id."""
    target_type = target_type.lower().strip()
    if target_type == "group":
        if mail_nickname:
            grp = client.find_group_by_mailnickname(mail_nickname)
        elif display_name:
            grp = client.find_group_by_display_name(display_name)
        else:
            raise ValueError("For target-type group provide --team or --team-nickname.")
        if not grp or not grp.get("id"):
            raise SystemExit(f"Group not found: display_name={display_name!r}, mail_nickname={mail_nickname!r}")
        return grp["id"], grp.get("displayName", grp["id"])
    if target_type == "site":
        if not site_path or not site_path.strip():
            raise ValueError("For target-type site provide --site-path (e.g. MySite or sites/MySite).")
        hostname = (site_hostname or os.getenv("SHAREPOINT_HOSTNAME") or os.getenv("SP_HOSTNAME") or "smarthausgroup.sharepoint.com").strip()
        path = site_path.strip().strip("/")
        if path.lower().startswith("sites/"):
            path = path[6:].strip("/")
        site = client.get_site_by_path(hostname, path)
        if not site or not site.get("id"):
            raise SystemExit(f"Site not found: {hostname} / {path}")
        return site["id"], site.get("name", site["id"])
    if target_type == "user":
        if not user or not user.strip():
            raise ValueError("For target-type user provide --user (id or UPN).")
        u = client.get_user(user.strip())
        if not u or not u.get("id"):
            raise SystemExit(f"User not found: {user!r}")
        return u["id"], u.get("displayName", u["id"])
    raise ValueError("target_type must be one of: group, site, user")


def collect_docx(root_dirs: list[Path]) -> list[tuple[Path, Path]]:
    """Return list of (absolute_path, relative_path) for each .docx under root_dirs."""
    out: list[tuple[Path, Path]] = []
    for root in root_dirs:
        root = root.resolve()
        if not root.is_dir():
            print(f"Warning: not a directory, skipping: {root}", file=sys.stderr)
            continue
        for f in root.rglob("*.docx"):
            if f.is_file():
                try:
                    rel = f.relative_to(root)
                except ValueError:
                    rel = Path(f.name)
                out.append((f, rel))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload .docx files to a Teams site, SharePoint site, or OneDrive (M365 agent-style)."
    )
    parser.add_argument(
        "--target-type",
        choices=["group", "site", "user"],
        required=True,
        help="Where to upload: group (Teams), site (SharePoint incl. communications), user (OneDrive).",
    )
    parser.add_argument(
        "--team",
        dest="display_name",
        metavar="NAME",
        help="Group display name (for --target-type group).",
    )
    parser.add_argument(
        "--team-nickname",
        dest="mail_nickname",
        metavar="NICKNAME",
        help="Group mail nickname (for --target-type group).",
    )
    parser.add_argument(
        "--site-path",
        metavar="PATH",
        help="SharePoint site path (e.g. sites/MySite) for --target-type site.",
    )
    parser.add_argument(
        "--site-hostname",
        metavar="HOST",
        help="SharePoint hostname (default: SHAREPOINT_HOSTNAME env or smarthausgroup.sharepoint.com).",
    )
    parser.add_argument(
        "--user",
        metavar="ID_OR_UPN",
        help="User id or UPN for --target-type user (OneDrive).",
    )
    parser.add_argument(
        "--folder",
        default=os.getenv("UPLOAD_FOLDER", "").strip().strip("/"),
        metavar="PATH",
        help="Subfolder under drive root (default: UPLOAD_FOLDER env).",
    )
    parser.add_argument(
        "dirs",
        nargs="+",
        type=Path,
        help="One or more directories to scan for .docx files (recursive).",
    )
    args = parser.parse_args()

    client = GraphClient()
    owner_id, label = resolve_target(
        client,
        args.target_type,
        display_name=args.display_name,
        mail_nickname=args.mail_nickname,
        site_path=args.site_path,
        site_hostname=args.site_hostname,
        user=args.user,
    )
    print(f"Target: {args.target_type} ({label}) id={owner_id}")

    folder_prefix = (args.folder or "").strip().strip("/")
    if folder_prefix:
        print(f"Upload folder in drive: {folder_prefix}")

    files = collect_docx(args.dirs)
    if not files:
        print("No .docx files found under the given directories.", file=sys.stderr)
        sys.exit(0)

    print(f"Uploading {len(files)} file(s)...")
    for abs_path, rel_path in files:
        drive_path = f"{folder_prefix}/{rel_path.as_posix()}" if folder_prefix else rel_path.as_posix()
        drive_path = drive_path.replace("\\", "/").lstrip("/")
        try:
            content = abs_path.read_bytes()
            client.upload_file_to_drive(
                args.target_type,
                owner_id,
                drive_path,
                content,
                content_type=DOCX_CONTENT_TYPE,
            )
            print(f"  OK {drive_path}")
        except Exception as e:
            print(f"  FAIL {drive_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
