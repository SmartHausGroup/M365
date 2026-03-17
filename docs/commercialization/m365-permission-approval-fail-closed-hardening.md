# M365 Permission, Approval, and Fail-Closed Hardening

**Status:** `P2B` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R3`, `plan:m365-enterprise-commercialization-readiness:P2B`

This document defines the control-boundary posture required to describe standalone M365 v1 honestly to an enterprise buyer. It distinguishes currently implemented control surfaces from the hardening expectations required for enterprise acceptance.

Deterministic control rule for this repository state:

`EnterpriseControlBoundary = PermissionTierRule + ApprovalRule + FailClosedRule + ExceptionPath`

If a privileged or high-risk path lacks one of those four elements, that path is not enterprise-ready and must be documented as a gap.

## Permission Tiers

The repository already contains a permission-tier model:

1. Tier definitions live in `registry/permission_tiers.yaml`.
2. Tenant-specific user-to-tier mapping lives in tenant configuration via `tenant_config.permission_tiers`.
3. Enforcement logic lives in `src/smarthaus_common/permission_enforcer.py`.

### Current tier model

| Tier | Risk class | Intended scope |
| --- | --- | --- |
| `global_admin` | critical | Full M365/UCP administrative access, with confirmations and audit still active |
| `department_admin` | high | Department-scoped administration without org-wide security, compliance, or admin rights |
| `power_user` | medium | Broad read and limited write access for productivity scenarios |
| `standard_user` | low | Basic productivity actions only |

### Hardening interpretation

1. Tier definitions are a real governance surface and should remain the primary user-level authorization model for the UCP/MCP side.
2. Critical domains such as `admin.*`, `security.*`, `compliance.*`, `ca.*`, and `audit.*` should remain restricted to `global_admin` unless an explicit exception is approved later.
3. Department or productivity tiers must not inherit org-wide mutation authority by convenience.

### Current gaps in tier enforcement

The tier model is present, but the current runtime posture is not fully fail-closed:

1. If `permission_tiers.yaml` is missing, `check_user_permission()` falls back to permissive behavior.
2. If `user_email` is missing, `check_user_permission()` currently allows the action instead of denying.
3. If tenant config cannot be loaded, `check_user_permission()` currently allows the action instead of denying.

Commercial consequence:

These permissive fallbacks are not acceptable as an enterprise-ready authorization claim. They must be treated as current hardening gaps, not as supported production behavior.

## Approval Boundaries

Approval behavior currently exists in the ops-adapter, but not every high-risk surface shares the same boundary.

### Current explicit approval requirements

Current OPA and registry-backed approval paths include:

1. `m365-administrator.users.disable`
2. `website-manager.deployment.production`
3. `hr-generalist.employee.offboard`
4. `outreach-coordinator.email.send_bulk` when recipients exceed `100`

Evidence sources:

1. `policies/ops.rego`
2. `policies/agents/*.rego`
3. `src/ops_adapter/main.py`
4. `src/ops_adapter/approvals.py`
5. `registry/agents.yaml`

### Control-boundary classification

| Surface | Current control boundary | Enterprise interpretation |
| --- | --- | --- |
| Ops-adapter privileged actions | OPA allow/deny + approval queue where configured | Real approval surface, but must be paired with fail-closed OPA posture |
| Teams/Graph approval workflow | Approval records and status transitions via approvals store | Real control surface, but depends on configured backend and signatures where enabled |
| Instruction API mutating actions (`create_site`, `create_team`, `add_channel`, `provision_service`, `reset_user_password`) | Auth plus `ALLOW_M365_MUTATIONS` gate, but no equivalent built-in approval queue | Mutation-gated, not approval-hardened |

Commercial consequence:

Standalone M365 v1 may claim explicit approval handling for the ops-adapter surface. It may not claim that every high-risk instruction-API mutation is already covered by the same approval model.

## Fail-Closed Rules

Enterprise commercialization requires the following rules to be explicit.

### Supported fail-closed rules

1. Unknown instruction actions fail closed.
2. Missing required auth context for the instruction contract fails closed.
3. Mutating instruction actions fail closed when `ALLOW_M365_MUTATIONS` is not enabled.
4. Idempotency conflicts fail closed.
5. Denied or rate-limited OPA decisions fail closed in the ops-adapter request path.

### Current fail-open or permissive exceptions

The current repo also contains behavior that is not enterprise-grade fail-closed:

1. `src/ops_adapter/policies.py` can return allow on OPA errors when `fail_open` is enabled or inferred from non-production environment.
2. `src/ops_adapter/app.py` can return an `"ok"` stub result for Graph failures when `opa.fail_open` is active.
3. `src/smarthaus_common/permission_enforcer.py` has permissive fallbacks when identity, tenant config, or tier definitions are unavailable.
4. Audit forwarding in `src/ops_adapter/audit.py` is best-effort and does not fail the caller.

### Enterprise commercialization rule

For enterprise posture, the following must be treated as required hardening expectations:

1. OPA unavailability in enterprise production must deny, not allow.
2. Missing user identity for governed actions must deny, not allow.
3. Missing tenant config or missing permission-tier definitions for governed actions must deny, not allow.
4. Fail-open stub execution paths must be classified as non-enterprise behavior.
5. Mutation-gated instruction actions without approval boundaries must be described as mutation-gated only, not as fully approval-hardened.

## Exceptions and Escalations

Exceptions must be explicit and narrow.

### Allowed non-enterprise exceptions

The following may exist for local development, sandbox, or controlled pilot work, but are not part of the enterprise claim:

1. `OPA_FAIL_OPEN=true`
2. delegated-auth local operator flows
3. local `.env`-driven bootstrap
4. approval-less use of instruction-API mutations in a controlled operator environment

### Escalation rules

1. Any request that would rely on missing identity, missing tiers, missing OPA, or fail-open Graph stubs must be escalated as a governance exception.
2. Any high-risk action without an explicit approval owner must be treated as not enterprise-ready.
3. Any change that broadens approval scope, weakens deny behavior, or expands privileged tiers requires a later approved runtime hardening phase, not a documentation-only waiver.

### Commercialization boundary

SmartHaus may claim:

1. a defined permission-tier model exists
2. a defined approval model exists for the ops-adapter surface
3. mutation gating exists for instruction-API mutating actions
4. fail-closed expectations are now explicitly documented

SmartHaus may not claim:

1. fully fail-closed enterprise enforcement across every governed surface today
2. equivalent approval hardening across both ops-adapter and instruction API today
3. enterprise-ready permissive fallback behavior
