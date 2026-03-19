# MATHS Prompt: C1C Live Mutation and Governance Certification

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:C1C`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-C1C-C0` -> `M365-READY-C1C-C6` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Execute controlled mutation and governance checks only in the approved live window.
- Final outputs exactly:
  - `GATE:M365-READY-C1C STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-C1C`
- Run ID: `c1c-live-mutation-governance-certification`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R6`
  - `plan:m365-enterprise-readiness-master-plan:C1C`

## Context

- Domain: `test`
- Dependencies: `C1A`, `C1B`
- Allowlist:
  - `artifacts/certification/m365-v1-candidate-52ca494/*`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `docs/commercialization/m365-release-gates-and-certification.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
- Denylist:
  - unapproved live execution outside the certification window

## M - Model

- Problem: mutation, approval, audit, and fail-closed behaviors still lack live enterprise evidence.
- Goal: execute the controlled write-path and governance checks in the approved non-production window.
- Success criteria:
  - required mutation rows are executed
  - approval and audit evidence is retained
  - governance checks are classified pass/fail/blocked

## H - Harness

- `M365-READY-C1C-C0` verify `C1A`, `C1B`, and live approval state.
- `M365-READY-C1C-C1` inventory required mutation and governance rows.
- `M365-READY-C1C-C2` execute controlled mutation checks.
- `M365-READY-C1C-C3` execute approval, audit, and fail-closed checks.
- `M365-READY-C1C-C4` persist transcripts and classify results.
- `M365-READY-C1C-C5` sync evidence packet and trackers.
- `M365-READY-C1C-C6` emit final gate and next-act state.

## Validation

1. `rg -n "mutation|approval|audit|fail-closed" docs/commercialization/m365-live-tenant-validation-matrix.md docs/commercialization/m365-release-gates-and-certification.md`
2. `git diff --check`

## No-Go Triggers

- `C1A` or `C1B` is not green
- approval or audit evidence is missing for a required row
- live mutation checks are attempted without explicit approval
