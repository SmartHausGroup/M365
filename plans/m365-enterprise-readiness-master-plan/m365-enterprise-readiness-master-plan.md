# Plan: M365 Repo — Enterprise Readiness Master Plan

**Plan ID:** `m365-enterprise-readiness-master-plan`
**Status:** Active (`A1`, `A2`, `A3`, `A4`, `B1`, `B2`, and `B3` complete on 2026-03-17; `B4A`, `B4B`, `B4C`, `B4D1`, `B4D2`, `B4D3`, `B4D4A`, `B4D4B`, `B4D4C`, `B4D4D`, `B4D5`, `B4E`, `B5A`, `B5B`, and `B5C` complete on 2026-03-18; `B5D` and `B5E` complete on 2026-03-19; `C1A` remains prepared but blocked until the approval backend is reachable and the exact standalone certification shell contract is active)
**Date:** 2026-03-18
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-enterprise-readiness-master-plan:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — production-ready, policy-gated, auditable, self-service M365 orchestration.
**Historical lineage:** absorbs `m365-enterprise-commercialization-readiness` as the active enterprise-readiness critical path on 2026-03-17.

**Prompt discipline:** Every execution act in this plan must have a formal MATHS prompt pair under `docs/prompts/`. Historical commercialization prompts remain in the repo for traceability only and are not active execution authority.

**MA process:** MATHS prompts are mandatory for every act. Notebook-first MA phases remain mandatory only when an act introduces new algorithmic behavior, mathematical guarantees, or notebook-governed runtime logic beyond the current contract surface.

---

## Objective

Define and execute the full critical path required to make the current M365 capability commercially honest, operationally supportable, technically hardened, standards-compliant, and enterprise-ready as a standalone deterministic module.

## Decision Rule

Enterprise readiness for standalone M365 v1 is not satisfied by documentation alone.

For this repository state:

`EnterpriseReady = ProductBoundaryLocked ∧ RuntimeHardeningImplemented ∧ IdentityExecutionArchitectureImplemented ∧ RepoValidationGreen ∧ LiveTenantCertificationGreen ∧ ReleaseDecisionClosed ∧ LaunchReadinessComplete`

`LiveTenantCertificationGreen => EntraAppRolesSeparated ∧ ExecutorCredentialContractFinalized ∧ ApprovalBackendReachable ∧ CertificationEvidenceClosed`

`ExecutableAct = Planned ∧ Prompted ∧ Approved ∧ Logged ∧ Validated`

If any term is false, the module remains `NO-GO`.

## Execution Status

