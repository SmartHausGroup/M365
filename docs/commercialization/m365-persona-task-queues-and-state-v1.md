# M365 Persona Task Queues and State v1

## Purpose

Define the deterministic task-queue and lifecycle contract for SMARTHAUS digital employees.

## Problem

The repo already had task and instruction collections in the dashboard router, but they were not a
real queue runtime. Task creation stored one record, task updates only appended log events, and
persona state could not be derived deterministically from the stored history.

## Decision

`registry/persona_task_queue_state_v1.yaml` is now the authoritative queue/state contract for the
digital-employee runtime.

The shared runtime is `src/smarthaus_common/persona_task_queue.py`.

The same runtime now powers:

- the existing dashboard task surface in `src/provisioning_api/routers/agent_dashboard.py`
- the humanized persona task/state surface in `src/ops_adapter/main.py`
- the legacy-aligned persona task/state surface in `src/ops_adapter/app.py`

## Task Status Contract

- `queued`
- `in_progress`
- `blocked`
- `completed`
- `failed`
- `cancelled`

Only the transitions declared in `registry/persona_task_queue_state_v1.yaml` are allowed.

## Persona State Contract

- `idle`
  - no open tasks and no queued instructions
- `queued`
  - queued work exists but nothing is active or blocked
- `active`
  - at least one task is in progress
- `blocked`
  - no task is active and at least one task is blocked
- `attention_required`
  - no task is active or blocked and at least one task has failed

## Runtime Rule

Task queues are shared, not duplicated.

That means:

- the dashboard and persona runtime read the same underlying task collections
- state is projected from created tasks plus update logs
- invalid transitions fail closed
- planned personas may hold queued work
- inactive personas may not

## Required Guarantees

- one shared queue/state projection across dashboard and persona runtime
- deterministic task ordering: open first, then priority, then last activity
- explicit transition matrix enforcement
- fail-closed task updates for unknown tasks or invalid transitions
- deterministic persona-state projection from task and instruction history

## No-Go Conditions

- dashboard and persona runtime disagree on task state
- task updates bypass the transition matrix
- inactive personas can receive queued work
- queue state is derived from implicit heuristics instead of the explicit authority file
