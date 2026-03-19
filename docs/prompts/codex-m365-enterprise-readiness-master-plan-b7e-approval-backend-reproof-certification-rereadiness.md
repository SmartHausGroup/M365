# MATHS Prompt: B7E Approval Backend Reproof and Certification Re-Readiness

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B7E`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B7E-C0` -> `M365-READY-B7E-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B7E`
- Run ID: `b7e-approval-backend-reproof-certification-rereadiness`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R11`
  - `plan:m365-enterprise-readiness-master-plan:B7E`

## Context

- Domain: `code`
- Goal: re-prove approval reachability through the bounded SharePoint executor path and reopen `C1A` only on the rebased multi-executor runtime.

## M - Model

- Success criteria:
  - approval backend is reachable through the SharePoint executor path
  - C1A packet is refreshed against the rebased target
  - the final pre-certification `GO/NO-GO` is explicit

## H - Harness

- `M365-READY-B7E-C0` verify dependency state.
- `M365-READY-B7E-C1` validate approval backend reachability.
- `M365-READY-B7E-C2` refresh certification packet inputs.
- `M365-READY-B7E-C3` refresh exact-shell contract proof.
- `M365-READY-B7E-C4` sync plan and tracker state.
- `M365-READY-B7E-C5` validate readiness results.
- `M365-READY-B7E-C6` emit final gate and C1A status.

## Validation

1. `rg -n "approval backend|SharePoint executor|C1A|NO-GO|GO" artifacts/certification docs plans Operations`
2. `git diff --check`

## No-Go Triggers

- approval backend is still only reachable through delegated or legacy single-executor paths
- C1A is reopened without the rebased runtime proof
