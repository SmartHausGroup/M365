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
| `provision_service` | Provision service from config | Yes | `key` |
| `list_users` | List M365 users | No | `top?` (1–999), `select?` |
| `list_teams` | List Teams workspaces | No | `top?` |
| `list_sites` | List SharePoint site collections | No | `top?` |
| `get_user` | Get single user by id or UPN | No | `userPrincipalName` or `user_id` or `id` |
| `reset_user_password` | Set temporary password; force change at next sign-in | Yes | `userPrincipalName` or `user_id`, `temporary_password` or `password`, `force_change_next_sign_in?` |

**Mutating actions** require `ALLOW_M365_MUTATIONS=true` (or `1`/`yes`) in M365 env; otherwise response is `ok: false`, `error: m365_mutations_disabled`.

---

## Response shapes (result)

- **list_users:** `{ "users": [ ... ], "count": N }`
- **list_teams:** `{ "teams": [ ... ], "count": N }`
- **list_sites:** `{ "sites": [ ... ], "count": N }`
- **get_user:** `{ "user": { ... } }`
- **reset_user_password:** `{ "user": "<id|upn>", "password_reset": true }`
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
