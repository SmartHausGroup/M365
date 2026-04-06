# Plan: M365 Direct Full Surface Certification

## Section 1: Plan Header

- **Plan ID:** `plan:m365-direct-full-surface-certification`
- **Parent Plan ID:** `none`
- **Title:** `Enable and certify the full repo-claimed direct M365 surface so supported actions are actually testable and trustworthy`
- **Version:** `1.0`
- **Status:** `active`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-04-06`
- **Date Updated:** `2026-04-06`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: M365 Direct Full Surface Certification`
- **Domain:** `infrastructure`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `Truthful M365-only execution through the repo-local runtime`
  - `Self-service direct operation without hidden tenant or workstation blockers`
  - `Fail-closed permission, approval, and actor identity enforcement with real live evidence`
- **Anti-alignment:**
  - `Does NOT widen into UCP runtime work`
  - `Does NOT pretend unsupported or unenabled actions are certified`
  - `Does NOT force green by bypassing Microsoft security or tenant policy boundaries`

## Section 3: Intent Capture

- **User's stated requirements:**
  - `Get to the point where Claude or Codex can interact with Microsoft 365 and do what is needed`
  - `Know that it works because it has actually been tested`
  - `Do not stop at repo-vs-external classification; identify blockers and fix them`
- **Intent verification:** `This program exists because the bounded direct-function wave proved the repo path is repaired but did not certify the full claimed surface.`

## Section 4: Objective

- **Objective:** Lock the authoritative supported direct M365 surface, remove the remaining workstation and tenant blockers inside scope, and run a real certification matrix until the supported surface is either certified green or truthfully reduced.
- **Current state:** The repo has 59 agents, 184 unique allowed actions in `registry/agents.yaml`, and 155 direct instruction actions in `src/provisioning_api/routers/m365.py`. A bounded direct-function validation wave proved the local runtime path works for SharePoint, Teams, and admin/governance reads, but the full claimed surface is not yet certified.
- **Target state:** The supported direct M365 surface is explicitly locked, enabled, and tested with published evidence. Any remaining unsupported or blocked actions are removed or explicitly fenced rather than implied to work.

## Section 4A: Current Phase State

- `F0` is complete.
- `F1` is complete.
- `F2` is complete.
- `F3` is now the active next act.
- The notebook-backed `F0` evidence is `notebooks/m365/INV-M365-CH-direct-full-surface-certification-universe-lock-v1.ipynb`.
- The current baseline artifact is `artifacts/diagnostics/m365_direct_full_surface_certification.json`.

## Section 5: Scope

### In scope (conceptual)

- lock the authoritative direct certification universe from repo truth sources
- identify and close tenant/workstation blockers required for direct testing
- execute read and mutation certification slices for the supported direct surface
- repair repo-local defects that block certification
- publish a final support matrix and diagnostics artifact

### Out of scope (conceptual)

- UCP runtime changes
- external-platform personas or non-M365 APIs
- fake green status via silent bypasses
- production release promotion

### File allowlist (agent MAY touch these)

- `plans/m365-direct-full-surface-certification/**`
- `docs/prompts/codex-m365-direct-full-surface-certification.md`
- `docs/prompts/codex-m365-direct-full-surface-certification-prompt.txt`
- `docs/commercialization/m365-direct-full-surface-certification.md`
- `artifacts/diagnostics/m365_direct_full_surface_certification.json`
- `docs/prompts/codex-m365-direct-function-validation.md`
- `docs/prompts/codex-m365-direct-function-validation-prompt.txt`
- `docs/commercialization/m365-direct-function-validation.md`
- `artifacts/diagnostics/m365_direct_function_validation.json`
- `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
- `registry/agents.yaml`
- `registry/auth_model_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `registry/capability_registry.yaml`
- `registry/executor_routing_v2.yaml`
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

Stop and re-scope if certification requires UCP-side edits or tenant changes that cannot be executed through the direct repo runtime and documented local operator tooling.

