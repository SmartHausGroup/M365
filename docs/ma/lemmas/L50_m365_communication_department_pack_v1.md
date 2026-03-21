# L50 — M365 Communication Department Pack v1

## Lemma

The Communication department may be treated as one runtime-real workforce pack only when its
persona, actions, workflows, approvals, and state are projected from one declared Communication
authority and one shared runtime projection rule.

## Assumptions

- `registry/persona_registry_v2.yaml` is the authoritative persona registry.
- `registry/department_pack_communication_v1.yaml` is the authoritative Communication pack boundary.
- Persona accountability and memory/work-history projections are already deterministic and valid.

## Proof Sketch

If the department pack reads personas directly from the authoritative persona registry and only for
the exact Communication persona declared in the pack authority, then the pack boundary is fixed. If
the pack also computes department state from persona status and persona accountability state, then
Communication pack readiness is deterministic. If the pack summary validates declared action counts
and workflow counts against the authority, then the department claim cannot silently drift.
Therefore one deterministic Communication pack snapshot exists for any fixed runtime state.

## Boundary Conditions

- Missing expected Communication persona -> fail closed.
- Inactive expected Communication persona -> pack state is `blocked`.
- Escalated Communication persona -> pack state is `attention_required`.
- Warning Communication persona with no escalation -> pack state is `watch`.
- Any mismatch between declared and projected supported-action totals -> fail closed.
