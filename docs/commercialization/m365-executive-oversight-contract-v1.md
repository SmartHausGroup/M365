# M365 Executive Oversight Contract v1

## Purpose

Give executives visibility and intervention controls across the workforce runtime by
defining oversight queries, intervention primitives, escalation paths, and audit
visibility so that the workforce can be monitored, paused, redirected, or overridden
through governed channels.

## Problem

Sections E7A through E7D define delegation, discovery, orchestration, and collaboration.
But no contract defines how executives observe and intervene in workforce operations.
Without this contract, executive oversight is ad-hoc and cannot be governed or audited.

## Decision

`registry/executive_oversight_contract_v1.yaml` is now the authoritative executive
oversight and intervention controls contract.

## Oversight Queries

1. **Workforce Status** — global state across all departments and personas
2. **Department Status** — specific department state with persona details
3. **Persona Status** — specific persona state with tasks and history
4. **Delegation Audit** — audit trail with flexible filtering
5. **Risk Summary** — current risk exposure and escalation state

## Intervention Primitives

1. **Pause Persona** — stop new tasks, complete in-progress (reversible)
2. **Pause Department** — stop all department activity (reversible)
3. **Redirect Task** — move task to another persona (irreversible)
4. **Override Decision** — override completed action result (irreversible)
5. **Emergency Halt** — halt all workforce activity (dual approval)

## Required Guarantees

- every workforce state queryable through oversight queries
- per-intervention audit envelopes with authority and justification
- explicit approval for every intervention
- escalation follows declared hierarchy
- no silent or unlinked overrides

## No-Go Conditions

- workforce state hidden from executive oversight
- an intervention produces no audit envelope
- an intervention proceeds without required approval
- an override is not linked to the original action
