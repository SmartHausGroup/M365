# MATHS Prompt: B6C Executor-Domain Partitioning and Minimum-Permission Model

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B6C`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B6C-C0` -> `M365-READY-B6C-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B6C`
- Run ID: `b6c-executor-domain-partitioning-minimum-permissions`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R10`
  - `plan:m365-enterprise-readiness-master-plan:B6C`

## Context

- Domain: `docs`
- Goal: replace the single giant executor posture with a bounded domain split and minimum-permission envelopes.

## M - Model

- Problem: the current executor posture is too broad to be a stable certification target.
- Success criteria:
  - executor domains are bounded and named
  - minimum-permission posture is explicit
  - persona identity is not turned into executor sprawl

## H - Harness

- `M365-READY-B6C-C0` verify dependency state.
- `M365-READY-B6C-C1` define executor domains.
- `M365-READY-B6C-C2` define minimum-permission envelopes.
- `M365-READY-B6C-C3` define routing assumptions.
- `M365-READY-B6C-C4` define non-goals and complexity boundaries.
- `M365-READY-B6C-C5` sync plan and prompt state.
- `M365-READY-B6C-C6` validate and emit gate.

## Validation

1. `rg -n "SharePoint|collaboration|messaging|directory|analytics|minim" docs/commercialization/m365-executor-domain-routing-and-minimum-permission-model.md`
2. `git diff --check`

## No-Go Triggers

- one giant executor remains the recommended production model
- one executor app per persona is implied
