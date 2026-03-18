# M365 Release Gates and Certification

**Status:** `P3B` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R4`, `plan:m365-enterprise-commercialization-readiness:P3B`

This document converts the live-tenant validation matrix into an explicit release-decision model for standalone M365 v1. It defines what must be true before SmartHaus can call the product enterprise-release ready, and it blocks release when required evidence is missing or when only mock confidence exists.

Deterministic release rule for this repository state:

`EnterpriseReleaseDecision = Gate1 ∧ Gate2 ∧ Gate3 ∧ Gate4 ∧ Gate5 ∧ Gate6`

If any gate fails, the certification result is `NO-GO`.

## Release Gates

Release gates are ordered and cumulative. A later gate may not pass if an earlier gate is unresolved.

### Gate 1 — Commercial boundary integrity

Required:

1. Release scope is limited to the 9 supported actions in `docs/commercialization/m365-v1-supported-surface.md`.
2. No release statement references the broader 260-action universe as if it were launch scope.
3. Product, support, and pilot claims stay inside the supported-surface document.

Evidence:

1. `docs/commercialization/m365-v1-supported-surface.md`
2. `docs/M365_MA_INDEX.md`
3. `registry/capability_registry.yaml`

### Gate 2 — Canonical configuration and auth posture

Required:

1. Production authority is tenant YAML selected by `UCP_TENANT`.
2. Production auth posture is `app_only` by default.
3. Enterprise-preferred credential is certificate auth.
4. Client secret is treated as transitional only.
5. `.env` is not treated as the production source of truth.

Evidence:

1. `docs/commercialization/m365-canonical-config-contract.md`
2. `docs/commercialization/m365-config-migration-and-auth-policy.md`

### Gate 3 — Governance and control boundary integrity

Required:

1. Audit and governance evidence boundaries are explicitly documented.
2. Permission-tier and approval boundaries are explicitly documented.
3. Known fail-open or permissive branches are disclosed as gaps, not release strengths.

Evidence:

1. `docs/commercialization/m365-audit-and-governance-evidence-model.md`
2. `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`

### Gate 4 — Live-tenant evidence completeness

Required:

1. Every enterprise-critical capability marked `Live required` or `Both` in `P3A` has an attached live evidence packet.
2. No mock-only artifact is used as enterprise release proof.
3. Live evidence exists for:
   - auth enforcement
   - idempotency
   - instruction audit
   - mutating supported actions
   - read-only supported actions
   - config authority posture
   - ops-adapter approval path
   - any governance/admin claim included in the release scope

Evidence:

1. `docs/commercialization/m365-live-tenant-validation-matrix.md`
2. live validation packet referenced by release manager

### Gate 5 — Gap acceptance and exclusion control

Required:

1. Any unresolved gap must be either:
   - closed before release, or
   - explicitly excluded from release claims
2. append-only admin audit evidence for the active ops-adapter admin surface must be exercised and collected in the live validation packet before a “fully enterprise-governed” claim is made.
3. Fail-open OPA or permissive permission fallback behavior may not be included in the enterprise release posture.

Evidence:

1. commercialization docs from `P2A` and `P2B`
2. release exception register or exclusion statement

### Gate 6 — Executive certification packet

Required:

1. One certification packet exists for the candidate release.
2. The packet links all required evidence and records the final decision.
3. The decision includes owner sign-off from engineering, security, and release.

Evidence:

1. release certification packet
2. sign-off record

## GO Criteria

The release decision is `GO` only if all of the following are true:

1. The release scope remains the 9-action standalone v1 boundary.
2. The canonical production config and auth posture are documented and internally consistent.
3. Governance and fail-closed boundaries are documented without unresolved ambiguity.
4. Live evidence exists for every enterprise-critical capability that materially depends on tenant behavior.
5. No release-critical decision depends solely on mock-only or artifact-only evidence where live evidence is required.
6. Every unresolved gap is explicitly excluded from the release claim.
7. Evidence packet and sign-off record are complete and retained.

## NO-GO Criteria

The release decision is `NO-GO` if any of the following are true:

1. A mock-passing auth or idempotency artifact is used as the only evidence for enterprise release.
2. Any of the 9 supported actions lacks the required live evidence classification or packet.
3. A governance or audit claim is made without mapped evidence or explicit gap disclosure.
4. admin audit is presented as enterprise-complete without the live admin evidence packet required by `C1`.
5. Release materials imply approval hardening or fail-closed behavior that the current repo does not support.
6. Evidence packet is incomplete, untraceable, or missing owner sign-off.
7. Release scope drifts beyond the supported v1 boundary.

## Evidence Retention

For each enterprise release candidate, retain one release evidence packet containing:

1. release identifier and candidate date
2. commit SHA or build identifier
3. tenant slug and validation environment summary
4. auth mode used during validation
5. supported actions tested
6. live request and response samples or test transcripts
7. audit and approval records where applicable
8. explicit pass/fail per release gate
9. unresolved gap list and exclusion statement
10. engineering, security, and release sign-off

Retention rules:

1. Keep the certification packet for the duration of the pilot and for the defined support window of that release.
2. Keep enough evidence to replay the release decision later without relying on memory or chat context.
3. Store evidence in a location controlled by SmartHaus governance, not only in ephemeral local logs.

## Current Decision Model for This Repo State

If evaluated today against these gates, the certification state is:

1. `Gate 1` structurally passable
2. `Gate 2` structurally passable
3. `Gate 3` structurally passable with documented gaps
4. `Gate 4` not yet passable because the required live evidence packet has not been produced
5. `Gate 5` partially passable only if unresolved gaps remain excluded from claims
6. `Gate 6` not yet passable because no release certification packet exists

Current deterministic outcome:

`NO-GO` for enterprise certification today, until `P3A` live-evidence execution is actually performed and a release packet exists.
