# SMARTHAUS M365 Customer Onboarding v2

## Purpose

Define the deterministic onboarding path for the expanded workforce product with tenant readiness, sequential persona activation, department rollout, and acceptance criteria.

## Authority

- **Contract:** `registry/customer_onboarding_v2.yaml`
- **Packaging:** `registry/workforce_packaging_v1.yaml`

## Onboarding Phases

1. **Tenant Readiness** — verify Azure AD, Graph API, M365 licensing.
2. **Core Persona Activation** — activate 4 registry-backed personas in sequence.
3. **Department Rollout Sequence** — operations first, then expand.
4. **Acceptance Criteria** — one governed action per persona, pack validation green.

## No-Go Conditions

- Missing tenant prerequisite. Persona activation failure. Unmet acceptance criterion.

## Next Dependency

`E9C` (Pilot and Rollout Model v2) is the next act.
