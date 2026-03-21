# M365 Persona Memory and Work History v1

## Purpose

Define the bounded, auditable memory and work-history contract for SMARTHAUS digital employees.

## Problem

`E5D` gave the workforce explicit ownership and escalation, but the runtime still lacked a bounded
way to preserve reusable context and replay recent work without relying on chat history or hidden
state. That meant a persona could hold work and accountability but still lose context between
delegations.

## Decision

`registry/persona_memory_work_history_v1.yaml` is now the authoritative memory/work-history
contract for the digital-employee runtime.

The shared runtime is `src/smarthaus_common/persona_memory.py`.

The same runtime now powers:

- dashboard memory and history projection in `src/provisioning_api/routers/agent_dashboard.py`
- governed persona memory and history projection in `src/ops_adapter/main.py`
- legacy-aligned persona memory and history projection in `src/ops_adapter/app.py`

## Memory Contract

Memory entries are immutable append-only records.

Every memory entry must include:

- memory type
- content
- visibility
- source
- actor who wrote it

Allowed memory types:

- `note`
- `fact`
- `decision`
- `handoff`
- `summary`

Allowed visibility levels:

- `internal`
- `manager`
- `approval_owner`

## Work History Contract

Work history is projected, not hand-edited.

The bounded work-history stream is composed from:

- created tasks
- task updates
- instructions
- memory entries

The stream is sorted deterministically in descending timestamp order and capped by the declared
history limit.

## Required Guarantees

- append-only memory writes
- bounded memory count per persona
- bounded history-event count per persona
- deterministic work-history projection from one shared queue runtime plus one memory store
- actor-attributed memory writes
- fail-closed rejection of unknown memory types, invalid visibility, invalid sources, or oversized content

## No-Go Conditions

- personas can write unbounded memory
- work history depends on chat context instead of explicit records
- dashboard and persona runtime disagree on history or memory counts
- memory writes bypass actor attribution
