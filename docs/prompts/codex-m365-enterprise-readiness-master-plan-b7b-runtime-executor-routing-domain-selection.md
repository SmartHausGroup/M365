# MATHS Prompt: B7B Runtime Executor Routing and Domain Selection

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B7B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B7B-C0` -> `M365-READY-B7B-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B7B`
- Run ID: `b7b-runtime-executor-routing-domain-selection`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R11`
  - `plan:m365-enterprise-readiness-master-plan:B7B`

## Context

- Domain: `code`
- Goal: route governed actions through the correct bounded executor domain.

## M - Model

- Success criteria:
  - routing is deterministic
  - fail-closed behavior is explicit for unknown or disallowed routes
  - actor-based approval and audit semantics are preserved

## H - Harness

- `M365-READY-B7B-C0` verify dependency state.
- `M365-READY-B7B-C1` define action-to-domain mapping.
- `M365-READY-B7B-C2` implement executor selection.
- `M365-READY-B7B-C3` preserve approval and audit bindings.
- `M365-READY-B7B-C4` add bounded tests.
- `M365-READY-B7B-C5` sync docs and trackers.
- `M365-READY-B7B-C6` validate and emit gate.

## Validation

1. `rg -n "executor routing|domain selection|unknown route|fail-closed" src tests`
2. `git diff --check`

## No-Go Triggers

- routing remains implicit or action-local
- unknown routes do not fail closed
