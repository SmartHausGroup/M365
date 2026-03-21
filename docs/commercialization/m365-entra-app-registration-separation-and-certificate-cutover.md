# SMARTHAUS Entra App Registration Separation and Certificate Cutover

## Purpose

Define the long-term SMARTHAUS Azure / Entra application-registration model for standalone M365 enterprise operation, eliminate overlapping app roles, and lock the executor app to a certificate-based production posture before live certification resumes.

## Current State

SMARTHAUS currently has two relevant app registrations in the tenant:

1. `SMARTHAUS M365`
   - client ID: `720788ac-1485-4073-b0c8-1a6294819a87`
   - current repo role: selected in the tenant contract as the app-only Graph executor
   - observed posture: no redirect URIs, multiple client secrets, no certificate
2. `SmartHaus M365 Enterprise Platform`
   - client ID: `e6fd71d3-4116-401e-a4f1-b2fda4318a8b`
   - observed posture: web redirect URIs exist, one client secret, no certificate

This is directionally useful, but still too ambiguous for final enterprise certification.

## Target Role Separation

### Executor App

- target display name: `SMARTHAUS M365 Executor`
- app ID: `720788ac-1485-4073-b0c8-1a6294819a87`
- purpose: backend-only Microsoft Graph execution
- auth mode: `app_only`
- redirect URIs: none
- runtime selection: tenant contract in `/Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml`
- target credential posture: certificate-based

### Operator Identity App

- target display name: `SMARTHAUS M365 Operator Identity`
- app ID: `e6fd71d3-4116-401e-a4f1-b2fda4318a8b`
- purpose: Entra user sign-in and governed API audience
- auth mode: delegated user auth
- redirect URIs: reviewed and retained only where needed
- application ID URI: required for stable API audience semantics
- target executor role: none

## Why Two Apps

The standalone enterprise runtime has two different authentication planes:

1. human operator identity
2. backend service execution

Using one app for both would mix:

- user-facing redirect and consent surfaces
- service-principal execution identity
- approval and audit actor semantics
- app-only Graph permission posture

That complexity does not improve determinism or governance. Two apps is the simpler and more enforceable long-term contract.

## Azure Cleanup Specification

### `B5D` — Entra App Registration Role Separation

1. Rename app `720788ac-1485-4073-b0c8-1a6294819a87` to `SMARTHAUS M365 Executor`.
2. Rename app `e6fd71d3-4116-401e-a4f1-b2fda4318a8b` to `SMARTHAUS M365 Operator Identity`.
3. Remove any accidental overlap where the identity app is being used as the primary app-only Graph executor.
4. Review redirect URIs on the identity app and keep only the governed operator-login set.
5. Set the identity app `Application ID URI`, preferably `api://e6fd71d3-4116-401e-a4f1-b2fda4318a8b`, unless a stronger SMARTHAUS namespace is approved.
6. Review Graph permissions so the executor app carries the app-only execution burden and the identity app carries only the delegated/API-audience burden required for governed operator auth.

### `B5E` — Executor Certificate Cutover and Tenant Contract Finalization

1. Generate the executor certificate pair under SMARTHAUS control.
2. Upload the public certificate to app `720788ac-1485-4073-b0c8-1a6294819a87`.
3. Place the private certificate on the runtime host at a secure path.
4. Update `/Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml` so:
   - `azure.client_certificate_path` is set
   - `azure.client_secret` is cleared after successful certificate validation
5. Validate app-only Graph execution through the certificate path before removing executor secrets.
6. Keep the operator-identity app separate from executor credential storage and Graph execution.

## Certification Impact

`C1A` may not resume as the active next act until:

1. `B5D` locks the app-registration roles
2. `B5E` locks the executor certificate-cutover contract
3. the approval backend is reachable through the SMARTHAUS tenant contract

This ensures `C1` certifies the intended production auth architecture rather than a transitional secret-based overlap.

## Runtime State After `B5D`

`B5D` is now complete in the live SMARTHAUS tenant:

1. App `720788ac-1485-4073-b0c8-1a6294819a87` is now named `SMARTHAUS M365 Executor`.
2. App `e6fd71d3-4116-401e-a4f1-b2fda4318a8b` is now named `SMARTHAUS M365 Operator Identity`.
3. The executor app now retains Graph application-role posture only.
4. The operator-identity app now retains delegated-scope posture only.
5. The operator-identity app now has `Application ID URI = api://e6fd71d3-4116-401e-a4f1-b2fda4318a8b`.
6. The operator-identity app redirect URIs remain:
   - `https://smarthausgroup.com/api/auth/callback`
   - `https://m365.smarthaus.ai/api/auth/callback`

What remained for the auth architecture after `B5D` was `B5E`: executor certificate cutover and tenant-contract finalization.

## Runtime State After `B5E`

`B5E` is now complete in the live SMARTHAUS tenant and local runtime contract:

1. The executor certificate material now lives at `/Users/smarthaus/.ucp/certs/smarthaus-m365-executor.pem`.
2. The executor app `720788ac-1485-4073-b0c8-1a6294819a87` now has one certificate credential:
   - `SMARTHAUS M365 Executor Certificate 2026-03-19`
3. The executor app now has zero password credentials.
4. `/Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml` now selects certificate auth with:
   - `azure.client_certificate_path = /Users/smarthaus/.ucp/certs/smarthaus-m365-executor.pem`
   - `azure.client_secret = ""`
5. Non-mutating Graph validation succeeded after the secret retirement:
   - `organization = 200`
   - `displayName = The SmartHaus Group`

What remains for certification is no longer executor auth posture. What remains is `C1A` approval-backend reachability for the SMARTHAUS Operations approval target.

## Non-Goals

This act does not:

1. complete the SharePoint approval-site discovery problem
2. run live certification
3. replace the existing runtime actor-versus-executor enforcement already implemented in `B5B` and `B5C`

## Long-Term Production Posture

The final SMARTHAUS enterprise auth model is:

1. operators authenticate through Microsoft Entra ID using the operator-identity app
2. the governed runtime validates that actor identity and maps it to tiers and approvals
3. the runtime executes Graph calls through the executor app
4. the executor app authenticates with a certificate, not a client secret
5. audit records preserve both the human actor and the service executor
