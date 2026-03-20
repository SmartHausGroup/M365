# M365 Pilot Acceptance and Customer Handoff

**Status:** `D2` complete
**Date:** 2026-03-20
**Plan refs:** `plan:m365-enterprise-readiness-master-plan:R6`, `plan:m365-enterprise-readiness-master-plan:D2`
**Certified product boundary:** bounded standalone SMARTHAUS M365 v1 with exactly `9` supported actions

This document defines how SMARTHAUS and the customer close a bounded standalone M365 v1 pilot and transfer day-to-day operating ownership. It does not expand the supported surface, the auth posture, or the runtime claim beyond the existing certified product state.

## Pilot Success Criteria

The pilot is successful only if all of the following are true:

1. the customer confirms the bounded standalone `9`-action surface matches the pilot scope
2. the customer confirms the canonical production authority is tenant YAML selected by `UCP_TENANT`
3. the customer confirms the approved runtime path is the standalone `m365-server` deployment model
4. the customer verifies the required operator roles are named:
   - runtime owner
   - approval owner
   - security owner
5. the customer verifies the approvals backend is reachable for the configured deployment
6. the customer verifies audit output is reachable and reviewable for the governed runtime path
7. the customer completes at least one bounded read-only validation pass across the supported surface relevant to the pilot
8. the customer completes at least one bounded controlled mutation window only for the supported actions approved for the pilot
9. no pilot success criterion depends on unsupported actions, the broader `260`-action universe, or customer-specific custom workflows outside the baseline product

## Acceptance Checklist

Pilot acceptance is complete only when every item below is checked:

1. [ ] customer acknowledges the supported surface is exactly the `9` actions defined in `docs/commercialization/m365-v1-supported-surface.md`
2. [ ] customer acknowledges unsupported actions are roadmap or separately scoped work only
3. [ ] customer acknowledges operator identity is Entra-authenticated and Graph execution is `app_only`
4. [ ] customer acknowledges certificate-backed executors are the preferred production posture
5. [ ] customer validates tenant YAML, secret injection, and approvals configuration on the target environment
6. [ ] customer validates the standalone launcher and app-root bootstrap path
7. [ ] customer validates read-only supported actions required by the pilot
8. [ ] customer validates any approved mutation-bearing supported actions in a controlled change window
9. [ ] customer validates approval creation, approval readback, and audit evidence where the deployment expects approval-bearing governance behavior
10. [ ] customer accepts the documented support boundary and escalation path

## Responsibility Matrix

| Duty | Primary owner | SMARTHAUS role | Exit condition |
| --- | --- | --- | --- |
| Tenant readiness, consent, and runtime environment | Customer platform/security | Clarify documented contract | Environment can run the certified standalone path |
| Tenant YAML, approvals target, and secret injection | Customer platform/security | Product guidance only | Runtime resolves the intended bounded tenant contract |
| Pilot scope discipline inside the `9`-action boundary | Customer business + platform owner | Enforce documented product boundary | Pilot does not depend on unsupported actions |
| Controlled validation windows for mutation-bearing actions | Customer operator + approver | Clarify supported controls only | Approved write windows are documented and bounded |
| Runtime defects inside the supported standalone path | SMARTHAUS engineering | Primary fix owner | Defect is reproduced, fixed, or classified outside product scope |
| Day-to-day post-handoff operation | Customer operator | Maintenance-only support | Customer owns normal runtime execution |
| Security incidents, secret rotation, and certificate lifecycle | Customer security/platform | Product guidance only | Security custody remains customer-owned |
| Release-packet, boundary, and support-doc maintenance | SMARTHAUS | Primary documentation owner | Product docs stay aligned to shipped repo state |

## Handoff Checklist

The customer handoff is complete only when the following are true:

1. the customer has named the runtime owner, approval owner, and security owner
2. the customer has the canonical install and bootstrap docs
3. the customer has the bounded enterprise collateral pack
4. the customer has this pilot acceptance and handoff document
5. the customer has access to the certification packet for the validated standalone release candidate
6. the customer understands the escalation boundary:
   - customer owns tenant and runtime operations
   - SMARTHAUS owns reproducible defects inside the documented supported path
7. the customer understands that unsupported actions, bespoke workflows, and customer-specific customization are outside baseline support unless separately approved
8. the customer confirms who signs off future production mutation windows
9. the customer confirms who monitors approvals and audit evidence after handoff

## Sign-Off Model

The handoff sign-off model is intentionally simple and owner-based.

Required customer sign-off:

1. platform/runtime owner signs that the documented standalone deployment is installed and understood
2. security owner signs that tenant custody, secret handling, certificate lifecycle, and approval ownership are assigned
3. business or pilot owner signs that the pilot scope is acceptable within the bounded `9`-action product claim

Required SMARTHAUS sign-off:

1. product or delivery owner signs that the pilot materials match the certified standalone product boundary
2. engineering signs that the shipped release candidate and certification packet are the ones being handed off

Sign-off rule:

The pilot is accepted and handoff is complete only when both the customer-side owners and the SMARTHAUS delivery side record agreement on the same bounded product scope, support boundary, and operating model.

## Residual Handoff Risks

1. customer-specific workflows, policy authoring, and dashboard customization still require separate scoping
2. future expansion beyond the `9`-action surface requires a new supported-surface and certification update, not a handoff-only change
3. this handoff model closes the repo-side launch-readiness plan; it does not replace customer contracting, procurement, or change-management policy
