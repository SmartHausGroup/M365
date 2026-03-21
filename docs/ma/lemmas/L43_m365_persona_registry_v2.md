# Lemma L43 — M365 Persona Registry v2

## Statement

If `registry/persona_registry_v2.yaml` is built from the authoritative roster, persona capability
map, and agent registry, and the runtime only loads personas from that registry, then the digital
employee runtime resolves exactly the authoritative `39` personas and excludes the `20`
non-authoritative overflow registry agents.

## Inputs

- `registry/ai_team.json`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`
- `src/ops_adapter/personas.py`

## Proof Sketch

1. The roster authority fixes the persona universe at `39`.
2. The capability map fixes department, approval-profile, and coverage metadata for that same
   universe.
3. The builder projects only roster members into `persona_registry_v2.yaml`.
4. The loader validates the registry document before use and rejects missing fields, count drift,
   alias collisions, or invalid status transitions.
5. Therefore runtime persona resolution is bounded to the authoritative roster and remains
   fail-closed if the registry drifts.

## Machine Bindings

- `registry/persona_registry_v2.yaml`
- `scripts/ci/build_persona_registry_v2.py`
- `scripts/ci/verify_persona_registry_v2.py`
- `tests/test_persona_registry_v2.py`
