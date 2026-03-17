# Uploading Files to Any M365 Drive (Agent Capability)

The M365 agent can upload files (e.g. `.docx`) to **any** of:

- **Teams site** — group-backed; the Team’s default document library
- **SharePoint site** — including **communications sites** and other site collections (default document library)
- **OneDrive** — a user’s OneDrive (by user id or UPN)

So it’s a single **upload-to-drive** capability that works across Teams, SharePoint, and OneDrive.

---

## What was added

1. **Graph client** (`src/smarthaus_graph/client.py`):
   - **`upload_file_to_drive(drive_owner, owner_id, path_in_drive, file_bytes, content_type)`**  
     Generic upload. `drive_owner` is `"group"` | `"site"` | `"user"`; `owner_id` is the group id, site id, or user id (or `"me"` where applicable).
   - **`upload_file_to_group_drive(...)`** — convenience for Teams (group drive).
   - **`upload_file_to_site_drive(...)`** — convenience for SharePoint (including communications sites).
   - **`upload_file_to_user_drive(...)`** — convenience for OneDrive.
   - **`find_group_by_display_name(...)`** — resolve group by display name for script/API use.

2. **Script** (`scripts/upload_docx_to_team_site.py`):  
   Batch-uploads all `.docx` from given directories to a chosen target. Requires **`--target-type`** and the matching target id/name.

---

## Prerequisites

- **Azure app** with Microsoft Graph **application** permission: **Files.ReadWrite.All** (or Sites.ReadWrite.All for group/site).
- **Env:** `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET` (or your existing Graph env vars).
- The **target** must already exist: Team (group), SharePoint site, or user.

---

## How to run the script

From the **M365 repo root** (set `PYTHONPATH="$(pwd)/src"` if needed):

```bash
# Teams site (group) — by display name or mail nickname
python scripts/upload_docx_to_team_site.py --target-type group --team "Investor Relations" /path/to/dirs
python scripts/upload_docx_to_team_site.py --target-type group --team-nickname InvestorRelations /path/to/dirs

# SharePoint site (incl. communications site) — by site path
python scripts/upload_docx_to_team_site.py --target-type site --site-path sites/MyCommSite /path/to/dirs
python scripts/upload_docx_to_team_site.py --target-type site --site-path sites/InvestorRelations --site-hostname contoso.sharepoint.com /path/to/dirs

# OneDrive — by user id or UPN
python scripts/upload_docx_to_team_site.py --target-type user --user user@domain.com /path/to/dirs
```

- **`--folder`** (or env **`UPLOAD_FOLDER`**): subfolder under the drive root (e.g. `Investor Relations`).
- **Positional args:** one or more directories; all `.docx` under them (recursive) are uploaded; relative paths are preserved in the drive.

### Example: Investor Relations Teams site

```bash
export UPLOAD_FOLDER="Investor Relations"
python scripts/upload_docx_to_team_site.py --target-type group --team "Investor Relations" \
  /path/to/Advisory/00-FOUNDATION /path/to/Advisory/01-OFFERS /path/to/SMARTHAUS/docs/gtm
```

---

## Permissions

| Purpose              | Permission (application) |
|----------------------|---------------------------|
| Resolve group/site/user | Group.Read.All, Sites.Read.All, User.Read.All (or existing read) |
| Upload to drive      | **Files.ReadWrite.All** (or Sites.ReadWrite.All for group/site) |

403 on upload → add **Files.ReadWrite.All** and grant admin consent.

---

## Exposing this as an instruction action (agent)

To make “upload file” a first-class M365 instruction (e.g. for CAIO or a dashboard):

1. In `provisioning_api/routers/m365.py`, add an action such as **`upload_to_drive`**.
2. **Params:**  
   `drive_owner` (`group` | `site` | `user`), `owner_id` (or resolvers: e.g. `group_display_name`, `site_path`, `user_upn`), `path_in_drive`, and file content (e.g. base64 or URL).
3. Call **`GraphClient.upload_file_to_drive(drive_owner, owner_id, path_in_drive, content_bytes, content_type)`** (and resolve owner_id from name/path/UPN if you pass those instead of raw id).

Then the agent can upload to **any** Teams site, communications site, or OneDrive in one consistent action.
