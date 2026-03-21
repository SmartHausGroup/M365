# MATHS Prompt: A4 Packaging and Operator Model

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:A4`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-A4-C0` -> `M365-READY-A4-C4` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Use this act prompt only if `A4` is explicitly reopened for revision.
- Final outputs exactly:
  - `GATE:M365-READY-A4 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-A4`
- Run ID: `a4-packaging-operator-model`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R2`
  - `plan:m365-enterprise-readiness-master-plan:A4`

## Context

- Domain: `docs`
- Dependencies:
  - `docs/commercialization/m365-packaging-install-bootstrap.md`
  - `docs/commercialization/m365-operator-onboarding-and-support-boundary.md`
- Allowlist:
  - `docs/commercialization/m365-packaging-install-bootstrap.md`
  - `docs/commercialization/m365-operator-onboarding-and-support-boundary.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
- Denylist:
  - runtime source files

## M - Model

- Problem: the canonical install path, onboarding model, and support boundary must remain explicit.
- Goal: preserve one operator-facing path and support model for standalone M365 v1.
- Success criteria:
  - canonical install/bootstrap path is explicit
  - operator runbooks remain explicit
  - support boundary and ownership matrix remain explicit

## H - Harness

- `M365-READY-A4-C0` verify plan refs and prerequisite status.
- `M365-READY-A4-C1` inventory packaging and operator-model docs.
- `M365-READY-A4-C2` verify canonical install and bootstrap path.
- `M365-READY-A4-C3` verify onboarding, runbooks, and support-boundary language.
- `M365-READY-A4-C4` sync plan and tracker artifacts if the act is reopened.

## Validation

1. `rg -n "install|bootstrap|operator|runbook|support|ownership" docs/commercialization/m365-packaging-install-bootstrap.md docs/commercialization/m365-operator-onboarding-and-support-boundary.md`
2. `git diff --check`

## No-Go Triggers

- multiple canonical packaging paths appear
- support boundary becomes ambiguous
- operator model diverges from the documented standalone runtime
