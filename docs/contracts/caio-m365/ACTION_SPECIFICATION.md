# CAIO ↔ M365 Instruction API — Action Specification

**MA Phase:** 2 — Per-action contract
**Source:** `docs/CAIO_M365_CONTRACT.md`, implementation in `src/provisioning_api/routers/m365.py`
**Full capability set:** North Star `SMARTHAUS/docs/projects/m365-tai/NORTH_STAR.md` §§3.1 (Admin), 3.2 (User).

This document enumerates **every action** that is part of the CAIO–M365 contract. For each **implemented** action we give full preconditions, result shape, and mutating flag. Actions not yet implemented are listed in the "Planned (North Star)" section for traceability; adding a new action requires updating this spec, MATHEMATICS.md, and the verification script.

---

## Implemented actions (current)

\(\mathcal{A}\) = set of supported action names. \(\mathcal{A}_m\) = mutating subset.

### 1. list_users

| Field | Specification |
|-------|----------------|
| **action** | `list_users` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional), `select` string (optional, comma-separated). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_users}}\) | `{ "users": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top` or `select`. |

### 2. list_teams

| Field | Specification |
|-------|----------------|
| **action** | `list_teams` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` positive integer (optional, default 100). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_teams}}\) | `{ "teams": array, "count": number }` |
| **Error cases** | Graph not configured. |

### 3. list_sites

| Field | Specification |
|-------|----------------|
| **action** | `list_sites` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` positive integer (optional). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_sites}}\) | `{ "sites": array, "count": number }` |
| **Error cases** | Graph not configured. |

### 4. get_user

| Field | Specification |
|-------|----------------|
| **action** | `get_user` |
| **Mutating** | No |
| **Preconditions** | One of `userPrincipalName`, `user_id`, or `id` present in `params` (string). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_user}}\) | `{ "user": object }` |
| **Error cases** | Missing identifier; user not found; Graph not configured. |

### 5. reset_user_password

| Field | Specification |
|-------|----------------|
| **action** | `reset_user_password` |
| **Mutating** | Yes |
| **Preconditions** | `params`: one of `userPrincipalName`/`user_id`/`id` (string); `temporary_password` or `password` (string). Optional: `force_change_next_sign_in` (boolean, default true). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{reset\_user\_password}}\) | `{ "user": string, "password_reset": true }` |
| **Error cases** | Missing params; Graph not configured; mutations disabled. |

### 6. create_user

| Field | Specification |
|-------|----------------|
| **action** | `create_user` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `userPrincipalName` (string, required), `password` or `temporary_password` (string, required). Optional: `displayName`, `mailNickname`, `accountEnabled`, `jobTitle`, `department`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_user}}\) | `{ "user": object, "temporaryPassword": string }` |
| **Error cases** | Missing required params; Graph not configured; mutations disabled. |

### 7. update_user

| Field | Specification |
|-------|----------------|
| **action** | `update_user` |
| **Mutating** | Yes |
| **Preconditions** | `params`: one of `userPrincipalName`/`user_id`/`id` plus at least one of `displayName`, `jobTitle`, `department`, `accountEnabled`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_user}}\) | `{ "user": object }` |
| **Error cases** | Missing identifier; empty patch; Graph not configured; mutations disabled. |

### 8. disable_user

| Field | Specification |
|-------|----------------|
| **action** | `disable_user` |
| **Mutating** | Yes |
| **Preconditions** | `params`: one of `userPrincipalName`/`user_id`/`id` (string). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{disable\_user}}\) | `{ "user": string, "disabled": true }` |
| **Error cases** | Missing identifier; Graph not configured; mutations disabled. |

### 9. list_groups

| Field | Specification |
|-------|----------------|
| **action** | `list_groups` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_groups}}\) | `{ "groups": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`. |

### 10. get_group

| Field | Specification |
|-------|----------------|
| **action** | `get_group` |
| **Mutating** | No |
| **Preconditions** | One of `group_id`, `id`, or `mail_nickname` present in `params` (string). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_group}}\) | `{ "group": object }` |
| **Error cases** | Missing identifier; group not found; Graph not configured. |

### 11. create_group

| Field | Specification |
|-------|----------------|
| **action** | `create_group` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `display_name` and `mail_nickname` (strings). Optional: `description`, `mail_enabled`, `security_enabled`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_group}}\) | `{ "group_id": string, "display_name": string, "mail_nickname": string }` |
| **Error cases** | Missing display_name or mail_nickname; Graph not configured; mutations disabled. |

### 12. list_group_members

