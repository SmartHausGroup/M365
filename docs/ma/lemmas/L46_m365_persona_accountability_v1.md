# Lemma L46 — M365 Persona Accountability v1

## Statement

If the digital-employee runtime uses one authoritative accountability contract, one authoritative
persona registry, and one shared queue-state runtime, then KPI, ownership, accountability, and
escalation semantics remain aligned across dashboard and persona-runtime surfaces and breach
conditions fail closed.

## Inputs

- `registry/persona_accountability_v1.yaml`
- `registry/persona_registry_v2.yaml`
- `registry/persona_task_queue_state_v1.yaml`
- `src/smarthaus_common/persona_accountability.py`
- `src/smarthaus_common/persona_task_queue.py`
- `src/provisioning_api/routers/agent_dashboard.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`

## Proof Sketch

1. The accountability authority fixes threshold profiles, accountability states, and escalation
   target order.
2. The persona registry fixes ownership and approval fields for each canonical digital employee.
3. The shared queue runtime fixes task and instruction counts for each canonical persona.
4. The accountability builder projects one ownership snapshot and one KPI envelope from those fixed
   authorities.
5. Therefore the dashboard and persona runtime expose the same accountability state, and any breach
   condition escalates deterministically through the declared owner order.

## Machine Bindings

- `registry/persona_accountability_v1.yaml`
- `scripts/ci/verify_persona_accountability_v1.py`
- `tests/test_persona_accountability_v1.py`
- `tests/test_agent_api.py`
