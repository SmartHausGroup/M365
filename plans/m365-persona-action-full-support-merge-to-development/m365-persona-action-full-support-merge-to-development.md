# Plan: M365 Persona-Action Full-Support Merge to Development

**Plan ID:** `plan:m365-persona-action-full-support-merge-to-development`
**Parent Plan ID:** `plan:m365-persona-action-full-support-remediation`
**Status:** `complete`
**Date:** `2026-04-08`
**Owner:** `SMARTHAUS`
**Execution plan reference:** `plan:m365-persona-action-full-support-merge-to-development:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — integrate the completed, truthful M365-only persona/action workforce surface into `development` through one review-approved, auditable, fail-closed merge without widening scope beyond the already governed post-`P5` truth.
**Governance evidence:** `notebooks/m365/INV-M365-DF-persona-action-recertification-closeout-v1.ipynb`, `configs/generated/persona_action_recertification_closeout_v1_verification.json`

**Draft vs Active semantics:** This package starts in **Draft**. It becomes **Active** only when the source branch remains clean and pushed, the approval packet is presented and receives explicit `go`, and no other merge or promotion package is concurrently active. It becomes **Complete** only after `development` is merged from the source branch, validated, pushed, and the trackers are synchronized truthfully.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including `command_exec`, `file_edit`, `commit`, and `push`. Stop on first red. Do not auto-advance to `staging`, `main`, or release-tag work.

**Branch discipline:** Source branch is fixed to `codex/m365-persona-action-full-support-remediation`. Target branch is fixed to `development`. Use an explicit merge commit into `development`. Fail closed if `origin/development` drift or merge conflicts require human judgment outside the bounded `P1` through `P5` remediation surface.

## Objective

Merge the completed persona-action full-support remediation branch into `development` and preserve the exact final governed workforce truth already proven on the source branch.

## Current State

- corrected source branch:
  - `codex/m365-persona-action-full-support-remediation @ b02e039`
- target branch at package creation:
  - `origin/development @ 8dfa986`
- validated merge commit:
  - `development @ 3894971`
- source branch status at package creation:
  - clean and pushed
- completed source-branch truth to preserve:
  - `172` unique persona-facing aliases
  - `445` active persona/action pairs
  - unique alias matrix: `103 green / 36 approval-gated / 1 actor-tier-gated / 32 fenced`
  - active pair matrix: `360 green / 49 approval-gated / 1 actor-tier-gated / 35 fenced`
  - `0 permission-blocked / 0 legacy-stubbed / 0 dead-routed / 0 orphaned`
- `staging`, `main`, and release tagging remain out of scope for this package

## Decision Rule

`MergeSourceReady = SourceBranchClean AND SourceBranchPushed AND P5_GO`

`MergeTargetReady = LocalDevelopmentClean AND OriginDevelopmentFetched`

`MergeScoped = MergeSurface ⊆ Diff(8dfa986..b02e039) ∪ {merge_package_files, governance_trackers}`

`MergeValidated = PyCompileGreen AND TargetedVerifiersGreen AND FocusedPytestGreen AND PreCommitGreen AND DiffCheckGreen`

`M1_GO = MergeSourceReady AND MergeTargetReady AND MergeScoped AND MergeValidated`

If `M1_GO` is false, this phase must emit `NO-GO`, stop fail-closed, and leave `development` unpushed.

## Scope

### In scope

- verify source and target branch readiness
- inspect branch drift between the completed source branch and `development`
- merge the source branch into `development` with an explicit merge commit
- resolve only bounded conflicts inside the already governed `P1` through `P5` remediation surface and governance trackers
- rerun the final persona-action remediation validation slice on merged `development`
- update the merge package and governance trackers truthfully
- push `development` only after green validation

### Out of scope

- promotion to `staging`
- promotion to `main`
- release-tag publication
- new persona, capability, or workforce-model changes
- UCP runtime edits

### File allowlist

- `plans/m365-persona-action-full-support-merge-to-development/**`
- `docs/prompts/codex-m365-persona-action-full-support-merge-to-development.md`
- `docs/prompts/codex-m365-persona-action-full-support-merge-to-development-prompt.txt`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- any file already changed in the governed `P1` through `P5` remediation surface between `8dfa986` and `b02e039`, but only when required for bounded merge conflict resolution that preserves the proven `P1` through `P5` semantics

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
- **R4** — Re-run the final persona-action remediation validation slice on the merged `development` state.
- **R5** — Synchronize trackers and package status truthfully.
- **R6** — Push `development` only after green validation and stop before any further promotion.

## Child Acts

### M1-A — Preflight and branch inventory

- fetch branch topology
- confirm the completed source branch is still the governed green merge surface
- confirm `development` is clean before merge execution

### M1-B — Merge and bounded conflict resolution

- merge `codex/m365-persona-action-full-support-remediation` into `development`
- resolve only bounded conflicts inside the governed persona-action remediation surface or tracker files
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

- **Detailed prompt:** `docs/prompts/codex-m365-persona-action-full-support-merge-to-development.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-persona-action-full-support-merge-to-development-prompt.txt`

## Validation Strategy

- capture source and target branch SHAs before merge
- require an explicit merge commit on `development`
- run:
  - `python3 -m py_compile src/ops_adapter/actions.py src/smarthaus_common/permission_enforcer.py src/smarthaus_common/executor_routing.py src/smarthaus_common/approval_risk.py tests/test_ops_adapter.py tests/test_policies.py tests/test_persona_registry_v2.py tests/test_operations_department_pack_v1.py tests/test_project_management_department_pack_v1.py tests/test_engineering_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_operations_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_project_management_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_engineering_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py tests/test_policies.py tests/test_persona_registry_v2.py tests/test_operations_department_pack_v1.py tests/test_project_management_department_pack_v1.py tests/test_engineering_department_pack_v1.py`
  - `pre-commit run --all-files`
  - `git diff --check`
- replay branch inspection after push and require local `development` plus `origin/development` to resolve to the same merge result

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] this package `status -> complete`

## Agent Constraints

- Do not merge to `staging` or `main` in this package.
- Do not silently rewrite `P1` through `P5` semantics during conflict resolution.
- Stop if `origin/development` drift changes the merge surface materially.

## Execution Status

- `R1` complete on 2026-04-08: confirmed the source branch at `b02e039`, confirmed local `development` matched `origin/development @ 8dfa986`, and prepared the bounded merge surface.
- `R2` complete on 2026-04-08: kept the merge bounded to `development` only and preserved the governed post-`P5` workforce truth.
- `R3` complete on 2026-04-08: merged `codex/m365-persona-action-full-support-remediation` into `development` with explicit merge commit `3894971`.
- `R4` complete on 2026-04-08: the merged-development validation slice passed `python3 -m py_compile`, the three department-pack verifiers, focused pytest (`163 passed`), `pre-commit run --all-files`, and `git diff --check`.
- `R5` complete on 2026-04-08: synchronized this merge package plus `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, and `Operations/PROJECT_FILE_INDEX.md` to reflect the successful merge outcome.
- `R6` complete on 2026-04-08: pushed `development` after green validation and stopped before any `staging`, `main`, or release-tag action.
