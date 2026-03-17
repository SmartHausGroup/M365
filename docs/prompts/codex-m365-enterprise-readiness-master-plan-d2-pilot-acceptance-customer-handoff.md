# MATHS Prompt: D2 Pilot Acceptance and Customer Handoff

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:D2`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-D2-C0` -> `M365-READY-D2-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-READY-D2 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-D2`
- Run ID: `d2-pilot-acceptance-customer-handoff`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R6`
  - `plan:m365-enterprise-readiness-master-plan:D2`
- Owners: `operations`, `product`, `customer-success`

## Context

- Domain: `docs`
- Dependency: `D1`
- Goal: define how SmartHaus and the customer complete pilot acceptance and transfer operating ownership.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/*`
- Denylist:
  - `src/**`
  - `docs/prompts/**`

## M - Model

- Problem: enterprise readiness is incomplete until success criteria and ownership transfer are explicit.
- Success criteria:
  - pilot acceptance checklist exists
  - handoff checklist exists
  - responsibility matrix and sign-off model exist

## H - Harness

- `C0` confirm certified surface and collateral baseline.
- `C1` draft pilot acceptance checklist and success criteria.
- `C2` draft customer handoff checklist.
- `C3` draft customer-responsibility matrix and sign-off model.
- `C4` verify the handoff model matches the operator/support boundary from `A4`.
- `C5` verify pilot success criteria do not exceed the certified surface.
- `C6` run strict document validation.
- `C7` run `git diff --check`.
- `C8` sync plan and log.
- `C9` record residual handoff risks.
- `C10` final gate decision.

## Validation

1. pilot and handoff docs align with the certified supported surface and operator model
2. `rg -n "support boundary|ownership matrix|pilot|handoff|sign-off" docs/commercialization`
3. `git diff --check`

## No-Go Triggers

- customer responsibilities conflict with the operator/support boundary
- pilot success criteria exceed the certified product state
- sign-off model is missing or ambiguous
