# MATHS Prompt: B4D1 Spillover Reset and Failure Inventory Pin

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4D1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4D1-C0` -> `M365-READY-B4D1-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B4D1`
- Run ID: `b4d1-spillover-reset-failure-inventory`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:B4D1`

## Context

- Domain: `governance`
- Dependencies: `B4C`
- Goal: restore the worktree to the approved post-`B4C` baseline and pin the remaining validation inventory.

## H - Harness

- `M365-READY-B4D1-C0` capture current tracked spillover from the latest repo-wide baseline run.
- `M365-READY-B4D1-C1` preserve approved governance and `B4C` artifacts.
- `M365-READY-B4D1-C2` revert unrelated hook spillover.
- `M365-READY-B4D1-C3` write a pinned failure-inventory artifact for `B4D2` through `B4D4`.
- `M365-READY-B4D1-C4` verify no approved artifacts were lost.
- `M365-READY-B4D1-C5` sync plan and tracker state.
- `M365-READY-B4D1-C6` validate diff hygiene.
- `M365-READY-B4D1-C7` declare `B4D2` next.

## Validation

1. `git status --short`
2. `git diff --name-only`
3. `git diff --check`

## No-Go Triggers

- approved `B4C` or governance artifacts are lost during reset
- spillover reset leaves unrelated formatter churn in the worktree
- failure inventory is not pinned for downstream subacts
