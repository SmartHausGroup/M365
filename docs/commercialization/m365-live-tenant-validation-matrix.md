# M365 Live-Tenant Validation Matrix

**Status:** `P3A` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R4`, `plan:m365-enterprise-commercialization-readiness:P3A`

This document defines which validation evidence is sufficient only for development confidence, which evidence is required for enterprise release claims, and which capabilities require both mock and live-tenant validation.

Deterministic validation rule for this repository state:

`ReleaseEligibleCapability = Supported_v1(capability) + ValidationMode(capability) + Prerequisites(capability) + EvidenceArtifact(capability)`

If a supported enterprise-critical capability lacks a live-evidence requirement where tenant behavior materially matters, that capability is not release-eligible.

## Matrix

| Capability | Validation Mode | Prerequisites | Evidence Artifact | Release Use |
| --- | --- | --- | --- | --- |
| Instruction response schema and postcondition for the 9 supported actions | Both | MA contract docs present; local/runtime endpoint reachable for replay when needed | `docs/contracts/caio-m365/MATHEMATICS.md`, `docs/contracts/caio-m365/M365_MASTER_CALCULUS.md`, `configs/generated/caio_m365_contract_verification.json` | Contract proof and baseline regression evidence; not alone sufficient for enterprise live claim |
| Auth gate for instruction API | Live required | real `CAIO_API_KEY` policy if enabled, live endpoint, tenant-backed auth path, expected auth headers | `configs/generated/m365_auth_verification.json` rerun in live mode, plus live execution record | Enterprise release claim requires live rerun because current artifact can pass in mock mode |
| Idempotency behavior for supported actions | Both | live reachable endpoint, stable idempotency store semantics, at least one repeated request pair | `configs/generated/m365_idempotency_verification.json` plus live rerun evidence | Mock/local proof is useful, but enterprise release requires live replay evidence |
| Instruction audit for supported actions | Both | `ENABLE_AUDIT_LOGGING=true`, reachable runtime, auditable storage path, repeatable request sample | `configs/generated/m365_audit_verification.json`, `docs/contracts/caio-m365/LEMMA_L4.md`, plus live audit sample | Current artifact supports narrow audit claim; enterprise release requires live tenant-backed execution evidence |
| Mutation gate for mutating supported actions (`create_site`, `create_team`, `add_channel`, `provision_service`, `reset_user_password`) | Live required | live tenant, valid Graph app permissions, explicit `ALLOW_M365_MUTATIONS` off/on checks, non-production validation tenant | live execution transcript, request/response captures, audit evidence, operator checklist record | Required for enterprise claim because tenant state change behavior matters |
| Read-only supported actions (`list_users`, `get_user`, `list_teams`, `list_sites`) | Both | live tenant with accessible objects and expected Graph permissions | contract artifact plus live request/response evidence | Mock/local contract proof is not enough for enterprise release; live tenant confirms permissions and shape against real data |
| Tenant-config authority and auth-mode posture | Live required | live deployment configured via `UCP_TENANT`, tenant YAML present, secret material injected outside repo, chosen auth mode active | operator runbook evidence, config snapshot, live startup evidence | Required for enterprise release because configuration authority is part of the product claim |
| Ops-adapter approval path | Live required | OPA reachable, approval backend configured, approval target action available, approver identity path configured | approval record, audit record, policy decision record, operator evidence | Required for enterprise governance claim; not covered by current generated MA artifacts |
| Ops-adapter admin audit/config inspection path | Live required | configured admin surface, tenant config available, admin actions exercised in controlled tenant | admin evidence packet, audit records, gap acknowledgement | Required before enterprise governance claims broaden beyond instruction API; currently still gap-bearing |
| Capability-universe registry integrity | Mock/local sufficient | generated registry artifacts available | `configs/generated/capability_registry_verification.json`, `docs/M365_MA_INDEX.md` | Supports claim that only 9 of 260 actions are implemented; not a live tenant requirement |

## Validation Mode Definitions

### Mock or local sufficient

Use only where tenant behavior is not the thing being certified.

Examples:

1. capability-registry integrity
2. static contract consistency
3. narrow schema or artifact existence checks

### Live required

Use where the enterprise claim depends on real tenant behavior, real permissions, or real governance routing.

Examples:

1. auth enforcement
2. mutation gates against actual tenant state
3. approval routing
4. config authority in a real deployment
5. any claim involving admin audit or governance evidence

### Both

Use where local or MA evidence proves structure, but live tenant execution is still required for release confidence.

Examples:

1. idempotency
2. instruction audit
3. supported read and write action behavior

## Prerequisites

Live-tenant validation for standalone M365 v1 requires all of the following:

1. non-production tenant or isolated validation tenant
2. supported app registration with the required Graph permissions for the 9-action v1 surface
3. canonical config path in effect:
   - `UCP_TENANT`
   - tenant YAML
   - secret injection outside committed repo files
4. explicit mutation safety controls for mutating tests
5. audit logging enabled where audit evidence is under test
6. approval backend configured where approval evidence is under test
7. correlation ID retention in request/response artifacts
8. operator-run validation log that records:
   - timestamp
   - tenant slug
   - auth mode
   - action tested
   - outcome
   - evidence file location

## Evidence Artifact Rules

For enterprise release consideration, a live evidence packet should include:

1. request sample or command used
2. response sample with request or trace correlation
3. audit record reference where applicable
4. approval record reference where applicable
5. environment and auth-mode summary
6. explicit designation of:
   - live pass
   - mock/local pass only
   - not yet validated

Current artifact trust levels:

1. `configs/generated/caio_m365_contract_verification.json`
   - useful for structural contract confidence
   - not sufficient alone for live enterprise certification
2. `configs/generated/m365_auth_verification.json`
   - currently insufficient for enterprise release because it can pass with `CAIO_API_KEY` unset or no `BASE_URL`
3. `configs/generated/m365_idempotency_verification.json`
   - currently insufficient for enterprise release because it can pass with no live `BASE_URL`
4. `configs/generated/m365_audit_verification.json`
   - useful but narrow; only proves the current audit schema check and small record sample

## Release Use

The following commercialization rules apply now:

1. No mock-only artifact may be presented as enterprise release proof.
2. Enterprise-critical claims for auth, idempotency, audit, mutation behavior, approvals, and config authority require live rerun evidence.
3. The standalone v1 release claim is limited to the 9 supported actions documented in `docs/commercialization/m365-v1-supported-surface.md`.
4. The 260-action universe and 251 planned actions are not part of the live validation scope for v1 release.
5. Ops-adapter approval and admin-governance claims require separate live evidence from the instruction API MA artifacts.

Current commercialization consequence:

1. The repo has credible structural MA evidence.
2. The repo does not yet have a complete live-tenant release evidence packet for standalone M365 v1.
3. `P3B` must turn this matrix into explicit go/no-go release gates.
