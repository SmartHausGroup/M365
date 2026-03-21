# SMARTHAUS M365 Persona Certification v1

## Purpose

Define the deterministic certification contract for every persona in the expanded SMARTHAUS workforce, certifying each persona class against its allowed domains and approval posture before the program may claim persona-level coverage.

## Authority

- **Contract:** `registry/persona_certification_v1.yaml`
- **Persona source:** `registry/persona_registry_v2.yaml`
- **Approval source:** `registry/approval_risk_matrix_v2.yaml`
- **Workload certification:** `registry/workload_certification_v1.yaml`

## Problem

E8A certified the workload surface at the executor domain level. However, no contract certifies that each individual persona has consistent fields, coverage status, approval posture, and domain alignment. Without this certification, the program cannot claim deterministic persona coverage.

## Decision

Make `registry/persona_certification_v1.yaml` the authoritative persona certification contract. The contract defines four ordered certification phases that every persona must pass.

## Certification Phases

1. **Field Completeness** — verify every persona has all 21 required fields.
2. **Coverage Status Consistency** — verify registry-backed personas have actions and contract-only personas have zero.
3. **Approval Posture Alignment** — verify risk_tier maps correctly to approval_profile.
4. **Domain Alignment** — verify registry-backed persona domains are within certified workload domains.

## Governance Rules

1. **Fail Closed** — any persona failing any phase is not-certified.
2. **Audit Completeness** — every attempt produces per-persona evidence.
3. **Bounded Claims** — verdicts cannot exceed the actual persona surface.
4. **Determinism** — same inputs produce the same verdicts on replay.
5. **Coverage Partition** — registry-backed + contract-only = total.

## Certification Results

- **39 personas pass four-phase certification.**
- 4 registry-backed personas (hr-generalist, m365-administrator, outreach-coordinator, website-manager) have non-zero actions and certified domains.
- 35 contract-only personas are certified as contract-defined.
- Risk tier distribution: 1 critical, 4 high, 6 medium, 28 low.

## No-Go Conditions

- Persona missing any required field.
- Registry-backed persona with zero actions.
- Contract-only persona with non-zero actions.
- Risk tier to approval profile mismatch.
- Registry-backed persona claiming uncertified domain.

## Next Dependency

`E8C` (Department Certification) is the next act.
