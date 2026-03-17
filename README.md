# SMARTHAUS M365 Ops Adapter (MVP)

![Policy Validation](https://github.com/smarthaus/M365/workflows/Policy%20Validation/badge.svg)

Production-ready scaffold for the SMARTHAUS Enterprise Ops Adapter with OPA policy enforcement, approvals, and audit logging.

## Stack
- FastAPI service (ops-adapter)
- Open Policy Agent (OPA) for runtime policy
- Basic approvals queue with Teams webhook notification
- Structured audit logs with correlation IDs

## Running as an application (Python 3.13+)

Install once, then launch the server like a normal app (no Makefile or dev steps):

```bash
pip install -e .
m365-server          # headless on port 9000
m365-server --gui    # window with status and Quit
```

See **[docs/M365_SERVER_APP.md](docs/M365_SERVER_APP.md)** for full app launcher details. Env vars: **[docs/ENV.md](docs/ENV.md)**. CAIO contract: **[docs/CAIO_M365_CONTRACT.md](docs/CAIO_M365_CONTRACT.md)**.

---

## Quickstart (Docker / dev)

1. Copy and configure environment:
   - `cp instances/sandbox.env.example instances/sandbox.env`
   - Fill in `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_CERTIFICATE_PATH`, and optional `VERCEL_API_TOKEN`.

2. Start services:
   - Local OPA + adapter: `docker compose --env-file instances/sandbox.env up -d --build`
   - Or point to Enterprise policy-engine (recommended):
     - Export `OPA_URL=http://localhost:8181` (or your gateway URL)
     - Start only the adapter: `docker compose --env-file instances/sandbox.env up -d --build ops-adapter`

3. Health checks:
   - `curl http://localhost:8080/health`
   - `curl http://localhost:8181/health`

4. Try a policy-checked action (Graph users.read):
   - `curl -s -X POST http://localhost:8080/actions/m365-administrator/users.read -H 'Content-Type: application/json' -d '{"params":{"userPrincipalName":"test@smarthaus.ai"}}' | jq`

5. Trigger an approval-required action:
   - `curl -s -X POST http://localhost:8080/actions/website-manager/deployment.production -H 'Content-Type: application/json' -d '{"params":{"env":"production"}}' | jq`
   - `curl -s http://localhost:8080/approvals/<approval_id-returned>`

Audit logs write to `logs/ops_audit.log`.

## Layout

```
src/ops_adapter/
  actions.py       # Graph/Vercel action executors
  approvals.py     # Basic approvals queue + Teams webhook
  audit.py         # Structured audit logger (+optional Log Analytics)
  main.py          # FastAPI app and routes
  models.py        # Pydantic request/response models
  policies.py      # OPA client wrapper
  rate_limit.py    # Token bucket rate limiter
policies/
  ops.rego
  agents/
    m365_administrator.rego
    website_manager.rego
    hr_generalist.rego
    outreach_coordinator.rego
registry/
  agents.yaml
Dockerfile.ops-adapter
docker-compose.yml
instances/
  sandbox.env.example
```

## Approvals with SharePoint + Teams

- Configure env:
  - `APPROVALS_SITE_URL=https://<tenant>.sharepoint.com/sites/<site>`
  - `APPROVALS_LIST_NAME=Approvals`
  - `TEAMS_APPROVALS_WEBHOOK=<incoming webhook URL>`
  - Optional public URL for card actions: `OPS_ADAPTER_PUBLIC_URL=https://ops-adapter.example.com`
  - Optional HMAC signing: `TEAMS_CARD_SIGNING_SECRET=<strong-shared-secret>` and `TEAMS_CARD_MAX_SKEW=600`

- Endpoints:
  - `GET /approvals/{id}` → Get status
  - `POST /approvals/{id}/approve` → Approve (body: `{ "params": {"reason": "..."} }`)
  - `POST /approvals/{id}/deny` → Deny (body: `{ "params": {"reason": "..."} }`)
  - `POST /approvals/bulk` → `{ "params": { "action": "approve|deny", "ids": ["..."], "reason": "..." } }`
  - `GET /approvals/query?status=pending&agent=website-manager&limit=50` → Filtered list for dashboards

- Optional bot webhook (authenticated):
  - `POST /teams/webhook` with header `Authorization: Bearer $TEAMS_BOT_TOKEN`
  - Body: `{ "params": { "approvalId": "...", "action": "approve|deny", "reason": "...", "user": { "upn": "..." } } }`
  - Env: `TEAMS_BOT_TOKEN=<shared-bot-token>`

## Policy Generation from Registry

Keep OPA policies in sync with the registry by generating per-agent policy files:

```
python scripts/generate-policies.py --registry registry/agents.yaml --outdir policies/agents
# Optionally run `opa fmt -w policies` and `opa check policies` if OPA is installed
```


## Example Runbook (Employee Lifecycle)

Run a full CRUD lifecycle against Graph via the adapter:

```
./scripts/runbooks/employee-lifecycle.sh test.user@smarthaus.ai "Test User" E3

# Assign multiple licenses
./scripts/runbooks/employee-lifecycle.sh test.user@smarthaus.ai "Test User" E3,E5
```

## Licensed Module Model + Local Validation

- Commercial plain-English model: `docs/TAI_LICENSED_MODULE_MODEL.md`
- Local test runbook (M365 module + instruction API): `docs/LOCAL_TEST_LICENSED_RUNTIME.md`

## Notes
- OPA enforcement is active; if OPA is unreachable, the adapter fails open (configurable).
- Graph integration uses certificate credentials if provided; otherwise calls are stubbed.
- Approvals store uses SQLite; enable Teams webhook with `TEAMS_APPROVALS_WEBHOOK`.
