# L73 — M365 Foundation Operators Activation v1

## Lemma

The six foundation operator personas (backend-architect, devops-automator, api-tester, analytics-reporter, project-shipper, support-responder) may be claimed as registry-backed, action-surfaced, domain-bound, approval-wired workers only when all six conditions from the P2A activation definition are satisfied for each persona against the authoritative persona registry, agents.yaml, capability map, and department pack authorities.

## Plan Reference

`plan:m365-post-expansion-promotion-and-persona-activation:P2B`

## Assumptions

- `registry/persona_registry_v2.yaml` is the authoritative persona roster.
- `registry/agents.yaml` is the authoritative action registry.
- `registry/persona_capability_map.yaml` is the authoritative capability map.
- `registry/department_pack_*_v1.yaml` are the authoritative department pack files.
- `registry/executor_routing_v2.yaml` is the authoritative routing table.
- The P2A activation definition (6-point test) is the gate for each persona.

## Proof Sketch

For each of the 6 foundation personas:

1. **Registry-backed**: `persona_registry_v2.yaml` shows `coverage_status: registry-backed` and `status: active`.
2. **Action-surfaced**: `agents.yaml` shows `allowed_actions` populated (not empty `[]`).
3. **Domain-bound**: Each action routes to an executor domain via `executor_routing_v2.yaml` prefix routes or agent_action_overrides.
4. **Approval-wired**: `agents.yaml` shows `approval_rules` matching the persona's `approval_profile` from the capability map.
5. **Notebook-evidenced**: This lemma and its invariant provide the evidence chain.
6. **Runtime-routed**: Actions are delegatable through the Claude -> UCP -> M365 pipeline via the existing tool surface.

## Activated Personas

| Persona | Department | Actions | Risk | Approval Profile |
|---------|-----------|---------|------|-----------------|
| backend-architect | engineering | 13 | medium | medium-operational |
| devops-automator | engineering | 10 | medium | medium-operational |
| api-tester | testing | 8 | low | low-observe-create |
| analytics-reporter | studio-operations | 9 | low | low-observe-create |
| project-shipper | project-management | 9 | low | medium-operational |
| support-responder | studio-operations | 8 | low | low-observe-create |

**Total new actions across 6 personas: 57**

## Boundary Conditions

- If any persona's `allowed_actions` in `agents.yaml` is empty → fail closed, persona remains contract-only.
- If any persona's `coverage_status` in `persona_registry_v2.yaml` is not `registry-backed` → fail closed.
- If any persona's action count in `persona_capability_map.yaml` does not match `agents.yaml` → fail closed.
- If any declared action lacks a routing entry in `executor_routing_v2.yaml` → fail closed.
- Personas not in this wave (the other 29) must remain `persona-contract-only` with `allowed_actions: []`.
