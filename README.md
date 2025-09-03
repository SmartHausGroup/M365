# 🚀 SmartHaus Group M365 SOA 🚀

Enterprise-grade, service-oriented automation for Microsoft 365. This repo hosts:
- Reusable libraries (Graph client, common utilities)
- A provisioning API (FastAPI) to orchestrate M365 resources
- A CLI for developer and operator workflows
- CI, linting, tests, and contribution standards

Quick start
- Install deps: `make install-deps`
- Run tests: `make test`
- Serve API: `make serve-api` then visit http://localhost:8000/health
- CLI: `python -m smarthaus_cli --help`

Docker
- Build: `make docker-build`
- Run default: `make docker-run`
- Run named/port: `make docker-run-instance NAME=tai-research PORT=9000`
- List: `make docker-list`
- Stop instance: `make docker-stop-instance NAME=tai-research`
- Logs: `make docker-logs NAME=tai-research`
- Stop all: `make docker-stop-all`

Credentials
- Set `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET` to use Graph operations.

Environment (optional integrations)
- `TAI_REPOSITORY`, `LATTICE_REPOSITORY`, `SMARTHAUS_WEBSITE_REPO`
- `SIGMA_REPOSITORY`, `C2_CLOUD_ENDPOINT`, `MARKETING_AGENT_ENDPOINT`, `PATENT_MANAGEMENT_ENDPOINT`
- `GITHUB_WEBHOOK_SECRET` (for future GitHub integrations)
- Feature flags: `RESEARCH_COLLABORATION_ENABLED`, `CROSS_PROJECT_INTEGRATION`

Docs
- `docs/architecture.md` – architecture overview
- `docs/adr/0001-repo-structure.md` – structure rationale

API Endpoints (POST)
- TAI: `/api/tai/research`, `/api/tai/memory`, `/api/tai/orchestration`, `/api/tai/performance`
- LATTICE: `/api/lattice/research`, `/api/lattice/aios`, `/api/lattice/lql`, `/api/lattice/lef`, `/api/lattice/architecture`
- Website: `/api/website/updates`, `/api/website/deployments`, `/api/website/content`, `/api/website/business`
- Research: `/api/research/collaboration`, `/api/research/resources`, `/api/research/synthesis`, `/api/research/performance`
- SIGMA: `/api/sigma/performance`, `/api/sigma/signals`, `/api/sigma/backtesting`, `/api/sigma/risk`
- C2: `/api/c2/security`, `/api/c2/infrastructure`, `/api/c2/compliance`, `/api/c2/documents`
- Marketing: `/api/marketing/leads`, `/api/marketing/campaigns`, `/api/marketing/analytics`, `/api/marketing/business`
- Patents: `/api/patents/applications`, `/api/patents/portfolio`, `/api/patents/autopsy`, `/api/patents/compliance`
- Infrastructure: `/api/infrastructure/cicd`, `/api/infrastructure/deployments`, `/api/infrastructure/monitoring`, `/api/infrastructure/optimization`
- Clients: `/api/clients/projects`, `/api/clients/showcase`, `/api/clients/automation`, `/api/clients/communication`

Storage
- By default, requests are recorded to `data/*.json` for easy verification.

Containers persist data under per-instance directories `./instances/<NAME>/` unless overridden by `HOST_DATA`, `HOST_CONFIG`, `HOST_LOGS`.

Vercel (cloud frontend)
- Build static dashboard: `make build-dashboard` → outputs to `dist/`
- Deploy with `vercel` CLI or Git integration using `vercel.json`
- Set env `API_BASE_URL` in Vercel to point at your API (e.g., `https://api.m365.smarthaus.ai` or `https://your-host:8000`)
- Configure custom domain `m365.smarthaus.ai` in Vercel project settings

CORS for Cloud Frontend
- Set `CORS_ORIGINS` on the API (comma-separated origins, e.g., `https://m365.smarthaus.ai,https://preview.m365.smarthaus.ai`)

Hybrid (cloud + local)
- Local API (Docker):
  - Start: `make docker-dev-up` → http://localhost:8000
  - Logs: `make docker-dev-logs`
  - Stop: `make docker-dev-down`
- Smart routing in UI: the enterprise dashboard auto-detects environment
  - If opened on localhost, it targets `http://localhost:8000`
  - Otherwise, it uses the injected `API_BASE_URL` (e.g., `https://api.m365.smarthaus.ai`)
- Compose file: `docker-compose.local.yml` (editable for dev env)

Notes
- Legacy helper scripts and setup guides were removed to keep this repo focused and modern.
