# Lemma L47 — M365 Persona Memory and Work History v1

## Statement

If the digital-employee runtime uses one authoritative memory/work-history contract, one shared
append-only memory store, and one deterministic projection over task, instruction, and memory
records, then persona memory and replayable work history remain bounded, auditable, and aligned
across dashboard and persona-runtime surfaces.

## Inputs

- `registry/persona_memory_work_history_v1.yaml`
- `src/smarthaus_common/persona_memory.py`
- `src/smarthaus_common/persona_task_queue.py`
- `src/provisioning_api/routers/agent_dashboard.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`

## Proof Sketch

1. The authority file fixes valid memory types, visibility levels, sources, and retention bounds.
2. Memory writes append immutable entries to one bounded store.
3. Work history is projected from queue records plus memory records in deterministic timestamp order.
4. The same shared runtime projects both dashboard and persona-runtime memory/history surfaces.
5. Therefore memory and work history remain bounded, auditable, and consistent across runtime
   surfaces, and invalid writes fail closed.

## Machine Bindings

- `registry/persona_memory_work_history_v1.yaml`
- `scripts/ci/verify_persona_memory_work_history_v1.py`
- `tests/test_persona_memory_work_history_v1.py`
- `tests/test_agent_api.py`
