# SMARTHAUS M365 Cross-Department Workflow Certification v1

## Purpose

Certify that cross-functional workflows spanning multiple departments and personas are governed by the collaboration contract, handoff rules, and bounded claims consistent with the certified department and persona surfaces.

## Authority

- **Contract:** `registry/cross_department_certification_v1.yaml`
- **Collaboration:** `registry/cross_persona_collaboration_contract_v1.yaml`
- **Department certification:** `registry/department_certification_v1.yaml`

## Certification Phases

1. **Collaboration Contract Presence** — collaboration contract exists with primitives and rules.
2. **Department Pair Coverage** — cross-department workflows possible between all certified departments.
3. **Handoff Rule Completeness** — transitions cover initiation through failure recovery.
4. **Bounded Claim Consistency** — no claim exceeds certified surfaces.

## Certification Results

All phases pass. Cross-department certification is green: 4 collaboration primitives, 5 handoff rules, 10 certified departments eligible.

## No-Go Conditions

- Missing collaboration contract.
- Missing handoff rules.
- Claims exceeding certified department or persona surface.

## Next Dependency

`E8E` (Enterprise Release Gate v2) is the next act.
