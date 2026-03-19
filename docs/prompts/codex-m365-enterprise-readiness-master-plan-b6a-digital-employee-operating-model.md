# MATHS Prompt: B6A Digital Employee Operating Model

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B6A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B6A-C0` -> `M365-READY-B6A-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B6A`
- Run ID: `b6a-digital-employee-operating-model`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R10`
  - `plan:m365-enterprise-readiness-master-plan:B6A`

## Context

- Domain: `docs`
- Goal: define the named digital-employee layer that humanizes delegation without weakening policy, approval, or audit boundaries.

## M - Model

- Problem: operators should delegate to named digital employees, not to raw agent or app identities.
- Success criteria:
  - persona identity is distinct from human requester identity and executor identity
  - the minimum persona contract is explicit
  - KPI, escalation, approval posture, and audit semantics are named

## H - Harness

- `M365-READY-B6A-C0` verify dependency state.
- `M365-READY-B6A-C1` define persona fields.
- `M365-READY-B6A-C2` define delegation semantics.
- `M365-READY-B6A-C3` define KPI and escalation semantics.
- `M365-READY-B6A-C4` define approval and audit posture.
- `M365-READY-B6A-C5` sync plan and prompt state.
- `M365-READY-B6A-C6` validate and emit gate.

## Validation

1. `rg -n "digital employee|persona|escalation|KPI|approval posture" docs/commercialization`
2. `git diff --check`

## No-Go Triggers

- persona identity and executor identity are conflated
- delegation semantics still expose raw agent mechanics
