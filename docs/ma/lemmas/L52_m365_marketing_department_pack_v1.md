# L52 — M365 Marketing Department Pack v1

## Lemma

The Marketing department may be treated as one bounded workforce pack before activation only when
its contract-only personas, zero-action boundary, workflows, approvals, and blocked state are
projected from one declared Marketing authority and one shared runtime rule.

## Assumptions

- `registry/persona_registry_v2.yaml` is the authoritative persona registry.
- `registry/department_pack_marketing_v1.yaml` is the authoritative Marketing pack boundary.
- The shared department-pack runtime supports both registry-backed and contract-only personas.

## Proof Sketch

If the department pack reads only the declared Marketing personas from the authoritative registry,
then the contract boundary is fixed. If contract-only personas are required to declare zero
supported actions and that zero-action claim is compared directly to the registry, then the pack
cannot overclaim live execution coverage. If the shared runtime computes `blocked` whenever
Marketing personas remain planned-only, then the runtime state is deterministic and fail-closed.
Therefore one deterministic Marketing pack snapshot exists for any fixed runtime state.

## Boundary Conditions

- Missing declared personas must fail closed.
- Any non-zero action claim for contract-only Marketing personas must fail closed.
- Any mismatch between declared and registry coverage status must fail closed.
- `ready` is impossible while the Marketing personas remain planned-only.
