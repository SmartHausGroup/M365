# SmartHaus AI Workforce — Codex Execution Plan

## Mission & Scope
- Mission: Deliver a production-ready AI Workforce on Microsoft 365 only (SharePoint, Teams, Power Automate, Power Apps, Power BI, Outlook, Azure AD), with 39 agents managed via interactive dashboards and automated cross‑department workflows.
- Scope: Infrastructure setup, agent configuration, interactive dashboards, workflow automation, analytics, testing, security, go‑live, and training — strictly within M365 tooling and this repo’s services.

## Documents Reviewed (order)
- AI_WORKFORCE_PROJECT_TEMPLATE.md
- AI_WORKFORCE_DETAILED_SPECIFICATIONS.md
- AI_WORKFORCE_INTERACTIVE_DASHBOARD_SPECS.md
- AI_WORKFORCE_COMPLETE_IMPLEMENTATION_GUIDE.md

## 5‑Phase Plan (Deliverables)
1) Infrastructure Setup (Weeks 1–2)
   - 10 SharePoint sites + libraries, 10 Teams workspaces + channels, shared mailboxes, Power Platform perms. Baseline dashboards online.
2) Agent Configuration (Weeks 3–6)
   - 39 agents mapped to SharePoint lists/libraries, Teams channels, Outlook rules, Power Automate flows per agent.
3) Interactive Dashboards (Weeks 7–8)
   - Agent overview + detail pages, status telemetry, task assignment, work review, approvals, basic real‑time updates.
4) Automation & Integration (Weeks 9–10)
   - Cross‑department workflows, escalation patterns, Power BI dashboards wired to SharePoint/Graph data.
5) Testing & Go‑Live (Weeks 11–12)
   - Full test suites (unit/integration/perf/security/UAT), production deployment, training, handoff.

## Repo Mapping (Where work lives)
- Provisioning API: `src/provisioning_api/*` (FastAPI, M365 orchestration, routers, status, auth)
- Agent Dashboards: `src/provisioning_api/routers/agent_dashboard.py` + `registry/ai_team.json`, `registry/agents.yaml`
- Graph/M365 Integration: `src/smarthaus_graph/client.py`, `src/provisioning_api/m365_provision.py`
- Ops Adapter (policy, approvals, audit): `src/ops_adapter/*`, `policies/*.rego`, `policies/agents/*.rego`
- Config & Bootstrap: `config/services.json`, `scripts/bootstrap_m365_services.py`, `scripts/ops/*`
- Frontend static build: `src/frontend/*`, `make build-dashboard` → `dist/`
- Auth: `MICROSOFT_OAUTH_SETUP.md`, `api/auth/*`, `src/provisioning_api/auth.py`
- Tests: `tests/*` (FastAPI endpoints, Graph client, OPA policies)

## Environment & Prereqs (M365 only)
- Azure AD App: Tenant, Client ID, Client Secret with Graph App permissions (per MICROSOFT_OAUTH_SETUP.md)
- Env vars:
  - Graph: `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`
  - SharePoint: `SP_HOSTNAME` (e.g., smarthausgroup.sharepoint.com)
  - Mutations gate: `ALLOW_M365_MUTATIONS=true` only when ready to provision
  - Optional: `CORS_ORIGINS`, `OPA_URL`, Teams webhook envs for approvals
- CLI/Tools: PowerShell modules (PnP.PowerShell, Microsoft.Graph), OPA CLI (for `policies` tests), Python (uvicorn, pytest), Node/Vercel for dashboard hosting.

## Implementation Checklist (Phase by Phase)
Phase 1 — Infrastructure (Weeks 1–2)
- SharePoint: Create 10 sites and libraries per specs (PnP.PowerShell or Graph)
- Teams: Create 10 workspaces + channels (Graph); confirm in `config/services.json`
- Outlook: Shared mailboxes + rules per roles
- Power Platform: Permissions, solutions scaffolding
- Repo tasks:
  - Verify Graph connectivity: `GET /status` → `m365_connectivity`
  - Dry‑run bootstrap (no mutations): `python scripts/bootstrap_m365_services.py`
  - Enable provisioning once ready: `ALLOW_M365_MUTATIONS=true`

Phase 2 — Agent Configuration (Weeks 3–6)
- Map 39 agents in `registry/ai_team.json` + `registry/agents.yaml`
- Create agent SharePoint lists, Teams channels; wire Outlook rules
- Author baseline Power Automate flows: onboarding, deployment, campaigns, approvals
- Generate/validate OPA policies from registry: `scripts/generate-policies.py`

Phase 3 — Interactive Dashboards (Weeks 7–8)
- Extend `agent_dashboard.py` with status endpoints, task/instruction posts, and work review UI
- Add real‑time updates (SSE/WebSocket) for status/progress where feasible
- Build “Agent Control Panel”, “Work Review”, and “Instruction” interfaces per specs

Phase 4 — Automation & Integration (Weeks 9–10)
- Wire cross‑department workflows via Power Automate + Graph + Ops Adapter approvals
- Implement escalation patterns and notifications (Teams webhooks)
- Publish Power BI reports tied to SharePoint/Graph datasets

Phase 5 — Testing & Go‑Live (Weeks 11–12)
- Run tests: unit (`tests/*`), integration (cross‑dept), perf, security (authZ/RBAC/DLP)
- UAT checklists per department; production deploy; runbooks; training

## Testing Strategy
- Unit: FastAPI endpoints (`tests/test_endpoints.py`), Graph client (`tests/test_graph_client.py`), API health
- Policy: OPA policy decisions (`tests/test_policies.py`, requires `opa`)
- Integration: Cross‑dept flows (onboarding, deployment, campaigns) via API + Flow validation
- Performance: API latency, workflow throughput (per implementation guide targets)
- Security: Auth/MFA, RBAC, DLP, logs, conditional access

## Security & Compliance
- Auth: Azure AD; MFA for admins; sessions per policy
- RBAC: Global Admin, Department Admin, Agent, Guest
- Data: Encryption in transit (TLS 1.3), at rest (M365); Key Vault for secrets
- DLP/Compliance: SharePoint/Teams/Email DLP policies; audit logging; retention policies

## Success Metrics
- Technical: 39 agents live; 99.9% uptime; <2s response; 100% security compliance; workflows automated
- Business: 90% task automation; 50% manual reduction; 95% user satisfaction; zero extra software cost; +25% efficiency

## Immediate Next Actions (Safe to start now)
1) Configure Graph auth (no mutations)
   - Set `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`
   - Hit `GET /status` → confirm `m365_connectivity: ok | not_configured_or_unreachable`
2) Validate dashboards locally
   - `make serve-api` → open `/api/agents/dashboard` and `/api/email/dashboard`
3) Validate tests (optional OPA)
   - Run `make test`; if OPA missing, run subset: `pytest -q tests/test_api_health.py tests/test_endpoints.py`
4) Prepare provisioning dry‑run
   - Review `config/services.json`; align with departments; dry‑run `scripts/bootstrap_m365_services.py`
5) Plan Phase 1 provisioning window
   - When ready, enable `ALLOW_M365_MUTATIONS=true` and execute bootstrap + PowerShell site creation

## Notes
- All M365‑changing operations are gated by `ALLOW_M365_MUTATIONS` and require valid Graph credentials.
- We will not run tenant‑impacting steps without explicit readiness. Dry‑runs and status checks first.

