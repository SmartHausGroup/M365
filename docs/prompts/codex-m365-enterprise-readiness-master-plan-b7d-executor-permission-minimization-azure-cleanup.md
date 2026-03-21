# MATHS Prompt: B7D Executor Permission Minimization and Azure Cleanup

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B7D`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B7D-C0` -> `M365-READY-B7D-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B7D`
- Run ID: `b7d-executor-permission-minimization-azure-cleanup`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R11`
  - `plan:m365-enterprise-readiness-master-plan:B7D`

## Context

- Domain: `code`
- Goal: reduce each bounded executor domain to the minimum permission envelope required for its supported surface.

## M - Model

- Success criteria:
  - each executor domain has a bounded permission envelope
  - Azure cleanup is explicit and deterministic
  - oversized executor tokens are no longer the production norm

## H - Harness

- `M365-READY-B7D-C0` verify dependency state.
- `M365-READY-B7D-C1` derive per-domain permission envelopes.
- `M365-READY-B7D-C2` apply Azure cleanup.
- `M365-READY-B7D-C3` validate bounded app-only access.
- `M365-READY-B7D-C4` add or refresh evidence artifacts.
- `M365-READY-B7D-C5` sync docs and trackers.
- `M365-READY-B7D-C6` validate and emit gate.

## Validation

1. `rg -n "permission matrix|minim|executor app|roleCount|SharePoint executor" docs src`
2. `git diff --check`

## No-Go Triggers

- executor permissions remain effectively god-mode
- per-domain permission envelopes are not explicit