| Field | Specification |
|-------|----------------|
| **action** | `list_group_members` |
| **Mutating** | No |
| **Preconditions** | `params`: `group_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_group\_members}}\) | `{ "members": array, "count": number }` |
| **Error cases** | Missing group_id; group not found; Graph not configured. |

### 13. add_group_member

| Field | Specification |
|-------|----------------|
| **action** | `add_group_member` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `group_id` and `member_id` (strings). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{add\_group\_member}}\) | `{ "group_id": string, "member_id": string, "added": true }` |
| **Error cases** | Missing identifiers; Graph not configured; mutations disabled. |

### 14. remove_group_member

| Field | Specification |
|-------|----------------|
| **action** | `remove_group_member` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `group_id` and `member_id` (strings). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{remove\_group\_member}}\) | `{ "group_id": string, "member_id": string, "removed": true }` |
| **Error cases** | Missing identifiers; Graph not configured; mutations disabled. |

### 15. assign_user_license

| Field | Specification |
|-------|----------------|
| **action** | `assign_user_license` |
| **Mutating** | Yes |
| **Preconditions** | `params`: one of `userPrincipalName`/`user_id`/`id` and a non-empty `licenses` array. Optional `disabled_plans` object. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{assign\_user\_license}}\) | `{ "user": string, "assigned": array, "skipped": array }` |
| **Error cases** | Missing user identifier; missing or invalid license list; Graph not configured; mutations disabled. |

### 16. list_directory_roles

| Field | Specification |
|-------|----------------|
| **action** | `list_directory_roles` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_directory\_roles}}\) | `{ "roles": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`. |

### 17. list_directory_role_members

| Field | Specification |
|-------|----------------|
| **action** | `list_directory_role_members` |
| **Mutating** | No |
| **Preconditions** | `params`: `role_id` or `roleId` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_directory\_role\_members}}\) | `{ "members": array, "count": number }` |
| **Error cases** | Missing role identifier; Graph not configured. |

### 18. list_domains

| Field | Specification |
|-------|----------------|
| **action** | `list_domains` |
| **Mutating** | No |
| **Preconditions** | `params` optional and ignored. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_domains}}\) | `{ "domains": array, "count": number }` |
| **Error cases** | Graph not configured. |

### 19. get_organization

| Field | Specification |
|-------|----------------|
| **action** | `get_organization` |
| **Mutating** | No |
| **Preconditions** | `params` optional and ignored. |
| **Result shape** \(\mathcal{S}_{\texttt{get\_organization}}\) | `{ "organization": object | null }` |
| **Error cases** | Graph not configured. |

### 20. list_applications

| Field | Specification |
|-------|----------------|
| **action** | `list_applications` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_applications}}\) | `{ "applications": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`. |

### 21. get_application

| Field | Specification |
|-------|----------------|
| **action** | `get_application` |
| **Mutating** | No |
| **Preconditions** | `params`: `app_id` or `appId` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_application}}\) | `{ "application": object }` |
| **Error cases** | Missing application identifier; Graph not configured. |

### 22. update_application

| Field | Specification |
|-------|----------------|
| **action** | `update_application` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `app_id` or `appId` or `id` (string, required) plus `body` (object, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_application}}\) | `{ "app_id": string, "status": "updated" }` |
| **Error cases** | Missing application identifier or body; Graph not configured; mutations disabled. |

### 23. list_service_principals

| Field | Specification |
|-------|----------------|
| **action** | `list_service_principals` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_service\_principals}}\) | `{ "service_principals": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`. |

### 24. create_site

| Field | Specification |
|-------|----------------|
| **action** | `create_site` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `display_name` (string, required) or `site_name`. Optional: `mail_nickname`/`url_slug`, `libraries` (array), `description`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_site}}\) | `{ "site_id": string, "site_url": string, "group_created": boolean, "libraries_created": array }` |
| **Error cases** | Missing display_name; Graph/site creation failure; mutations disabled. |

### 25. create_team

| Field | Specification |
|-------|----------------|
| **action** | `create_team` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `mail_nickname` (string, required). Optional: `channels` (array of strings). Mutations must be enabled. Group must exist (e.g. create_site first). |
| **Result shape** \(\mathcal{S}_{\texttt{create\_team}}\) | `{ "team_id": string, "team_url": string, "channels_created": array }` |
| **Error cases** | Missing mail_nickname; group not found; mutations disabled. |

### 26. add_channel

| Field | Specification |
|-------|----------------|
| **action** | `add_channel` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `mail_nickname` (string), `channel_name` (string). Optional: `description`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{add\_channel}}\) | `{ "team": object, "channel": string }` |
| **Error cases** | Missing mail_nickname or channel_name; group/team not found; mutations disabled. |

### 27. provision_service

| Field | Specification |
|-------|----------------|
| **action** | `provision_service` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `key` (string, required) — must match a key in `config/services.json`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{provision\_service}}\) | `{ "status": "ok", "site": object, "team": object }` |
| **Error cases** | Missing key; config/services.json missing; unknown service key; mutations disabled. |

### Outlook / Exchange expansion actions

The following actions are implemented as part of `E2B`. They share the same deterministic instruction envelope and are routed to the bounded `messaging` executor with `hybrid` auth semantics.

### 28. list_messages

| Field | Specification |
|-------|----------------|
| **action** | `list_messages` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `userId` or `userPrincipalName` or `mailbox` selects an explicit mailbox target; `top` ∈ [1, 999] (optional); `select` string (optional). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_messages}}\) | `{ "messages": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; app-only request without explicit mailbox context. |

### 29. get_message

| Field | Specification |
|-------|----------------|
| **action** | `get_message` |
| **Mutating** | No |
| **Preconditions** | `params`: `messageId` or `message_id` or `id` (string, required). Optional mailbox selector: `userId` or `userPrincipalName` or `mailbox`. |
| **Result shape** \(\mathcal{S}_{\texttt{get\_message}}\) | `{ "message": object }` |
| **Error cases** | Missing message identifier; Graph not configured; app-only request without explicit mailbox context. |

### 30. send_mail

| Field | Specification |
|-------|----------------|
| **action** | `send_mail` |
| **Mutating** | Yes |
| **Preconditions** | `params`: recipient (`recipient_or_to` or `to` or `recipient`), `subject`, and `body` or `content` (required). Optional mailbox selector: `userId` or `userPrincipalName` or `mailbox` or `from`. Optional `contentType`, `saveToSentItems`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{send\_mail}}\) | `{ "sent": true, "to": array, "subject": string, "from": string, "saveToSentItems": boolean }` |
| **Error cases** | Missing recipient, subject, or body; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 31. move_message

| Field | Specification |
|-------|----------------|
| **action** | `move_message` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `messageId` or `message_id` or `id`, `destinationId` or `folderId`. Optional mailbox selector: `userId` or `userPrincipalName` or `mailbox`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{move\_message}}\) | `{ "moved": true, "messageId": string, "destinationId": string, "message": object | null }` |
| **Error cases** | Missing message or destination identifier; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 32. delete_message

| Field | Specification |
|-------|----------------|
| **action** | `delete_message` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `messageId` or `message_id` or `id` (required). Optional mailbox selector: `userId` or `userPrincipalName` or `mailbox`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{delete\_message}}\) | `{ "deleted": true, "messageId": string }` |
| **Error cases** | Missing message identifier; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 33. list_mail_folders

| Field | Specification |
|-------|----------------|
| **action** | `list_mail_folders` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: explicit mailbox selector plus optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_mail\_folders}}\) | `{ "folders": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; app-only request without explicit mailbox context. |

### 34. get_mailbox_settings

| Field | Specification |
|-------|----------------|
| **action** | `get_mailbox_settings` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `userId` or `userPrincipalName` or `mailbox`. |
| **Result shape** \(\mathcal{S}_{\texttt{get\_mailbox\_settings}}\) | `{ "settings": object }` |
| **Error cases** | Graph not configured; app-only request without explicit mailbox context. |

### 35. update_mailbox_settings

| Field | Specification |
|-------|----------------|
| **action** | `update_mailbox_settings` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `body` (object, required). Optional mailbox selector: `userId` or `userPrincipalName` or `mailbox`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_mailbox\_settings}}\) | `{ "updated": true, "settings": object }` |
| **Error cases** | Missing or invalid body; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 36. list_events

| Field | Specification |
|-------|----------------|
| **action** | `list_events` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: explicit mailbox selector plus optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_events}}\) | `{ "events": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; app-only request without explicit mailbox context. |

### 37. create_event

| Field | Specification |
|-------|----------------|
| **action** | `create_event` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `subject`, `start`, and `end` (required). Optional `bodyContent`, `location`, `attendees`, and mailbox selector. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_event}}\) | `{ "event": object, "status": "created" }` |
| **Error cases** | Missing required event body fields; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 38. get_event

| Field | Specification |
|-------|----------------|
| **action** | `get_event` |
| **Mutating** | No |
| **Preconditions** | `params`: `eventId` or `event_id` or `id` (required). Optional mailbox selector. |
| **Result shape** \(\mathcal{S}_{\texttt{get\_event}}\) | `{ "event": object }` |
| **Error cases** | Missing event identifier; Graph not configured; app-only request without explicit mailbox context. |

### 39. update_event

| Field | Specification |
|-------|----------------|
| **action** | `update_event` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `eventId` or `event_id` or `id` plus at least one patch field among `body`, `subject`, `start`, `end`, `location`, `attendees`. Optional mailbox selector. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_event}}\) | `{ "updated": true, "eventId": string }` |
| **Error cases** | Missing event identifier; empty patch; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 40. delete_event

| Field | Specification |
|-------|----------------|
| **action** | `delete_event` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `eventId` or `event_id` or `id` (required). Optional mailbox selector. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{delete\_event}}\) | `{ "deleted": true, "eventId": string }` |
| **Error cases** | Missing event identifier; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 41. get_schedule

| Field | Specification |
|-------|----------------|
| **action** | `get_schedule` |
| **Mutating** | No |
| **Preconditions** | `params`: non-empty `schedules` array or an explicit mailbox selector, plus `startTime` or `start`, and `endTime` or `end`. Optional `availabilityViewInterval`. |
| **Result shape** \(\mathcal{S}_{\texttt{get\_schedule}}\) | `{ "schedules": array, "count": number }` |
| **Error cases** | Missing or invalid schedules; missing time bounds; Graph not configured; app-only request without explicit mailbox context. |

### 42. list_contacts

