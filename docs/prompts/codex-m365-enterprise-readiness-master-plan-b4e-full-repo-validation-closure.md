# MATHS Prompt: B4E Full Repo Validation Closure

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4E`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4E-C0` -> `M365-READY-B4E-C6` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-B4E STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B4E`
- Run ID: `b4e-full-repo-validation-closure`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:B4E`

## Context

- Domain: `test`
- Dependencies: `B4C`, `B4D`
- Allowlist:
  - repo root for validation commands
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
- Denylist:
  - tenant-impacting live-certification steps

## M - Model

- Problem: readiness cannot proceed while repo-wide validation is red.
- Goal: achieve one clean repo-wide validation run and record it as a hard gate.
- Success criteria:
  - `pre-commit run --all-files` passes
  - worktree remains clean after validation
  - trackers record green validation state

## H - Harness

- `M365-READY-B4E-C0` verify prerequisites and clean baseline.
- `M365-READY-B4E-C1` run repo-wide validation.
- `M365-READY-B4E-C2` verify no residual spillover remains in the worktree.
- `M365-READY-B4E-C3` confirm targeted remediation evidence from `B4C` and `B4D`.
- `M365-READY-B4E-C4` sync execution plan and action log with the green state.
- `M365-READY-B4E-C5` confirm `C1A` is now the next executable act.
- `M365-READY-B4E-C6` emit final gate and next-act state.

## Validation

1. `pre-commit run --all-files`
2. `git status --short`
3. `git diff --check`

## No-Go Triggers

- repo-wide validation is still red
- validation success requires ignoring residual worktree spillover
- the plan still points anywhere other than `C1A` after closure
