# Local Test Guide: Licensed Modules + Voice-to-M365

This guide is the fastest way to prove the setup works on your machine today.

This is a local validation guide, not the canonical production configuration contract. For production config authority, see `docs/commercialization/m365-canonical-config-contract.md`.

## Goal

Validate two things quickly:

1. M365 instruction contract is working (`action + params -> ok/result/error/trace_id`).
2. M365 module connector works in embedded mode with safety controls.

## Quick Path (10-15 minutes)

Run this from the `M365` repo.

### 1) Start with safety ON (mutations blocked)

```bash
export ALLOW_M365_MUTATIONS=false
export AUTH_DISABLED=true
```

### 2) Run focused tests

```bash
PYTHONPATH=src .venv/bin/pytest -q tests/test_m365_module_entrypoint.py tests/test_endpoints.py::test_m365_instruction_gated_idempotent
```

Expected result:
- Tests pass.
- You confirm auth/mutation/idempotency behavior is enforced.

### 3) Start API locally

```bash
PYTHONPATH=src .venv/bin/uvicorn provisioning_api.main:app --reload --port 9000
```

### 4) Call instruction endpoint

In a second terminal:

```bash
curl -s -X POST http://localhost:9000/api/m365/instruction \
  -H 'Content-Type: application/json' \
  -d '{"action":"create_team","params":{"mail_nickname":"pilot-team","channels":["General"]}}'
```

Expected result while mutations are blocked:
- `ok=false`
- `error="m365_mutations_disabled"`
- `trace_id` present

That is the expected safe default behavior.

## Embedded Module Smoke Test (No HTTP required)

Run:

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
from m365.module.entrypoint import M365ConnectorModule
module = M365ConnectorModule(require_user_context=True)
result = module.execute({
    "action": "create_team",
    "params": {"mail_nickname": "pilot-team", "channels": ["General"]},
    "trace_id": "local-smoke",
    "user_info": {"id": "local-user"}
})
print(result)
PY
```

Expected result with `ALLOW_M365_MUTATIONS=false`:
- `ok=False`
- `error='m365_mutations_disabled'`

This proves the module path and the API path enforce the same safety policy.

## Full End-to-End (TAI Host) Reality Check

The full "license key + toggle module on + voice flow" run path spans multiple repos.

For now, local proof is best done in two stages:
- Stage A: Validate M365 contract and M365 module in this repo (steps above).
- Stage B: Validate module host/toggles in `tai-core` using `/api/modules` endpoints.

This split is normal while you are still consolidating into a tighter single-runtime launch profile.

## When You Are Ready for Live M365 Writes

Only do this when your Graph credentials and tenant target are correct.

```bash
export ALLOW_M365_MUTATIONS=true
export GRAPH_TENANT_ID=...
export GRAPH_CLIENT_ID=...
export GRAPH_CLIENT_SECRET=...
```

Then re-run with a controlled test action in a test tenant.

## Recommended "Demo Script" for Stakeholders

Use this sequence in demos:

1. Show module/business model overview (`docs/TAI_LICENSED_MODULE_MODEL.md`).
2. Run tests and show green status.
3. Hit `/api/m365/instruction` and show blocked mutation (safe-by-default).
4. Explain that enabling writes is a deliberate gate, not an accident.

That gives a credible commercial + technical story in one pass.
