# L48 — M365 Operations Department Pack v1

## Lemma

The Operations department may be treated as one runtime-real workforce pack only when its personas,
actions, workflows, approvals, and state are projected from one declared department authority and one
shared runtime projection rule.

## Assumptions

- `registry/persona_registry_v2.yaml` is the authoritative persona registry.
- `registry/department_pack_operations_v1.yaml` is the authoritative Operations pack boundary.
- Persona accountability and memory/work-history projections are already deterministic and valid.

## Proof Sketch

If the department pack reads personas directly from the authoritative persona registry and only for
the exact Operations personas declared in the pack authority, then the pack boundary is fixed. If
the pack also computes department state from persona status and persona accountability state, then
pack readiness is deterministic. If the pack summary validates declared action counts and workflow
counts against the authority, then the department claim cannot silently drift. Therefore one
deterministic Operations pack snapshot exists for any fixed runtime state.

## Boundary Conditions

- Missing expected persona -> fail closed.
- Inactive expected persona -> pack state is `blocked`.
- Any escalated Operations persona -> pack state is `attention_required`.
- Any warning Operations persona with no escalations -> pack state is `watch`.
- Any mismatch between declared and projected supported-action totals -> fail closed.
