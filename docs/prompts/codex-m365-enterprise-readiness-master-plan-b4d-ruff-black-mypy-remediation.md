# MATHS Prompt: B4D Ruff/Black/Mypy Remediation Overview

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:R5`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Use this prompt only as the coordination overview for `B4D1` through `B4D5`.
- Execute subacts in strict order: `B4D1` -> `B4D2` -> `B4D3` -> `B4D4` -> `B4D5`.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-B4D STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B4D-OVERVIEW`
- Run ID: `b4d-ruff-black-mypy-remediation-overview`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:B4D1`
  - `plan:m365-enterprise-readiness-master-plan:B4D2`
  - `plan:m365-enterprise-readiness-master-plan:B4D3`
  - `plan:m365-enterprise-readiness-master-plan:B4D4`
  - `plan:m365-enterprise-readiness-master-plan:B4D5`

## Context

- Domain: `code`
- Dependencies: `B4C`
- Allowlist:
  - `scripts/**`
  - `src/**`
  - `tests/**`
  - `governance/invariants/**`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
- Denylist:
  - tenant-impacting live-certification artifacts

## M - Model

- Problem: repo-wide Ruff, Black, and Mypy debt prevents governed clean validation, and the act is too large to execute as one opaque step.
- Goal: coordinate the bounded `B4D1` through `B4D5` sequence after `B4C`.
- Success criteria:
  - Ruff issues are resolved or explicitly removed through approved structural fixes
  - Black runs cleanly
  - Mypy missing-stub and duplicate-module issues are resolved for the governed path

## H - Harness

- `B4D1` spillover reset and failure inventory pin
- `B4D2` scripts and CI Ruff cleanup
- `B4D3` runtime and CLI Ruff/Black cleanup
- `B4D4` Mypy stub and module-path remediation
- `B4D5` targeted validation closure and handoff to `B4E`

## Validation

1. use the act-specific validation commands from `B4D1` through `B4D5`
2. do not use this overview prompt as the execution surface for direct edits

## No-Go Triggers

- any subact proceeds out of order
- spillover from repo-wide hooks is mixed into remediation without explicit reset
- changes drift outside the validation-debt scope
