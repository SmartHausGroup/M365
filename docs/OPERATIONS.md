# Ops Adapter & Policy Engine

This document outlines the enterprise Ops Adapter service, OPA policy engine, and the integration model for SmartHaus M365 and website operations.

## Components

- Ops Adapter (FastAPI): `src/ops_adapter/`
  - `/health` — liveness probe
  - `/actions/{agent}/{action}` — execute a permitted action
  - `/approvals/{id}` — get/update approval state
  - Correlation ID propagation via `X-Request-ID`
  - Structured audit logs with optional file sink (`OPS_AUDIT_FILE`)
  - Per-agent rate limiting (token bucket)
- OPA (Open Policy Agent): `policies/`
  - Top-level policy: `policies/ops.rego`
  - Per-agent policies under `policies/agents/`

## Local Run

```bash
docker compose up -d opa ops-adapter
curl -s http://localhost:8080/health
curl -s -X POST http://localhost:8080/actions/m365-administrator/user.provision \
  -H 'Content-Type: application/json' \
  -d '{"params": {"userPrincipalName": "jdoe@contoso.com"}}'
```

## Environment Variables

- `OPS_ADAPTER_PORT` — default `8080`
- `OPA_URL` — default `http://opa:8181`
- `OPS_DRY_RUN` — default `true` (no external side effects)
- `OPS_RATE_DEFAULT_RPS` — default `5`
- `OPS_RATE_BURST` — default `10`
- `OPS_AUDIT_FILE` — optional file path for audit append-only logs
- `OPA_FAIL_OPEN` — set `true` in dev to allow when OPA unreachable

## Policy Contract (OPA)

The adapter POSTs to `/v1/data/ops/decision` with:

```json
{
  "input": { "agent": "m365-administrator", "action": "user.provision", "payload": {}}
}
```

OPA returns a decision object:

```json
{ "result": { "allow": true, "approval_required": false } }
```

## Approval Workflow

- `approval_required=true` results in `202`-like response with `status=pending` and an `approval_id`.
- Approvers POST decision to `/approvals/{id}` with `{ "decision": "approved" | "rejected" }`.
- In production, back this with SharePoint lists and Teams notifications.

## Integration Pattern

1. Agents call Ops Adapter only (no direct Graph calls).
2. Ops Adapter evaluates OPA policies and, if allowed, runs action handlers.
3. Handlers call internal clients (e.g., `GraphClient`) unless `OPS_DRY_RUN=true`.
4. All requests carry `X-Request-ID`; audit logs record every step.

## Adding Actions

1. Implement handler in `src/ops_adapter/actions.py`.
2. Register under `action_registry` for the agent.
3. Allow it in the appropriate Rego under `policies/agents/`.
4. Add tests in `tests/test_ops_adapter.py`.
