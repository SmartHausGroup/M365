# Plan: M365 Persona-Action P3 Department-Pack Scope Correction

**Plan ID:** `m365-persona-action-p3-department-pack-scope-correction`
**Parent Plan ID:** `m365-persona-action-full-support-remediation`
**Status:** 🟢 Complete
**Date:** 2026-04-07
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-p3-department-pack-scope-correction:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the persona-action remediation truthful and fail-closed by refusing to retire the last non-M365 permission-blocked aliases until the affected department-pack authority surfaces are explicitly admitted and notebook-backed.
**Canonical predecessor:** `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
**Governance evidence:** `notebooks/m365/INV-M365-DC-persona-action-p3-department-pack-scope-correction-v1.ipynb`, `configs/generated/persona_action_p3_department_pack_scope_correction_v1_verification.json`
**Historical lineage:** successor blocker package after the first bounded `P3` wave reduced the frozen `permission_blocked_aliases_with_no_tier_support` set to four aliases whose truthful retirement now crosses department-pack authority surfaces outside the original parent allowlist.
**Completion status (2026-04-07 13:05 EDT):** `GO` — widened the parent `P3` repair surface to the affected operations / project-management / engineering department-pack contracts, then handed the parent initiative back to the second bounded `P3` retirement wave, which closed the remaining non-M365 aliases and returned the parent plan to `P4`.

**Draft vs Active semantics:** This child plan starts in **Draft**. It becomes **Active** only when the parent initiative remains on `P3`, the approval packet is presented and receives explicit `go`, and no sibling phase under the parent initiative is concurrently active. It becomes **Complete** only after the widened authority scope is notebook-backed, the parent plan and trackers are synchronized, the child package is committed and pushed, and control is truthfully returned to the parent `P3` retirement wave.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook extraction, file edits, tests, commit, and push. Stop on first red. Do not auto-advance to `P4`.

**Notebook-first discipline:** `P3S` is a notebook-backed governance-unblock phase. The remaining alias inventory, the cross-surface authority gap, and the admissible future repair set must be frozen in notebooks first. No widened `P3` runtime, registry, or department-pack edits are allowed before the scope evidence is green.

## Objective

Create the bounded child phase that widens `P3` into the affected department-pack authority surfaces and publishes notebook-backed governance evidence so the parent initiative can truthfully retire the final non-M365 permission-blocked aliases and their companion stale department-pack claims.

## Current State

- Parent initiative:
  - `plan:m365-persona-action-full-support-remediation`
- Completed parent phases:
  - `P0`
  - `P1`
  - `P2`
  - first bounded `P3` wave
- Remaining frozen `P3` aliases with no truthful canonical permission target:
  - `create-project`
  - `deployment.preview`
  - `list-projects`
  - `provision-client-services`
- Companion already-retired runtime claims still present in the same affected department packs:
  - `deployment.production`
  - `content.create`
  - `content.update`
  - `analytics.read`
  - `seo.update`
  - `update-project-status`
  - `deprovision-client-services`
  - `get-client-status`
- Affected department-pack authority surfaces currently outside the parent allowlist:
  - `registry/department_pack_operations_v1.yaml`
  - `registry/department_pack_project_management_v1.yaml`
  - `registry/department_pack_engineering_v1.yaml`
- Matching commercialization and validation surfaces currently outside the parent allowlist:
  - `docs/commercialization/m365-operations-department-pack-v1.md`
  - `docs/commercialization/m365-project-management-department-pack-v1.md`
  - `docs/commercialization/m365-engineering-department-pack-v1.md`
  - `scripts/ci/verify_operations_department_pack_v1.py`
  - `scripts/ci/verify_project_management_department_pack_v1.py`
  - `scripts/ci/verify_engineering_department_pack_v1.py`
  - `tests/test_operations_department_pack_v1.py`
  - `tests/test_project_management_department_pack_v1.py`
  - `tests/test_engineering_department_pack_v1.py`
- Live governance blocker:
  - `validate_action(governance_edit)` for this scope-correction package returned `allowed:false`
  - violation id: `map-5-governance-notebook-evidence`
  - blocker reason: a governance scope change requires explicit notebook backing

## Decision Rule

`RemainingAliasSetFrozen = {create-project, deployment.preview, list-projects, provision-client-services}`

`CompanionClaimDriftFrozen = {deployment.production, content.create, content.update, analytics.read, seo.update, update-project-status, deprovision-client-services, get-client-status}`

`AuthorityScopeGapEstablished = affected department-pack contracts, docs, verifiers, and tests fall outside the original parent allowlist even though they still claim the remaining aliases or companion retired claims`

`NotebookBackedScopeDefined = P3S owns a phase-specific governance notebook and generated verification output proving the widened repair set`

`P3S_GO = RemainingAliasSetFrozen AND CompanionClaimDriftFrozen AND AuthorityScopeGapEstablished AND NotebookBackedScopeDefined`

If `P3S_GO` is false, `P3S` must emit `NO-GO`, stop fail-closed, and keep the parent initiative at `P3`.

## Scope

### In scope

- restate the exact `P3` scope gap from live runtime, registry, and department-pack truth
- add the affected department-pack authority, commercialization, verifier, and test surfaces to the admissible `P3` repair set
- publish notebook-backed governance evidence and generated verification output for the widened `P3` boundary
- synchronize the parent remediation plan and trackers so the next bounded `P3` act may retire the remaining aliases truthfully
- hand control back to the parent initiative only after the child package is committed and pushed

### Out of scope

- executing the actual second-wave `P3` retirement edits
- `P4` policy-fence remediation
- UCP runtime changes
- unrelated department-pack surfaces outside operations, project-management, and engineering

### File allowlist

- `plans/m365-persona-action-p3-department-pack-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-p3-department-pack-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-p3-department-pack-scope-correction-prompt.txt`
- `notebooks/m365/INV-M365-DC-persona-action-p3-department-pack-scope-correction-v1.ipynb`
- `configs/generated/persona_action_p3_department_pack_scope_correction_v1_verification.json`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `src/ops_adapter/actions.py`
- `tests/test_ops_adapter.py`
- `registry/agents.yaml`
- `registry/persona_registry_v2.yaml`
- `registry/department_pack_operations_v1.yaml`
- `registry/department_pack_project_management_v1.yaml`
- `registry/department_pack_engineering_v1.yaml`
- `docs/commercialization/m365-operations-department-pack-v1.md`
- `docs/commercialization/m365-project-management-department-pack-v1.md`
- `docs/commercialization/m365-engineering-department-pack-v1.md`
- `scripts/ci/verify_operations_department_pack_v1.py`
- `scripts/ci/verify_project_management_department_pack_v1.py`
- `scripts/ci/verify_engineering_department_pack_v1.py`
- `tests/test_operations_department_pack_v1.py`
- `tests/test_project_management_department_pack_v1.py`
- `tests/test_engineering_department_pack_v1.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `../UCP/**`
- any path not listed in the allowlist

