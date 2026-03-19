# MATHS Prompt: A1 Product Boundary and Positioning

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:A1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-A1-C0` -> `M365-READY-A1-C4` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Use this act prompt only if `A1` is explicitly reopened for revision.
- Final outputs exactly:
  - `GATE:M365-READY-A1 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-A1`
- Run ID: `a1-product-boundary-positioning`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R2`
  - `plan:m365-enterprise-readiness-master-plan:A1`

## Context

- Domain: `docs`
- Dependencies: `Operations/NORTHSTAR.md`, `docs/commercialization/m365-v1-supported-surface.md`, `docs/commercialization/m365-v1-positioning-and-north-star-delta.md`
- Allowlist:
  - `docs/commercialization/m365-v1-supported-surface.md`
  - `docs/commercialization/m365-v1-positioning-and-north-star-delta.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
- Denylist:
  - runtime source files

## M - Model

- Problem: the supported surface, non-goals, buyer, and operator boundary must remain explicit and fail-closed.
- Goal: preserve an honest standalone M365 v1 commercial boundary.
- Success criteria:
  - supported surface is explicit
  - non-goals are explicit
  - buyer, operator, and deployment model remain explicit

## H - Harness

- `M365-READY-A1-C0` verify plan refs and prerequisite status.
- `M365-READY-A1-C1` inventory current supported-surface and positioning docs.
- `M365-READY-A1-C2` verify supported and unsupported capability boundaries.
- `M365-READY-A1-C3` verify buyer, operator, and deployment language.
- `M365-READY-A1-C4` sync plan and tracker artifacts if the act is reopened.

## Validation

1. `rg -n "supported|non-goals|buyer|operator|deployment" docs/commercialization/m365-v1-supported-surface.md docs/commercialization/m365-v1-positioning-and-north-star-delta.md`
2. `git diff --check`

## No-Go Triggers

- supported-surface claims exceed the current proven module boundary
- buyer or operator boundary becomes ambiguous
- historical commercialization documents are treated as optional instead of authoritative for `A1`