| Field | Specification |
|-------|----------------|
| **action** | `list_contacts` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: explicit mailbox selector plus optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_contacts}}\) | `{ "contacts": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; app-only request without explicit mailbox context. |

### 43. get_contact

| Field | Specification |
|-------|----------------|
| **action** | `get_contact` |
| **Mutating** | No |
| **Preconditions** | `params`: `contactId` or `contact_id` or `id` (required). Optional mailbox selector. |
| **Result shape** \(\mathcal{S}_{\texttt{get\_contact}}\) | `{ "contact": object }` |
| **Error cases** | Missing contact identifier; Graph not configured; app-only request without explicit mailbox context. |

### 44. create_contact

| Field | Specification |
|-------|----------------|
| **action** | `create_contact` |
| **Mutating** | Yes |
| **Preconditions** | `params`: either `body` or one or more contact fields such as `displayName`, `givenName`, `surname`, `emailAddresses`, or `email`. Optional mailbox selector. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_contact}}\) | `{ "contact": object, "status": "created" }` |
| **Error cases** | Missing contact body; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 45. update_contact

| Field | Specification |
|-------|----------------|
| **action** | `update_contact` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `contactId` or `contact_id` or `id` plus either `body` or one or more contact fields to patch. Optional mailbox selector. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_contact}}\) | `{ "updated": true, "contactId": string }` |
| **Error cases** | Missing contact identifier; missing patch body; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 46. delete_contact

| Field | Specification |
|-------|----------------|
| **action** | `delete_contact` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `contactId` or `contact_id` or `id` (required). Optional mailbox selector. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{delete\_contact}}\) | `{ "deleted": true, "contactId": string }` |
| **Error cases** | Missing contact identifier; Graph not configured; mutations disabled; app-only request without explicit mailbox context. |

### 47. list_contact_folders

| Field | Specification |
|-------|----------------|
| **action** | `list_contact_folders` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: explicit mailbox selector plus optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_contact\_folders}}\) | `{ "folders": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; app-only request without explicit mailbox context. |

### SharePoint / OneDrive / Files expansion actions

The following actions are implemented as part of `E2C`. They share the same deterministic instruction envelope and are routed to the bounded `sharepoint` executor with `app_only` site/list semantics and `hybrid` drive/file semantics.

### 48. get_site

| Field | Specification |
|-------|----------------|
| **action** | `get_site` |
| **Mutating** | No |
| **Preconditions** | `params`: `siteId` or `site_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_site}}\) | `{ "site": object }` |
| **Error cases** | Missing site identifier; Graph not configured. |

### 49. list_site_lists

| Field | Specification |
|-------|----------------|
| **action** | `list_site_lists` |
| **Mutating** | No |
| **Preconditions** | `params`: `siteId` or `site_id` or `id` (string, required). Optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_site\_lists}}\) | `{ "lists": array, "count": number }` |
| **Error cases** | Missing site identifier; Graph not configured; invalid `top`. |

### 50. get_list

| Field | Specification |
|-------|----------------|
| **action** | `get_list` |
| **Mutating** | No |
| **Preconditions** | `params`: `siteId` or `site_id` (string, required), `listId` or `list_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_list}}\) | `{ "list": object }` |
| **Error cases** | Missing site or list identifier; Graph not configured. |

### 51. list_list_items

| Field | Specification |
|-------|----------------|
| **action** | `list_list_items` |
| **Mutating** | No |
| **Preconditions** | `params`: `siteId` or `site_id` (string, required), `listId` or `list_id` or `id` (string, required). Optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_list\_items}}\) | `{ "items": array, "count": number }` |
| **Error cases** | Missing site or list identifier; Graph not configured; invalid `top`. |

### 52. create_list_item

| Field | Specification |
|-------|----------------|
| **action** | `create_list_item` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `siteId` or `site_id` (string, required), `listId` or `list_id` or `id` (string, required), `fields` (non-empty object, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_list\_item}}\) | `{ "item": object, "status": "created" }` |
| **Error cases** | Missing site or list identifier; missing fields; Graph not configured; mutations disabled. |

### 53. list_drives

| Field | Specification |
|-------|----------------|
| **action** | `list_drives` |
| **Mutating** | No |
| **Preconditions** | `params` optional. Explicit context may be supplied via `groupId`, `siteId`, `userId`, or `userPrincipalName`. Without explicit context, delegated `/me` must be available. Optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_drives}}\) | `{ "drives": array, "count": number }` |
| **Error cases** | No usable drive context; Graph not configured; invalid `top`. |

### 54. get_drive

| Field | Specification |
|-------|----------------|
| **action** | `get_drive` |
| **Mutating** | No |
| **Preconditions** | `params`: `driveId` or `drive_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_drive}}\) | `{ "drive": object }` |
| **Error cases** | Missing drive identifier; Graph not configured. |

### 55. list_drive_items

| Field | Specification |
|-------|----------------|
| **action** | `list_drive_items` |
| **Mutating** | No |
| **Preconditions** | `params` optional. Explicit drive context may be supplied via `driveId`, `groupId`, `siteId`, `userId`, or `userPrincipalName`. Optional path selectors: `folderId`, `folderPath`, or `path`. Without explicit context, delegated `/me` must be available. Optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_drive\_items}}\) | `{ "items": array, "count": number }` |
| **Error cases** | No usable drive context; Graph not configured; invalid `top`. |

### 56. get_drive_item

| Field | Specification |
|-------|----------------|
| **action** | `get_drive_item` |
| **Mutating** | No |
| **Preconditions** | `params`: `driveId` or `drive_id` (string, required), `itemId` or `item_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_drive\_item}}\) | `{ "item": object }` |
| **Error cases** | Missing drive or item identifier; Graph not configured. |

### 57. create_folder

| Field | Specification |
|-------|----------------|
| **action** | `create_folder` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `name` or `folderName` (string, required). Explicit drive context may be supplied via `driveId`, `groupId`, `siteId`, `userId`, or `userPrincipalName`; otherwise delegated `/me` must be available. Optional `parentId`, `conflictBehavior`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_folder}}\) | `{ "folder": object, "status": "created" }` |
| **Error cases** | Missing folder name; no usable drive context; Graph not configured; mutations disabled. |

### 58. upload_file

| Field | Specification |
|-------|----------------|
| **action** | `upload_file` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `filePath` or `localPath` (string, required), `remotePath` or `path` or `fileName` (string, required). Explicit drive context may be supplied via `driveId`, `groupId`, `siteId`, `userId`, or `userPrincipalName`; otherwise delegated `/me` must be available. Optional `conflictBehavior`, `contentType`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{upload\_file}}\) | `{ "file": object, "status": "uploaded" }` |
| **Error cases** | Missing local or remote path; local file missing; no usable drive context; Graph not configured; mutations disabled. |

### 59. get_team

| Field | Specification |
|-------|----------------|
| **action** | `get_team` |
| **Mutating** | No |
| **Preconditions** | `params`: one of `teamId`, `team_id`, `id`, `groupId`, `group_id`, `mail_nickname`, or `mailNickname` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_team}}\) | `{ "team": object }` |
| **Error cases** | Missing team selector; group not found when resolving by mail nickname; Graph not configured. |

### 60. list_channels

| Field | Specification |
|-------|----------------|
| **action** | `list_channels` |
| **Mutating** | No |
| **Preconditions** | `params`: one of `teamId`, `team_id`, `id`, `groupId`, `group_id`, `mail_nickname`, or `mailNickname` (string, required). Optional `top` ∈ [1, 999]. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_channels}}\) | `{ "channels": array, "count": number }` |
| **Error cases** | Missing team selector; group not found when resolving by mail nickname; Graph not configured; invalid `top`. |

### 61. create_channel

| Field | Specification |
|-------|----------------|
| **action** | `create_channel` |
| **Mutating** | Yes |
| **Preconditions** | `params`: one of `teamId`, `team_id`, `id`, `groupId`, `group_id`, `mail_nickname`, or `mailNickname` (string, required), plus `channel_name` or `displayName` or `name` (string, required). Optional `description`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_channel}}\) | `{ "channel": object, "status": "created" }` |
| **Error cases** | Missing team selector or channel name; group not found when resolving by mail nickname; Graph not configured; mutations disabled. |

### 62. list_plans

