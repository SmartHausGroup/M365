# MATHS Prompt: C1B Live Read-Only Certification

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:C1B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-C1B-C0` -> `M365-READY-C1B-C6` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Execute read-only live checks only.
- Final outputs exactly:
  - `GATE:M365-READY-C1B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-C1B`
- Run ID: `c1b-live-read-only-certification`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R6`
  - `plan:m365-enterprise-readiness-master-plan:C1B`

## Context

- Domain: `test`
- Dependencies: `C1A`
- Allowlist:
  - `artifacts/certification/m365-v1-candidate-52ca494/*`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `configs/generated/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
- Denylist:
  - controlled mutation checks

## M - Model

- Problem: the supported read-only surface still lacks live tenant evidence.
- Goal: execute and record live read-only validation in the approved non-production tenant.
- Success criteria:
  - all required read-only checks are executed
  - transcripts are retained
  - results are classified pass/fail/blocked

## H - Harness

- `M365-READY-C1B-C0` verify `C1A` green and live approval state.
- `M365-READY-C1B-C1` inventory required read-only rows from the validation matrix.
- `M365-READY-C1B-C2` execute live read-only checks.
- `M365-READY-C1B-C3` persist transcripts and operator notes.
- `M365-READY-C1B-C4` classify each row as pass/fail/blocked.
- `M365-READY-C1B-C5` sync evidence packet and trackers.
- `M365-READY-C1B-C6` emit final gate and next-act state.

## Validation

1. `rg -n "read-only|list_|get_" docs/commercialization/m365-live-tenant-validation-matrix.md`
2. `git diff --check`

## No-Go Triggers

- `C1A` is not green
- a required read-only row lacks live evidence after execution
- mutation work is attempted inside this act
