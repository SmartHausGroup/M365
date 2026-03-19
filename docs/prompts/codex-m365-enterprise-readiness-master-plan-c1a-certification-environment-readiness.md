# MATHS Prompt: C1A Certification Environment Readiness

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:C1A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-C1A-C0` -> `M365-READY-C1A-C6` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Do not execute any live tenant-impacting check without explicit live approval.
- Final outputs exactly:
  - `GATE:M365-READY-C1A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-C1A`
- Run ID: `c1a-certification-environment-readiness`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R9`
  - `plan:m365-enterprise-readiness-master-plan:R6`
  - `plan:m365-enterprise-readiness-master-plan:C1A`

## Context

- Domain: `test`
- Dependencies: `B4E`, `B5E`, `artifacts/certification/m365-v1-candidate-52ca494/*`
- Scope note: standalone M365 certification only; CAIO and instruction-API operator inputs are out of scope for this act.
- Allowlist:
  - `artifacts/certification/m365-v1-candidate-52ca494/*`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
- Denylist:
  - direct live mutation execution

## M - Model

- Problem: live certification cannot begin until both the production identity architecture and the environment and operator prerequisites are satisfied.
- Goal: prove or deny readiness to start live certification.
- Success criteria:
  - all required environment prerequisites are present
  - operator checklist is complete
  - readiness is classified explicitly as `GO` or `NO-GO`
  - approval-path readiness resolves through the selected tenant contract for standalone M365

## H - Harness

- `M365-READY-C1A-C0` verify `B4E` and `B5E` completion and approval state.
- `M365-READY-C1A-C1` inventory current prerequisite report and operator checklist.
- `M365-READY-C1A-C2` probe environment readiness without exposing secrets, preferring tenant-contract approval-path resolution over shell-only approval inputs.
- `M365-READY-C1A-C3` classify missing prerequisites by blocking impact.
- `M365-READY-C1A-C4` update the certification packet readiness state.
- `M365-READY-C1A-C5` sync plan and tracker artifacts.
- `M365-READY-C1A-C6` emit final gate and next-act state.

## Validation

1. `rg -n "UCP_TENANT|ALLOW_M365_MUTATIONS|ENABLE_AUDIT_LOGGING|APPROVALS|NO-GO|GATE" artifacts/certification/m365-v1-candidate-52ca494/*`
2. `git diff --check`

## No-Go Triggers

- `B4E` is not green
- `B5E` is not complete
- required certification prerequisites remain missing
- live checks are attempted before readiness is explicitly green