- `A1` complete on 2026-03-17: imported the supported-surface and buyer/operator boundary work from `P0A` and `P0B` in `docs/commercialization/m365-v1-supported-surface.md` and `docs/commercialization/m365-v1-positioning-and-north-star-delta.md`.
- `A2` complete on 2026-03-17: imported the canonical config-contract and auth/secret posture work from `P1A` and `P1B` in `docs/commercialization/m365-canonical-config-contract.md` and `docs/commercialization/m365-config-migration-and-auth-policy.md`.
- `A3` complete on 2026-03-17: imported the governance, audit, live-validation, and release-gate definition work from `P2A`, `P2B`, `P3A`, and `P3B` in the commercialization document set.
- `A4` complete on 2026-03-17: imported the packaging, onboarding, runbooks, and support-boundary work from `P4A` and `P4B` in `docs/commercialization/m365-packaging-install-bootstrap.md` and `docs/commercialization/m365-operator-onboarding-and-support-boundary.md`.
- `B1` complete on 2026-03-17: added the repo-local `configs/ma_phases.yaml` bridge required by governed code-edit validation, made `UCP_TENANT`-selected tenant config the runtime authority in `src/smarthaus_common/config.py`, extended tenant lookup to the sibling `UCP/tenants` directory in `src/smarthaus_common/tenant_config.py`, converted the standalone server and legacy dashboard entrypoints to shared bootstrap-only dotenv loading, updated `src/provisioning_api/routers/m365.py`, `src/provisioning_api/m365_provision.py`, and `src/provisioning_api/enterprise_dashboard.py` to honor tenant-first authority, and added targeted precedence coverage in `tests/test_env_loading.py`.
- `B2` complete on 2026-03-17: hardened the active ops-adapter and shared permission-enforcement path so missing acting identity, missing tenant selection, missing tenant config, missing permission tiers, denied OPA decisions, and missing approval-owner configuration fail closed by default, expanded high-risk `m365-administrator` approval requirements in `policies/ops.rego` and `registry/agents.yaml`, removed inferred non-production OPA fail-open behavior, and added targeted deny/approval coverage in `tests/test_ops_adapter.py` and `tests/test_policies.py`.
- `B3` complete on 2026-03-17: replaced `admin.audit_log` snapshot-mode behavior with an append-only admin event trail in `src/ops_adapter/audit.py` and `src/ops_adapter/actions.py`, aligned `m365-administrator` admin-action dispatch with the registry contract, added targeted admin-audit coverage in `tests/test_ops_adapter.py`, and synchronized the enterprise audit/evidence model to the real runtime surface.
- `B4D3` complete on 2026-03-18: added notebook-backed `L9` traceability for the runtime, CLI, and notebook validation surface; eliminated the remaining targeted Ruff debt under `src/ops_adapter/`, `src/provisioning_api/`, `src/smarthaus_cli/`, and `tests/test_policies.py`; fixed the notebook formatter parse blocker in `notebooks/ma_m365_batch1_groups.ipynb`; stabilized targeted formatting across the governed runtime and notebook surface; and validated with targeted `ruff check`, `ruff format --check`, and `git diff --check`.
- `B4D4A` complete on 2026-03-18: added `types-PyYAML` to the governed mypy hook and dev dependency set, removed duplicate module discovery for `src/ops_adapter/actions.py`, and converted the governed mypy path from environment blockers into a real actionable type inventory.
- `B4D4B` complete on 2026-03-18: reduced the core governed mypy surface from 90 errors across 11 files to green by tightening the runtime typing surfaces in `src/ops_adapter/`, `src/smarthaus_common/`, and `src/smarthaus_graph/`, correcting the duplicated CLI analyzer `Path` and signature issues in `src/smarthaus_cli/`, and validating the bounded surface with targeted `pre-commit run mypy --files ...`, `python3 -m py_compile`, and `git diff --check`.
- `B4D4C` complete on 2026-03-18: reduced the remaining dashboard, script, and test mypy surface from 126 errors across 15 files to green by adding bounded annotations and type-shape corrections in the legacy dashboard routes under `src/provisioning_api/`, hardening the dynamic GraphClient typing and nullable group-id handling in the standalone scripts under `scripts/`, and validating the full bounded surface with targeted `pre-commit run mypy --files ...` and `git diff --check`.
- `B4D4D` complete on 2026-03-18: proved the repo-wide mypy remainder is stable enough for handoff by running the governed `pre-commit run mypy --all-files` surface twice under UCP-approved `test_run` validation, confirming the same 67-error / 21-file remainder both times, and recording the deterministic inventory in `artifacts/b4d4d_failure_inventory.json`.
- `B4D5` completed on 2026-03-18: the bounded `B4D` remediation surface is green under targeted Ruff, format, Mypy, and diff checks, and the current `B4E` blocker inventory is pinned in `artifacts/b4d5_validation_handoff.json`.
- `B4E` complete on 2026-03-18: the repo-wide validation gate is green under `ruff check .`, `ruff format --check .`, `PYTHONPATH=src pre-commit run mypy --all-files`, `pre-commit run --all-files`, and `git diff --check`, with the full closeout recorded in `artifacts/b4e_full_repo_validation_closure.json`.
- `B5A` complete on 2026-03-18: locked the enterprise production identity model in `docs/commercialization/m365-entra-identity-and-app-execution-model.md`, explicitly separated Entra-authenticated human actors from the app-only SMARTHAUS service-principal executor, updated the canonical config/auth, governance, audit, and live-certification docs to reflect that architecture, and confirmed that `C1A` remains blocked until `B5C` implements the runtime authorization and audit binding.
- `B5B` complete on 2026-03-18: enforced JWT-backed actor identity on the governed ops-adapter execution path in `src/ops_adapter/main.py`, aligned the legacy `src/ops_adapter/app.py` path to deny raw header-only actor access unless the explicit non-enterprise override is enabled, propagated the validated actor identity through the action request path, fixed the middleware fail-closed response boundary to return deterministic auth errors instead of leaking ASGI exceptions, and validated the bounded identity-enforcement surface with `python3 -m py_compile`, `PYTHONPATH=src pytest -q tests/test_ops_adapter.py tests/test_policies.py`, and `git diff --check`.
- `B5C` complete on 2026-03-18: bound the authenticated SMARTHAUS Entra actor into tier resolution, approvals, and actor-versus-executor audit semantics by adding group-aware tier resolution in `src/smarthaus_common/tenant_config.py` and `src/smarthaus_common/permission_enforcer.py`, preserving actor tier, actor groups, tenant, and executor metadata in `src/ops_adapter/main.py`, `src/ops_adapter/app.py`, `src/ops_adapter/approvals.py`, `src/ops_adapter/audit.py`, and `src/ops_adapter/actions.py`, and validating the bounded binding surface with `python3 -m py_compile`, `PYTHONPATH=src pytest -q tests/test_ops_adapter.py tests/test_policies.py`, and `git diff --check`.
- `B5D` complete on 2026-03-19: the live Azure / Entra app-registration split is now locked in the SMARTHAUS tenant, with app `720788ac-1485-4073-b0c8-1a6294819a87` renamed to `SMARTHAUS M365 Executor`, app `e6fd71d3-4116-401e-a4f1-b2fda4318a8b` renamed to `SMARTHAUS M365 Operator Identity`, Graph application-role overlap removed from the operator-identity app, Graph delegated-scope overlap removed from the executor app, and `Application ID URI = api://e6fd71d3-4116-401e-a4f1-b2fda4318a8b` set on the operator-identity app.
- `B5E` complete on 2026-03-19: the governed runtime now supports valid MSAL certificate credentials from the tenant-selected PEM path, the executor certificate lives at `/Users/smarthaus/.ucp/certs/smarthaus-m365-executor.pem`, app `720788ac-1485-4073-b0c8-1a6294819a87` now carries the certificate credential `SMARTHAUS M365 Executor Certificate 2026-03-19` and zero password credentials, `/Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml` now selects certificate auth with an empty `azure.client_secret`, and non-mutating Graph validation still returns `organization=200` after secret retirement.
- `C1A` remains blocked on 2026-03-19: the SMARTHAUS tenant YAML contract now resolves deterministically through the tenant loader, carries the Operations approval target, and provides an app-only certificate-backed credential contract; the exact standalone shell contract is `UCP_ROOT=/Users/smarthaus/Projects/GitHub/UCP`, `UCP_TENANT=smarthaus`, `ALLOW_M365_MUTATIONS=true`, and `ENABLE_AUDIT_LOGGING=true`; direct Graph probes under that contract return `organization=200` but `site_discovery=503 UnknownError` for the SMARTHAUS Operations site; and the readiness gate therefore remains `NO-GO` until the approval backend is reachable and the exact shell contract is active. CAIO is out of scope for this certification path.

