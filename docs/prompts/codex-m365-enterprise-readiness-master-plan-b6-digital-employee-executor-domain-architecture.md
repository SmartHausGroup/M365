# MATHS Prompt: B6 Digital Employee and Executor-Domain Architecture

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B6`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B6-C0` -> `M365-READY-B6-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-B6 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B6`
- Run ID: `b6-digital-employee-executor-domain-architecture`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R8`
  - `plan:m365-enterprise-readiness-master-plan:R10`
  - `plan:m365-enterprise-readiness-master-plan:B6`

## Context

- Domain: `docs`
- Dependencies: `B5E`
- Goal: lock the SMARTHAUS digital-employee operating model, bounded executor-domain architecture, and certification rebase before any new certification attempt.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `docs/commercialization/m365-digital-employee-operating-model.md`
  - `docs/commercialization/m365-capability-api-license-auth-matrix.md`
  - `docs/commercialization/m365-executor-domain-routing-and-minimum-permission-model.md`
  - `docs/commercialization/m365-persona-registry-and-humanized-delegation-contract.md`
  - `docs/commercialization/m365-certification-rebase-digital-employee-multi-executor-model.md`
  - `docs/prompts/*b6*`
- Denylist:
  - runtime implementation
  - live tenant execution
  - Azure permission mutation

## M - Model

- Problem: the operator-facing product intent is digital employees, but the legacy certification target still assumes a single giant executor posture.
- Success criteria:
  - named digital employees are the primary delegation surface
  - bounded executor domains replace the legacy single-executor architecture
  - certification is explicitly rebased away from the old target

## H - Harness

- `M365-READY-B6-C0` verify `B5E` closure and current `C1A` blockage state.
- `M365-READY-B6-C1` define the digital-employee operating model.
- `M365-READY-B6-C2` define the capability, API, license, and auth matrix.
- `M365-READY-B6-C3` define the executor-domain and minimum-permission model.
- `M365-READY-B6-C4` define the persona-registry and humanized delegation contract.
- `M365-READY-B6-C5` rebase certification to the digital-employee multi-executor target.
- `M365-READY-B6-C6` sync the plan, prompts, and trackers.
- `M365-READY-B6-C7` emit final gate and next-act state.

## Validation

1. `rg -n "digital employee|executor-domain|persona registry|certification rebase|B6|B7" docs plans Operations`
2. `git diff --check`

## No-Go Triggers

- digital employees are treated as raw Microsoft executor identities
- the bounded executor-domain split is not explicit
- `C1A` still points at the legacy single-executor certification target