| Field | Specification |
|-------|----------------|
| **action** | `list_plans` |
| **Mutating** | No |
| **Preconditions** | `params`: `groupId` or `group_id` or `id` or `mail_nickname` or `mailNickname` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_plans}}\) | `{ "plans": array, "count": number }` |
| **Error cases** | Missing group selector; group not found when resolving by mail nickname; Graph not configured. |

### 63. create_plan

| Field | Specification |
|-------|----------------|
| **action** | `create_plan` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `groupId` or `group_id` or `id` or `mail_nickname` or `mailNickname` (string, required), plus `title` or `name` (string, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_plan}}\) | `{ "plan": object, "status": "created" }` |
| **Error cases** | Missing group selector or title; group not found when resolving by mail nickname; Graph not configured; mutations disabled. |

### 64. list_plan_buckets

| Field | Specification |
|-------|----------------|
| **action** | `list_plan_buckets` |
| **Mutating** | No |
| **Preconditions** | `params`: `planId` or `plan_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_plan\_buckets}}\) | `{ "buckets": array, "count": number }` |
| **Error cases** | Missing plan identifier; Graph not configured. |

### 65. create_plan_bucket

| Field | Specification |
|-------|----------------|
| **action** | `create_plan_bucket` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `planId` or `plan_id` or `id` (string, required) plus `name` or `bucketName` (string, required). Optional `orderHint`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_plan\_bucket}}\) | `{ "bucket": object, "status": "created" }` |
| **Error cases** | Missing plan identifier or bucket name; Graph not configured; mutations disabled. |

### 66. create_plan_task

| Field | Specification |
|-------|----------------|
| **action** | `create_plan_task` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `planId` or `plan_id` (string, required), `bucketId` or `bucket_id` (string, required), `title` or `name` (string, required). Optional `description`, `referenceUrl`, `percentComplete` (integer). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_plan\_task}}\) | `{ "task": object, "status": "created" }` |
| **Error cases** | Missing plan, bucket, or title; invalid `percentComplete`; Graph not configured; mutations disabled. |

### 67. create_document

| Field | Specification |
|-------|----------------|
| **action** | `create_document` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `remotePath` or `path` or `fileName` (string, required). Explicit drive context may be supplied via `driveId`, `groupId`, `siteId`, `userId`, or `userPrincipalName`; otherwise delegated `/me` must be available. Optional `title`, `paragraphs`, `content`, `conflictBehavior`. If the provided path has no extension, `.docx` is appended. If it has an extension, it must be `.docx`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_document}}\) | `{ "document": object, "status": "created" }` |
| **Error cases** | Missing remote path; invalid extension; no usable drive context; Graph not configured; mutations disabled. |

### 68. update_document

| Field | Specification |
|-------|----------------|
| **action** | `update_document` |
| **Mutating** | Yes |
| **Preconditions** | Same as `create_document`. The target document is regenerated deterministically from the provided title/content payload and uploaded over the existing path. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_document}}\) | `{ "document": object, "status": "updated" }` |
| **Error cases** | Missing remote path; invalid extension; no usable drive context; Graph not configured; mutations disabled. |

### 69. create_workbook

| Field | Specification |
|-------|----------------|
| **action** | `create_workbook` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `remotePath` or `path` or `fileName` (string, required). Explicit drive context may be supplied via `driveId`, `groupId`, `siteId`, `userId`, or `userPrincipalName`; otherwise delegated `/me` must be available. Either `worksheets` (non-empty list of worksheet objects) or `rows` must be supplied. Optional `sheetName`, `conflictBehavior`. If the provided path has no extension, `.xlsx` is appended. If it has an extension, it must be `.xlsx`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_workbook}}\) | `{ "workbook": object, "status": "created" }` |
| **Error cases** | Missing remote path; missing worksheet data; invalid extension; no usable drive context; Graph not configured; mutations disabled. |

### 70. update_workbook

| Field | Specification |
|-------|----------------|
| **action** | `update_workbook` |
| **Mutating** | Yes |
| **Preconditions** | Same as `create_workbook`. The target workbook is regenerated deterministically from the provided worksheet payload and uploaded over the existing path. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_workbook}}\) | `{ "workbook": object, "status": "updated" }` |
| **Error cases** | Missing remote path; missing worksheet data; invalid extension; no usable drive context; Graph not configured; mutations disabled. |

### 71. create_presentation

| Field | Specification |
|-------|----------------|
| **action** | `create_presentation` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `remotePath` or `path` or `fileName` (string, required). Explicit drive context may be supplied via `driveId`, `groupId`, `siteId`, `userId`, or `userPrincipalName`; otherwise delegated `/me` must be available. Optional `title`; either `slides` (non-empty list of slide objects) or `bullets`/`items` must be supplied. Optional `conflictBehavior`. If the provided path has no extension, `.pptx` is appended. If it has an extension, it must be `.pptx`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_presentation}}\) | `{ "presentation": object, "status": "created" }` |
| **Error cases** | Missing remote path; invalid slide payload; invalid extension; no usable drive context; Graph not configured; mutations disabled. |

### 72. update_presentation

| Field | Specification |
|-------|----------------|
| **action** | `update_presentation` |
| **Mutating** | Yes |
| **Preconditions** | Same as `create_presentation`. The target presentation is regenerated deterministically from the provided slide payload and uploaded over the existing path. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_presentation}}\) | `{ "presentation": object, "status": "updated" }` |
| **Error cases** | Missing remote path; invalid slide payload; invalid extension; no usable drive context; Graph not configured; mutations disabled. |

### 73. list_flows_admin

| Field | Specification |
|-------|----------------|
| **action** | `list_flows_admin` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required). Optional `top` (integer). The selected `powerplatform` executor must have service-principal admin credentials with `client_secret` for `Add-PowerAppsAccount`. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_flows\_admin}}\) | `{ "flows": array, "count": number }` |
| **Error cases** | Missing environment selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 74. get_flow_admin

| Field | Specification |
|-------|----------------|
| **action** | `get_flow_admin` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), plus `flowName` or `flow_name` or `flowId` or `flow_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_flow\_admin}}\) | `{ "flow": object }` |
| **Error cases** | Missing environment or flow selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 75. list_http_flows

| Field | Specification |
|-------|----------------|
| **action** | `list_http_flows` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required). Optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_http\_flows}}\) | `{ "flows": array, "count": number }` |
| **Error cases** | Missing environment selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 76. list_flow_owners

