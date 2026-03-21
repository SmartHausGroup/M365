# CAIO ↔ M365 Instruction API Contract

This document is the **single contract** for TAI → CAIO → M365. CAIO calls the M365 **instruction API** only (no direct ops-adapter dependency for the voice flow).

**Mathematical Autopsy (MA):** This contract is formalized and mathematically guaranteed under the MA process. See **`docs/contracts/README.md`** and **`docs/contracts/caio-m365/`** (Intent, Mathematics, Lemma L1) and **`invariants/INV-CAIO-M365-001.yaml`**. Verification: `scripts/ci/verify_caio_m365_contract.py` → `configs/generated/caio_m365_contract_verification.json`.

**Base URL:** The M365 Provisioning API (e.g. `http://localhost:9000` when running from repo, or your deployed URL).

---

## Endpoint

**POST** `/api/m365/instruction`

---

## Authentication

- **Header:** `X-CAIO-API-Key` or `X-CAIO-Token` (optional). If env `CAIO_API_KEY` is set on M365, the request must include this header with the same value; otherwise 401.

---

## Request

```json
{
  "action": "<action_name>",
  "params": { ... }
}
```

- **action** (string, required): One of the supported actions below.
- **params** (object, optional): Action-specific parameters. Default `{}`.
- **Idempotency-Key** (header, optional): If present, duplicate same request returns cached response.

---

## Response

```json
{
  "ok": true | false,
  "result": { ... } | null,
  "error": "<message>" | null,
  "trace_id": "<uuid>" | null
}
```

- **ok:** `true` if the action succeeded; `false` on validation or execution error.
- **result:** Present when `ok` is `true`; shape depends on action.
- **error:** Present when `ok` is `false`; short message (e.g. `Unknown action`, `m365_mutations_disabled`, `Graph not configured`).
- **trace_id:** Request id; also in response header `X-Request-ID`.

---

## Supported actions