## Open Enterprise Blockers

The repo is not enterprise-ready yet because the remaining critical-path blockers are implementation, governance, and evidence blockers:

1. Live-tenant certification remains `NO-GO` until the non-production environment persists the exact launch contract (`UCP_ROOT=/Users/smarthaus/Projects/GitHub/UCP`, `UCP_TENANT=smarthaus`, `ALLOW_M365_MUTATIONS=true`, `ENABLE_AUDIT_LOGGING=true`) and the tenant-backed approval target becomes reachable through Graph or is supplied via explicit site and list IDs.
2. `C2`, `D1`, and `D2` remain downstream of the live-certification blockers.

## Scope

### In scope

- Preserve the narrow, honest standalone M365 v1 product boundary.
- Convert the documented production config contract into the real runtime authority.
- Harden permission, approval, fail-closed, and audit behavior for enterprise review.
- Bring the repo itself back into standards compliance before more runtime readiness claims are made.
- Execute live-tenant certification and release-gate closure for the supported v1 surface.
- Produce final collateral and handoff artifacts only after runtime, standards, and certification blockers are addressed.
- Synchronize `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, `Operations/PROJECT_FILE_INDEX.md`, and prompt artifacts whenever the active critical path changes.

### Out of scope

- Implementing the remaining planned M365 capability universe solely to claim breadth.
- Broad SAID or UCP rework outside direct M365 dependency requirements.
- New inference algorithms or unrelated mathematical systems.
- Unapproved tenant-impacting activity beyond explicitly approved validation or certification work.

## Requirements

### R1 — Integrated enterprise-readiness control plane

- Establish one active master plan for standalone enterprise readiness.
- Prevent documentation-only completion from being misread as full readiness closure.

### R2 — Imported foundation and product-boundary traceability

- Preserve the completed commercialization-definition work as traceable readiness foundation.
- Keep the supported surface, config contract, governance boundary, and operator model explicitly tied into the active master plan.

### R3 — Runtime hardening implementation

- Make tenant-scoped configuration the actual runtime authority.
- Enforce fail-closed governance and approval posture.
- Close the admin-audit runtime gap.

### R4 — Repo standards and governance baseline closure

- Bring planning, prompting, tracker alignment, file indexing, and governance templates back into compliance with `AGENTS.md` and `.cursor/rules/*.mdc`.
- Treat governance drift as a readiness blocker, not as incidental cleanup.

### R5 — Repo validation closure

- Recover from current formatter, linter, typing, and YAML parse failures.
- Require repo-wide green validation before additional readiness execution continues.

### R6 — Live-tenant certification and release closure

- Execute the required supported-surface validation in a controlled non-production tenant.
- Produce the release certification packet and explicit `GO` or `NO-GO` outcome.

### R7 — Launch collateral and handoff

- Produce the enterprise-facing collateral, pilot acceptance, and customer handoff artifacts after runtime, standards, and certification blockers are addressed.

### R8 — Governance synchronization and prompt regeneration

- Keep the old commercialization artifacts historically traceable while ensuring the master plan is the only active critical path.
- Maintain one active MATHS prompt pair for every master-plan act.

### R9 — Entra user identity, app-registration role separation, and app-only execution architecture

- Authenticate SMARTHAUS human operators through Microsoft Entra ID.
- Execute Graph calls through the SMARTHAUS M365 app registration using app-only service identity.
- Bind authorization, approvals, and audit to the authenticated actor while preserving the service executor identity.
- Keep the operator-identity app and the executor app explicitly separate.
- Finalize the executor app on a certificate-based production posture before standalone certification resumes.

## Execution Act Model

- Every act below is an explicit executable unit.
- Completed acts remain traceable in the plan and in the action log.
- Open acts require:
  - active plan presence
  - active MATHS prompt pair
  - explicit approval before write-effect execution
  - action-log and execution-plan synchronization after completion
- `C1` is a grouped certification phase and may not be executed as one opaque step; it must proceed through `C1A` → `C1D`.

## Integrated Execution Stack

### A — Imported Foundation and Product Boundary

This phase is complete and remains authoritative as historical foundation work, not as the active critical path by itself.

#### A1 — Product Boundary and Positioning

**Status:** ✅ Complete (2026-03-17)

**Goal:** Lock the supported v1 product claim, non-goals, buyer, operator, and deployment model.

**Outputs:**
- supported-action matrix
- unsupported-action matrix
- product-claim boundary
- buyer/operator/deployment definition

#### A2 — Canonical Config Contract and Auth Posture

**Status:** ✅ Complete (2026-03-17)

**Goal:** Define the supported production contract before runtime remediation begins.

**Outputs:**
- canonical config contract
- source-precedence model
- secret-management policy
- auth-mode policy and deprecation map

#### A3 — Governance Boundary and Certification Model

**Status:** ✅ Complete (2026-03-17)

**Goal:** Define the audit, approval, fail-closed, live-validation, and release-gate rules that runtime must satisfy.

**Outputs:**
- governance-evidence model
- fail-closed and approval boundary
- live-tenant validation matrix
- release-gate and certification model

#### A4 — Packaging and Operator Model

**Status:** ✅ Complete (2026-03-17)

**Goal:** Define the install path, onboarding flow, runbooks, and support boundary for the standalone runtime.

**Outputs:**
- canonical package/install/bootstrap path
- onboarding checklist
- day-0/day-1 runbooks
- support boundary and ownership matrix

### B — Runtime and Standards Hardening Implementation

This is the active critical path.

#### B1 — Runtime Config Authority Remediation

**Status:** ✅ Complete (2026-03-17)

**Goal:** Make the documented production contract the real runtime authority everywhere it matters.

**Outputs:**
- canonical config-loader implementation path
- legacy dotenv path classification in runtime
- runtime tests proving tenant-scoped authority wins
- implementation notes mapped back to `A2`

#### B2 — Fail-Closed Governance and Approval Remediation

**Status:** ✅ Complete (2026-03-17)

**Goal:** Bring runtime permission, approval, and policy behavior up to the enterprise posture documented in `A3`.

**Outputs:**
- fail-closed runtime behavior for missing policy/identity/config preconditions
- approval-boundary remediation for supported mutating actions
- targeted tests for deny behavior and approval gating
- implementation notes mapped back to `A3`

#### B3 — Admin Audit and Evidence-Surface Remediation

**Status:** ✅ Complete (2026-03-17)

**Goal:** Close the admin-audit gap so the runtime has an enterprise-reviewable audit surface.

**Outputs:**
- remediated admin audit behavior
- normalized evidence map across instruction and admin surfaces
- targeted audit tests or verification outputs
- implementation notes mapped back to `A3`

#### B4 — Governance Baseline and Repo Validation Closure

**Status:** ✅ Complete (`B4A`, `B4B`, `B4C`, `B4D1`, `B4D2`, `B4D3`, `B4D4A`, `B4D4B`, `B4D4C`, `B4D4D`, `B4D5`, and `B4E` complete on 2026-03-18)

**Goal:** Bring the repo itself back to AGENTS-compliant standards before live certification and launch work continue.

**Outputs:**
- governance baseline alignment
- active prompt inventory regeneration
- repo-validation blocker recovery
- repo-wide green validation

**Exit rule:** `B4E` must be green before `C1A` may start.

##### B4A — Governance Baseline Alignment

**Status:** ✅ Complete (2026-03-18)

**Goal:** Align the plan, trackers, template, file index, and active execution state with `AGENTS.md`.

**Outputs:**
- `Operations/PROJECT_FILE_INDEX.md` baseline exists
- `docs/governance/MATHS_PROMPT_TEMPLATE.md` references real repo paths and current workflow
- active master plan, `Operations/EXECUTION_PLAN.md`, and `Operations/ACTION_LOG.md` agree on next act and blocker set
- current active act is explicit and sequenced correctly

##### B4B — Prompt System Regeneration

**Status:** ✅ Complete (2026-03-18)

**Goal:** Recreate the active master-plan MATHS prompt inventory so every act has one formal prompt pair.

**Outputs:**
- regenerated master-plan prompt pair
- one prompt pair for every act `A1` → `D2`
- historical commercialization prompts explicitly treated as traceability artifacts, not active execution authority

##### B4C — Validation Blockers and Syntax Recovery

**Status:** ✅ Complete (2026-03-18)

**Goal:** Fix the hard parse and schema blockers that prevent formatter and validation recovery.

**Outputs:**
- Black parse blocker removed from `scripts/generate-policies.py`
- malformed YAML invariants under `governance/invariants/m365/` corrected
- formatter baseline restored without unrelated spillover

##### B4D — Ruff/Black/Mypy Remediation

**Status:** ✅ Complete (`B4D1`, `B4D2`, `B4D3`, `B4D4A`, `B4D4B`, `B4D4C`, `B4D4D`, and `B4D5` complete on 2026-03-18)

**Goal:** Close the remaining repo-wide Ruff, Black, and Mypy debt after hard parse blockers are gone.

**Outputs:**
- Ruff debt remediated or explicitly scoped away through approved configuration changes
- Black completes successfully across the repo
- Mypy duplicate-module and stub issues are resolved for the governed execution path

##### B4D1 — Spillover Reset and Failure Inventory Pin

**Status:** ✅ Complete (2026-03-18)

**Goal:** Restore the worktree to the approved post-`B4C` baseline and pin the exact remaining Ruff/Black/Mypy inventory before category cleanup begins.

**Outputs:**
- unintended hook spillover from the latest repo-wide baseline run is reverted
- a pinned failure inventory artifact exists for `B4D2` → `B4D4`
- no approved `B4C` or governance artifacts are lost during reset

##### B4D2 — Scripts and CI Ruff Cleanup

**Status:** ✅ Complete (2026-03-18)

**Goal:** Eliminate the remaining Ruff debt in scripts and CI-adjacent tooling without widening into runtime behavior changes.

**Outputs:**
- script and CI Ruff violations are resolved
- exception handling, import order, and unused-symbol fixes remain behavior-preserving
- `L8` notebook-backed traceability exists for the scoped tooling remediation

##### B4D3 — Runtime, CLI, and Notebook Ruff/Black Cleanup

**Status:** ✅ Complete (2026-03-18)

**Goal:** Eliminate the remaining Ruff debt in runtime and CLI code and stabilize formatting on the governed execution path, including the notebook-backed validation surface that still fails formatter checks.

**Outputs:**
- runtime and CLI Ruff violations are resolved
- formatter output is stable for the touched runtime surfaces
- notebook-backed validation files no longer contain formatter parse blockers

##### B4D4 — Mypy Stub and Module-Path Remediation

**Status:** ✅ Complete (2026-03-18)

**Goal:** Resolve the current Mypy environment and module-layout blockers without weakening type checking.

**Outputs:**
- `yaml` stub requirement is handled explicitly
- duplicate-module resolution for `src/ops_adapter/actions.py` is fixed
- governed-path mypy runs become actionable

###### B4D4A — Typing Environment and Module-Path Unblock

**Status:** ✅ Complete (2026-03-18)

**Goal:** Remove the Mypy environment and package-path blockers that prevented governed-path type checking from reaching real diagnostics.

**Outputs:**
- `types-PyYAML` is present in the governed mypy hook environment
- the repo dev dependency set declares the same typing support explicitly
- duplicate module discovery for `src/ops_adapter/actions.py` is removed

###### B4D4B — Core Runtime and Governance Mypy Remediation

**Status:** ✅ Complete (2026-03-18)

**Goal:** Reduce the actionable Mypy debt in the core governed runtime and governance path first.

**Outputs:**
- core `ops_adapter`, `smarthaus_common`, `smarthaus_graph`, and CLI-analyzer typing issues are reduced
- checker output over the enterprise-governed path is materially smaller and inventory-backed

Validation:
- targeted `pre-commit run mypy --files ...` over the 11-file governed surface passed
- `python3 -m py_compile` passed for the same bounded surface
- `git diff --check` passed

Residual handoff:
- the remaining bounded mypy closure work is now reduced to `B4D4D`

###### B4D4C — Dashboard, Script, and Test Mypy Remediation

**Status:** ✅ Complete (2026-03-18)

**Goal:** Reduce the remaining dashboard, script, and test typing debt after the core governed path is corrected.

**Outputs:**
- dashboard, script, and test typing issues are reduced in bounded groups
- remaining failures are limited and explicit before closure

Validation:
- targeted `pre-commit run mypy --files ...` passed for the full 15-file `B4D4C` surface
- `git diff --check` passed

###### B4D4D — Targeted Mypy Closure

**Status:** ✅ Complete (2026-03-18)

**Goal:** Prove the bounded Mypy surface is stable enough to hand off to `B4D5`.

**Outputs:**
- governed mypy reruns are repeatable
- the failure set is either closed or explicitly reduced to the handoff inventory

Validation:
- governed `pre-commit run mypy --all-files` was run twice under approved `test_run` validation
- both runs produced the same `67` errors across `21` files
- the stable remainder is captured in `artifacts/b4d4d_failure_inventory.json`
- `git diff --check` passed

##### B4D5 — Targeted Validation Closure

**Status:** ✅ Complete (2026-03-18)

**Goal:** Prove the `B4D` cleanup surface is stable before the repo moves to `B4E`.

**Outputs:**
- targeted Ruff, Black, and Mypy checks pass for the remediated surfaces
- the handoff to `B4E` is explicit and inventory-backed

Validation:
- targeted `ruff check` passed for the bounded `B4D` remediation surface
- targeted `ruff format --check` passed for the bounded `B4D` remediation surface
- targeted `PYTHONPATH=src pre-commit run mypy --files ...` passed for the bounded `B4D` remediation surface
- `git diff --check` passed
- the current `B4E` blocker inventory is captured in `artifacts/b4d5_validation_handoff.json`

##### B4E — Full Repo Validation Closure

**Goal:** Achieve one green repo-wide validation run and make it a hard prerequisite for further readiness execution.

**Outputs:**
- `pre-commit run --all-files` passes
- validation outcome is logged and reflected in execution tracking
- downstream acts may rely on repo-wide green state without repeated spillover cleanup

Validation:
- repo-wide `ruff check .` passed
- repo-wide `ruff format --check .` passed
- repo-wide `PYTHONPATH=src pre-commit run mypy --all-files` passed
- repo-wide `pre-commit run --all-files` passed
- `git diff --check` passed
- closure artifact captured in `artifacts/b4e_full_repo_validation_closure.json`

#### B5 — Entra Identity, App Registration Separation, and Executor Hardening

**Status:** ✅ Complete (`B5A`, `B5B`, `B5C`, `B5D`, and `B5E` complete on 2026-03-19)

**Goal:** Lock and implement the enterprise production identity model where SMARTHAUS users authenticate with Microsoft Entra ID, the backend executes Microsoft Graph actions through a dedicated SMARTHAUS executor app, and the executor app reaches the final certificate-based production posture before certification resumes.

**Outputs:**
- explicit actor-versus-executor identity model
- runtime enforcement plan and implementation for Entra-authenticated users
- authorization, approval, and audit binding between actor identity and app-only execution
- explicit operator-identity-versus-executor app-registration role separation
- executor certificate-cutover and tenant-contract finalization plan

**Exit rule:** `B5E` is complete; `C1A` may proceed once the approval backend is reachable and the exact standalone shell contract is active.

##### B5A — Identity Architecture Lock

**Goal:** Lock the production identity model and tenant-contract implications before runtime implementation.

**Outputs:**
- canonical production identity model: `Entra user auth + app-only Graph execution`
- tenant-contract update plan for user identity, allowed domains, and group-to-tier mapping
- commercialization, config, and certification docs updated to reflect the correct auth architecture

##### B5B — Runtime Identity Enforcement

**Goal:** Ensure active user-facing execution paths require authenticated Entra identity while preserving app-only service execution to Graph.

**Outputs:**
- explicit JWT and actor-identity enforcement on governed user-facing paths
- actor identity propagated through the active ops-adapter execution path
- deny behavior and tests for missing or invalid actor identity

##### B5C — Authorization and Audit Binding

**Goal:** Bind authenticated SMARTHAUS users and groups to governed authorization and audit semantics.

**Outputs:**
- user or group to permission-tier mapping model for SMARTHAUS operators
- approval and audit model that records both actor identity and executor identity
- targeted validation for actor-tier enforcement and actor/executor audit traceability

##### B5D — Entra App Registration Role Separation

**Status:** ✅ Complete (2026-03-19)

**Goal:** Lock the Azure / Entra app-registration split so the operator-identity app and the backend executor app are no longer ambiguous before certification resumes.

**Outputs:**
- explicit executor-app lock for `720788ac-1485-4073-b0c8-1a6294819a87`
- explicit operator-identity-app lock for `e6fd71d3-4116-401e-a4f1-b2fda4318a8b`
- deterministic Azure cleanup specification for names, redirect-URI posture, Application ID URI posture, and permission separation

Validation:
- live Azure readback confirms `displayName = SMARTHAUS M365 Executor` for app `720788ac-1485-4073-b0c8-1a6294819a87`
- live Azure readback confirms `displayName = SMARTHAUS M365 Operator Identity` and `identifierUris = [api://e6fd71d3-4116-401e-a4f1-b2fda4318a8b]` for app `e6fd71d3-4116-401e-a4f1-b2fda4318a8b`
- executor app now carries Graph application-role posture only
- operator-identity app now carries delegated-scope posture only

##### B5E — Executor Certificate Cutover and Tenant Contract Finalization

**Status:** ✅ Complete (2026-03-19)

**Goal:** Move the SMARTHAUS executor app from the transitional client-secret posture to an explicit certificate-based production contract before `C1A` resumes.

**Outputs:**
- executor certificate material and runtime-path contract at `/Users/smarthaus/.ucp/certs/smarthaus-m365-executor.pem`
- tenant contract updated to certificate-first executor auth with `azure.client_secret = ""`
- live executor app now carries one certificate credential and zero password credentials
- non-mutating Graph validation passed after certificate cutover and secret retirement

### C — Live-Tenant Certification

#### C1 — Live Certification Execution

**Status:** 🟡 Prepared, blocked

**Goal:** Execute the supported v1 validation matrix against a controlled non-production tenant.

**Outputs:**
- live validation transcript set
- evidence packet for supported actions and governance surfaces
- controlled-environment operator checklist
- pass/fail summary tied to `A3`

**Prerequisites:**
- `B4E` complete and green
- `B5E` complete
- approved non-production environment ready
- `UCP_TENANT` present
- one supported Graph or Azure credential set present
- `ALLOW_M365_MUTATIONS=true`
- `ENABLE_AUDIT_LOGGING=true`
- tenant-backed approval target present and reachable

##### C1A — Certification Environment Readiness

**Goal:** Close the environment and operator prerequisites for the certification run.

**Outputs:**
- environment readiness checklist
- prerequisite evidence
- explicit `GO/NO-GO` on readiness to run live checks

##### C1B — Live Read-Only Certification

**Goal:** Execute the read-only supported-surface checks against the non-production tenant.

**Outputs:**
- read-only live transcripts
- pass/fail classification for read-only rows in the validation matrix

##### C1C — Live Mutation and Governance Certification

**Goal:** Execute controlled mutation, approval, audit, and governance checks in the approved window.

**Outputs:**
- mutation-surface transcripts
- approval and audit evidence
- pass/fail classification for controlled write-path rows

##### C1D — Evidence Packet Completion and Matrix Closure

**Goal:** Close the evidence packet and map all live results back to the validation matrix.

**Outputs:**
- complete evidence index
- updated validation-matrix status
- explicit blocker list for any failed or ambiguous rows

#### C2 — Release Certification Packet and Decision

**Status:** ⛔ Blocked by `C1D`

**Goal:** Turn live evidence into one formal release decision.

**Outputs:**
- release certification packet
- evidence-retention index
- explicit `GO` or `NO-GO` decision record
- blocker list if certification remains red

### D — Launch Readiness

#### D1 — Enterprise Collateral Pack

**Status:** ⛔ Blocked by `C2`

**Goal:** Produce buyer-facing and delivery-facing collateral only after runtime and certification are in acceptable shape.

**Outputs:**
- product one-pager
- security and compliance posture brief
- supported-action matrix for sales and delivery
- architecture and operating-summary brief

#### D2 — Pilot Acceptance and Customer Handoff

**Status:** ⛔ Blocked by `D1` and `C2`

**Goal:** Define how SMARTHAUS and the customer close the pilot and transfer operating ownership.

**Outputs:**
- pilot acceptance checklist
- pilot success criteria
- customer handoff checklist
- customer-responsibility matrix
- sign-off model

## Prompt Inventory Rule

- Active MATHS prompt pairs must exist for:
  - overview: `m365-enterprise-readiness-master-plan`
  - acts: `A1`, `A2`, `A3`, `A4`, `B1`, `B2`, `B3`, `B4A`, `B4B`, `B4C`, `B4D1`, `B4D2`, `B4D3`, `B4D4`, `B4D5`, `B4E`, `B5A`, `B5B`, `B5C`, `B5D`, `B5E`, `C1A`, `C1B`, `C1C`, `C1D`, `C2`, `D1`, `D2`
- Historical commercialization prompt pairs remain for traceability only and are not active execution authority.
- No new act may be added to the plan without a matching MATHS prompt pair.

## Critical-Path Rules

1. No act after `B4E` may proceed while `pre-commit run --all-files` is red.
2. `B5A` may not start until `B4E` is complete.
3. `B5D` may not start until `B5C` is complete.
4. `B5E` may not start until `B5D` is complete.
5. `C1A` may not start until `B5E` is complete.
6. `C1B` and `C1C` may not run without explicit live-execution approval.
7. `C2`, `D1`, and `D2` may not imply enterprise readiness while any `B5*` or `C1*` act remains incomplete or blocked.
8. Historical commercialization prompts and historical absorbed-plan references may not be used as active execution authority.

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

- `Operations/EXECUTION_PLAN.md` lists this master plan as the active enterprise-readiness initiative and records `B5E` complete with `C1A` prepared but blocked on approval-backend reachability plus exact-shell activation.
- `plans/m365-enterprise-commercialization-readiness/` is explicitly marked as absorbed/historical.
- `Operations/PROJECT_FILE_INDEX.md` exists and tracks the active governance artifacts.
- The prompt pair for this master plan exists.
- Prompt pairs exist for every active act listed in `Prompt Inventory Rule`.
- No future act may claim enterprise readiness closure unless `B4E`, `C1D`, `C2`, `D1`, and `D2` all satisfy their exit criteria.

## Success Criteria

- There is one active enterprise-readiness plan for standalone M365 v1.
- The active critical path is aligned to `AGENTS.md` and `.cursor/rules/*.mdc`.
- Runtime config authority matches the documented production contract.
- Governance and approval behavior is fail-closed in the enterprise posture.
- Admin audit is enterprise-reviewable and traceable.
- Repo-wide validation is green before live certification resumes.
- Live-tenant certification evidence exists and the release decision is explicit.
- Launch collateral and pilot handoff are produced only after the true blockers are addressed.
