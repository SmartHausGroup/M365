# L74 — M365 Commercial Growth and Experience Activation v1

## Lemma

The eight P2C commercial growth and experience personas (content-creator, growth-hacker, ui-designer, brand-guardian, feedback-synthesizer, sprint-prioritizer, ux-researcher, studio-producer) may be claimed as registry-backed, action-surfaced, domain-bound, approval-wired workers only when all six conditions from the P2A activation definition are satisfied for each persona against the authoritative persona registry, agents.yaml, capability map, and department pack authorities.

## Plan Reference

`plan:m365-post-expansion-promotion-and-persona-activation:P2C`

## Assumptions

- `registry/persona_registry_v2.yaml` is the authoritative persona roster.
- `registry/agents.yaml` is the authoritative action registry.
- `registry/persona_capability_map.yaml` is the authoritative capability map.
- `registry/department_pack_*_v1.yaml` are the authoritative department pack files.
- `registry/executor_routing_v2.yaml` is the authoritative routing table.
- The P2A activation definition (6-point test) is the gate for each persona.
- P2B foundation operators are already activated (10 registry-backed personas).

## Proof Sketch

For each of the 8 P2C personas:

1. **Registry-backed**: `persona_registry_v2.yaml` shows `coverage_status: registry-backed` and `status: active`.
2. **Action-surfaced**: `agents.yaml` shows `allowed_actions` populated (not empty `[]`).
3. **Domain-bound**: Each action routes to an executor domain via `executor_routing_v2.yaml` prefix routes.
4. **Approval-wired**: `agents.yaml` shows `approval_rules` for medium-operational personas (growth-hacker); low-observe-create personas operate without explicit approval rules per P2B convention.
5. **Notebook-evidenced**: Primary notebook `notebooks/m365/INV-M365-BV-growth-experience-activation-v1.ipynb` and lemma proof `notebooks/lemma_proofs/L74_m365_growth_experience_activation_v1.ipynb` provide the evidence chain.
6. **Runtime-routed**: Actions are delegatable through the Claude -> UCP -> M365 pipeline via the existing tool surface.

## Activated Personas

| Persona | Department | Actions | Risk | Approval Profile |
|---------|-----------|---------|------|-----------------|
| content-creator | marketing | 8 | low | low-observe-create |
| growth-hacker | marketing | 10 | medium | medium-operational |
| ui-designer | design | 7 | low | low-observe-create |
| brand-guardian | design | 8 | low | low-observe-create |
| feedback-synthesizer | product | 7 | low | low-observe-create |
| sprint-prioritizer | product | 8 | low | low-observe-create |
| ux-researcher | design | 7 | low | low-observe-create |
| studio-producer | project-management | 9 | low | low-observe-create |

**Total new actions across 8 personas: 64**

## Boundary Conditions

- If any persona's `allowed_actions` in `agents.yaml` is empty -> fail closed, persona remains contract-only.
- If any persona's `coverage_status` in `persona_registry_v2.yaml` is not `registry-backed` -> fail closed.
- If any persona's action count in `persona_capability_map.yaml` does not match `agents.yaml` -> fail closed.
- If any declared action lacks a routing entry in `executor_routing_v2.yaml` -> fail closed.
- Personas not in this wave must retain their existing status.
- No persona in this wave requires non-M365 external-channel APIs.
