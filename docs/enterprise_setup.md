# SmartHaus M365 Enterprise Platform – Setup Guide

This guide provisions Microsoft 365 resources (Teams, Planner) for all 13 services, configures GitHub → M365 automation, and exposes API endpoints for dashboards and integrations.

Prereqs
- Azure AD app with Graph application permissions: Group.ReadWrite.All, Team.ReadWrite.All, Channel.ReadWrite.All, Sites.ReadWrite.All, Planner.ReadWrite.All
- Tenant admin consent granted for the app
- Environment variables set: `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`
- Optional: `GITHUB_TOKEN` (repo admin:repo_hook) for webhook setup, `GITHUB_WEBHOOK_SECRET` for signature validation
- `jq` installed (for webhook script)

1) Configure environment
- Create `.env` or export variables:
  - `GRAPH_TENANT_ID`=...
  - `GRAPH_CLIENT_ID`=...
  - `GRAPH_CLIENT_SECRET`=...
  - `ALLOW_M365_MUTATIONS`=true
  - `ENABLE_M365_AUTOMATION`=true

2) Provision Teams + Planner for all services
- Review `config/services.json` for names, mail nicknames, and channels
- Run: `make bootstrap-m365`
- This will:
  - Ensure group-connected site exists (SharePoint)
  - Ensure a Team exists and create standard channels
  - Ensure a Planner plan with default buckets: Backlog, In Progress, Code Review, Done
  - Write discovered IDs back into `config/services.json`

3) Configure GitHub webhooks
- Choose your API endpoint (local dev or prod), e.g. `https://your-api/api/webhooks/github/{project}`
- Export: `WEBHOOK_URL=https://your-api/api/webhooks/github/{project}`
- Export: `GITHUB_TOKEN=...` and optionally `GITHUB_WEBHOOK_SECRET=...`
- Run: `bash scripts/configure-github-webhooks.sh`

4) Run the API
- Local dev: `make serve-api` → `http://localhost:9000`
- Health: `GET /health`
- Status: `GET /status`
- Empire overview: `GET /api/m365/empire-overview`
- Instruction API (for CAIO): `POST /api/m365/instruction`

5) Validate automation
- Trigger an event (open an issue/PR) on any configured repo
- The API webhook (`POST /api/webhooks/github/{project}`) will:
  - Create a Planner task in the appropriate bucket (Issues → Backlog, PR → Code Review, Release → Done)
  - Post a Teams channel message (PR → Code Review if present, otherwise General)

6) M365 instruction API (for CAIO)
- Endpoint: `POST /api/m365/instruction`
- Headers: `Content-Type: application/json`; optional `Idempotency-Key`; optional `X-CAIO-API-Key` if `CAIO_API_KEY` is set; `Authorization: Bearer <token>` if auth enabled
- Body:
  `{"action": "create_site", "params": {"display_name": "Project X", "mail_nickname": "project-x", "libraries": ["Docs"]}}`
- Actions: `create_site`, `create_team`, `add_channel`, `provision_service`
- Response: `{ "ok": true|false, "result": { ... }, "error": "...", "trace_id": "..." }`

7) Embedded module contract (TAI licensed runtime)
- Python entrypoint: `m365.module.entrypoint:M365ConnectorModule`
- Capability: `m365.instruction.execute`
- Manifest helper: `m365.module.manifest:m365_connector_module_manifest`
- Module payload shape:
  `{"action":"create_team","params":{"mail_nickname":"project-x","channels":["General"]},"trace_id":"...","idempotency_key":"...","user_info":{"id":"user-123"}}`
- Module response shape:
  `{ "ok": true|false, "result": { ... }, "error": "...", "trace_id": "..." }`
- Planning reference: `plans/tai-licensed-modular-runtime/master-plan.md` (`plan:tai-licensed-modular-runtime:m365`)
- Entitlement expected by TAI host: `m365_actions`
- Permissions metadata: `graph:m365`, `audit:write`, `mutations:gated`
- Module auth expectation: host supplies caller context (`user_info` or `context.user_info`) when `M365_MODULE_REQUIRE_AUTH=true` (default)

Power BI (Executive Dashboards)
- Connect Power BI to the API endpoints (`/api/m365/empire-overview`, `/api/research/insights`, `/api/bi/analytics`)
- Model and publish dashboards. Optionally, use SharePoint lists as a data source for persistent metrics.

Power Apps (Client + Status)
- Use SharePoint lists (created in your service sites) to bootstrap low-code apps:
  - Create a list named `RepositoryStatus` with columns (Text: Repo, Choice: Status, Number: OpenIssues, Number: Velocity, Date: LastUpdated)
  - Power Apps → Create app from data → SharePoint → select `RepositoryStatus`

Notes
- Set `ENABLE_M365_AUTOMATION=false` to dry-run webhook processing without touching M365
- Ensure Graph app permissions are granted; Planner APIs require proper tenant configuration
- `CAIO_API_KEY` enables shared‑secret auth for `/api/m365/instruction`; send `X-CAIO-API-Key` when set
- `Idempotency-Key` is supported for `/api/m365/instruction` to prevent duplicate execution
- `M365_MODULE_REQUIRE_AUTH` controls embedded module auth enforcement (default `true`)
