# Plan: M365 Repo — Enterprise Readiness Master Plan

**Plan ID:** `m365-enterprise-readiness-master-plan`
**Status:** Active (`A1`, `A2`, `A3`, `A4`, `B1`, and `B2` complete on 2026-03-17; `B3` next)
**Date:** 2026-03-17
**Owner:** SmartHaus
**Execution plan reference:** `plan:m365-enterprise-readiness-master-plan:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — production-ready, policy-gated, auditable, self-service M365 orchestration.
**Historical lineage:** absorbs `m365-enterprise-commercialization-readiness` as the active enterprise-readiness critical path on 2026-03-17.

**MA process:** This master plan includes commercialization, runtime hardening, live certification, and launch-readiness work. MA phases are required only if a future execution unit introduces new algorithmic behavior, mathematical guarantees, or notebook-governed runtime logic beyond the current contract surface.

---

## Objective

Define and execute the full critical path required to make the current M365 capability commercially honest, operationally supportable, technically hardened, and enterprise-ready as a standalone deterministic module.

## Decision Rule

Enterprise readiness for standalone M365 v1 is not satisfied by documentation alone.

For this repository state:

`EnterpriseReady = ProductBoundaryLocked ∧ RuntimeHardeningImplemented ∧ LiveTenantCertificationGreen ∧ LaunchReadinessComplete`

If any one of those factors is incomplete, the standalone module remains `NO-GO` for enterprise readiness closure.

## Execution Status

- `A1` complete on 2026-03-17: imported the supported-surface and buyer/operator boundary work from `P0A` and `P0B` in `docs/commercialization/m365-v1-supported-surface.md` and `docs/commercialization/m365-v1-positioning-and-north-star-delta.md`.
- `A2` complete on 2026-03-17: imported the canonical config-contract and auth/secret posture work from `P1A` and `P1B` in `docs/commercialization/m365-canonical-config-contract.md` and `docs/commercialization/m365-config-migration-and-auth-policy.md`.
- `A3` complete on 2026-03-17: imported the governance, audit, live-validation, and release-gate definition work from `P2A`, `P2B`, `P3A`, and `P3B` in `docs/commercialization/m365-audit-and-governance-evidence-model.md`, `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`, `docs/commercialization/m365-live-tenant-validation-matrix.md`, and `docs/commercialization/m365-release-gates-and-certification.md`.
- `A4` complete on 2026-03-17: imported the packaging, onboarding, runbooks, and support-boundary work from `P4A` and `P4B` in `docs/commercialization/m365-packaging-install-bootstrap.md` and `docs/commercialization/m365-operator-onboarding-and-support-boundary.md`.
- `B1` complete on 2026-03-17: added the repo-local `configs/ma_phases.yaml` bridge required by governed code-edit validation, made `UCP_TENANT`-selected tenant config the runtime authority in `src/smarthaus_common/config.py`, extended tenant lookup to the sibling `UCP/tenants` directory in `src/smarthaus_common/tenant_config.py`, converted the standalone server and legacy dashboard entrypoints to shared bootstrap-only dotenv loading, updated `src/provisioning_api/routers/m365.py`, `src/provisioning_api/m365_provision.py`, and `src/provisioning_api/enterprise_dashboard.py` to honor tenant-first authority, and added targeted precedence coverage in `tests/test_env_loading.py`.
- `B2` complete on 2026-03-17: hardened the active ops-adapter and shared permission-enforcement path so missing acting identity, missing tenant selection, missing tenant config, missing permission tiers, denied OPA decisions, and missing approval-owner configuration fail closed by default, expanded high-risk `m365-administrator` approval requirements in `policies/ops.rego` and `registry/agents.yaml`, removed inferred non-production OPA fail-open behavior, and added targeted deny/approval coverage in `tests/test_ops_adapter.py` and `tests/test_policies.py`.
- `B3` is the next execution unit.

## Open Enterprise Blockers

The repo is not enterprise-ready yet because the remaining critical-path blockers are implementation and evidence blockers, not merely documentation blockers:

1. Admin audit remains incomplete for enterprise review.
2. Live-tenant certification evidence has not yet been executed and assembled.
3. Launch collateral and pilot handoff remain downstream of the runtime and certification blockers.

## Scope

### In scope

- Preserve the narrow, honest standalone M365 v1 product boundary.
- Convert the documented production config contract into the real runtime authority.
- Harden permission, approval, fail-closed, and audit behavior for enterprise review.
- Execute live-tenant certification and release-gate closure for the supported v1 surface.
- Produce the final collateral and handoff artifacts only after the true readiness blockers are addressed.
- Synchronize `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`, and `Operations/ACTION_LOG.md` whenever the active critical path changes.

### Out of scope

- Implementing the remaining planned M365 capability universe solely to claim breadth.
- Broad SAID or UCP rework outside direct M365 dependency requirements.
- New inference algorithms or unrelated mathematical systems.
- Unapproved tenant-impacting activity beyond explicitly approved validation or certification work.

## Requirements

### R1 — Integrated enterprise-readiness control plane

- Establish one active master plan for standalone enterprise readiness.
- Prevent documentation-only completion from being misread as full readiness closure.

### R2 — Runtime configuration authority remediation

- Make tenant-scoped configuration the actual runtime authority.
- Remove ambiguous production reliance on legacy `.env` loading paths.

### R3 — Fail-closed governance and approval remediation

- Enforce enterprise-safe deny behavior when policy, identity, tier, or approval prerequisites are missing.
- Eliminate approval ambiguity for supported high-risk actions.

### R4 — Admin audit and evidence-surface remediation

- Replace incomplete or snapshot-style administrative audit behavior with an enterprise-reviewable audit surface.
- Align retained audit evidence with the claims made in commercialization documents.

### R5 — Live-tenant certification and release closure

- Execute the required supported-surface validation in a controlled non-production tenant.
- Produce the release certification packet and explicit `GO` or `NO-GO` outcome.

### R6 — Launch collateral and handoff

- Produce the enterprise-facing collateral, pilot acceptance, and customer handoff artifacts after runtime and certification blockers are addressed.

### R7 — Governance synchronization

- Keep the old commercialization artifacts historically traceable while ensuring the master plan is the only active critical path.

## Integrated Execution Stack

### A — Imported Foundation and Product Boundary

This phase is complete and imported from the absorbed commercialization plan. It remains authoritative as historical foundation work, not as the active critical path by itself.

#### A1 — Product Boundary and Positioning

**Goal:** Lock the supported v1 product claim, non-goals, buyer, operator, and deployment model.

**Outputs:**
- supported-action matrix
- unsupported-action matrix
- product-claim boundary
- buyer/operator/deployment definition

#### A2 — Canonical Config Contract and Auth Posture

**Goal:** Define the supported production contract before runtime remediation begins.

**Outputs:**
- canonical config contract
- source-precedence model
- secret-management policy
- auth-mode policy and deprecation map

#### A3 — Governance Boundary and Certification Model

**Goal:** Define the audit, approval, fail-closed, live-validation, and release-gate rules that runtime must satisfy.

**Outputs:**
- governance-evidence model
- fail-closed and approval boundary
- live-tenant validation matrix
- release-gate and certification model

#### A4 — Packaging and Operator Model

**Goal:** Define the install path, onboarding flow, runbooks, and support boundary for the standalone runtime.

**Outputs:**
- canonical package/install/bootstrap path
- onboarding checklist
- day-0/day-1 runbooks
- support boundary and ownership matrix

### B — Runtime Hardening Implementation

This phase is now the active critical path.

#### B1 — Runtime Config Authority Remediation

**Goal:** Make the documented production contract the real runtime authority everywhere it matters.

**Status:** ✅ Complete (2026-03-17)

**Outputs:**
- canonical config-loader implementation path
- legacy dotenv path classification in runtime
- runtime tests proving tenant-scoped authority wins
- implementation notes mapped back to `A2`

**Completion notes:**
- Added local `configs/ma_phases.yaml` so UCP `validate_action` resolves this repo at MA phase `9` instead of `0`.
- `src/smarthaus_common/config.py` now resolves Graph credentials and SharePoint hostname from the selected tenant config first, with env as fallback only.
- `src/smarthaus_common/tenant_config.py` now searches the sibling `UCP/tenants` directory in this workspace.
- Runtime entrypoints now use shared bootstrap-only dotenv loading rather than ad hoc direct `load_dotenv(...)` authority.
- Targeted verification passed: `python3 -m py_compile ...`, `PYTHONPATH=src pytest tests/test_env_loading.py`, and `git diff --check`.

#### B2 — Fail-Closed Governance and Approval Remediation

**Goal:** Bring runtime permission, approval, and policy behavior up to the enterprise posture documented in `A3`.

**Status:** ✅ Complete (2026-03-17)

**Outputs:**
- fail-closed runtime behavior for missing policy/identity/config preconditions
- approval-boundary remediation for supported mutating actions
- targeted tests for deny behavior and approval gating
- implementation notes mapped back to `A3`

**Completion notes:**
- `src/smarthaus_common/permission_enforcer.py` now denies by default when acting identity, tenant selection, tenant config, or permission-tier definitions are missing, with `M365_PERMISSION_FAIL_OPEN=true` as an explicit non-enterprise override only.
- `src/ops_adapter/policies.py` no longer infers fail-open behavior outside production; `OPA_FAIL_OPEN=true` must be set explicitly.
- `src/ops_adapter/main.py` and `src/ops_adapter/app.py` now require resolved acting identity and tenant context, enforce permission tiers before execution, merge approval requirements from OPA and tier overrides, and deny `approval_configuration_missing` when high-risk actions lack configured approvers.
- `src/ops_adapter/approvals.py`, `policies/ops.rego`, and `registry/agents.yaml` now carry explicit approval-owner metadata for the expanded set of high-risk `m365-administrator` mutations.
- Targeted verification passed: `python3 -m py_compile ...`, `PYTHONPATH=src pytest -q tests/test_ops_adapter.py tests/test_policies.py`, and `git diff --check`.

#### B3 — Admin Audit and Evidence-Surface Remediation

**Goal:** Close the current admin-audit gap so the runtime has an enterprise-reviewable audit surface.

**Outputs:**
- remediated admin audit behavior
- normalized evidence map across instruction and admin surfaces
- targeted audit tests or verification outputs
- implementation notes mapped back to `A3`

### C — Live-Tenant Certification

#### C1 — Live-Tenant Certification Execution

**Goal:** Execute the supported v1 validation matrix against a controlled non-production tenant.

**Outputs:**
- live validation transcript set
- evidence packet for supported actions and governance surfaces
- controlled-environment operator checklist
- pass/fail summary tied to `A3`

#### C2 — Release Certification Packet and Decision

**Goal:** Turn live evidence into one formal release decision.

**Outputs:**
- release certification packet
- evidence-retention index
- explicit `GO` or `NO-GO` decision record
- blocker list if certification remains red

### D — Launch Readiness

#### D1 — Enterprise Collateral Pack

**Goal:** Produce buyer-facing and delivery-facing collateral only after runtime and certification are in acceptable shape.

**Outputs:**
- product one-pager
- security and compliance posture brief
- supported-action matrix for sales and delivery
- architecture and operating-summary brief

#### D2 — Pilot Acceptance and Customer Handoff

**Goal:** Define how SmartHaus and the customer close the pilot and transfer operating ownership.

**Outputs:**
- pilot acceptance checklist
- pilot success criteria
- customer handoff checklist
- customer-responsibility matrix
- sign-off model

## Critical-Path Rule

`D1` and `D2` are not allowed to imply enterprise readiness if `B1`, `B2`, `B3`, `C1`, or `C2` remain incomplete or red.

This master plan exists specifically to prevent collateral work from outrunning runtime reality.

## Legacy Mapping

| Historical commercialization phase | Master-plan destination |
| --- | --- |
| `P0A`, `P0B` | `A1` |
| `P1A`, `P1B` | `A2` |
| `P2A`, `P2B`, `P3A`, `P3B` | `A3` |
| `P4A`, `P4B` | `A4` |
| `P5A` | `D1` |
| `P5B` | `D2` |

The absorbed plan remains in the repo for traceability, but no new execution should be scheduled there.

## Validation

- `Operations/EXECUTION_PLAN.md` lists this master plan as the active enterprise-readiness initiative.
- `plans/m365-enterprise-commercialization-readiness/` is explicitly marked as absorbed/historical.
- The prompt pair for this master plan exists.
- Prompt pairs exist for the open execution units `B1`, `B2`, `B3`, `C1`, `C2`, `D1`, and `D2`.
- No future phase may claim enterprise readiness closure unless `B`, `C`, and `D` all satisfy their exit criteria.

## Success Criteria

- There is one active enterprise-readiness plan for standalone M365 v1.
- Runtime config authority matches the documented production contract.
- Governance and approval behavior is fail-closed in the enterprise posture.
- Admin audit is enterprise-reviewable and traceable.
- Live-tenant certification evidence exists and the release decision is explicit.
- Launch collateral and pilot handoff are produced only after the true blockers are addressed.