| Field | Specification |
|-------|----------------|
| **action** | `list_flow_owners` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), plus `flowName` or `flow_name` or `flowId` or `flow_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_flow\_owners}}\) | `{ "owners": array, "count": number }` |
| **Error cases** | Missing environment or flow selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 77. list_flow_runs

| Field | Specification |
|-------|----------------|
| **action** | `list_flow_runs` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), plus `flowName` or `flow_name` or `flowId` or `flow_id` or `id` (string, required). Optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_flow\_runs}}\) | `{ "runs": array, "count": number }` |
| **Error cases** | Missing environment or flow selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 78. set_flow_owner_role

| Field | Specification |
|-------|----------------|
| **action** | `set_flow_owner_role` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), `flowName` or `flow_name` or `flowId` or `flow_id` or `id` (string, required), and `principalObjectId` or `principal_object_id` or `userId` (string, required). Optional `roleName` (default `CanEdit`) and `principalType` (default `User`). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{set\_flow\_owner\_role}}\) | `{ "flowName": string, "principalObjectId": string, "roleName": string, "status": "updated" }` |
| **Error cases** | Missing environment, flow, or principal selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 79. remove_flow_owner_role

| Field | Specification |
|-------|----------------|
| **action** | `remove_flow_owner_role` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), `flowName` or `flow_name` or `flowId` or `flow_id` or `id` (string, required), and `roleId` or `role_id` (string, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{remove\_flow\_owner\_role}}\) | `{ "flowName": string, "roleId": string, "removed": true }` |
| **Error cases** | Missing environment, flow, or role selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 80. enable_flow

| Field | Specification |
|-------|----------------|
| **action** | `enable_flow` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), plus `flowName` or `flow_name` or `flowId` or `flow_id` or `id` (string, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{enable\_flow}}\) | `{ "flowName": string, "status": "enabled" }` |
| **Error cases** | Missing environment or flow selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 81. disable_flow

| Field | Specification |
|-------|----------------|
| **action** | `disable_flow` |
| **Mutating** | Yes |
| **Preconditions** | Same as `enable_flow`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{disable\_flow}}\) | `{ "flowName": string, "status": "disabled" }` |
| **Error cases** | Missing environment or flow selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 82. delete_flow

| Field | Specification |
|-------|----------------|
| **action** | `delete_flow` |
| **Mutating** | Yes |
| **Preconditions** | Same as `enable_flow`. The action is bounded to soft-delete semantics through the admin module. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{delete\_flow}}\) | `{ "flowName": string, "status": "deleted" }` |
| **Error cases** | Missing environment or flow selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 83. restore_flow

| Field | Specification |
|-------|----------------|
| **action** | `restore_flow` |
| **Mutating** | Yes |
| **Preconditions** | Same as `enable_flow`. The action restores a soft-deleted flow. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{restore\_flow}}\) | `{ "flowName": string, "status": "restored" }` |
| **Error cases** | Missing environment or flow selector; Power Automate admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 84. invoke_flow_callback

| Field | Specification |
|-------|----------------|
| **action** | `invoke_flow_callback` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `callbackUrl` or `callback_url` or `url` (string, required). Optional `body` or `payload` (JSON value), `headers` (string map), and `timeoutSeconds` (integer). The callback URL must already be known and is treated as an explicit invocation target. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{invoke\_flow\_callback}}\) | `{ "invoked": true, "status_code": number, "response": object \| string }` |
| **Error cases** | Missing callback URL; invalid headers; callback returns non-success HTTP status; mutations disabled. |

### 85. list_powerapps_admin

| Field | Specification |
|-------|----------------|
| **action** | `list_powerapps_admin` |
| **Mutating** | No |
| **Preconditions** | Optional `params`: `environmentName` or `environment_name` or `environment` (string), `owner` (string), `filter` (string), and `top` (integer). The selected `powerplatform` executor must have service-principal admin credentials with `client_secret` for `Add-PowerAppsAccount`. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerapps\_admin}}\) | `{ "apps": array, "count": number }` |
| **Error cases** | Invalid `top`; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 86. get_powerapp_admin

| Field | Specification |
|-------|----------------|
| **action** | `get_powerapp_admin` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), plus `appName` or `app_name` or `appId` or `app_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_powerapp\_admin}}\) | `{ "app": object }` |
| **Error cases** | Missing environment or app selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 87. list_powerapp_role_assignments

| Field | Specification |
|-------|----------------|
| **action** | `list_powerapp_role_assignments` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), `appName` or `app_name` or `appId` or `app_id` or `id` (string, required), and optional `userId` (string). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerapp\_role\_assignments}}\) | `{ "roles": array, "count": number }` |
| **Error cases** | Missing environment or app selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 88. set_powerapp_owner

| Field | Specification |
|-------|----------------|
| **action** | `set_powerapp_owner` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), `appName` or `app_name` or `appId` or `app_id` or `id` (string, required), and `ownerObjectId` or `owner_object_id` or `principalObjectId` or `principal_object_id` or `userId` (string, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{set\_powerapp\_owner}}\) | `{ "appName": string, "ownerObjectId": string, "status": "updated" }` |
| **Error cases** | Missing environment, app, or owner selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 89. remove_powerapp_role_assignment

| Field | Specification |
|-------|----------------|
| **action** | `remove_powerapp_role_assignment` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), `appName` or `app_name` or `appId` or `app_id` or `id` (string, required), and `roleId` or `role_id` (string, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{remove\_powerapp\_role\_assignment}}\) | `{ "appName": string, "roleId": string, "removed": true }` |
| **Error cases** | Missing environment, app, or role selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 90. delete_powerapp

| Field | Specification |
|-------|----------------|
| **action** | `delete_powerapp` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` (string, required), plus `appName` or `app_name` or `appId` or `app_id` or `id` (string, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{delete\_powerapp}}\) | `{ "appName": string, "status": "deleted" }` |
| **Error cases** | Missing environment or app selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure; mutations disabled. |

### 91. list_powerapp_environments

| Field | Specification |
|-------|----------------|
| **action** | `list_powerapp_environments` |
| **Mutating** | No |
| **Preconditions** | Optional `params`: `top` (integer). The selected `powerplatform` executor must have service-principal admin credentials with `client_secret` for `Add-PowerAppsAccount`. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerapp\_environments}}\) | `{ "environments": array, "count": number }` |
| **Error cases** | Invalid `top`; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 92. get_powerapp_environment

| Field | Specification |
|-------|----------------|
| **action** | `get_powerapp_environment` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_powerapp\_environment}}\) | `{ "environment": object }` |
| **Error cases** | Missing environment selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 93. list_powerapp_environment_role_assignments

| Field | Specification |
|-------|----------------|
| **action** | `list_powerapp_environment_role_assignments` |
| **Mutating** | No |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` or `id` (string, required), and optional `userId` (string). This surface is bounded to non-Dataverse environment-role inspection. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerapp\_environment\_role\_assignments}}\) | `{ "roles": array, "count": number }` |
| **Error cases** | Missing environment selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure. |

### 94. set_powerapp_environment_role_assignment

| Field | Specification |
|-------|----------------|
| **action** | `set_powerapp_environment_role_assignment` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` or `id` (string, required), `principalObjectId` or `principal_object_id` or `userId` (string, required), `roleName` or `role_name` (string, required), and optional `principalType` (default `User`). This surface is bounded to non-Dataverse environment-role mutation. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{set\_powerapp\_environment\_role\_assignment}}\) | `{ "environmentName": string, "principalObjectId": string, "roleName": string, "status": "updated" }` |
| **Error cases** | Missing environment, principal, or role selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure; forbidden Dataverse environment; mutations disabled. |

### 95. remove_powerapp_environment_role_assignment

| Field | Specification |
|-------|----------------|
| **action** | `remove_powerapp_environment_role_assignment` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `environmentName` or `environment_name` or `environment` or `id` (string, required), and `roleId` or `role_id` (string, required). This surface is bounded to non-Dataverse environment-role mutation. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{remove\_powerapp\_environment\_role\_assignment}}\) | `{ "environmentName": string, "roleId": string, "removed": true }` |
| **Error cases** | Missing environment or role selector; Power Apps admin runtime not configured; PowerShell module import failure; service-principal auth failure; forbidden Dataverse environment; mutations disabled. |

### 96. list_powerbi_workspaces

| Field | Specification |
|-------|----------------|
| **action** | `list_powerbi_workspaces` |
| **Mutating** | No |
| **Preconditions** | Optional `params`: `top` (integer). The selected `powerplatform` executor must have service-principal Power BI REST access via the tenant contract. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerbi\_workspaces}}\) | `{ "workspaces": array, "count": number }` |
| **Error cases** | Invalid `top`; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 97. get_powerbi_workspace

| Field | Specification |
|-------|----------------|
| **action** | `get_powerbi_workspace` |
| **Mutating** | No |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_powerbi\_workspace}}\) | `{ "workspace": object }` |
| **Error cases** | Missing workspace selector; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 98. list_powerbi_reports

| Field | Specification |
|-------|----------------|
| **action** | `list_powerbi_reports` |
| **Mutating** | No |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` or `id` (string, required), plus optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerbi\_reports}}\) | `{ "reports": array, "count": number }` |
| **Error cases** | Missing workspace selector; invalid `top`; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 99. get_powerbi_report

