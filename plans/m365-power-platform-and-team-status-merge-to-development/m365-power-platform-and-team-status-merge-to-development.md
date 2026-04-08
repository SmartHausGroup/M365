# Plan: M365 Power Platform and Team Status Merge to Development

**Plan ID:** `plan:m365-power-platform-and-team-status-merge-to-development`
**Parent Plan ID:** `plan:m365-team-status-workflow-enablement`
**Status:** `in_progress`
**Date:** `2026-04-08`
**Owner:** `SMARTHAUS`
**Execution plan reference:** `plan:m365-power-platform-and-team-status-merge-to-development:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — integrate the completed tenant-generic Power Platform auth repair and weekly team-status workflow enablement into `development` through one bounded, auditable, fail-closed merge so the repo’s direct M365 workflow surface is usable without SmartHaus-specific engine assumptions.
**Governance evidence:** `notebooks/m365/INV-M365-DH-team-status-workflow-plan-governance-alignment-v1.ipynb`, `configs/generated/team_status_workflow_plan_governance_alignment_v1_verification.json`

**Draft vs Active semantics:** This package starts in **Draft**. It becomes **Active** only when the source branch remains clean and pushed, the operator has explicitly requested the merge, and no other merge or promotion package is concurrently active. It becomes **Complete** only after `development` contains the validated merge result, `origin/development` matches it, and the trackers are synchronized truthfully.

**Approval and governance gates:** Call MCP `validate_action` before every mutating action, including `command_exec`, `file_edit`, `commit`, and `push`. Use an explicit merge commit into `development`. Stop on first red. Do not touch `staging`, `main`, or release tags in this package.

**Branch discipline:** Source branch is fixed to `codex/m365-power-platform-executor-auth-remediation`. Target branch is fixed to `development`. Fail closed if `origin/development` drift or merge conflicts require edits outside the bounded source-branch diff and governance trackers.

## Objective

Merge the completed tenant-generic Power Platform auth repair and team-status workflow enablement branch into `development` and preserve the exact governed runtime truth already proven on the source branch.

## Current State

- corrected source branch:
  - `codex/m365-power-platform-executor-auth-remediation @ 5b4efb6`
- target branch at package creation:
  - `origin/development @ 541c00e`
- source branch status at package creation:
  - clean and pushed
- completed source-branch truth to preserve:
  - Power Platform executor resolution is tenant-generic at the engine layer
  - the repo no longer depends on shared Graph/Azure env aliases for Power Platform auth
  - SharePoint list creation is exposed on the instruction surface
  - the bounded weekly status workflow provisioning path is live
  - the live reference workflow is provisioned successfully on the Founding Team site
- `staging`, `main`, and release tagging remain out of scope

## Decision Rule

`MergeSourceReady = SourceBranchClean AND SourceBranchPushed AND WorkflowPackageComplete`

`MergeTargetReady = LocalDevelopmentClean AND OriginDevelopmentFetched`

`MergeScoped = MergeSurface ⊆ Diff(541c00e..5b4efb6) ∪ {merge_package_files, governance_trackers}`

`MergeValidated = PyCompileGreen AND VerifiersGreen AND FocusedPytestGreen AND PreCommitGreen AND DiffCheckGreen`

`M1_GO = MergeSourceReady AND MergeTargetReady AND MergeScoped AND MergeValidated`

If `M1_GO` is false, this package must emit `NO-GO`, stop fail-closed, and leave `development` unpushed.

## Scope

### In scope

- verify source and target branch readiness
- inspect branch drift between the completed source branch and `development`
- merge the source branch into `development` with an explicit merge commit
- resolve only bounded conflicts inside the governed Power Platform auth and team-status workflow surface
- rerun the final bounded validation slice on merged `development`
- update the merge package and governance trackers truthfully
- push `development` only after green validation

### Out of scope

- promotion to `staging`
- promotion to `main`
- release-tag publication
- new workflow design work
- UCP runtime edits

### File allowlist

- `plans/m365-power-platform-and-team-status-merge-to-development/**`
- `docs/prompts/codex-m365-power-platform-and-team-status-merge-to-development.md`
- `docs/prompts/codex-m365-power-platform-and-team-status-merge-to-development-prompt.txt`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- any file already changed in the governed source-branch diff between `541c00e` and `5b4efb6`, but only when required for bounded merge conflict resolution that preserves the proven semantics

### File denylist

- `../UCP/**`
- `staging`
- `main`
- release tags
- any file outside the bounded source-branch diff unless separately governed

## Requirements

- **R1** — Verify source and target branch readiness before mutating `development`.
- **R2** — Keep the merge bounded to `development` only.
- **R3** — Merge the governed source branch via an explicit merge commit and bounded conflict resolution.
- **R4** — Re-run the final bounded validation slice on the merged `development` state.
- **R5** — Synchronize trackers and package status truthfully.
- **R6** — Push `development` only after green validation and stop before any further promotion.

## Child Acts

### M1-A — Preflight and branch inventory

- fetch branch topology
- confirm the completed source branch is still the governed green merge surface
- confirm `development` is clean before merge execution

### M1-B — Merge and bounded conflict resolution

- merge `codex/m365-power-platform-executor-auth-remediation` into `development`
- resolve only bounded conflicts inside the governed Power Platform auth and team-status workflow surface or tracker files
- stop if conflict resolution changes the proven semantics

### M1-C — Validation and development push

- rerun the merge-state validation suite
- push `development` only if every required gate is green

### M1-D — Governance closeout

- update this package status
- update `Operations/EXECUTION_PLAN.md`
- update `Operations/ACTION_LOG.md`
- update `Operations/PROJECT_FILE_INDEX.md`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-power-platform-and-team-status-merge-to-development.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-power-platform-and-team-status-merge-to-development-prompt.txt`

## Validation Strategy

- capture source and target branch SHAs before merge
- require an explicit merge commit on `development`
- run:
  - `python3 -m py_compile src/provisioning_api/routers/m365.py src/smarthaus_common/tenant_config.py src/smarthaus_common/power_apps_client.py src/smarthaus_common/power_automate_client.py src/smarthaus_common/team_status_workflow.py scripts/ops/provision_team_status_workflow.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_sharepoint_onedrive_files_expansion.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_power_automate_expansion.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_capability_registry.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_caio_m365_contract.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_tenant_config_powerplatform.py tests/test_sharepoint_onedrive_files_expansion_v2.py tests/test_power_automate_expansion_v2.py tests/test_team_status_workflow.py`
  - `pre-commit run --all-files`
  - `git diff --check`
- replay branch inspection after push and require local `development` plus `origin/development` to resolve to the same merge result

## Governance Closure

- [ ] `Operations/ACTION_LOG.md`
- [ ] `Operations/EXECUTION_PLAN.md`
- [ ] `Operations/PROJECT_FILE_INDEX.md`
- [ ] this package `status -> complete`

## Agent Constraints

- Do not merge to `staging` or `main` in this package.
- Do not silently rewrite the proven Power Platform auth or team-status workflow semantics during conflict resolution.
- Stop if `origin/development` drift changes the merge surface materially.

## Execution Status

- `R1` pending.
- `R2` pending.
- `R3` pending.
- `R4` pending.
- `R5` pending.
- `R6` pending.
