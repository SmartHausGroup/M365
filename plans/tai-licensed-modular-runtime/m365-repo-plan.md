# Plan: M365 Repo — Embedded Connector Module for TAI Licensed Runtime

**Plan ID:** `m365-repo-plan` (parent: `tai-licensed-modular-runtime`)
**Status:** Completed (Implemented 2026-02-06)
**Date:** 2026-02-06
**Owner:** SmartHaus
**Master plan:** `plans/tai-licensed-modular-runtime/master-plan.md`
**Execution plan reference:** `plan:tai-licensed-modular-runtime:m365`
**North Star alignment:** `Operations/NORTHSTAR.md` — secure M365 orchestration, policy-gated mutations, auditability.

**MA process:** This plan is integration/module packaging and governance wiring. MA phases are not required unless algorithmic/math behavior is introduced.

---

## Objective

Define the M365 capability as a **TAI-loadable connector module** so M365 actions are available through the licensed modular runtime without requiring M365 as a separately managed standalone service in default deployments.

---

## Scope (M365 repo only)

- **In scope:**
  - M365 connector module contract (actions, params, result shape)
  - Module-facing execution entrypoint for instruction handling
  - Preserve auth, ALLOW_M365_MUTATIONS gate, idempotency, and audit requirements
  - Documentation for capability registration and entitlement needs
- **Out of scope:**
  - TAI host implementation
  - CAIO/MAIA/VFE internals
  - New intent or inference algorithms

---

## Requirements

### Functional

- [x] Define/confirm connector module interface for M365 execution (`m365.instruction.execute`).
- [x] Ensure request/response shape remains compatible with CAIO/TAI runtime (`action`, `params` -> `ok/result/error/trace_id`).
- [x] Preserve policy gates (`ALLOW_M365_MUTATIONS`) and caller auth expectations.
- [x] Preserve per-action audit logging and traceability fields.

### Non-functional

- [x] No secrets in module manifests or logs.
- [x] Backward-compatible contract behavior for existing voice->M365 path.
- [x] Documentation for entitlement and permission requirements (Graph scopes, mutation gates).

---

## Detailed Tasks

1. Define the M365 connector module capability contract and manifest inputs.
2. Expose/confirm module entrypoint that routes instruction calls to existing provisioning/orchestration functions.
3. Enforce auth + mutation gate + idempotency at module boundary.
4. Add tests for connector contract behavior under module-style invocation.
5. Document module contract and runtime integration assumptions.

---

## Validation

- Targeted endpoint/contract tests pass for module invocation shape.
- Mutation-gated behavior remains enforced.
- Audit records still include action, actor/context, outcome, timestamp, and trace data.

---

## Success Criteria

- [x] M365 capability is defined and documented as a TAI-loadable connector module.
- [x] Contract remains compatible with CAIO orchestration and TAI runtime expectations.
- [x] Security gates and auditability remain intact.

---

## Dependencies

- TAI core module host contract and entitlement model.
- CAIO core module invocation contract for `m365.instruction.execute`.

---

## Status Updates

- Log planning and completion in `Operations/ACTION_LOG.md` with `plan:tai-licensed-modular-runtime:m365`.
- Update `Operations/EXECUTION_PLAN.md` when status changes.