| Action | Description | Mutating | Params |
|--------|-------------|----------|--------|
| `create_site` | Create SharePoint site with group | Yes | `display_name`, `mail_nickname?`, `libraries?`, `description?` |
| `create_team` | Create Teams workspace | Yes | `mail_nickname`, `channels?` |
| `add_channel` | Add channel to team | Yes | `mail_nickname`, `channel_name`, `description?` |
| `get_team` | Get a Teams workspace | No | `teamId` or `team_id` or `id` or `groupId` or `group_id` or `mail_nickname` |
| `list_channels` | List channels for a Teams workspace | No | `teamId` or `team_id` or `id` or `groupId` or `group_id` or `mail_nickname`, `top?` |
| `create_channel` | Create a channel in a Teams workspace | Yes | `teamId` or `team_id` or `id` or `groupId` or `group_id` or `mail_nickname`, `channel_name` or `displayName` or `name`, `description?` |
| `list_plans` | List Planner plans for a group | No | `groupId` or `group_id` or `id` or `mail_nickname` |
| `create_plan` | Create a Planner plan for a group | Yes | `groupId` or `group_id` or `id` or `mail_nickname`, `title` or `name` |
| `list_plan_buckets` | List buckets for a Planner plan | No | `planId` or `plan_id` or `id` |
| `create_plan_bucket` | Create a bucket in a Planner plan | Yes | `planId` or `plan_id` or `id`, `name` or `bucketName`, `orderHint?` |
| `create_plan_task` | Create a task in a Planner plan bucket | Yes | `planId` or `plan_id`, `bucketId` or `bucket_id`, `title` or `name`, `description?`, `referenceUrl?`, `percentComplete?` |
| `provision_service` | Provision service from config | Yes | `key` |
| `list_users` | List M365 users | No | `top?` (1–999), `select?` |
| `list_teams` | List Teams workspaces | No | `top?` |
| `list_sites` | List SharePoint site collections | No | `top?` |
| `get_site` | Get a SharePoint site by id | No | `siteId` or `site_id` or `id` |
| `list_site_lists` | List SharePoint lists for a site | No | `siteId` or `site_id` or `id`, `top?` |
| `get_list` | Get a SharePoint list by site and list id | No | `siteId` or `site_id`, `listId` or `list_id` or `id` |
| `list_list_items` | List SharePoint list items | No | `siteId` or `site_id`, `listId` or `list_id` or `id`, `top?` |
| `create_list_item` | Create a SharePoint list item | Yes | `siteId` or `site_id`, `listId` or `list_id` or `id`, `fields` |
| `list_drives` | List drives for a site, group, user, or delegated self context | No | `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `top?` |
| `get_drive` | Get a drive by id | No | `driveId` or `drive_id` or `id` |
| `list_drive_items` | List items in a drive, site drive, group drive, or delegated self drive | No | `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `folderId?`, `folderPath?`, `path?`, `top?` |
| `get_drive_item` | Get a drive item by drive and item id | No | `driveId` or `drive_id`, `itemId` or `item_id` or `id` |
| `create_folder` | Create a folder in a drive, site drive, group drive, or delegated self drive | Yes | `name` or `folderName`, `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `parentId?`, `conflictBehavior?` |
| `upload_file` | Upload a local file into a drive, site drive, group drive, or delegated self drive | Yes | `filePath` or `localPath`, `remotePath` or `path` or `fileName`, `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `conflictBehavior?`, `contentType?` |
| `create_document` | Generate and upload a DOCX document into a drive, site drive, group drive, or delegated self drive | Yes | `remotePath` or `path` or `fileName`, `title?`, `paragraphs?` or `content?`, `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `conflictBehavior?` |
| `update_document` | Regenerate and upload a DOCX document into a drive, site drive, group drive, or delegated self drive | Yes | `remotePath` or `path` or `fileName`, `title?`, `paragraphs?` or `content?`, `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `conflictBehavior?` |
| `create_workbook` | Generate and upload an XLSX workbook into a drive, site drive, group drive, or delegated self drive | Yes | `remotePath` or `path` or `fileName`, `worksheets?` or `rows?`, `sheetName?`, `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `conflictBehavior?` |
| `update_workbook` | Regenerate and upload an XLSX workbook into a drive, site drive, group drive, or delegated self drive | Yes | `remotePath` or `path` or `fileName`, `worksheets?` or `rows?`, `sheetName?`, `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `conflictBehavior?` |
| `create_presentation` | Generate and upload a PPTX presentation into a drive, site drive, group drive, or delegated self drive | Yes | `remotePath` or `path` or `fileName`, `title?`, `slides?` or `bullets?` or `items?`, `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `conflictBehavior?` |
| `update_presentation` | Regenerate and upload a PPTX presentation into a drive, site drive, group drive, or delegated self drive | Yes | `remotePath` or `path` or `fileName`, `title?`, `slides?` or `bullets?` or `items?`, `driveId?`, `groupId?`, `siteId?`, `userId?`, `userPrincipalName?`, `conflictBehavior?` |
| `get_user` | Get single user by id or UPN | No | `userPrincipalName` or `user_id` or `id` |
| `reset_user_password` | Set temporary password; force change at next sign-in | Yes | `userPrincipalName` or `user_id`, `temporary_password` or `password`, `force_change_next_sign_in?` |
| `create_user` | Create an Entra user | Yes | `userPrincipalName`, `displayName?`, `mailNickname?`, `password`, `accountEnabled?`, `jobTitle?`, `department?` |
| `update_user` | Update Entra user profile fields | Yes | `userPrincipalName` or `user_id` or `id`, `displayName?`, `jobTitle?`, `department?`, `accountEnabled?` |
| `disable_user` | Disable an Entra user account | Yes | `userPrincipalName` or `user_id` or `id` |
| `list_groups` | List Entra groups | No | `top?` |
| `get_group` | Get a single Entra group | No | `group_id` or `id` or `mail_nickname` |
| `create_group` | Create an Entra group | Yes | `display_name`, `mail_nickname`, `description?`, `mail_enabled?`, `security_enabled?` |
| `list_group_members` | List Entra group members | No | `group_id` or `id` |
| `add_group_member` | Add a member to an Entra group | Yes | `group_id` or `id`, `member_id` |
| `remove_group_member` | Remove a member from an Entra group | Yes | `group_id` or `id`, `member_id` |
| `assign_user_license` | Assign one or more licenses to an Entra user | Yes | `userPrincipalName` or `user_id` or `id`, `licenses`, `disabled_plans?` |
| `list_directory_roles` | List Entra directory roles | No | `top?` |
| `list_directory_role_members` | List members of an Entra directory role | No | `role_id` or `roleId` or `id` |
| `list_domains` | List Entra verified domains | No | none |
| `get_organization` | Get Entra organization metadata | No | none |
| `list_applications` | List Entra app registrations | No | `top?` |
| `get_application` | Get an Entra app registration | No | `app_id` or `appId` or `id` |
| `update_application` | Update an Entra app registration | Yes | `app_id` or `appId` or `id`, `body` |
| `list_service_principals` | List Entra service principals | No | `top?` |
| `list_messages` | List mailbox messages for a user or shared mailbox | No | `userId?`, `userPrincipalName?`, `mailbox?`, `top?`, `select?` |
| `get_message` | Get a mailbox message by id | No | `messageId` or `message_id` or `id`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `send_mail` | Send mail from the current user or an explicit mailbox context | Yes | `recipient_or_to` or `to` or `recipient`, `subject`, `body` or `content`, `userId?`, `userPrincipalName?`, `mailbox?`, `from?`, `contentType?`, `saveToSentItems?` |
| `move_message` | Move a mailbox message to another folder | Yes | `messageId` or `message_id` or `id`, `destinationId` or `folderId`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `delete_message` | Delete a mailbox message | Yes | `messageId` or `message_id` or `id`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `list_mail_folders` | List mail folders for a user or shared mailbox | No | `userId?`, `userPrincipalName?`, `mailbox?`, `top?` |
| `get_mailbox_settings` | Get mailbox settings | No | `userId?`, `userPrincipalName?`, `mailbox?` |
| `update_mailbox_settings` | Update mailbox settings | Yes | `body`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `list_events` | List calendar events for a user or shared mailbox | No | `userId?`, `userPrincipalName?`, `mailbox?`, `top?` |
| `create_event` | Create a calendar event | Yes | `subject`, `start`, `end`, `bodyContent?`, `location?`, `attendees?`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `get_event` | Get a calendar event by id | No | `eventId` or `event_id` or `id`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `update_event` | Update a calendar event | Yes | `eventId` or `event_id` or `id`, `body?`, `subject?`, `start?`, `end?`, `location?`, `attendees?`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `delete_event` | Delete a calendar event | Yes | `eventId` or `event_id` or `id`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `get_schedule` | Get free/busy schedule for one or more mailboxes | No | `schedules`, `startTime` or `start`, `endTime` or `end`, `availabilityViewInterval?`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `list_contacts` | List Outlook contacts for a user or shared mailbox | No | `userId?`, `userPrincipalName?`, `mailbox?`, `top?` |
| `get_contact` | Get an Outlook contact by id | No | `contactId` or `contact_id` or `id`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `create_contact` | Create an Outlook contact | Yes | `body?`, `displayName?`, `givenName?`, `surname?`, `emailAddresses?`, `email?`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `update_contact` | Update an Outlook contact | Yes | `contactId` or `contact_id` or `id`, `body?`, `displayName?`, `givenName?`, `surname?`, `emailAddresses?`, `email?`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `delete_contact` | Delete an Outlook contact | Yes | `contactId` or `contact_id` or `id`, `userId?`, `userPrincipalName?`, `mailbox?` |
| `list_contact_folders` | List Outlook contact folders for a user or shared mailbox | No | `userId?`, `userPrincipalName?`, `mailbox?`, `top?` |

**Mutating actions** require `ALLOW_M365_MUTATIONS=true` (or `1`/`yes`) in M365 env; otherwise response is `ok: false`, `error: m365_mutations_disabled`.

---

## Response shapes (result)

- **list_users:** `{ "users": [ ... ], "count": N }`
- **list_teams:** `{ "teams": [ ... ], "count": N }`
- **get_team:** `{ "team": { ... } }`
- **list_channels:** `{ "channels": [ ... ], "count": N }`
- **create_channel:** `{ "channel": { ... }, "status": "created" }`
- **list_plans:** `{ "plans": [ ... ], "count": N }`
- **create_plan:** `{ "plan": { ... }, "status": "created" }`
- **list_plan_buckets:** `{ "buckets": [ ... ], "count": N }`
- **create_plan_bucket:** `{ "bucket": { ... }, "status": "created" }`
- **create_plan_task:** `{ "task": { ... }, "status": "created" }`
- **list_sites:** `{ "sites": [ ... ], "count": N }`
- **get_site:** `{ "site": { ... } }`
- **list_site_lists:** `{ "lists": [ ... ], "count": N }`
- **get_list:** `{ "list": { ... } }`
- **list_list_items:** `{ "items": [ ... ], "count": N }`
- **create_list_item:** `{ "item": { ... }, "status": "created" }`
- **list_drives:** `{ "drives": [ ... ], "count": N }`
- **get_drive:** `{ "drive": { ... } }`
- **list_drive_items:** `{ "items": [ ... ], "count": N }`
- **get_drive_item:** `{ "item": { ... } }`
- **create_folder:** `{ "folder": { ... }, "status": "created" }`
- **upload_file:** `{ "file": { ... }, "status": "uploaded" }`
- **create_document:** `{ "document": { ... }, "status": "created" }`
- **update_document:** `{ "document": { ... }, "status": "updated" }`
- **create_workbook:** `{ "workbook": { ... }, "status": "created" }`
- **update_workbook:** `{ "workbook": { ... }, "status": "updated" }`
- **create_presentation:** `{ "presentation": { ... }, "status": "created" }`
- **update_presentation:** `{ "presentation": { ... }, "status": "updated" }`
- **get_user:** `{ "user": { ... } }`
- **reset_user_password:** `{ "user": "<id|upn>", "password_reset": true }`
- **create_user:** `{ "user": { ... }, "temporaryPassword": "<password>" }`
- **update_user:** `{ "user": { ... } }`
- **disable_user:** `{ "user": "<id|upn>", "disabled": true }`
- **list_groups:** `{ "groups": [ ... ], "count": N }`
- **get_group:** `{ "group": { ... } }`
- **create_group:** `{ "group_id": "<id>", "display_name": "<name>", "mail_nickname": "<nickname>" }`
- **list_group_members:** `{ "members": [ ... ], "count": N }`
- **add_group_member:** `{ "group_id": "<id>", "member_id": "<id>", "added": true }`
- **remove_group_member:** `{ "group_id": "<id>", "member_id": "<id>", "removed": true }`
- **assign_user_license:** `{ "user": "<id|upn>", "assigned": [ ... ], "skipped": [ ... ] }`
- **list_directory_roles:** `{ "roles": [ ... ], "count": N }`
- **list_directory_role_members:** `{ "members": [ ... ], "count": N }`
- **list_domains:** `{ "domains": [ ... ], "count": N }`
- **get_organization:** `{ "organization": { ... } }`
- **list_applications:** `{ "applications": [ ... ], "count": N }`
- **get_application:** `{ "application": { ... } }`
- **update_application:** `{ "app_id": "<id>", "status": "updated" }`
- **list_service_principals:** `{ "service_principals": [ ... ], "count": N }`
- **list_messages:** `{ "messages": [ ... ], "count": N }`
- **get_message:** `{ "message": { ... } }`
- **send_mail:** `{ "sent": true, "to": [ ... ], "subject": "<subject>", "from": "<mailbox|me>", "saveToSentItems": true|false }`
- **move_message:** `{ "moved": true, "messageId": "<id>", "destinationId": "<folder>", "message": { ... } | null }`
- **delete_message:** `{ "deleted": true, "messageId": "<id>" }`
- **list_mail_folders:** `{ "folders": [ ... ], "count": N }`
- **get_mailbox_settings:** `{ "settings": { ... } }`
- **update_mailbox_settings:** `{ "updated": true, "settings": { ... } }`
- **list_events:** `{ "events": [ ... ], "count": N }`
- **create_event:** `{ "event": { ... }, "status": "created" }`
- **get_event:** `{ "event": { ... } }`
- **update_event:** `{ "updated": true, "eventId": "<id>" }`
- **delete_event:** `{ "deleted": true, "eventId": "<id>" }`
- **get_schedule:** `{ "schedules": [ ... ], "count": N }`
- **list_contacts:** `{ "contacts": [ ... ], "count": N }`
- **get_contact:** `{ "contact": { ... } }`
- **create_contact:** `{ "contact": { ... }, "status": "created" }`
- **update_contact:** `{ "updated": true, "contactId": "<id>" }`
- **delete_contact:** `{ "deleted": true, "contactId": "<id>" }`
- **list_contact_folders:** `{ "folders": [ ... ], "count": N }`
- **create_site / create_team / add_channel / provision_service:** Action-specific (site_id, team, etc.).

---

## Idempotency

Send **Idempotency-Key** header (or body `idempotency_key`) with a stable value for the same logical request. If a previous request with the same key and same (action, params) succeeded, the same response is returned without re-running the action.

---

## References

- Implementation: `src/provisioning_api/routers/m365.py`
- Schema for dashboard: **GET** `/api/m365/actions`
- Agent registry: **GET** `/api/m365/agents`
- Status: **GET** `/api/m365/status`
