# MATHS Prompt: B4D3 Runtime, CLI, and Notebook Ruff/Black Cleanup

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4D3`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4D3-C0` -> `M365-READY-B4D3-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B4D3`
- Run ID: `b4d3-runtime-cli-ruff-black-cleanup`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:B4D3`

## Context

- Domain: `code`
- Dependencies: `B4D1`
- Goal: close the remaining runtime and CLI Ruff debt and stabilize formatting on the governed execution path, including the notebook-backed validation surface that still fails formatter checks.

## Validation

1. `ruff check <touched runtime, CLI, and notebook files>`
2. `black --check <touched runtime, CLI, and notebook files>` or approved equivalent
3. `git diff --check`

## No-Go Triggers

- changes alter supported product behavior instead of lint/format compliance
- formatter churn is mixed with unrelated repo-wide spillover
