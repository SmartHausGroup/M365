# Plan: M365 Direct Function Validation

## Section 1: Plan Header

- **Plan ID:** `plan:m365-direct-function-validation`
- **Parent Plan ID:** `none`
- **Title:** `Execute direct repo function tests one by one and fix repo-local defects until the surface is truthfully usable`
- **Version:** `1.0`
- **Status:** `complete`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-04-06`
- **Date Updated:** `2026-04-06`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: M365 Direct Function Validation`
- **Domain:** `infrastructure`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `Truthful M365-only direct execution through this repo version`
  - `Self-service posture with real, repeatable local validation`
  - `Fail-closed actor identity, permission, and tenant-boundary enforcement`
- **Anti-alignment:**
  - `Does NOT widen into UCP runtime work`
  - `Does NOT fake green by bypassing tenant permissions or local admin-module requirements`
  - `Does NOT relabel repo-local defects as Microsoft-side failures`

## Section 3: Intent Capture

- **User's stated requirements:**
  - `Be able to ask for direct testing of specific functions from this repo version`
  - `Do whatever is required under governance to test everything and fix repo-local defects`
  - `Do not stop at partial smoke checks or known repo-local blockers`
- **Intent verification:** `R0 through R4 define the bounded direct function-validation and repair path required to make direct function checks genuinely usable.`

## Section 4: Objective

- **Objective:** Execute direct function-by-function validation against the repo-local M365 runtime, classify outcomes truthfully, and repair any repo-local defects that still prevent meaningful direct testing.
- **Current state:** The direct repo runtime imports, routes, and executes representative actions truthfully enough that specific function checks can now be requested directly from this repo version.
- **Target state:** The repo has a truthful direct-function matrix showing which functions now succeed directly and which remaining failures are external prerequisites rather than local code, routing, or harness defects.

## Section 5: Scope

### In scope (conceptual)

- create the governed direct function-validation package and prompt pair
- execute a repeatable direct test matrix across core M365 function families
- repair repo-local defects exposed by that matrix when they remain inside the direct-runtime boundary
- publish a human-readable and machine-readable closeout for direct function readiness

### Out of scope (conceptual)

- UCP runtime changes
- tenant-admin permission grants or Microsoft service-side fixes
- release promotion or branch-merging work
- silent bypasses of actor identity, approval, or mutation controls

### File allowlist (agent MAY touch these)

- `plans/m365-direct-function-validation/**`
- `docs/prompts/codex-m365-direct-function-validation.md`
- `docs/prompts/codex-m365-direct-function-validation-prompt.txt`
- `docs/commercialization/m365-direct-function-validation.md`
- `artifacts/diagnostics/m365_direct_function_validation.json`
- `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
- `src/provisioning_api/main.py`
- `src/provisioning_api/routers/m365.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/actions.py`
- `src/smarthaus_common/tenant_config.py`
- `src/smarthaus_common/executor_routing.py`
- `src/smarthaus_common/power_apps_client.py`
- `src/smarthaus_common/power_automate_client.py`
- `src/smarthaus_graph/client.py`
- `registry/executor_routing_v2.yaml`
- `tests/test_endpoints.py`
- `tests/test_ops_adapter.py`
- `tests/test_executor_routing_v2.py`
- `tests/test_power_apps_expansion_v2.py`
- `tests/test_power_automate_expansion_v2.py`
- `tests/test_auth_model_v2.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist (agent MUST NOT touch these)

- `../UCP/**`
- `registry/persona_registry_v2.yaml`
- `registry/persona_certification_v1.yaml`
- `registry/department_certification_v1.yaml`
- `registry/activated_persona_surface_v1.yaml`
- `registry/workforce_packaging_v1.yaml`
- `Any path not listed in the allowlist`

### Scope fence rule

Agent must STOP and re-scope if truthful direct function testing requires UCP-side edits, tenant-admin changes, or paths outside the allowlist.

## Section 6: Requirements

- **R0 — Create the governed direct function-validation package**
  - Create the bounded plan triplet, prompt pair, and tracker activation before any new direct live tests.
- **R1 — Execute the direct function matrix**
  - Run representative direct tests for admin/governance, Teams, SharePoint, email, calendar, Power Apps, Power Automate, and service health from this repo version.
- **R2 — Repair repo-local defects surfaced by the matrix**
  - If a direct function fails because of a repo-local code, routing, or harness defect, repair it within this bounded package and rerun the affected checks.
- **R3 — Classify external prerequisites truthfully**
  - If a function fails because of Microsoft permissions, missing local admin modules, or service-side errors, preserve that as external truth instead of widening into tenant-admin work.
- **R4 — Close out direct function readiness**
  - Publish a direct-function diagnostics artifact and commercialization note recording the final usable test surface and the remaining external prerequisites.

## Section 7: Execution Sequence

- `T1 -> T2 -> T3 -> T4 -> T5`
- Stop on first red that escapes the allowlist or requires tenant/UCP changes.

## Section 8: Tasks

- **T1 — Package and baseline lock**
  - Create the governed package, mark the initiative active, and freeze the direct test matrix.
