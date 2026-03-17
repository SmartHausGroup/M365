# Plan: M365 Repo — Voice Integration (Instruction API for CAIO)

**Plan ID:** `m365-repo-plan` (parent: `tai-maia-caio-vfe-m365-integration`)
**Status:** Draft (Pending Approval)
**Date:** 2026-02-06
**Owner:** SmartHaus
**Master plan:** `plans/tai-maia-caio-vfe-m365-integration/master-plan.md`
**Execution plan reference:** `plan:tai-maia-caio-vfe-m365-integration:m365`
**North Star alignment:** `Operations/NORTHSTAR.md` — M365 AI Workforce, provisioning API, Graph integration.

**MA process:** This plan is integration/API work (no new mathematical operations or performance guarantees). MA Phases 1–5 are not required for this repo’s scope. If any task is later deemed mathematical/algorithmic, that task will follow `.cursor/rules/ma-process-mandatory.mdc` and `.cursor/rules/notebook-first-mandatory.mdc` before implementation.

---

## Objective

Define and expose an **instruction/command API** in the M365 repo that the CAIO M365 adapter can call to execute user-intent actions (e.g. create team, add channel, create SharePoint site). Ensure auth (Graph), idempotency, and auditability. Do not implement the CAIO adapter in this repo (that is CAIO’s plan).

---

## Scope (M365 repo only)

- **In scope:** Design and implement (or document existing) an HTTP API that accepts structured “M365 instructions” (action + parameters), validates them, calls existing Provisioning API / Graph client / orchestrator, and returns a structured result. Auth, rate limits, and audit logging.
- **Out of scope:** TAI, MAIA, CAIO, or VFE code; voice or intent logic; CAIO adapter implementation.

---

## Prerequisites

- Existing Provisioning API running (`src/provisioning_api/`, `src/smarthaus_graph/client.py`, `src/provisioning_api/orchestrator.py`).
- Graph credentials and `ALLOW_M365_MUTATIONS` gating per `Operations/EXECUTION_PLAN.md`.
- Master plan and CAIO contract agreed (intent shape and M365 instruction schema).

---

## Requirements

### Functional

- [x] One or more endpoints (e.g. `POST /api/m365/instruction` or under existing router) that accept a JSON body: `{ "action": string, "params": object }` (or schema agreed with CAIO).
- [x] Map `action` to existing orchestrator/Graph operations (e.g. create_team, add_channel, create_site).
- [x] Return structured response: `{ "ok": boolean, "result"?: object, "error"?: string, "trace_id"?: string }`.
- [x] All M365-changing calls remain gated by `ALLOW_M365_MUTATIONS` and use existing Graph client.
- [x] Audit log for each instruction (who, action, params, result, timestamp).

### Non-functional

- [x] Auth: API key or token validation for CAIO adapter calls (per security policy).
- [x] Idempotency: Where applicable, support idempotency key to avoid duplicate execution.
- [x] Validation: Reject unknown actions or invalid params before calling Graph.
- [x] Documentation: OpenAPI/Swagger or equivalent for the instruction API.

---

## Detailed tasks

1. **Define contract** — Document request/response schema for M365 instructions (action enum, params per action). Share with CAIO plan owner.
2. **Implement or extend router** — Add instruction endpoint(s) under `src/provisioning_api/routers/` (e.g. extend `m365.py` or add `instruction.py`). Wire to orchestrator and Graph client.
3. **Auth and gates** — Enforce auth for instruction endpoint; keep `ALLOW_M365_MUTATIONS` gate for any mutating call.
4. **Audit** — Log each instruction to existing audit mechanism (e.g. `provisioning_api/audit.py` or ops_adapter).
5. **Tests** — Unit tests for schema validation and routing; integration test (dry-run or with test tenant) for at least one action.
6. **Docs** — Update API docs and reference in master plan.

---

## Validation procedures

- Run `make test` (or equivalent) for M365 repo; all tests pass.
- Call instruction endpoint with a known action (e.g. read-only or create_team in test env); verify response shape and audit log.
- Security review: no credentials in logs; auth required.

---

## Success criteria

- [x] Instruction API is documented and implemented in M365 repo.
- [x] CAIO adapter can call it with intent-derived payload and receive a structured result.
- [x] All M365 mutations remain gated and audited.
- [x] Per-repo plan checklist and tests pass.

---

## Dependencies

- Master plan approved.
- CAIO repo plan (adapter) will depend on this API contract; coordinate schema before CAIO implementation.

---

## Status updates

- Update this plan with task checkboxes and status as work proceeds.
- Log completion in `Operations/ACTION_LOG.md` with plan reference `plan:tai-maia-caio-vfe-m365-integration:m365`.
