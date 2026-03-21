# MATHS Prompt: D1 Enterprise Collateral Pack

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:D1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-D1-C0` -> `M365-READY-D1-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Do not use collateral to overclaim scope or readiness.
- Final outputs:
  - `GATE:M365-READY-D1 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-D1`
- Run ID: `d1-enterprise-collateral-pack`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R6`
  - `plan:m365-enterprise-readiness-master-plan:D1`
- Owners: `product`, `operations`, `security`

## Context

- Domain: `docs`
- Dependency: `C2`
- Goal: produce buyer-facing and delivery-facing collateral that matches the actual certified product state.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/*`
  - `docs/TAI_LICENSED_MODULE_MODEL.md`
- Denylist:
  - `src/**`
  - `docs/prompts/**`

## M - Model

- Problem: collateral is dangerous if it outruns runtime and certification truth.
- Success criteria:
  - product one-pager exists
  - security/compliance brief exists
  - supported-action matrix for sales/delivery exists
  - architecture/operating summary exists

## H - Harness

- `C0` confirm certification state from `C2`.
- `C1` draft the product one-pager.
- `C2` draft the security/compliance posture brief.
- `C3` draft the supported-action matrix for sales and delivery.
- `C4` draft the architecture and operating summary.
- `C5` verify all collateral stays within the certified surface and current operator model.
- `C6` run strict document validation.
- `C7` run `git diff --check`.
- `C8` sync plan and log.
- `C9` record residual commercial risks.
- `C10` final gate decision.

## Validation

1. collateral references the 9-action supported boundary and current certification state
2. `rg -n "9|supported|operator|certification|approval" docs/commercialization`
3. `git diff --check`

## No-Go Triggers

- collateral overclaims unsupported actions or uncertified behavior
- collateral conflicts with operator/runbook or release-gate documents