## Section 6: Requirements

- **R0 — Create the governed full-surface certification package**
  - Create the bounded plan triplet, prompt pair, and tracker activation before inventory or enablement work.
- **R1 — Lock the authoritative certification universe**
  - Freeze the supported action universe, family mapping, auth class, risk class, and direct-surface path from repo truth sources.
- **R2 — Remove workstation and tenant blockers inside scope**
  - Install or configure missing local tooling and fix direct-tenant permission gaps required for the certified surface.
- **R3 — Execute certification slices**
  - Run direct read, mutation, approval, actor-tier, and audit slices until the supported surface is truthfully classified.
- **R4 — Repair repo-local defects or reduce the claimed surface**
  - Any repo-local defect found during certification must be fixed and rerun; any action that cannot be made truthful must be explicitly fenced out of the certified surface.
- **R5 — Publish the final support matrix**
  - Close the phase only when the supported direct surface is either certified or explicitly reduced with written evidence.

## Section 7: Execution Sequence

- `F0 -> F1 -> F2 -> F3 -> F4`
- Stop on first red that escapes the allowlist or requires unsafe/undocumented tenant changes.

## Section 8: Phases

- **F0 — Universe lock**
  - Freeze the direct certification universe from `registry/agents.yaml`, `registry/capability_registry.yaml`, `registry/auth_model_v2.yaml`, `registry/approval_risk_matrix_v2.yaml`, and the direct instruction surface.
- **F1 — Enablement**
  - Remove workstation and tenant blockers required for direct certification.
- **F2 — Read-path certification**
  - Certify read-only and safe non-mutating functions family by family.
- **F3 — Mutation/approval certification**
  - Certify write paths, approval-required paths, and actor-tier boundaries.
- **F4 — Closeout**
  - Publish the certified support matrix, diagnostics, and governance closeout.

## Section 9: Gates

- **CHECK:C0 — Package and tracker truth locked**
  - The master package and tracker state must exist before inventory or enablement work.
- **CHECK:C1 — Universe lock published**
  - The authoritative supported direct surface must be frozen before claiming certification coverage.
- **CHECK:C2 — Enablement blockers addressed**
  - Required workstation and tenant blockers inside scope must be removed or explicitly escalated.
- **CHECK:C3 — Certification slices green or fenced**
  - Each tested family must be green or explicitly removed from the certified surface.
- **CHECK:C4 — Repo-local defects repaired**
  - Any repo-local defect exposed during certification must be fixed and rerun.
- **CHECK:C5 — Final support matrix published**
  - The phase closes only with a truthful support matrix and diagnostics artifact.

## Section 10: Artifacts

- `plans/m365-direct-full-surface-certification/m365-direct-full-surface-certification.md`
- `plans/m365-direct-full-surface-certification/m365-direct-full-surface-certification.yaml`
- `plans/m365-direct-full-surface-certification/m365-direct-full-surface-certification.json`
- `docs/prompts/codex-m365-direct-full-surface-certification.md`
- `docs/prompts/codex-m365-direct-full-surface-certification-prompt.txt`
- `docs/commercialization/m365-direct-full-surface-certification.md`
- `artifacts/diagnostics/m365_direct_full_surface_certification.json`

## Section 11: Current Result

- `F2` is complete.
- The implemented non-mutating direct surface was classified as `45` certified green actions and `46` fenced actions.
- `CHECK:C3` passed because every tested read family is now either green or explicitly fenced with a written reason.
- `CHECK:C4` passed because the two repo-local defects exposed during `F2` were repaired and rerun:
  - `GraphClient.list_directory_roles` no longer sends unsupported `$top` to `/directoryRoles`
  - `PowerAppsClient` treats warning-only PowerShell stdout as empty data for environment role-assignment reads
- `CHECK:C5` passed because the support matrix and machine-readable diagnostics artifact now include the `F2` result.
- `F3` mutation / approval certification is the next act.