| Field | Specification |
|-------|----------------|
| **action** | `get_powerbi_report` |
| **Mutating** | No |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` (string, required), plus `reportId` or `report_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_powerbi\_report}}\) | `{ "report": object }` |
| **Error cases** | Missing workspace or report selector; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 100. list_powerbi_datasets

| Field | Specification |
|-------|----------------|
| **action** | `list_powerbi_datasets` |
| **Mutating** | No |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` or `id` (string, required), plus optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerbi\_datasets}}\) | `{ "datasets": array, "count": number }` |
| **Error cases** | Missing workspace selector; invalid `top`; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 101. get_powerbi_dataset

| Field | Specification |
|-------|----------------|
| **action** | `get_powerbi_dataset` |
| **Mutating** | No |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` (string, required), plus `datasetId` or `dataset_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_powerbi\_dataset}}\) | `{ "dataset": object }` |
| **Error cases** | Missing workspace or dataset selector; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 102. refresh_powerbi_dataset

| Field | Specification |
|-------|----------------|
| **action** | `refresh_powerbi_dataset` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` (string, required), `datasetId` or `dataset_id` or `id` (string, required), and optional `notifyOption` (default `NoNotification`). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{refresh\_powerbi\_dataset}}\) | `{ "workspaceId": string, "datasetId": string, "status": "queued", "requestId"?: string, "location"?: string }` |
| **Error cases** | Missing workspace or dataset selector; Power BI identity missing; token acquisition failure; Power BI REST request failure; mutations disabled. |

### 103. list_powerbi_dataset_refreshes

| Field | Specification |
|-------|----------------|
| **action** | `list_powerbi_dataset_refreshes` |
| **Mutating** | No |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` (string, required), `datasetId` or `dataset_id` (string, required), and optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerbi\_dataset\_refreshes}}\) | `{ "refreshes": array, "count": number }` |
| **Error cases** | Missing workspace or dataset selector; invalid `top`; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 104. list_powerbi_dashboards

| Field | Specification |
|-------|----------------|
| **action** | `list_powerbi_dashboards` |
| **Mutating** | No |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` or `id` (string, required), plus optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_powerbi\_dashboards}}\) | `{ "dashboards": array, "count": number }` |
| **Error cases** | Missing workspace selector; invalid `top`; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 105. get_powerbi_dashboard

| Field | Specification |
|-------|----------------|
| **action** | `get_powerbi_dashboard` |
| **Mutating** | No |
| **Preconditions** | `params`: `workspaceId` or `workspace_id` or `groupId` or `group_id` (string, required), plus `dashboardId` or `dashboard_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_powerbi\_dashboard}}\) | `{ "dashboard": object }` |
| **Error cases** | Missing workspace or dashboard selector; Power BI identity missing; token acquisition failure; Power BI REST request failure. |

### 106. get_approval_solution

| Field | Specification |
|-------|----------------|
| **action** | `get_approval_solution` |
| **Mutating** | No |
| **Preconditions** | `params`: none. Runtime must execute in delegated or hybrid auth mode. |
| **Result shape** \(\mathcal{S}_{\texttt{get\_approval\_solution}}\) | `{ "solution": object }` |
| **Error cases** | Delegated identity missing; approval-solution API unavailable; Graph beta request failure. |

### 107. list_approval_items

| Field | Specification |
|-------|----------------|
| **action** | `list_approval_items` |
| **Mutating** | No |
| **Preconditions** | `params`: optional `top` (integer). Runtime must execute in delegated or hybrid auth mode. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_approval\_items}}\) | `{ "approvals": array, "count": number }` |
| **Error cases** | Delegated identity missing; invalid `top`; approval-items API unavailable; Graph beta request failure. |

### 108. get_approval_item

| Field | Specification |
|-------|----------------|
| **action** | `get_approval_item` |
| **Mutating** | No |
| **Preconditions** | `params`: `approvalId` or `approval_id` or `id` (string, required). Runtime must execute in delegated or hybrid auth mode. |
| **Result shape** \(\mathcal{S}_{\texttt{get\_approval\_item}}\) | `{ "approval": object }` |
| **Error cases** | Missing approval selector; delegated identity missing; approval-item API unavailable; Graph beta request failure. |

### 109. create_approval_item

| Field | Specification |
|-------|----------------|
| **action** | `create_approval_item` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `displayName` or `display_name` or `title` (string, required), `description` (string, required), `approverUserIds` or `approver_user_ids` (array[string], required), optional `approverGroupIds` or `approver_group_ids` (array[string]), optional `approvalType` or `approval_type` (string), and optional `allowEmailNotification` or `allow_email_notification` (boolean). Runtime must execute in delegated or hybrid auth mode. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_approval\_item}}\) | `{ "status": string, "displayName": string, "operationId"?: string, "location"?: string, "requestId"?: string }` |
| **Error cases** | Missing display name, description, or approver list; delegated identity missing; approval creation rejected; Graph beta request failure. |

### 110. list_approval_item_requests

| Field | Specification |
|-------|----------------|
| **action** | `list_approval_item_requests` |
| **Mutating** | No |
| **Preconditions** | `params`: `approvalId` or `approval_id` or `id` (string, required), plus optional `top` (integer). Runtime must execute in delegated or hybrid auth mode. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_approval\_item\_requests}}\) | `{ "requests": array, "count": number }` |
| **Error cases** | Missing approval selector; invalid `top`; delegated identity missing; approval-requests API unavailable; Graph beta request failure. |

### 111. respond_to_approval_item

| Field | Specification |
|-------|----------------|
| **action** | `respond_to_approval_item` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `approvalId` or `approval_id` or `id` (string, required), `response` (string, required), and optional `comments` (string). Runtime must execute in delegated or hybrid auth mode. |
| **Result shape** \(\mathcal{S}_{\texttt{respond\_to\_approval\_item}}\) | `{ "status": string, "approvalId": string, "response": string, "operationId"?: string, "location"?: string, "requestId"?: string }` |
| **Error cases** | Missing approval selector or response; delegated identity missing; approval-response API unavailable; Graph beta request failure. |

### 112. list_external_connections

| Field | Specification |
|-------|----------------|
| **action** | `list_external_connections` |
| **Mutating** | No |
| **Preconditions** | `params`: optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_external\_connections}}\) | `{ "connections": array, "count": number }` |
| **Error cases** | Invalid `top`; connector identity missing; Graph request failure. |

### 113. get_external_connection

| Field | Specification |
|-------|----------------|
| **action** | `get_external_connection` |
| **Mutating** | No |
| **Preconditions** | `params`: `connectionId` or `connection_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_external\_connection}}\) | `{ "connection": object }` |
| **Error cases** | Missing connection selector; connector identity missing; Graph request failure. |

### 114. create_external_connection

| Field | Specification |
|-------|----------------|
| **action** | `create_external_connection` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `connectionId` or `connection_id` or `id` (string, required), `name` or `displayName` or `display_name` or `title` (string, required), and optional `description` (string). |
| **Result shape** \(\mathcal{S}_{\texttt{create\_external\_connection}}\) | `{ "connection": object }` |
| **Error cases** | Missing connection selector or name; connector identity missing; external-connection create failure; Graph request failure. |

### 115. register_external_connection_schema

