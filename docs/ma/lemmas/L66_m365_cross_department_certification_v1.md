# L66 — M365 Cross-Department Workflow Certification v1

## Lemma

Cross-department workflows may be treated as deterministically certified only when: (1) the cross-department certification contract exists with four phases and five governance rules, (2) the collaboration contract defines collaboration primitives and handoff rules, (3) all certified departments can participate through those primitives, and (4) no claim exceeds the certified collaboration surface.

## Assumptions

- `registry/cross_persona_collaboration_contract_v1.yaml` is authoritative.
- E8A, E8B, and E8C certifications are prerequisites.

## Proof Sketch

1. If collaboration contract exists with 4 primitives and 5 handoff rules, presence is satisfied.
2. If all 10 departments are certified, department pair coverage holds.
3. If handoff rules are complete, transitions are governed.
4. Therefore cross-department certification is deterministic and bounded.

## Boundary Conditions

- Missing collaboration contract fails validation.
- Missing handoff rules fails validation.
- Claim exceeding surfaces fails validation.
