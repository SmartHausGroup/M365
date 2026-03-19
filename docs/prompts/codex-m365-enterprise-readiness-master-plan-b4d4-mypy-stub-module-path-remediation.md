# MATHS Prompt: B4D4 Mypy Stub and Module-Path Remediation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4D4`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4D4-C0` -> `M365-READY-B4D4-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B4D4`
- Run ID: `b4d4-mypy-stub-module-path-remediation`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:B4D4`

## Context

- Domain: `code`
- Dependencies: `B4D1`
- Goal: resolve the current Mypy stub and duplicate-module blockers without weakening type checking.

## Validation

1. `mypy <approved governed module set>`
2. `git diff --check`

## No-Go Triggers

- type checking is weakened globally just to silence errors
- duplicate-module state for `src/ops_adapter/actions.py` remains unresolved