- **T2 — Harness baseline**
  - Reconfirm the documented local harness for the top-level instruction surface and the governed action surface.
- **T3 — Direct function matrix execution**
  - Execute the bounded matrix across admin/governance, Teams, SharePoint, email, calendar, Power Apps, Power Automate, and service health.
- **T4 — Targeted remediation and rerun**
  - Repair any repo-local defects surfaced by T3 and rerun the affected direct checks plus focused regression coverage.
- **T5 — Diagnostics and governance closeout**
  - Publish diagnostics, sync trackers, and close the phase only when the direct function surface is truthfully usable.

## Section 9: Gates

- **CHECK:C0 — Package and tracker truth locked**
  - The plan, prompt pair, and tracker state must exist before new live tests run.
- **CHECK:C1 — Harness baseline usable**
  - The documented direct instruction and governed action harnesses must still start and run locally.
- **CHECK:C2 — Core direct functions truthfully classified**
  - Admin/governance, Teams, and SharePoint must either succeed or fail only for truthful external reasons.
- **CHECK:C3 — Remaining families truthfully classified**
  - Email, calendar, Power Apps, Power Automate, and service health must either succeed or be classified by truthful external prerequisites instead of repo-local defects.
- **CHECK:C4 — Repo-local defects repaired if found**
  - Any repo-local defect discovered inside scope must be repaired and revalidated before closeout.
- **CHECK:C5 — Final validation green**
  - Focused regressions, direct runtime probes, `pre-commit run --all-files`, and `git diff --check` must pass.

## Section 10: Determinism Requirements

- `N/A — this phase is bounded live-function validation and direct-runtime repair work rather than numerical or matching logic. Determinism is enforced through fixed local harness configuration, repeated direct runs, and focused regression coverage.`

## Section 11: Artifacts

- `plans/m365-direct-function-validation/m365-direct-function-validation.md`
- `plans/m365-direct-function-validation/m365-direct-function-validation.yaml`
- `plans/m365-direct-function-validation/m365-direct-function-validation.json`
- `docs/prompts/codex-m365-direct-function-validation.md`
- `docs/prompts/codex-m365-direct-function-validation-prompt.txt`
- `docs/commercialization/m365-direct-function-validation.md`
- `artifacts/diagnostics/m365_direct_function_validation.json`

## Section 12: Environment

- **Python version:** `repo .venv / local developer workstation`
- **Venv:** `.venv/bin/python`
- **External data:**
  - `local tenant contract via UCP_ROOT/UCP_TENANT when present`
  - `Microsoft 365 tenant credentials, permissions, and Power Platform admin modules when live actions are executed`

## Section 13: Implementation Approach

- **Option A:** Run a bounded direct function matrix now and repair only the repo-local defects it exposes.
  - **Pros:** directly answers the user request; keeps the work anchored to the actual repo runtime; preserves truthful local-versus-external failure classification.
  - **Cons:** may surface one more layer of direct-runtime defects before the matrix is fully stable.
- **Option B:** Stop at the remediation closeout and treat the repo as sufficiently proven already.
  - **Pros:** less work.
  - **Cons:** does not satisfy the user's requirement to directly test specific functions one by one.
- **Chosen:** `Option A`
- **Rationale:** the runtime is now ready enough for a governed live matrix, so the next truthful move is to execute that matrix and fix only the repo-local defects it still surfaces.

## Section 14: Risks and Mitigations

- **Risk:** one or more direct function families still hide repo-local defects.
  - **Impact:** `high`
  - **Mitigation:** keep the allowlist broad enough for the direct-runtime boundary and repair defects within the same package before closeout.
  - **Status:** `open`
- **Risk:** some function families remain blocked by live tenant permissions or missing local Power Platform modules.
  - **Impact:** `medium`
  - **Mitigation:** preserve truthful external classification rather than forcing green through tenant-admin changes.
  - **Status:** `open`
- **Risk:** a proposed fix weakens permission enforcement or actor identity.
  - **Impact:** `high`
  - **Mitigation:** require the governed action harness to stay fail-closed and rerun focused auth/regression coverage after any code change.
  - **Status:** `open`
- **Hard blockers:** `none local to this repo; the remaining boundaries are tenant permissions, local Power Platform admin modules, and Graph service-health behavior`

## Section 16: Outcome Summary

- `R0 complete` — governed plan triplet, prompt pair, and tracker activation created
- `R1 complete` — direct function matrix executed across instruction and governed action surfaces
- `R2 complete` — no new repo-local defects were surfaced, so no runtime edits were required inside this package
- `R3 complete` — external prerequisites were classified truthfully:
  - `mail/calendar -> Graph ErrorAccessDenied`
  - `Power Apps / Power Automate -> missing Microsoft.PowerApps.Administration.PowerShell`
  - `service health -> Graph UnknownError`
- `R4 complete` — diagnostics and commercialization closeout published and the package is ready to close green

## Section 15: Rollback

- **Procedure:**
  - revert only the bounded allowlist files changed by this phase
  - restore the prior direct-runtime-remediation branch state if the live-function package cannot stay truthful
  - update governance trackers to reflect rollback truthfully
