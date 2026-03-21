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

---

## Canonical sets

- **\(\mathcal{A}\) (implemented in router):** `list_users`, `list_teams`, `get_team`, `list_channels`, `create_channel`, `list_plans`, `create_plan`, `list_plan_buckets`, `create_plan_bucket`, `create_plan_task`, `list_sites`, `get_site`, `list_site_lists`, `get_list`, `list_list_items`, `create_list_item`, `list_drives`, `get_drive`, `list_drive_items`, `get_drive_item`, `create_folder`, `upload_file`, `create_document`, `update_document`, `create_workbook`, `update_workbook`, `create_presentation`, `update_presentation`, `list_flows_admin`, `get_flow_admin`, `list_http_flows`, `list_flow_owners`, `list_flow_runs`, `set_flow_owner_role`, `remove_flow_owner_role`, `enable_flow`, `disable_flow`, `delete_flow`, `restore_flow`, `invoke_flow_callback`, `get_user`, `reset_user_password`, `create_user`, `update_user`, `disable_user`, `list_groups`, `get_group`, `create_group`, `list_group_members`, `add_group_member`, `remove_group_member`, `assign_user_license`, `list_directory_roles`, `list_directory_role_members`, `list_domains`, `get_organization`, `list_applications`, `get_application`, `update_application`, `list_service_principals`, `list_messages`, `get_message`, `send_mail`, `move_message`, `delete_message`, `list_mail_folders`, `get_mailbox_settings`, `update_mailbox_settings`, `list_events`, `create_event`, `get_event`, `update_event`, `delete_event`, `get_schedule`, `list_contacts`, `get_contact`, `create_contact`, `update_contact`, `delete_contact`, `list_contact_folders`, `create_site`, `create_team`, `add_channel`, `provision_service`.
- **\(\mathcal{A}_m\) (mutating):** `create_channel`, `create_plan`, `create_plan_bucket`, `create_plan_task`, `create_list_item`, `create_folder`, `upload_file`, `create_document`, `update_document`, `create_workbook`, `update_workbook`, `create_presentation`, `update_presentation`, `set_flow_owner_role`, `remove_flow_owner_role`, `enable_flow`, `disable_flow`, `delete_flow`, `restore_flow`, `invoke_flow_callback`, `reset_user_password`, `create_user`, `update_user`, `disable_user`, `create_group`, `add_group_member`, `remove_group_member`, `assign_user_license`, `update_application`, `send_mail`, `move_message`, `delete_message`, `update_mailbox_settings`, `create_event`, `update_event`, `delete_event`, `create_contact`, `update_contact`, `delete_contact`, `create_site`, `create_team`, `add_channel`, `provision_service`.

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
