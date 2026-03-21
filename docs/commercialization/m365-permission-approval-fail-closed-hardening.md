# M365 Permission, Approval, and Fail-Closed Hardening

**Status:** `A3` imported; runtime synchronized through `B2`; identity architecture synchronized through `B5A`
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R3`, `plan:m365-enterprise-commercialization-readiness:P2B`, `plan:m365-enterprise-readiness-master-plan:B2`, `plan:m365-enterprise-readiness-master-plan:B5A`, `plan:m365-enterprise-readiness-master-plan:R7`, `plan:m365-enterprise-readiness-master-plan:R9`

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
4. Enterprise actor identity should come from validated Microsoft Entra ID claims, not from local synthetic user state.
5. Tenant config now supports both direct user-to-tier mappings and Entra group-to-tier mappings; target enterprise posture should prefer Entra group-to-tier bindings where SmartHaus group hygiene is mature.

### Current runtime state after `B2` and `B5C`

The active ops-adapter and shared permission-enforcement path is now fail-closed for the core authorization prerequisites:

1. If `registry/permission_tiers.yaml` is missing, `check_user_permission()` denies with `permission_tiers_missing` unless the explicit non-enterprise override `M365_PERMISSION_FAIL_OPEN=true` is enabled.
2. If `user_email` is missing, `check_user_permission()` denies with `user_identity_missing` unless `M365_PERMISSION_FAIL_OPEN=true` is enabled.
3. If `UCP_TENANT` is missing, `check_user_permission()` denies with `tenant_selection_missing` unless `M365_PERMISSION_FAIL_OPEN=true` is enabled.
4. If tenant config cannot be loaded, `check_user_permission()` denies with `tenant_config_unavailable:*` unless `M365_PERMISSION_FAIL_OPEN=true` is enabled.
5. The active ops-adapter request path now requires a resolved acting identity and tenant context before governed action execution.
6. The active ops-adapter request path now resolves the effective permission tier from either an explicit SmartHaus user mapping or a configured Entra group mapping.
7. Approval records created on the governed ops-adapter path now preserve actor, tier, groups, tenant, and executor identity metadata for later review.

Commercial consequence:

For the ops-adapter and shared permission-enforcement surface, these prerequisites are now hardened runtime behavior rather than documentation-only expectations. Equivalent approval and fail-closed guarantees still do not automatically extend to every legacy instruction-API mutation path.

Identity consequence after `B5C`:

1. The actor whose tier is enforced should be a validated SmartHaus Entra user.
2. The app-only executor identity should not be treated as the permission-tier subject.
3. Group-derived administrative authority is now supported on the governed runtime path when the tenant contract maps Entra groups to tiers.

## Approval Boundaries

Approval behavior currently exists in the ops-adapter, but not every high-risk surface shares the same boundary.

### Current explicit approval requirements

Current OPA and registry-backed approval paths include:

1. `m365-administrator.users.disable`
2. `m365-administrator.users.create`
3. `m365-administrator.users.update`
4. `m365-administrator.groups.create`
5. `m365-administrator.groups.add_member`
6. `m365-administrator.teams.create`
7. `m365-administrator.teams.add_channel`
8. `m365-administrator.sites.provision`
9. `m365-administrator.licenses.assign`
10. `website-manager.deployment.production`
11. `hr-generalist.employee.offboard`
12. `outreach-coordinator.email.send_bulk` when recipients exceed `100`

Evidence sources:

1. `policies/ops.rego`
2. `policies/agents/*.rego`
3. `src/ops_adapter/main.py`
4. `src/ops_adapter/approvals.py`
5. `registry/agents.yaml`

### Control-boundary classification

| Surface | Current control boundary | Enterprise interpretation |
| --- | --- | --- |
| Ops-adapter privileged actions | Acting identity + tenant resolution + permission tier check + OPA allow/deny + approval queue where configured | Real approval surface with fail-closed prerequisite enforcement for the active request path |
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
5. Missing acting identity, missing tenant selection, missing tenant config, or missing permission-tier definitions fail closed in the active ops-adapter request path unless an explicit non-enterprise override is enabled.
6. Denied or rate-limited OPA decisions fail closed in the ops-adapter request path.
7. Approval-required actions without configured approval owners fail closed with `approval_configuration_missing`.

### Current fail-open or permissive exceptions

The current repo still contains behavior that is not enterprise-grade fail-closed:

1. `src/ops_adapter/policies.py` can still return allow on OPA errors if `OPA_FAIL_OPEN=true` is set explicitly as a non-enterprise override.
2. `src/smarthaus_common/permission_enforcer.py` can still allow on missing identity, tenant context, or tier config if `M365_PERMISSION_FAIL_OPEN=true` is set explicitly as a non-enterprise override.
3. Audit forwarding in `src/ops_adapter/audit.py` is best-effort and does not fail the caller.
4. The instruction API mutating actions remain mutation-gated rather than approval-hardened.

### Enterprise commercialization rule

For enterprise posture, the following must be treated as required hardening expectations:

1. OPA unavailability in enterprise production must deny, not allow, unless the repo is intentionally running under the explicit non-enterprise override `OPA_FAIL_OPEN=true`.
2. Missing user identity for governed actions must deny, not allow, unless the repo is intentionally running under the explicit non-enterprise override `M365_PERMISSION_FAIL_OPEN=true`.
3. Missing tenant config or missing permission-tier definitions for governed actions must deny, not allow, unless the repo is intentionally running under the explicit non-enterprise override `M365_PERMISSION_FAIL_OPEN=true`.
4. Mutation-gated instruction actions without approval boundaries must be described as mutation-gated only, not as fully approval-hardened.

## Exceptions and Escalations

Exceptions must be explicit and narrow.

### Allowed non-enterprise exceptions

The following may exist for local development, sandbox, or controlled pilot work, but are not part of the enterprise claim:

1. `OPA_FAIL_OPEN=true`
2. `M365_PERMISSION_FAIL_OPEN=true`
3. delegated-auth local operator flows
4. local `.env`-driven bootstrap
5. approval-less use of instruction-API mutations in a controlled operator environment

### Escalation rules

1. Any request that would rely on missing identity, missing tiers, missing OPA, or fail-open Graph stubs must be escalated as a governance exception.
2. Any high-risk action without an explicit approval owner must be treated as not enterprise-ready.
3. Any change that broadens approval scope, weakens deny behavior, or expands privileged tiers requires a later approved runtime hardening phase, not a documentation-only waiver.

### Commercialization boundary

SmartHaus may claim:

1. a defined permission-tier model exists
2. a defined approval model exists for the ops-adapter surface, including explicit high-risk `m365-administrator` mutation approvals
3. mutation gating exists for instruction-API mutating actions
4. fail-closed expectations are now explicitly documented and substantially implemented for the active ops-adapter request path

SmartHaus may not claim:

1. fully fail-closed enterprise enforcement across every governed surface today
2. equivalent approval hardening across both ops-adapter and instruction API today
3. enterprise-ready use of the explicit non-enterprise fail-open overrides
