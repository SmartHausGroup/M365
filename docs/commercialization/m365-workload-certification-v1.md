# SMARTHAUS M365 Workload Certification v1

## Purpose

Define the deterministic certification contract for every executor domain in the expanded SMARTHAUS workforce, certifying each workload surface against the live tenant routing table and the bounded executor model before the program may claim workload-level coverage.

## Authority

- **Contract:** `registry/workload_certification_v1.yaml`
- **Routing source:** `registry/executor_routing_v2.yaml`
- **Action contract:** `registry/universal_action_contract_v2.yaml`
- **Capability source:** `registry/capability_registry.yaml`
- **Wave map:** `registry/workforce_release_wave_map.yaml` (W9 exit criteria)

## Problem

Sections 0 through 7 built the universe definition, control plane, workload expansions, department packs, and Claude/UCP delegation experience. However, no single contract certifies that each executor domain actually has routed actions, auth alignment, and bounded-claim consistency. Without this certification, the program cannot claim deterministic workload coverage.

## Decision

Make `registry/workload_certification_v1.yaml` the authoritative workload certification contract. The contract defines four ordered certification phases that every executor domain must pass before it can be marked as certified.

## Certification Phases

1. **Schema Validation** — verify each executor domain has a valid routing table entry with at least one mapped action.
2. **Action Coverage Audit** — count routed actions per domain and compute coverage against the capability registry.
3. **Auth Posture Alignment** — verify declared permissions exist in the auth model for every routed action.
4. **Bounded Claim Consistency** — verify no domain claims certification without passing all prior phases.

## Governance Rules

1. **Fail Closed** — any domain failing any phase is not-yet-certified.
2. **Audit Completeness** — every attempt produces per-domain evidence.
3. **Bounded Claims** — verdicts cannot exceed the actual routed surface.
4. **Determinism** — same inputs produce the same verdicts on replay.
5. **Wave Alignment** — verdicts are consistent with W9 exit criteria.

## Certification Results

| Executor Domain | Routed Actions | Verdict |
| --- | --- | --- |
| directory | 21 | certified |
| collaboration | 11 | certified |
| sharepoint | 20 | certified |
| messaging | 20 | certified |
| workmanagement | 0 | not-yet-certified |
| knowledge | 8 | certified |
| powerplatform | 39 | certified |
| reports | 3 | certified |
| access_reviews | 5 | certified |
| compliance | 8 | certified |
| security | 7 | certified |
| identity_security | 7 | certified |
| devices | 4 | certified |
| publishing | 0 | not-yet-certified |
| composite | 2 | certified |

**Summary:** 13 of 15 executor domains pass certification. 2 domains (workmanagement, publishing) have zero routed actions and are explicitly not-yet-certified.

## Required Guarantees

- One authoritative workload certification contract.
- Deterministic per-domain certification verdicts.
- Fail-closed behavior: no partial certification.
- Bounded claims: verdicts cannot exceed the actual routed action surface.
- Audit evidence for every certification attempt.

## No-Go Conditions

- Domain claims certification without passing all four phases.
- Zero-action domain is marked certified.
- Certification verdict changes without routing table change.
- Missing audit evidence for any domain.
- Claim of full 15-domain certification when 2 domains have zero actions.

## Bounded Claims

**What E8A certifies:**

- 13 of 15 executor domains have routed actions and pass the four-phase certification.
- 155 total actions are routed through the executor model.
- Certification is deterministic and replay-stable.

**What E8A does not certify:**

- All 15 executor domains are fully certified (2 are explicitly not-yet-certified).
- Live tenant execution evidence for every action (that is beyond the bounded executor model scope).
- Workmanagement or publishing domain readiness.

## Next Dependency

`E8B` (Persona Certification) is the next act. It must certify each persona class against its allowed domains and approval posture.
