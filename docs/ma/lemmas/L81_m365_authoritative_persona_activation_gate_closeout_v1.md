# Lemma L81 — M365 Authoritative Persona Activation Gate Closeout v1

## Statement

If H2 through H4 are green and every governed promoted persona already has a
name, title, department, manager, escalation owner, capability-map entry, and
authoritative registry entry, then H5 may close the final activation gate by
promoting all `20` governed personas from `persona-contract-only` to
`registry-backed`, leaving only the `5` deferred external-platform personas in
`planned` status.

## Inputs

- `registry/authoritative_digital_employee_records_v1.yaml`
- `registry/persona_capability_map.yaml`
- `registry/persona_registry_v2.yaml`
- `registry/agents.yaml`
- `registry/activated_persona_surface_v1.yaml`
- `registry/workforce_packaging_v1.yaml`
- `docs/commercialization/m365-activated-persona-surface-v1.md`
- `docs/commercialization/m365-workforce-packaging-v1.md`
- `docs/commercialization/m365-persona-registry-v2.md`

## Governing Formula

`H5_GO = PrereqGreen AND ActivationPrereqsSatisfied AND FinalRegistryTruthful AND FinalSurfaceTruthful AND DeterministicReplay`

where:

- `PrereqGreen := H2_GO AND H3_GO AND H4_GO`
- `ActivationPrereqsSatisfied := FOR ALL promoted_persona: required authoritative fields exist and current status = planned`
- `FinalRegistryTruthful := total_personas = 59 AND total_departments = 10 AND active_personas = 54 AND planned_personas = 5`
- `FinalSurfaceTruthful := registry_backed_personas = 54 AND deferred_external_personas = 5 AND total_allowed_persona_actions = 430`
- `DeterministicReplay := repeated proof/build replay emits the same verification hash`

## Proof Sketch

1. H3 rebased the authoritative registry to the governed `59`-persona roster and
   H4 rebased the certification/count truth to the staged pre-activation state
   of `34` active and `25` planned personas.
2. The governed `20` promoted personas already exist in
   `registry/authoritative_digital_employee_records_v1.yaml`, the authoritative
   roster, and the capability map, so H5 is not adding new personas or widening
   the department model.
3. Each of the `20` promoted personas already has a corresponding runtime agent
   definition with bounded allowed actions in `registry/agents.yaml`; the final
   activation step is therefore a deterministic coverage-state transition, not a
   runtime-surface invention.
4. Flipping those `20` personas from `persona-contract-only` to `registry-backed`
   yields exactly `54` active personas and leaves only the `5` external-platform
   personas deferred.
5. Summing the allowed actions for the `54` active personas yields exactly `430`
   routed actions, while the deferred external `5` remain at zero actions.
6. Therefore H5 may close the activation gate if and only if the scoped
   registry, active-surface, packaging, verifier, and test surfaces reconcile to
   that same final truth without partial activation.

## Machine Bindings

- `scripts/ci/build_persona_registry_v2.py`
- `scripts/ci/verify_persona_registry_v2.py`
- `scripts/ci/verify_activated_persona_surface_v1.py`
- `scripts/ci/verify_workforce_packaging_v1.py`
- `tests/test_persona_registry_v2.py`
- `tests/test_activated_persona_surface_v1.py`
- `tests/test_workforce_packaging_v1.py`
- `configs/generated/authoritative_persona_activation_gate_closeout_v1_verification.json`