| Field | Specification |
|-------|----------------|
| **action** | `register_external_connection_schema` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `connectionId` or `connection_id` or `id` (string, required) and `schema` (object, required). |
| **Result shape** \(\mathcal{S}_{\texttt{register\_external\_connection\_schema}}\) | `{ "connectionId": string, "status": string }` |
| **Error cases** | Missing connection selector or schema; connector identity missing; schema registration failure; Graph request failure. |

### 116. get_external_item

| Field | Specification |
|-------|----------------|
| **action** | `get_external_item` |
| **Mutating** | No |
| **Preconditions** | `params`: `connectionId` or `connection_id` (string, required), plus `itemId` or `item_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_external\_item}}\) | `{ "item": object }` |
| **Error cases** | Missing connection or item selector; connector identity missing; Graph request failure. |

### 117. upsert_external_item

| Field | Specification |
|-------|----------------|
| **action** | `upsert_external_item` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `connectionId` or `connection_id` (string, required), `itemId` or `item_id` or `id` (string, required), `acl` (array[object], required), `properties` (object, required), and optional `content` (object). |
| **Result shape** \(\mathcal{S}_{\texttt{upsert\_external\_item}}\) | `{ "itemId": string, "status": string }` |
| **Error cases** | Missing connection or item selector; missing ACL or properties; connector identity missing; external-item upsert failure; Graph request failure. |

### 118. create_external_group

| Field | Specification |
|-------|----------------|
| **action** | `create_external_group` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `connectionId` or `connection_id` (string, required), `groupId` or `group_id` or `id` (string, required), optional `displayName` or `display_name` or `name`, and optional `description`. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_external\_group}}\) | `{ "group": object, "status": string }` |
| **Error cases** | Missing connection or group selector; connector identity missing; external-group create failure; Graph beta request failure. |

### 119. add_external_group_member

| Field | Specification |
|-------|----------------|
| **action** | `add_external_group_member` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `connectionId` or `connection_id` (string, required), `groupId` or `group_id` (string, required), `memberId` or `member_id` or `id` (string, required), and optional `memberType` or `member_type` plus optional `identitySource` or `identity_source`. |
| **Result shape** \(\mathcal{S}_{\texttt{add\_external\_group\_member}}\) | `{ "groupId": string, "memberId": string, "status": string }` |
| **Error cases** | Missing connection, group, or member selector; connector identity missing; external-group membership add failure; Graph beta request failure. |

### 120. list_automation_recipes

| Field | Specification |
|-------|----------------|
| **action** | `list_automation_recipes` |
| **Mutating** | No |
| **Preconditions** | `params`: optional `department`, optional `persona`, optional `workload`, and optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_automation\_recipes}}\) | `{ "recipes": array, "count": number }` |
| **Error cases** | Invalid `top`; recipe catalog missing or malformed. |

### 121. get_automation_recipe

| Field | Specification |
|-------|----------------|
| **action** | `get_automation_recipe` |
| **Mutating** | No |
| **Preconditions** | `params`: `recipeId` or `recipe_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_automation\_recipe}}\) | `{ "recipe": object }` |
| **Error cases** | Missing recipe selector; recipe catalog missing or malformed; unknown recipe id. |

### 122. list_devices

| Field | Specification |
|-------|----------------|
| **action** | `list_devices` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional, default 50). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_devices}}\) | `{ "devices": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; device executor not configured. |

### 123. get_device

| Field | Specification |
|-------|----------------|
| **action** | `get_device` |
| **Mutating** | No |
| **Preconditions** | `params`: `deviceId` or `device_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_device}}\) | `{ "device": object }` |
| **Error cases** | Missing device identifier; Graph not configured; device executor not configured. |

### 124. list_device_compliance_summaries

| Field | Specification |
|-------|----------------|
| **action** | `list_device_compliance_summaries` |
| **Mutating** | No |
| **Preconditions** | `params` optional and ignored. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_device\_compliance\_summaries}}\) | `{ "summaries": array, "count": number }` |
| **Error cases** | Graph not configured; device executor not configured. |

### 125. execute_device_action

| Field | Specification |
|-------|----------------|
| **action** | `execute_device_action` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `deviceId` or `device_id` or `id` (string, required). Optional `action` or `deviceAction` (string, default `syncDevice`). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{execute\_device\_action}}\) | `{ "executed": true, "deviceId": string, "action": string }` |
| **Error cases** | Missing device identifier; Graph not configured; mutations disabled; device executor not configured. |

### 126. list_security_alerts

| Field | Specification |
|-------|----------------|
| **action** | `list_security_alerts` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional, default 50). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_security\_alerts}}\) | `{ "alerts": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; security executor not configured. |

### 127. get_security_alert

| Field | Specification |
|-------|----------------|
| **action** | `get_security_alert` |
| **Mutating** | No |
| **Preconditions** | `params`: `alertId` or `alert_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_security\_alert}}\) | `{ "alert": object }` |
| **Error cases** | Missing alert identifier; Graph not configured; security executor not configured. |

### 128. list_security_incidents

| Field | Specification |
|-------|----------------|
| **action** | `list_security_incidents` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional, default 50). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_security\_incidents}}\) | `{ "incidents": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; security executor not configured. |

### 129. get_security_incident

| Field | Specification |
|-------|----------------|
| **action** | `get_security_incident` |
| **Mutating** | No |
| **Preconditions** | `params`: `incidentId` or `incident_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_security\_incident}}\) | `{ "incident": object }` |
| **Error cases** | Missing incident identifier; Graph not configured; security executor not configured. |

### 130. list_secure_scores

| Field | Specification |
|-------|----------------|
| **action** | `list_secure_scores` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` ∈ [1, 999] (integer, optional, default 25). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_secure\_scores}}\) | `{ "scores": array, "count": number }` |
| **Error cases** | Graph not configured; invalid `top`; security executor not configured. |

### 131. get_secure_score_profile

| Field | Specification |
|-------|----------------|
| **action** | `get_secure_score_profile` |
| **Mutating** | No |
| **Preconditions** | `params`: `profileId` or `profile_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_secure\_score\_profile}}\) | `{ "profile": object }` |
| **Error cases** | Missing profile identifier; Graph not configured; security executor not configured. |

### 132. update_security_incident

| Field | Specification |
|-------|----------------|
| **action** | `update_security_incident` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `incidentId` or `incident_id` or `id` (string, required) plus at least one of `status`, `assignedTo`, `classification`, `determination`, or `comments`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{update\_security\_incident}}\) | `{ "updated": true, "incidentId": string }` |
| **Error cases** | Missing incident identifier; empty patch; Graph not configured; mutations disabled; security executor not configured. |

### 133. list_ediscovery_cases

| Field | Specification |
|-------|----------------|
| **action** | `list_ediscovery_cases` |
| **Mutating** | No |
| **Preconditions** | Optional `params`: `top` (integer). The selected `compliance` executor must be configured for Microsoft Graph eDiscovery case inspection. |
| **Result shape** \(\mathcal{S}_{\texttt{list\_ediscovery\_cases}}\) | `{ "cases": array, "count": number }` |
| **Error cases** | Invalid `top`; Graph not configured; compliance executor not configured. |

### 134. get_ediscovery_case

