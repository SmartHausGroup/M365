# M365 environment variables

This document describes environment variables and local bootstrap compatibility surfaces.

For the canonical production configuration contract, see `docs/commercialization/m365-canonical-config-contract.md`.

Production authority is the tenant-scoped contract in `src/smarthaus_common/tenant_config.py`, not `.env` alone. `.env` remains relevant for local bootstrap, local testing, and secret fallback behavior.

---

## Graph (Microsoft 365)

| Variable | Purpose |
|----------|---------|
| `GRAPH_TENANT_ID` | Azure AD tenant id (or `AZURE_TENANT_ID`, `MICROSOFT_TENANT_ID`) |
| `GRAPH_CLIENT_ID` | App (client) id (or `AZURE_CLIENT_ID`, `MICROSOFT_CLIENT_ID`, `AZURE_APP_CLIENT_ID_TAI`) |
| `GRAPH_CLIENT_SECRET` | Client secret (or `AZURE_CLIENT_SECRET`, `MICROSOFT_CLIENT_SECRET`, `AZURE_APP_CLIENT_SECRET_TAI`) |

Optional: `AZURE_CLIENT_CERTIFICATE_PATH` for certificate auth instead of secret.

---

## M365 server (app launcher)

| Variable | Purpose |
|----------|---------|
| `M365_APP_ROOT` | Directory containing `registry/agents.yaml` and optional `.env` |
| `M365_SERVER_PORT` | Port for m365-server (default 9000) |
| `M365_SERVER_HOST` | Bind host (default 0.0.0.0) |

---

## Instruction API (CAIO)

| Variable | Purpose |
|----------|---------|
| `CAIO_API_KEY` | If set, CAIO must send `X-CAIO-API-Key` or `X-CAIO-Token` with this value |
| `ALLOW_M365_MUTATIONS` | `true`/`1`/`yes` to allow create_site, create_team, add_channel, provision_service, reset_user_password |

---

## SharePoint / sites

| Variable | Purpose |
|----------|---------|
| `SHAREPOINT_HOSTNAME` or `SP_HOSTNAME` | e.g. `smarthausgroup.sharepoint.com` |

---

## Ops adapter (when run separately)

| Variable | Purpose |
|----------|---------|
| `REGISTRY_FILE` | Path to `agents.yaml` (default `./registry/agents.yaml`) |
| `LOG_DIR` | Audit/log directory (default `./logs`) |
| `OPA_URL` | OPA policy engine URL (e.g. `http://localhost:8181`) |
| `OPA_FAIL_OPEN` | If true, allow when OPA unreachable |
| `JWT_REQUIRED` | If true, require Bearer JWT on `/actions/*` |
| `TEAMS_APPROVALS_WEBHOOK` | Incoming webhook for approval cards |

---

## App / provisioning API

| Variable | Purpose |
|----------|---------|
| `APP_VERSION` | API version string |
| `APP_ENV` | e.g. `dev`, `production` |
| `LOG_LEVEL` | e.g. `info`, `debug` |

---

## Local Bootstrap Loading Order

1. `.env` in app root (current working directory or `M365_APP_ROOT`)
2. `~/.smarthaus/m365/.env`

Later files do not override earlier (`override=False`).

This loading order describes launcher/bootstrap behavior only. It is not the canonical production identity model.
