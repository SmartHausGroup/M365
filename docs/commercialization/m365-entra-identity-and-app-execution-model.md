# M365 Entra Identity and App-Only Execution Model

**Status:** `B5A` complete
**Date:** 2026-03-18
**Plan refs:** `plan:m365-enterprise-readiness-master-plan:R9`, `plan:m365-enterprise-readiness-master-plan:B5A`

This document locks the enterprise production identity model for standalone M365 v1.

Deterministic identity rule for this repository state:

`EnterpriseIdentity = EntraActorIdentity + TierResolution + ApprovalBoundary + AuditBinding + AppOnlyExecutorIdentity`

If the human actor identity and the backend executor identity are conflated, the enterprise identity model is invalid.

## Canonical Production Model

The production identity model is:

1. **Human user authentication:** Microsoft Entra ID
2. **Backend execution identity:** SmartHaus M365 app registration
3. **Graph execution mode:** `app_only`
4. **Authorization basis:** authenticated human actor mapped to permission tier
5. **Approval basis:** authenticated human actor and requested governed action
6. **Audit basis:** both actor identity and executor identity

This means:

1. SmartHaus employees sign in as SmartHaus users.
2. The governed API validates that user identity as the actor.
3. The runtime authorizes and approves based on that actor.
4. The backend still calls Microsoft Graph as the SmartHaus service principal.

## Actor Versus Executor

| Role | Meaning | Production source | Why it matters |
| --- | --- | --- | --- |
| Actor | The human who requested the governed action | Microsoft Entra ID token or validated SmartHaus identity | Policy, approval, and accountability must attach to the human operator |
| Executor | The service identity that performs the Graph call | SmartHaus M365 app registration from tenant-scoped config | Background execution must remain stable and not depend on an interactive user token |

The actor is not the executor.

Commercial consequence:

1. SmartHaus may claim real operator identity and accountability.
2. SmartHaus may also keep unattended service execution stable and deterministic.
3. Standalone M365 v1 is not a delegated-only operator model.

## Authentication Boundaries

The identity model has two separate authentication planes.

### User authentication plane

1. Source of truth is Microsoft Entra ID.
2. The production runtime should accept authenticated SmartHaus users from Entra, not from a local user database.
3. Expected production claims include a stable user identifier such as `preferred_username`, `upn`, or equivalent email identity.

### Service execution plane

1. Source of truth is the tenant-scoped M365 app registration.
2. The current SmartHaus execution contract remains [smarthaus.yaml](/Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml).
3. The current execution auth posture remains `app_only`.
4. Certificate auth remains the preferred long-term production credential model; client secret remains transitional.

## Authorization Model

The production authorization path is actor-first.

1. The runtime authenticates the human actor through Entra.
2. The runtime resolves that actor to a permission tier.
3. The runtime evaluates approvals and policy against that actor and the requested action.
4. The runtime executes the action through the app-only service principal if allowed.

Current and target mapping posture:

1. Current transitional mapping is direct user-to-tier mapping in tenant config via `permission_tiers.users`.
2. Target production mapping is Entra group-to-tier binding.
3. Direct user mappings remain acceptable for pilot and migration posture, but they are not the preferred long-term enterprise model.

## Tenant-Contract Implications

The current tenant contract is sufficient for app-only execution, but not yet the full final identity architecture.

### Current contract authority

The current tenant contract already remains authoritative for:

1. tenant identity
2. Graph execution auth mode
3. app registration credentials
4. org mappings
5. direct user-to-tier assignments

### Future identity section

The production tenant contract should add a distinct `identity` section for the human-authentication plane.

Planned direction:

1. `identity.provider = entra_id`
2. `identity.allowed_domains`
3. `identity.expected_audience`
4. `identity.expected_issuer`
5. `identity.group_tiers`

Rules:

1. These fields define human-authentication and authorization context.
2. They do not replace the existing app-only execution fields under `azure.*` and `auth.*`.
3. They should remain non-secret tenant-contract data.

`B5A` locks this contract direction. `B5B` and `B5C` implement it.

## Approval and Audit Implications

Approval and audit must reason over both identities.

### Approval rule

1. Approval records must capture the human actor who requested the action.
2. Approval decisions must remain traceable to that actor and the governed action.
3. Approval identity must not collapse into the app registration identity.

### Audit rule

1. Audit records must capture the actor identity.
2. Audit records must capture the executor identity.
3. Enterprise review must be able to answer both:
   - who requested this
   - what service principal executed this

## Certification Implications

`C1` must certify the final identity model, not just app-only execution.

That means live certification must prove:

1. SmartHaus users authenticate through Entra on governed user-facing paths
2. actor identity reaches policy, approval, and audit surfaces
3. Graph execution still occurs through the SmartHaus app registration
4. actor and executor are both visible in the evidence packet

`C1A` was blocked on identity work until `B5C` completed. The active master plan now extends that auth-hardening track through `B5D` and `B5E` so live certification certifies the final SMARTHAUS app-registration split and executor credential posture instead of the transitional secret-based overlap.

## Historical B5A Non-Goals

`B5A` does not:

1. implement Entra JWT enforcement in runtime
2. switch the repo to delegated-only execution
3. remove the current app-only execution contract
4. implement group-to-tier resolution yet

Those are downstream acts:

1. `B5B` for runtime identity enforcement
2. `B5C` for authorization and audit binding

## Runtime State After `B5C`

The governed ops-adapter runtime now implements the production identity model on its active path:

1. JWT-backed SmartHaus actor identity is required on `/actions/*` by default.
2. Tier resolution now supports both direct user mappings and Entra-group-to-tier mappings from tenant config.
3. Approval records preserve the actor, tier, groups, tenant, and executor identity.
4. Audit records preserve the actor, actor tier, actor groups, tenant, and executor identity on the governed runtime path.

`C1A` no longer depends on missing runtime identity implementation, but it is still blocked on final auth-architecture closure through `B5D` and `B5E` plus the remaining live-environment readiness items.
