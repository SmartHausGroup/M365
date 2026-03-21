# L59 — M365 Persona Discovery Contract v1

## Lemma

Persona discovery may be treated as deterministic only when every persona in the
authoritative registry is reachable through at least one of six declared discovery
dimensions and the selection rules produce consistent results for any fixed registry state.

## Assumptions

- `registry/persona_discovery_contract_v1.yaml` is the authoritative discovery contract.
- `registry/persona_registry_v2.yaml` is the authoritative persona registry.
- `registry/persona_capability_map.yaml` provides capability-family mappings.

## Proof Sketch

If six discovery dimensions cover name, department, capability, workload, risk, and
coverage status, then every persona with at least one of these attributes is discoverable.
If selection rules handle single, multiple, and zero matches deterministically, then
discovery results are consistent for fixed state. Therefore deterministic persona
discovery exists for any fixed registry state.

## Boundary Conditions

- Missing discovery dimensions must fail validation.
- Persona count must match the authoritative registry.
- Department count must match the authoritative department set.
