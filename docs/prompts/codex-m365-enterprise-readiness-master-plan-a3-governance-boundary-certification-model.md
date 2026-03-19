# MATHS Prompt: A3 Governance Boundary and Certification Model

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:A3`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-A3-C0` -> `M365-READY-A3-C4` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Use this act prompt only if `A3` is explicitly reopened for revision.
- Final outputs exactly:
  - `GATE:M365-READY-A3 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-A3`
- Run ID: `a3-governance-boundary-certification-model`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R2`
  - `plan:m365-enterprise-readiness-master-plan:A3`

## Context

- Domain: `docs`
- Dependencies:
  - `docs/commercialization/m365-audit-and-governance-evidence-model.md`
  - `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `docs/commercialization/m365-release-gates-and-certification.md`
- Allowlist:
  - `docs/commercialization/m365-audit-and-governance-evidence-model.md`
  - `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `docs/commercialization/m365-release-gates-and-certification.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
- Denylist:
  - runtime source files

## M - Model

- Problem: governance, audit, approval, and certification rules must remain explicit and fail-closed.
- Goal: preserve the evidence and certification contract the runtime must satisfy.
- Success criteria:
  - audit boundary is explicit
  - fail-closed and approval requirements remain explicit
  - live-certification and release-gate rules remain explicit

## H - Harness

- `M365-READY-A3-C0` verify plan refs and prerequisite status.
- `M365-READY-A3-C1` inventory current governance and certification docs.
- `M365-READY-A3-C2` verify audit, approval, and fail-closed boundaries.
- `M365-READY-A3-C3` verify live-validation and release-gate rules.
- `M365-READY-A3-C4` sync plan and tracker artifacts if the act is reopened.

## Validation

1. `rg -n "audit|approval|fail-closed|live|release|GO|NO-GO" docs/commercialization/m365-audit-and-governance-evidence-model.md docs/commercialization/m365-permission-approval-fail-closed-hardening.md docs/commercialization/m365-live-tenant-validation-matrix.md docs/commercialization/m365-release-gates-and-certification.md`
2. `git diff --check`

## No-Go Triggers

- governance boundary becomes weaker than runtime claims
- certification criteria become ambiguous
- live evidence is implied when only mock evidence exists
