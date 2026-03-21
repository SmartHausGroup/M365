# MATHS Prompt: B6D Persona Registry and Humanized Delegation Routing

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B6D`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B6D-C0` -> `M365-READY-B6D-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B6D`
- Run ID: `b6d-persona-registry-humanized-delegation-routing`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R10`
  - `plan:m365-enterprise-readiness-master-plan:B6D`

## Context

- Domain: `docs`
- Goal: define how named digital employees map to responsibilities, approval posture, executor domains, and audit semantics.

## M - Model

- Problem: humanized delegation needs a deterministic registry contract behind it.
- Success criteria:
  - named personas resolve deterministically
  - allowed domains and responsibility sets are explicit
  - audit captures human requester, persona, and executor domain

## H - Harness

- `M365-READY-B6D-C0` verify dependency state.
- `M365-READY-B6D-C1` define persona-registry fields.
- `M365-READY-B6D-C2` define delegation resolution.
- `M365-READY-B6D-C3` define approval and escalation bindings.
- `M365-READY-B6D-C4` define audit semantics.
- `M365-READY-B6D-C5` sync plan and prompt state.
- `M365-READY-B6D-C6` validate and emit gate.

## Validation

1. `rg -n "Elena Rodriguez|persona registry|delegation|executor domain|audit" docs/commercialization/m365-persona-registry-and-humanized-delegation-contract.md`
2. `git diff --check`

## No-Go Triggers

- persona resolution remains ambiguous
- audit omits either the human requester or the resolved persona
