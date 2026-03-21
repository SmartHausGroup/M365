# M365 Enterprise Collateral Pack

**Status:** `D1` complete
**Date:** 2026-03-20
**Plan refs:** `plan:m365-enterprise-readiness-master-plan:R6`, `plan:m365-enterprise-readiness-master-plan:D1`
**Certification state:** `C2 GO` for bounded standalone M365 v1 candidate `52ca494`

This document is the buyer-facing and delivery-facing collateral pack for the standalone SMARTHAUS M365 v1 module. It is intentionally narrower than the broader repo vision. If any statement here conflicts with `docs/commercialization/m365-v1-supported-surface.md`, the supported-surface document wins.

## Product Summary

SMARTHAUS M365 v1 is a governed Microsoft 365 operations module for a narrow set of high-value administrative actions across identity, Teams, and SharePoint. The launch product is intentionally bounded to exactly `9` supported actions and is not a claim of broad Microsoft Graph or full M365 administration coverage.

Primary buyer:

1. head of IT
2. M365 platform owner
3. identity and collaboration lead
4. enterprise automation owner responsible for M365 governance

Core value:

1. reduce repetitive M365 operator work without adding non-M365 tool sprawl
2. keep control boundaries inside existing enterprise identity, approvals, and audit models
3. ship a deterministic, policy-gated M365 operating surface instead of a generic super-connector

Positioning statement:

SMARTHAUS M365 v1 is a certified standalone M365 operations module that exposes exactly `9` supported actions through a governed runtime with Entra-authenticated operators, bounded executor identities, approval-aware mutations, and retained live-tenant certification evidence.

Commercial claim boundary:

1. this is a standalone module, not the full 39-persona workforce vision
2. this is compatible with the broader TAI licensed-module model, but it is sellable as a bounded standalone M365 capability today
3. this does not claim full tenant administration, full Graph coverage, or all `260` actions in the broader capability universe

## Security and Compliance

The current security and governance posture for the standalone module is:

1. production authority is tenant YAML selected by `UCP_TENANT`
2. operator identity is Microsoft Entra ID
3. Microsoft Graph execution is `app_only`
4. certificate auth is the enterprise-preferred credential posture
5. client secrets are transitional only and not the long-term production target
6. approval-aware mutations, audit evidence, and bounded executor routing are part of the certified runtime path

Control model:

1. human actor identity is preserved separately from the executor service identity
2. mutation-bearing actions remain gated by approvals, policy, audit, and `ALLOW_M365_MUTATIONS`
3. the approvals backend is pinned to a real SharePoint list target instead of relying on unstable URL discovery
4. the standalone release gate is already closed to `GO` for the bounded launch claim recorded in the certification packet

Evidence-backed security posture:

1. the supported surface is live-certified through `C1A` to `C1D`
2. the release decision is formally closed through `C2`
3. engineering, security, and release-owner sign-off are retained in the certification packet

Explicit exclusions:

1. this pack is not a claim of unified enterprise audit coverage for every historic repo surface
2. this pack is not a claim of customer-specific policy authoring or tenant-specific workflow customization
3. this pack is not a claim that delegated auth is the default enterprise production posture

## Supported Action Matrix

Only the actions below are supported for standalone M365 v1 sales, pilot, and delivery commitments.

| Action | Domain | Mutation | Delivery use | Runtime controls |
| --- | --- | --- | --- | --- |
| `list_users` | `identity` | No | operator inventory and user lookup | bounded executor, audit, live-certified |
| `get_user` | `identity` | No | user inspection and support lookup | bounded executor, audit, live-certified |
| `reset_user_password` | `identity` | Yes | controlled credential reset | approval-aware governance path, audit, live-certified |
| `list_teams` | `teams` | No | collaboration inventory | bounded executor, audit, live-certified |
| `list_sites` | `sharepoint` | No | SharePoint inventory | bounded executor, audit, live-certified |
| `create_site` | `sharepoint` | Yes | controlled site provisioning | mutation gate, approvals, audit, live-certified |
| `create_team` | `teams` | Yes | controlled team provisioning | mutation gate, approvals, audit, live-certified |
| `add_channel` | `teams` | Yes | controlled channel expansion | mutation gate, approvals, audit, live-certified |
| `provision_service` | `sharepoint` | Yes | bounded service workspace provisioning | mutation gate, approvals, audit, live-certified |

Sales and delivery rule:

1. do not promise unsupported actions
2. do not market the broader `260`-action universe as launch scope
3. treat unsupported actions as roadmap or separately scoped work only

## Operating Model

### Architecture Summary

The certified standalone path is:

1. operator authenticates with Microsoft Entra ID
2. governed runtime evaluates policy, approval, and audit requirements
3. runtime selects the bounded executor domain required for the action
4. executor performs the M365 action through Microsoft Graph
5. approval and audit evidence are retained in the bounded standalone packet and runtime sinks

This operating model supports named digital employees and persona-aware delegation, but the launch claim is still bounded to the `9` certified actions above.

### Deployment Summary

The canonical standalone deployment model is:

1. install the Python package
2. launch with `m365-server`
3. bootstrap from the app root
4. resolve production authority through tenant YAML, bounded executors, and externalized secret material

The module remains compatible with the broader TAI licensed-module model, but the standalone launch story remains valid without requiring the customer to buy a broader platform rollout first.

### Delivery and Ownership Summary

Customer-owned responsibilities:

1. tenant readiness, consent, and environment configuration
2. tenant YAML values, approvals target, and secret injection
3. runtime hosting, operator staffing, and production change control
4. day-to-day execution decisions inside the supported surface

SMARTHAUS-owned baseline responsibilities:

1. defects in the documented standalone path
2. defects inside the supported `9`-action boundary
3. maintenance of the bounded product contract, runtime, and release evidence model

### Residual Commercial Risks

1. this pack closes launch collateral, but customer-specific pilot execution, contracting, and change-management remain outside repo-side closeout
2. unsupported actions outside the `9`-action boundary still require separate scoping or a future release
3. customer-specific policy, workflow, or dashboard customization remains outside the baseline standalone support boundary unless separately approved
