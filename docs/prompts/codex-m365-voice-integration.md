# Codex Detailed Prompt: M365 Voice Integration (Instruction API)

**Plan reference:** `plan:tai-maia-caio-vfe-m365-integration:m365`  
**Detailed plan:** `plans/tai-maia-caio-vfe-m365-integration/m365-repo-plan.md`  
**Master plan:** `plans/tai-maia-caio-vfe-m365-integration/master-plan.md`

---

## Executive summary

Implement (or document and expose) the **M365 instruction/command API** so the CAIO M365 adapter can call it with structured intent (action + params), execute via existing Provisioning API/Graph/orchestrator, and return a structured result. This repo does **not** implement the CAIO adapter—only the API that the adapter will call.

---

## Context and background

- **Flow:** User speaks → TAI → MAIA (intent) → CAIO (orchestration) → **M365 API** (this repo) → result back to TAI.
- **M365 role:** Expose an HTTP API that accepts M365 instructions (e.g. `create_team`, `add_channel`, `create_site`) and parameters; validate; call existing `src/provisioning_api/`, `src/smarthaus_graph/client.py`, orchestrator; return JSON result.
- **Governance:** Plan-first; change approval before implementation. No implementation without explicit "go."

---

## Current state

- Provisioning API exists (`src/provisioning_api/`, routers, `m365.py`, orchestrator).
- Graph client and `ALLOW_M365_MUTATIONS` gating are in place.
- There may or may not be an existing “instruction” endpoint; the plan requires a **documented contract** and a **single entry point** (or agreed set of endpoints) for CAIO to call.

---

## Target state

- One or more endpoints (e.g. `POST /api/m365/instruction` or under existing router) accepting JSON: `{ "action": string, "params": object }` (or schema agreed with CAIO).
- Action mapped to existing orchestrator/Graph operations.
- Response: `{ "ok": boolean, "result"?: object, "error"?: string, "trace_id"?: string }`.
- Auth for CAIO adapter calls; `ALLOW_M365_MUTATIONS` gate; audit log for each instruction.
- OpenAPI/docs for the instruction API.

---

## Step-by-step implementation (from m365-repo-plan)

1. **Define contract** — Document request/response schema (action enum, params per action). Align with CAIO plan owner.
2. **Implement or extend router** — Add instruction endpoint(s) under `src/provisioning_api/routers/` (e.g. extend `m365.py` or add `instruction.py`). Wire to orchestrator and Graph client.
3. **Auth and gates** — Enforce auth on instruction endpoint; keep `ALLOW_M365_MUTATIONS` for mutating calls.
4. **Audit** — Log each instruction (who, action, params, result, timestamp).
5. **Tests** — Unit tests for schema validation and routing; integration test for at least one action (dry-run or test tenant).
6. **Docs** — Update API docs; reference master plan.

---

## Validation

- `make test` (or equivalent) passes.
- Call instruction endpoint with a known action; verify response shape and audit log.
- Security: no credentials in logs; auth required.

---

## Troubleshooting

- If orchestrator/Graph calls fail: use existing error handling; map to response `ok: false` and `error` message.
- If schema diverges from CAIO: update contract doc and align with CAIO plan before changing code.

---

## Success criteria (from plan)

- [ ] Instruction API documented and implemented.
- [ ] CAIO adapter can call it with intent-derived payload and get structured result.
- [ ] M365 mutations gated and audited.
- [ ] Plan checklist and tests pass.

---

## References

- `plans/tai-maia-caio-vfe-m365-integration/m365-repo-plan.md` (and .yaml, .json)
- `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`
- `.cursor/rules/rsf-change-approval.mdc`, `.cursor/rules/plan-first-execution.mdc`