| Field | Specification |
|-------|----------------|
| **action** | `get_ediscovery_case` |
| **Mutating** | No |
| **Preconditions** | `params`: `caseId` or `case_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_ediscovery\_case}}\) | `{ "case": object }` |
| **Error cases** | Missing case identifier; Graph not configured; compliance executor not configured. |

### 135. create_ediscovery_case

| Field | Specification |
|-------|----------------|
| **action** | `create_ediscovery_case` |
| **Mutating** | Yes |
| **Preconditions** | `params`: either `body` (object) or one of `displayName`, `display_name`, `name`, or `title` (string, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_ediscovery\_case}}\) | `{ "case": object, "status": "created" }` |
| **Error cases** | Missing case payload; Graph not configured; mutations disabled; compliance executor not configured. |

### 136. list_ediscovery_case_searches

| Field | Specification |
|-------|----------------|
| **action** | `list_ediscovery_case_searches` |
| **Mutating** | No |
| **Preconditions** | `params`: `caseId` or `case_id` or `id` (string, required) and optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_ediscovery\_case\_searches}}\) | `{ "searches": array, "count": number }` |
| **Error cases** | Missing case identifier; invalid `top`; Graph not configured; compliance executor not configured. |

### 137. get_ediscovery_case_search

| Field | Specification |
|-------|----------------|
| **action** | `get_ediscovery_case_search` |
| **Mutating** | No |
| **Preconditions** | `params`: `caseId` or `case_id` (string, required) and `searchId` or `search_id` or `id` (string, required). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_ediscovery\_case\_search}}\) | `{ "search": object }` |
| **Error cases** | Missing case or search identifier; Graph not configured; compliance executor not configured. |

### 138. create_ediscovery_case_search

| Field | Specification |
|-------|----------------|
| **action** | `create_ediscovery_case_search` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `caseId` or `case_id` or `id` (string, required), plus either `body` (object) or one of `displayName`, `display_name`, `name`, or `title` (string, required). Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_ediscovery\_case\_search}}\) | `{ "search": object, "status": "created" }` |
| **Error cases** | Missing case identifier or search payload; Graph not configured; mutations disabled; compliance executor not configured. |

### 139. list_ediscovery_case_custodians

| Field | Specification |
|-------|----------------|
| **action** | `list_ediscovery_case_custodians` |
| **Mutating** | No |
| **Preconditions** | `params`: `caseId` or `case_id` or `id` (string, required) and optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_ediscovery\_case\_custodians}}\) | `{ "custodians": array, "count": number }` |
| **Error cases** | Missing case identifier; invalid `top`; Graph not configured; compliance executor not configured. |

### 140. list_ediscovery_case_legal_holds

| Field | Specification |
|-------|----------------|
| **action** | `list_ediscovery_case_legal_holds` |
| **Mutating** | No |
| **Preconditions** | `params`: `caseId` or `case_id` or `id` (string, required) and optional `top` (integer). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_ediscovery\_case\_legal\_holds}}\) | `{ "legalHolds": array, "count": number }` |
| **Error cases** | Missing case identifier; invalid `top`; Graph not configured; compliance executor not configured. |

---

## Canonical sets

- **\(\mathcal{A}\) (implemented in router):** `list_users`, `list_teams`, `get_team`, `list_channels`, `create_channel`, `list_plans`, `create_plan`, `list_plan_buckets`, `create_plan_bucket`, `create_plan_task`, `list_sites`, `get_site`, `list_site_lists`, `get_list`, `list_list_items`, `create_list_item`, `list_drives`, `get_drive`, `list_drive_items`, `get_drive_item`, `create_folder`, `upload_file`, `create_document`, `update_document`, `create_workbook`, `update_workbook`, `create_presentation`, `update_presentation`, `list_flows_admin`, `get_flow_admin`, `list_http_flows`, `list_flow_owners`, `list_flow_runs`, `set_flow_owner_role`, `remove_flow_owner_role`, `enable_flow`, `disable_flow`, `delete_flow`, `restore_flow`, `invoke_flow_callback`, `list_powerapps_admin`, `get_powerapp_admin`, `list_powerapp_role_assignments`, `set_powerapp_owner`, `remove_powerapp_role_assignment`, `delete_powerapp`, `list_powerapp_environments`, `get_powerapp_environment`, `list_powerapp_environment_role_assignments`, `set_powerapp_environment_role_assignment`, `remove_powerapp_environment_role_assignment`, `list_powerbi_workspaces`, `get_powerbi_workspace`, `list_powerbi_reports`, `get_powerbi_report`, `list_powerbi_datasets`, `get_powerbi_dataset`, `refresh_powerbi_dataset`, `list_powerbi_dataset_refreshes`, `list_powerbi_dashboards`, `get_powerbi_dashboard`, `get_approval_solution`, `list_approval_items`, `get_approval_item`, `create_approval_item`, `list_approval_item_requests`, `respond_to_approval_item`, `list_external_connections`, `get_external_connection`, `create_external_connection`, `register_external_connection_schema`, `get_external_item`, `upsert_external_item`, `create_external_group`, `add_external_group_member`, `list_automation_recipes`, `get_automation_recipe`, `list_devices`, `get_device`, `list_device_compliance_summaries`, `execute_device_action`, `list_security_alerts`, `get_security_alert`, `list_security_incidents`, `get_security_incident`, `list_secure_scores`, `get_secure_score_profile`, `update_security_incident`, `list_ediscovery_cases`, `get_ediscovery_case`, `create_ediscovery_case`, `list_ediscovery_case_searches`, `get_ediscovery_case_search`, `create_ediscovery_case_search`, `list_ediscovery_case_custodians`, `list_ediscovery_case_legal_holds`, `get_user`, `reset_user_password`, `create_user`, `update_user`, `disable_user`, `list_groups`, `get_group`, `create_group`, `list_group_members`, `add_group_member`, `remove_group_member`, `assign_user_license`, `list_directory_roles`, `list_directory_role_members`, `list_domains`, `get_organization`, `list_applications`, `get_application`, `update_application`, `list_service_principals`, `list_messages`, `get_message`, `send_mail`, `move_message`, `delete_message`, `list_mail_folders`, `get_mailbox_settings`, `update_mailbox_settings`, `list_events`, `create_event`, `get_event`, `update_event`, `delete_event`, `get_schedule`, `list_contacts`, `get_contact`, `create_contact`, `update_contact`, `delete_contact`, `list_contact_folders`, `create_site`, `create_team`, `add_channel`, `provision_service`.
- **\(\mathcal{A}_m\) (mutating):** `create_channel`, `create_plan`, `create_plan_bucket`, `create_plan_task`, `create_list_item`, `create_folder`, `upload_file`, `create_document`, `update_document`, `create_workbook`, `update_workbook`, `create_presentation`, `update_presentation`, `set_flow_owner_role`, `remove_flow_owner_role`, `enable_flow`, `disable_flow`, `delete_flow`, `restore_flow`, `invoke_flow_callback`, `set_powerapp_owner`, `remove_powerapp_role_assignment`, `delete_powerapp`, `set_powerapp_environment_role_assignment`, `remove_powerapp_environment_role_assignment`, `refresh_powerbi_dataset`, `create_approval_item`, `respond_to_approval_item`, `create_external_connection`, `register_external_connection_schema`, `upsert_external_item`, `create_external_group`, `add_external_group_member`, `execute_device_action`, `update_security_incident`, `create_ediscovery_case`, `create_ediscovery_case_search`, `reset_user_password`, `create_user`, `update_user`, `disable_user`, `create_group`, `add_group_member`, `remove_group_member`, `assign_user_license`, `update_application`, `send_mail`, `move_message`, `delete_message`, `update_mailbox_settings`, `create_event`, `update_event`, `delete_event`, `create_contact`, `update_contact`, `delete_contact`, `create_site`, `create_team`, `add_channel`, `provision_service`.

---

## Planned (North Star)

The North Star defines the broader capability set beyond the currently implemented instruction-router actions. When a new action is implemented:

1. Add it to this document with preconditions and result shape.
2. Add it to `scripts/ci/verify_caio_m365_contract.py` result-shape verification.
3. Update `scripts/ci/verify_capability_registry.py` if the action joins the implemented set.
4. Regenerate the capability-registry verification artifacts and the relevant MA evidence chain.

---

## Verification

The script `scripts/ci/verify_caio_m365_contract.py` must validate response shape for every action in \(\mathcal{A}\). Result shape checks use the required keys per action from this specification.
