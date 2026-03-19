# MATHS Prompt: C1D Evidence Packet and Matrix Closure

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:C1D`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-C1D-C0` -> `M365-READY-C1D-C6` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-C1D STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-C1D`
- Run ID: `c1d-evidence-packet-matrix-closure`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R6`
  - `plan:m365-enterprise-readiness-master-plan:C1D`

## Context

- Domain: `governance`
- Dependencies: `C1B`, `C1C`
- Allowlist:
  - `artifacts/certification/m365-v1-candidate-52ca494/*`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `docs/commercialization/m365-release-gates-and-certification.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
- Denylist:
  - new live execution

## M - Model

- Problem: live evidence must be turned into one complete, reviewable packet before release certification can start.
- Goal: close the evidence packet and map all required rows to explicit statuses.
- Success criteria:
  - evidence index is complete
  - validation matrix reflects live outcomes
  - residual blockers are explicit

## H - Harness

- `M365-READY-C1D-C0` verify `C1B` and `C1C` completion state.
- `M365-READY-C1D-C1` inventory all produced transcripts and notes.
- `M365-READY-C1D-C2` update the evidence index and packet contents.
- `M365-READY-C1D-C3` map every required row to pass/fail/blocked.
- `M365-READY-C1D-C4` verify packet completeness and residual blockers.
- `M365-READY-C1D-C5` sync plan and tracker artifacts.
- `M365-READY-C1D-C6` emit final gate and next-act state.

## Validation

1. `rg -n "status|pending|blocked|pass|fail" artifacts/certification/m365-v1-candidate-52ca494/evidence_index.json artifacts/certification/m365-v1-candidate-52ca494/prerequisites_report.json docs/commercialization/m365-live-tenant-validation-matrix.md`
2. `git diff --check`

## No-Go Triggers

- evidence packet remains incomplete
- validation matrix still has ambiguous required rows
- `C2` is advanced without explicit `C1D` closure
