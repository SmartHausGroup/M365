# L65 — M365 Department Certification v1

## Lemma

The M365 workforce department surface may be treated as deterministically certified only when: (1) the department certification contract exists with four ordered phases and five governance rules, (2) all 10 departments have valid pack files, (3) persona counts per department match the persona registry, (4) every pack has at least one workflow family, and (5) the sum of department persona counts equals total personas.

## Assumptions

- Department pack YAMLs are authoritative.
- `registry/persona_registry_v2.yaml` is the authoritative persona registry.
- The certification contract defines exactly four phases and five governance rules.

## Proof Sketch

1. If all 10 packs exist with required keys, pack presence is satisfied.
2. If persona counts match registry, alignment holds.
3. If workflow families are non-empty, coverage is satisfied.
4. If sum of department personas = 39, partition is exhaustive.
5. Therefore department certification is deterministic and bounded.

## Boundary Conditions

- Missing pack file fails validation.
- Persona count mismatch fails validation.
- Zero workflow families fails validation.
- Sum mismatch fails validation.
