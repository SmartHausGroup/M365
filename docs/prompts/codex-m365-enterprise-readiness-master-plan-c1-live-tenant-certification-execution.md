# MATHS Prompt: C1 Live-Tenant Certification Execution

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:C1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-C1-C0` -> `M365-READY-C1-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Do not execute any tenant-impacting step without explicit approval for live validation.
- Final outputs:
  - `GATE:M365-READY-C1 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-C1`
- Run ID: `c1-live-tenant-certification-execution`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:C1`
- Owners: `operations`, `security`, `engineering`

## Context

- Domain: `test`
- Dependency: `B1`, `B2`, `B3`
- Goal: execute the supported v1 validation matrix in a controlled non-production tenant.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `docs/commercialization/m365-release-gates-and-certification.md`
  - `configs/generated/*`
  - `artifacts/scorecards/*`
  - `docs/commercialization/*`
- Denylist:
  - `docs/prompts/**`

## M - Model

- Problem: enterprise claims remain red until live-tenant evidence exists.
- Success criteria:
  - all required supported-surface live checks are executed in a non-production tenant
  - evidence packet is complete and traceable
  - failed checks are explicit and block certification

## H - Harness

- `C0` confirm explicit approval for live-tenant execution.
- `C1` confirm prerequisites from the validation matrix.
- `C2` execute read-only supported-surface checks.
- `C3` execute controlled write-path checks in the approved non-production window.
- `C4` execute governance, approval, audit, and mutation-gate checks.
- `C5` collect evidence artifacts and operator notes.
- `C6` classify each required validation row as pass/fail/blocked.
- `C7` update generated evidence artifacts or packet indexes.
- `C8` run strict evidence completeness checks.
- `C9` sync plan and log.
- `C10` final gate decision.

## Validation

1. Evidence packet matches the rows in `docs/commercialization/m365-live-tenant-validation-matrix.md`
2. `rg -n "Live required|supported actions|approval|audit" docs/commercialization/m365-live-tenant-validation-matrix.md`
3. `git diff --check`

## No-Go Triggers

- live work is attempted without explicit approval
- evidence packet is incomplete for any required supported-surface row
- certification-critical checks fail or remain ambiguous
