# Lemma L45 — M365 Persona Task Queues and State v1

## Statement

If the digital-employee runtime uses one authoritative queue/state contract, one shared append-only
store, and one deterministic projection engine for created tasks, task updates, and queued
instructions, then dashboard and persona-runtime state remain aligned and invalid lifecycle changes
fail closed.

## Inputs

- `registry/persona_task_queue_state_v1.yaml`
- `src/smarthaus_common/json_store.py`
- `src/smarthaus_common/persona_task_queue.py`
- `src/provisioning_api/routers/agent_dashboard.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`

## Proof Sketch

1. The authority file fixes the valid task statuses, persona states, and allowed transitions.
2. The shared runtime stores created tasks, queued instructions, and lifecycle updates in one
   append-only JSON store.
3. The projection engine overlays updates onto created tasks in deterministic timestamp order.
4. Persona state is derived from explicit state precedence, not ad hoc route-local logic.
5. Therefore task queues and persona state remain aligned across the dashboard and persona runtime,
   and invalid transitions fail closed.

## Machine Bindings

- `registry/persona_task_queue_state_v1.yaml`
- `scripts/ci/verify_persona_task_queue_state_v1.py`
- `tests/test_persona_task_queue_state_v1.py`
- `tests/test_agent_api.py`
