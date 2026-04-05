# Lemma L78 — M365 Authoritative Persona Registry Rebase v1

## Statement

If the H2 employee records are merged into the authoritative roster and
capability map while every promoted persona remains `persona-contract-only`,
then the workforce can be rebased from `39` to `59` authoritative personas
without activating the promoted set before H5.

## Inputs

- `registry/ai_team.json`
- `registry/persona_capability_map.yaml`
- `registry/persona_registry_v2.yaml`
- `registry/authoritative_digital_employee_records_v1.yaml`
- `docs/commercialization/m365-persona-registry-v2.md`
- `docs/commercialization/m365-persona-capability-and-risk-map.md`

## Governing Formula

`H3_GO = Roster59 AND Registry59_34_25 AND Capability59_34_25 AND ActivationSeparation`

where:

- `Roster59 := total_authoritative_personas = 59`
- `Registry59_34_25 := total_personas = 59 AND active_personas = 34 AND planned_personas = 25`
- `Capability59_34_25 := total_personas = 59 AND current_registry_backed_personas = 34 AND persona_contract_only_personas = 25 AND non_authoritative_registry_agents = 0`
- `ActivationSeparation := FOR ALL promoted_persona, allowed_actions = [] AND allowed_domains = [] AND action_count = 0`

## Proof Sketch

1. H1 fixes the department placement for the `20` promoted personas.
2. H2 fixes the names, titles, manager tokens, escalation tokens, and bounded
   humanization fields for the same `20` personas.
3. H3 appends those personas into the authoritative roster and capability map
   using the H2 bindings, so the authoritative set increases from `39` to `59`.
4. The promoted personas remain `persona-contract-only`, so their registry
   projection must suppress raw runtime actions even if `registry/agents.yaml`
   already contains implementation surfaces for those agents.
5. Therefore the authoritative surfaces can truthfully report `59` total
   personas while preserving the pre-H5 staged split of `34` active and `25`
   planned personas.

## Machine Bindings

- `scripts/ci/build_persona_registry_v2.py`
- `scripts/ci/verify_persona_registry_v2.py`
- `tests/test_persona_registry_v2.py`
- `tests/test_authoritative_persona_registry_rebase_v1.py`
