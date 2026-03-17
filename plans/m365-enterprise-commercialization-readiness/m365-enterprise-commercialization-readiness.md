# Plan: M365 Repo — Enterprise Commercialization Readiness

**Plan ID:** `m365-enterprise-commercialization-readiness`
**Status:** Active (`P0A`, `P0B`, `P1A`, `P1B`, `P2A`, `P2B`, `P3A`, `P3B`, and `P4A` complete 2026-03-17; `P4B` next)
**Date:** 2026-03-17
**Owner:** SmartHaus
**Execution plan reference:** `plan:m365-enterprise-commercialization-readiness:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — production-ready, policy-gated, auditable, self-service M365 orchestration.

**MA process:** This plan is commercialization, configuration, governance, packaging, and validation work. MA phases are not required unless a phase introduces new algorithmic behavior, mathematical guarantees, or notebook-governed runtime logic beyond the current contract surface.

---

## Objective

Define the minimum set of M365-only changes required to make the current M365 capability commercially honest, operationally supportable, and enterprise-ready as a standalone deterministic module ASAP.

## Execution Status

- `P0A` complete on 2026-03-17: locked the standalone M365 v1 commercial boundary to the 9 implemented instruction actions in `docs/commercialization/m365-v1-supported-surface.md`, explicitly excluding the remaining 251 planned actions and the 5 notebook/spec-only group actions from launch claims.
- `P0B` complete on 2026-03-17: defined the standalone buyer, operator, positioning, and deployment model in `docs/commercialization/m365-v1-positioning-and-north-star-delta.md`, and synchronized `Operations/NORTHSTAR.md` so the broader AI Workforce vision no longer overclaims the standalone M365 v1 commercial boundary.
- `P1A` complete on 2026-03-17: inventoried the current config-loading surfaces, locked tenant YAML plus env-assisted secret fallback as the canonical production contract in `docs/commercialization/m365-canonical-config-contract.md`, and narrowed the env docs so `.env` is no longer described as the production authority.
- `P1B` complete on 2026-03-17: defined the migration path, auth-mode decision matrix, secret policy, certificate guidance, and legacy-surface deprecation map in `docs/commercialization/m365-config-migration-and-auth-policy.md`. The supported posture is now singular: tenant YAML selected by `UCP_TENANT` is the production authority, `app_only` is the default production auth mode, certificate auth is the enterprise-preferred credential model, client secret is transitional only, and delegated auth is local/test/support only.
- `P2A` complete on 2026-03-17: defined the audit-event model, governance-evidence model, current gap map, and enterprise acceptance boundary in `docs/commercialization/m365-audit-and-governance-evidence-model.md`. The repo now explicitly distinguishes the formally evidenced instruction API audit surface from the broader but only partially evidenced ops-adapter and admin audit surfaces, and it documents `snapshot_mode` admin audit as a real commercialization gap rather than an implied feature.
- `P2B` complete on 2026-03-17: defined the permission-tier posture, approval-boundary model, fail-closed rules, and exception/escalation boundary in `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`. The repo now explicitly documents that permission tiers and ops-adapter approvals exist, but permissive tier fallbacks, OPA fail-open paths, and approval-less instruction-API mutations remain hardening gaps rather than enterprise-ready claims.
- `P3A` complete on 2026-03-17: defined the live-tenant validation matrix, prerequisite set, evidence-artifact rules, and release-use boundary in `docs/commercialization/m365-live-tenant-validation-matrix.md`. The repo now explicitly separates mock/local MA confidence from live-tenant release evidence and blocks enterprise release claims from relying on mock-passing auth or idempotency artifacts.
- `P3B` complete on 2026-03-17: defined the ordered release-gate sequence, explicit go/no-go rules, evidence-retention expectations, and current deterministic certification outcome in `docs/commercialization/m365-release-gates-and-certification.md`. The repo now has an explicit rule that enterprise certification is `NO-GO` until the live evidence packet exists and the release certification packet is assembled and signed.
- `P4A` complete on 2026-03-17: defined the package variants, canonical standalone install path, bootstrap flow, environment setup split, and prerequisite set in `docs/commercialization/m365-packaging-install-bootstrap.md`. The repo now treats Python package install plus the `m365-server` launcher as the one canonical standalone path for the current repo state, while the TAI-hosted module form remains a compatible but non-canonical packaging variant.
- `P4B` is the next execution unit.

---

## Commercial Gap Summary

The current M365 repo is architecturally credible but not yet enterprise-commercial ready for a standalone offer because:

1. The marketable capability boundary is not locked to the proven v1 surface.
2. Production configuration is still split between a stronger tenant model and direct `.env` loading paths.
3. Some verification evidence can still pass in mock mode rather than tenant-backed certification mode.
4. Audit posture is incomplete for enterprise administration and governance review.
5. Packaging, onboarding, and enterprise collateral are not yet unified into one sellable operator path.

---

## Scope

### In scope

- Define and document the commercially supported M365 v1 action surface.
- Establish one canonical production configuration and identity model.
- Harden governance, audit, and fail-closed behavior for enterprise review.
- Produce live-tenant validation evidence and release-gate criteria.
- Define packaging, onboarding, runbooks, and support boundaries for a standalone M365 module.
- Create enterprise-facing commercial, security, and pilot-acceptance artifacts.
- Update `Operations/NORTHSTAR.md` if commercialization scope, target customer, or success metrics change materially.

### Out of scope

- Implementing the remaining planned capability universe solely to claim breadth.
- Broad SAID or UCP platform rework outside direct M365 dependency requirements.
- New inference algorithms, orchestration logic, or mathematical systems unrelated to commercialization readiness.
- Unapproved tenant-impacting provisioning beyond the validation scope explicitly approved later.

---

## Requirements

### R1 — Commercial boundary lock

- Lock the M365 v1 product claim to the currently proven and supportable action surface.
- Define explicit non-goals and unsupported actions.

### R2 — Canonical production config

- Replace ad hoc production reliance on repo-root `.env` semantics with a canonical tenant/config model.
- Keep `.env` only as a local development secret-injection path unless explicitly documented otherwise.

### R3 — Enterprise governance and audit hardening

- Define the required enterprise audit, approval, permission-tier, and fail-closed controls for the M365 runtime.
- Remove ambiguity between snapshot/admin inspection and real enterprise audit expectations.

### R4 — Live evidence and release gates

- Define tenant-backed validation requirements for auth, idempotency, audit, mutation gates, and supported actions.
- Separate mock validation from enterprise release acceptance.

### R5 — Packaging and onboarding

- Define the install, bootstrap, operator onboarding, environment setup, and support path for a standalone M365 module.
- Preserve alignment with the TAI-licensed module model while keeping the M365 product independently understandable.

### R6 — Commercial and governance synchronization

- Produce customer-facing product, security, operations, and pilot artifacts.
- Update `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`, and `Operations/ACTION_LOG.md` whenever commercialization scope changes require governance synchronization.

---

## Refined Execution Stack

The original `P0` through `P5` phases are directionally correct but too large for low-risk deterministic execution. Execution should proceed using the refined subphases below.

### P0 — Commercial Boundary Lock

#### P0A — Supported Surface and Non-Goals Lock

**Goal:** Lock the commercially supported M365 v1 surface to the actions that are currently proven and supportable.

**Outputs:**
- Supported action matrix for M365 v1
- Explicit unsupported-action matrix
- Product-claim boundary language tied to current evidence
- Evidence-source map for each supported action

#### P0B — Buyer / Operator Positioning and North Star Delta

**Goal:** Define who this standalone module is for, how it is positioned, and whether North Star requires synchronization.

**Outputs:**
- Target buyer definition
- Target operator definition
- Standalone product positioning statement
- Deployment-model statement
- North Star delta review and update decision

### P1 — Canonical Config and Identity Model

#### P1A — Config Inventory and Canonical Target Contract

**Goal:** Inventory the current configuration and identity loading paths and define the one canonical production contract.

**Outputs:**
- Current-state config inventory
- Canonical tenant-config target contract
- Production config source-precedence model
- Identity and tenancy model statement

#### P1B — Config Migration and Auth / Secret Policy

**Goal:** Define how the repo moves from the current state to the canonical production contract without ambiguity.

**Outputs:**
- Migration path away from direct production `.env` dependence
- Secret-management policy
- Auth-mode decision matrix
- Certificate-auth versus client-secret policy
- Deprecation map for legacy loading patterns

### P2 — Governance and Audit Hardening

#### P2A — Audit and Governance Evidence Model

**Goal:** Define the audit and governance evidence required for enterprise review of the M365 runtime.

**Outputs:**
- Required audit-event model
- Governance evidence model
- Gap map for snapshot or partial audit surfaces
- Administrative traceability requirements

#### P2B — Permission, Approval, and Fail-Closed Hardening

**Goal:** Define the hardening expectations for permission tiers, approvals, and fail-closed behavior.

**Outputs:**
- Permission-tier hardening checklist
- Approval-boundary checklist
- Fail-closed behavior checklist
- Exception and escalation policy

### P3 — Live Tenant Evidence and Release Gates

#### P3A — Live-Tenant Validation Matrix

**Goal:** Define exactly what must be validated against a live tenant to support enterprise release claims.

**Outputs:**
- Live-tenant validation matrix
- Environment prerequisites
- Evidence artifact checklist
- Mock versus live validation separation

#### P3B — Release Gates and Certification Decision Model

**Goal:** Convert evidence requirements into explicit release and certification decisions.

**Outputs:**
- Release-gate checklist
- Enterprise go / no-go criteria
- Certification decision model
- Evidence retention requirements

### P4 — Packaging, Install, and Operator Onboarding

#### P4A — Packaging, Install, and Bootstrap

**Goal:** Define how the standalone module is packaged, installed, and bootstrapped.

**Outputs:**
- Canonical package variants
- Install path
- Bootstrap flow
- Environment setup runbook
- Dependency and prerequisite list

#### P4B — Operator Onboarding, Runbooks, and Support Boundary

**Goal:** Define the operator experience after installation.

**Outputs:**
- Operator onboarding checklist
- Day-0 and day-1 runbooks
- Support-boundary statement
- Escalation path
- Ownership matrix

### P5 — Enterprise Collateral and Pilot Acceptance

#### P5A — Enterprise Collateral Pack

**Goal:** Produce the buyer-facing and review-facing collateral for the standalone module.

**Outputs:**
- Product one-pager
- Security / compliance posture brief
- Supported-action matrix for sales and delivery
- Architecture and operating-summary brief

#### P5B — Pilot Acceptance and Customer Handoff

**Goal:** Define how SmartHaus and the customer determine a successful pilot and handoff.

**Outputs:**
- Pilot acceptance checklist
- Pilot success criteria
- Customer handoff checklist
- Customer-responsibility matrix
- Sign-off and acceptance model

---

## Validation

- `Operations/EXECUTION_PLAN.md` references this initiative and plan ID.
- The plan triplet (`.md`, `.yaml`, `.json`) exists and remains consistent.
- The Codex prompt pair exists and points to this plan.
- Each later implementation phase must define explicit validation commands and acceptance evidence before execution.
- No future phase may claim enterprise readiness without separating mock evidence from live-tenant evidence.

---

## Success Criteria

- SmartHaus can describe exactly what the standalone M365 module v1 does and does not do.
- Production configuration is defined by one canonical contract rather than multiple competing loading paths.
- Enterprise governance and audit expectations are explicit and testable.
- Release acceptance requires live-tenant evidence for the enterprise-critical surfaces.
- Packaging, onboarding, and collateral support a real pilot or enterprise buyer review.

---

## Dependencies

- Existing M365 instruction contract and MA verification set in `docs/contracts/` and `configs/generated/`.
- Existing TAI licensed module model in `docs/TAI_LICENSED_MODULE_MODEL.md`.
- UCP tenant-configuration conventions where M365 depends on shared tenant governance patterns.

---

## Status Updates

- Log all planning and implementation actions in `Operations/ACTION_LOG.md` with `plan:m365-enterprise-commercialization-readiness:*`.
- Update `Operations/EXECUTION_PLAN.md` when phase status changes.
- If commercialization scope changes product definition, target operator, or enterprise acceptance metrics, update `Operations/NORTHSTAR.md` and log the rationale.
- Execute future work against `P0A` through `P5B`, not the higher-level parent phases, unless an explicit governance decision re-combines scope.
