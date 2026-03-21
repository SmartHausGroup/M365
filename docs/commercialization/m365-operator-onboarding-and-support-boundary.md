# M365 Operator Onboarding and Support Boundary

**Status:** `P4B` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R5`, `plan:m365-enterprise-commercialization-readiness:P4B`

This document defines the operator experience after the canonical standalone install path documented in `docs/commercialization/m365-packaging-install-bootstrap.md`.

Deterministic operator rule for the current repository state:

`CanonicalOperatorFlow = Install -> Bootstrap -> HealthCheck -> GovernanceDependencyCheck -> SupportedSurfaceConfirmation -> OperateOrEscalateByOwner`

If a required day-0 or day-1 task has no named owner, the standalone support model is commercially ambiguous and `P4B` fails.

## Onboarding Checklist

The intended standalone operator is the customer's internal M365 administration or platform operations team, not SmartHaus day-to-day operations.

The onboarding checklist is complete only when every step below is satisfied:

1. Confirm the named customer-side runtime owner, approval owner, and security owner.
2. Confirm Python `3.14+` is available for the standalone server path.
3. Install the package using the canonical `P4A` path and confirm the `m365-server` launcher is available.
4. Prepare an app root that contains `registry/agents.yaml`.
5. Set `M365_APP_ROOT` if the operator will not launch from the distribution root.
6. Configure bootstrap-only launcher inputs as needed:
   - `M365_SERVER_HOST`
   - `M365_SERVER_PORT`
   - optional local bootstrap `.env`
7. Configure the supported production authority separately from bootstrap:
   - `UCP_TENANT`
   - tenant YAML contract
   - externally injected secret material
   - `app_only` default auth posture
   - certificate auth when available
8. Set `ALLOW_M365_MUTATIONS=false` for the first startup and initial smoke validation.
9. Configure governance dependencies required by the target deployment:
   - `OPA_URL` for policy enforcement
   - tenant-backed approvals target configuration, with `APPROVALS_SITE_URL` or `APPROVALS_SITE_ID` only as explicit compatibility overrides
   - optional `AUDIT_SERVICE_URL` when enterprise audit forwarding is expected
10. Start `m365-server`.
11. Confirm the launcher created `logs/` under the app root and that `logs/ops_audit.log` is writable after the first action or approval event.
12. Run the day-0 smoke checks in the runbooks below and record the output.
13. Confirm the exposed customer-facing capability claim remains bounded to the 9 supported actions in `docs/commercialization/m365-v1-supported-surface.md`.

## Runbooks

### Day 0 — First Start and Smoke Validation

Use this runbook for first install, host migration, or clean rebuild.

1. Launch the server:

```bash
m365-server
```

2. If the launcher exits immediately, classify the failure before escalating:
   - `SMARTHAUS M365 Server requires Python 3.14 or newer.` means customer environment mismatch.
   - `Registry not found at ... Run from the M365 repo root or set M365_APP_ROOT.` means app-root/bootstrap mismatch.
3. Verify server health:

```bash
curl -s http://127.0.0.1:9000/health
```

Expected result:
- `status=healthy`
- timestamp present
- version present

4. Confirm the runtime owns the expected registry and log path:
   - `REGISTRY_FILE` resolves to the app-root `registry/agents.yaml`
   - `LOG_DIR` resolves to the app-root `logs/`
5. Confirm commercial boundary discipline before broader enablement:
   - do not expose unsupported actions
   - do not enable live mutations yet
   - do not treat bootstrap `.env` as production authority

### Day 0 — Governance Dependency Validation

Use this runbook before any approval-bearing or policy-gated use.

1. Confirm the target deployment expects policy enforcement and approvals.
2. Verify `OPA_URL` points to a reachable OPA instance if enterprise policy enforcement is required.
3. Verify the approvals backend target resolves from the selected tenant contract if approval-required actions are in scope.
4. Query the approval backend only after configuration is in place:

```bash
curl -s "http://127.0.0.1:9000/approvals/query?limit=5"
```

Interpretation:
- a structured item list indicates the approval surface is reachable
- `approvals_backend_not_configured` is a customer-owned environment/config issue, not a SmartHaus runtime defect by itself

5. Commercial rule for enterprise operation:
   - runtime branches that rely on fail-open policy behavior are not an enterprise-ready operating posture even if the server technically starts
   - if policy enforcement is part of the target deployment and OPA is unavailable, stop and treat the environment as not enterprise-ready

### Day 1 — Supported Operation and Change Control

Use this runbook after the initial smoke pass succeeds.

1. Keep `ALLOW_M365_MUTATIONS=false` until the customer approves a controlled non-production write window.
2. Validate the supported surface against `docs/commercialization/m365-v1-supported-surface.md` before enabling any internal operator workflows.
3. If the target deployment includes approvals, verify one approval path end to end before relying on mutating behavior:
   - create or inspect a pending approval
   - confirm the approval record can be queried
   - confirm approval events append to `logs/ops_audit.log`
4. Enable writes only for controlled non-production validation and only after tenant identity, permissions, and approval controls are confirmed.
5. Re-disable broad write windows after validation if continuous mutation is not required.
6. Treat any request for unsupported actions, unsupported auth posture, or tenant-specific custom behavior as outside the v1 baseline support boundary until separately approved.

### Day 1 — Incident Triage

Use this runbook when the runtime is healthy but behavior is wrong or risky.

1. If the issue is active unintended mutation risk, immediately set `ALLOW_M365_MUTATIONS=false` and pause operator use.
2. If credentials or secrets may be exposed, the customer security owner rotates them first; SmartHaus is informed after containment begins.
3. If the issue is approval or policy denial, determine whether it is:
   - expected policy behavior
   - customer policy/config error
   - product defect reproducible on the canonical standalone path
4. If the issue is runtime startup failure, reproduce using the canonical `m365-server` path before escalating.
5. If the issue is outside the 9-action supported surface, classify it as out of baseline support scope before assigning SmartHaus engineering time.

## Support Boundary

The standalone support model is bounded. SmartHaus supports the supported product path; the customer operates the tenant and surrounding environment.

### SmartHaus-owned baseline support

SmartHaus owns:

1. defects in the documented standalone `m365-server` packaging and launcher path
2. defects in the documented v1 supported surface boundary and commercialization docs
3. defects reproducible on the canonical path within the supported 9-action boundary
4. clarification of documented bootstrap, onboarding, and support-boundary behavior

### Customer-owned runtime and tenant operations

The customer owns:

1. tenant readiness, Graph consent, and permission grants
2. tenant YAML values, org mappings, and secret injection
3. certificate lifecycle, secret rotation, and security incident containment
4. runtime hosting, Python environment, app-root contents, and `registry/agents.yaml`
5. OPA availability, policy data, and approval backend configuration
6. day-to-day operator staffing, approval staffing, and production execution decisions
7. live-tenant validation execution and evidence capture required for enterprise release

### Out of baseline support scope

The following are outside baseline standalone v1 support unless separately contracted or re-approved:

1. unsupported actions outside the 9-action commercial boundary
2. custom tenant workflows or custom policy authoring
3. SmartHaus acting as the customer's day-to-day operator
4. environments that intentionally rely on deprecated production `.env` authority or fail-open governance posture
5. customer-specific dashboards, bespoke UI work, or unsupported deployment topologies

## Escalation Path

Escalation is deterministic and owner-led.

1. `L1` Customer operator:
   - startup issues
   - app-root or registry-path mistakes
   - bootstrap env mistakes
   - mutation gate state mistakes
2. `L2` Customer platform or security owner:
   - tenant config mistakes
   - Graph permission issues
   - approval backend configuration
   - OPA availability
   - credential rotation or security incidents
3. `L3` SmartHaus support or engineering:
   - reproducible defects in the canonical standalone path
   - reproducible defects in the supported 9-action baseline
   - documentation defects that block correct operator execution
4. `L4` Joint release decision:
   - enterprise release certification remains blocked until the live evidence and release-gate requirements in `P3A` and `P3B` are satisfied

Escalation rule:

If an issue cannot be reproduced on the canonical standalone path with the documented supported surface, default ownership remains with the customer environment until proven otherwise.

## Ownership Matrix

| Duty | Primary owner | SmartHaus role | Exit condition |
| --- | --- | --- | --- |
| Python runtime and package installation | Customer platform operations | Documented install guidance only | `m365-server` launches on the chosen host |
| App-root preparation and `registry/agents.yaml` presence | Customer platform operations | Clarify documented app-root contract | Server resolves registry and does not exit on startup |
| Tenant YAML and production identity authority | Customer platform operations | Clarify canonical contract only | Runtime points at the intended tenant-scoped config source |
| Secret injection and certificate lifecycle | Customer security/platform operations | Product guidance only | Secrets are externalized and usable without checked-in values |
| Initial smoke validation (`/health`, log path, supported-surface confirmation) | Customer operator | Clarify expected outputs | Day-0 checklist is recorded complete |
| Policy engine and approval backend readiness | Customer platform operations | Reproduce product defects if configuration is correct | OPA and approvals surfaces behave as intended for target deployment |
| Mutation-window control | Customer operator with customer approver | Explain documented safety gates | Writes are enabled only in approved controlled windows |
| Audit-log review and retention routing | Customer operator/platform operations | Clarify current product audit behavior | `logs/ops_audit.log` and any configured forwarding path are verified |
| Reproducible defect inside canonical standalone v1 path | SmartHaus support/engineering | Primary fix owner | Defect is reproduced, fixed, or documented as not a product issue |
| Unsupported action requests or tenant-specific customization | Customer business/platform owner | Optional separate scoping only | Request is rejected from baseline support or separately scoped |

## Decision Summary

`P4B` closes the post-install operator gap by defining one bounded standalone operating model:

1. the customer operates the runtime and tenant
2. SmartHaus supports the documented canonical path and supported v1 surface
3. every day-0 and day-1 duty has a named owner
4. enterprise release remains gated by the live-evidence and certification requirements already defined in `P3A` and `P3B`
