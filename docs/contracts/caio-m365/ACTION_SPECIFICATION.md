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
| **Result shape** \(\mathcal{S}_{\texttt{list\_users}}\) | `{ "users": array, "count": number }` — `users` is array of user objects; `count` is length of `users`. |
| **Error cases** | Graph not configured; invalid `top` or `select`. |

### 2. list_teams

| Field | Specification |
|-------|----------------|
| **action** | `list_teams` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` positive integer (optional, default 100). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_teams}}\) | `{ "teams": array, "count": number }` — `teams` is array of team objects; `count` is length of `teams`. |
| **Error cases** | Graph not configured. |

### 3. list_sites

| Field | Specification |
|-------|----------------|
| **action** | `list_sites` |
| **Mutating** | No |
| **Preconditions** | `params` optional. If present: `top` positive integer (optional). |
| **Result shape** \(\mathcal{S}_{\texttt{list\_sites}}\) | `{ "sites": array, "count": number }` — `sites` is array of site objects; `count` is length of `sites`. |
| **Error cases** | Graph not configured. |

### 4. get_user

| Field | Specification |
|-------|----------------|
| **action** | `get_user` |
| **Mutating** | No |
| **Preconditions** | One of `userPrincipalName`, `user_id`, or `id` present in `params` (string). |
| **Result shape** \(\mathcal{S}_{\texttt{get\_user}}\) | `{ "user": object }` — single user object from Graph. |
| **Error cases** | Missing identifier; user not found; Graph not configured. |

### 5. reset_user_password

| Field | Specification |
|-------|----------------|
| **action** | `reset_user_password` |
| **Mutating** | Yes |
| **Preconditions** | `params`: one of `userPrincipalName`/`user_id`/`id` (string); `temporary_password` or `password` (string). Optional: `force_change_next_sign_in` (boolean, default true). Mutations must be enabled (env). |
| **Result shape** \(\mathcal{S}_{\texttt{reset\_user\_password}}\) | `{ "user": string, "password_reset": true }` — `user` is id or UPN. |
| **Error cases** | Missing params; Graph not configured; mutations disabled. |

### 6. create_site

| Field | Specification |
|-------|----------------|
| **action** | `create_site` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `display_name` (string, required) or `site_name`. Optional: `mail_nickname`/`url_slug`, `libraries` (array), `description`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{create\_site}}\) | `{ "site_id": string, "site_url": string, "group_created": boolean, "libraries_created": array }` — site_id and site_url from Graph; group_created true if group was created; libraries_created list of library names. |
| **Error cases** | Missing display_name; Graph/site creation failure; mutations disabled. |

### 7. create_team

| Field | Specification |
|-------|----------------|
| **action** | `create_team` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `mail_nickname` (string, required). Optional: `channels` (array of strings). Mutations must be enabled. Group must exist (e.g. create_site first). |
| **Result shape** \(\mathcal{S}_{\texttt{create\_team}}\) | `{ "team_id": string, "team_url": string, "channels_created": array }` — team_id is group id; team_url from Graph; channels_created list of channel display names. |
| **Error cases** | Missing mail_nickname; group not found; mutations disabled. |

### 8. add_channel

| Field | Specification |
|-------|----------------|
| **action** | `add_channel` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `mail_nickname` (string), `channel_name` (string). Optional: `description`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{add\_channel}}\) | `{ "team": object, "channel": string }` — `team` has `team_id`, `team_url`, `channels_created`; `channel` is the channel name added. |
| **Error cases** | Missing mail_nickname or channel_name; group/team not found; mutations disabled. |

### 9. provision_service

| Field | Specification |
|-------|----------------|
| **action** | `provision_service` |
| **Mutating** | Yes |
| **Preconditions** | `params`: `key` (string, required) — must match a key in `config/services.json`. Mutations must be enabled. |
| **Result shape** \(\mathcal{S}_{\texttt{provision\_service}}\) | `{ "status": "ok", "site": object, "team": object }` — `site` is create_site result shape; `team` is create_team result shape. |
| **Error cases** | Missing key; config/services.json missing; unknown service key; mutations disabled. |

---

## Canonical sets

- **\(\mathcal{A}\) (implemented):** `list_users`, `list_teams`, `list_sites`, `get_user`, `reset_user_password`, `create_site`, `create_team`, `add_channel`, `provision_service`.
- **\(\mathcal{A}_m\) (mutating):** `reset_user_password`, `create_site`, `create_team`, `add_channel`, `provision_service`.

---

## Planned (North Star)

The North Star defines the full capability set for Admin (§3.1) and User (§3.2). Actions not yet in \(\mathcal{A}\) above (e.g. create_user, list_groups, send_mail, list_events, …) are specified there. When an action is implemented:

1. Add it to this document with preconditions and result shape.
2. Add it to MATHEMATICS.md result-shapes table.
3. Add it to the verification script RESULT_SHAPES and mocks/live checks.
4. Update INV-CAIO-M365-001 acceptance if needed.

---

## Verification

The script `scripts/ci/verify_caio_m365_contract.py` must validate response shape for every action in \(\mathcal{A}\). Result shape checks use the required keys per action from this specification.