## Requirements

- **R1** — Make the remaining `P3` authority-scope gap explicit from live repo truth.
- **R2** — Produce notebook-backed governance evidence for the widened `P3` repair set.
- **R3** — Admit the affected department-pack authority, commercialization, verifier, and test surfaces into the bounded `P3` repair set.
- **R4** — Reopen the future bounded `P3` file-edit validation under child-plan authority for runtime, registry, and department-pack retirement.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Commit and push `P3S` before resuming the parent initiative.

## Child Acts

### P3SA — Scope-gap freeze

- freeze the remaining alias inventory, companion claim drift, and affected department-pack surfaces

### P3SB — Governance notebook evidence

- publish the phase-specific notebook-backed scope evidence and generated verification output

### P3SC — Parent handback

- widen the parent `P3` repair surface truthfully
- synchronize trackers
- validate, commit, push, and return the initiative to `P3`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-persona-action-p3-department-pack-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-persona-action-p3-department-pack-scope-correction-prompt.txt`

## Validation Strategy

- require the governance notebook and generated verification to preserve:
  - the exact `4` remaining `P3` aliases
  - the exact `8` companion stale department-pack claims
  - the exact `3` affected department-pack authority files and their matching docs/verifiers/tests
- require the parent plan allowlist to widen only to the affected department-pack surfaces
- require tracker truth to point to `P3S` while the child package is active
- run `git diff --check`

## Agent Constraints

- Do not execute the second-wave `P3` retirement edits inside `P3S`.
- Do not widen beyond operations, project-management, and engineering department-pack surfaces.
- Do not widen into `P4`.
- Commit and push `P3S` before any second-wave `P3` file edits begin.

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] this child plan `status -> complete`

## Execution Outcome

- **Decision:** `GO`
- **Approved by:** `operator explicit go`
- **Completion timestamp:** `2026-04-07 13:05:18 EDT`
