# MATHS Prompt: B7C Persona Registry and Humanized Delegation Integration

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B7C`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B7C-C0` -> `M365-READY-B7C-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B7C`
- Run ID: `b7c-persona-registry-humanized-delegation-integration`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R11`
  - `plan:m365-enterprise-readiness-master-plan:B7C`

## Context

- Domain: `code`
- Goal: bind named digital employees into the runtime delegation surface without exposing raw agent mechanics.

## M - Model

- Success criteria:
  - named personas resolve deterministically at runtime
  - persona responsibilities and allowed domains are enforced
  - audit and approval semantics retain human requester plus persona context

## H - Harness

- `M365-READY-B7C-C0` verify dependency state.
- `M365-READY-B7C-C1` implement persona registry loading.
- `M365-READY-B7C-C2` implement delegation resolution.
- `M365-READY-B7C-C3` bind persona policy and audit context.
- `M365-READY-B7C-C4` add bounded tests.
- `M365-READY-B7C-C5` sync docs and trackers.
- `M365-READY-B7C-C6` validate and emit gate.

## Validation

1. `rg -n "persona|digital employee|delegation|requester|executor domain" src tests`
2. `git diff --check`

## No-Go Triggers

- persona resolution stays docs-only
- runtime audit omits persona context
