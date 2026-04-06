# Plan: M365 Authoritative Persona Humanization Merge to Development

**Plan ID:** `m365-authoritative-persona-humanization-merge-to-development`
**Parent Plan ID:** `m365-authoritative-persona-humanization-expansion`
**Status:** 🟡 Draft
**Date:** 2026-04-05
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-humanization-merge-to-development:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — integrate the completed authoritative persona humanization surface into `development` through a review-approved, auditable, fail-closed merge without silently widening scope beyond the already governed final `59 total / 54 active / 5 planned` truth.
**Canonical predecessor:** `plans/m365-authoritative-persona-activation-gate-closeout/m365-authoritative-persona-activation-gate-closeout.md`
**Historical lineage:** follow-on merge package for the completed H1-H5 authoritative persona humanization initiative on `codex/m365-authoritative-persona-humanization-expansion-plan`.

**Draft vs Active semantics:** This package starts in **Draft**. It becomes **Active** only when the source branch remains clean and pushed, the approval packet is presented and receives explicit `go`, and no other merge or promotion phase is concurrently active. It becomes **Complete** only after `development` is merged, validated, pushed, and the trackers are synchronized truthfully.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including `command_exec`, `file_edit`, `commit`, and `push`. Stop on first red. Do not auto-advance to `staging`, `main`, or release-tag work.

**Branch discipline:** Source branch is fixed to `codex/m365-authoritative-persona-humanization-expansion-plan`. Target branch is fixed to `development`. Use an explicit merge commit into `development`. Fail closed if `origin/development` drift or merge conflicts require human judgment outside the bounded merge surface.

## Objective

Merge the fully validated authoritative persona humanization surface into `development` and preserve the exact final governed truth already proven on the source branch.

## Current State

- source branch head at package creation: `cca8a90`
- target branch head at package creation: `4c997ea`
- source branch status at package creation: clean and pushed
- completed source-branch truth to preserve: `59 total / 54 active / 5 planned`
- `staging`, `main`, and release tagging are out of scope for this package

## Decision Rule

`SourceReady = SourceBranchClean AND SourceBranchPushed AND H5_GO`

`DevelopmentReady = LocalDevelopmentClean AND OriginDevelopmentFetched`

`MergeScoped = MergeSurface ⊆ Diff(4c997ea..cca8a90) ∪ {merge_package_files, governance_trackers}`

`MergeValidated = PreCommitGreen AND PersonaBuilderGreen AND TargetedVerifiersGreen AND FocusedPytestGreen AND DiffCheckGreen`

`M1_GO = SourceReady AND DevelopmentReady AND MergeScoped AND MergeValidated`

If `M1_GO` is false, this phase must emit `NO-GO`, stop fail-closed, and leave `development` unpushed.

## Scope

### In scope

- verify source and target branch readiness
- inspect branch drift between the source branch and `development`
- merge the completed source branch into `development` with an explicit merge commit
- resolve only bounded conflicts inside the already governed H1-H5 merge surface and governance trackers
- rerun the final humanization validation slice on merged `development`
- update the merge package and governance trackers truthfully
- push `development` only after green validation

### Out of scope

- promotion to `staging`
- promotion to `main`
- release-tag publication
- new persona, capability, or department-model changes
- edits to `registry/agents.yaml`
- edits to `registry/ai_team.json`

### File allowlist

- `plans/m365-authoritative-persona-humanization-merge-to-development/**`
- `docs/prompts/codex-m365-authoritative-persona-humanization-merge-to-development.md`
- `docs/prompts/codex-m365-authoritative-persona-humanization-merge-to-development-prompt.txt`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- any file already changed in the governed humanization surface between `4c997ea` and `cca8a90`, but only when required for bounded merge conflict resolution that preserves the proven H1-H5 semantics

### File denylist

- `registry/agents.yaml`
- `registry/ai_team.json`
- `staging`
- `main`
- release tags
- any file outside the bounded source-branch diff unless separately governed

## Requirements

- **R1** — Verify source and target branch readiness before mutating `development`.
- **R2** — Keep the merge bounded to `development` only.
- **R3** — Merge via an explicit merge commit and bounded conflict resolution.
- **R4** — Re-run the final humanization validation slice on the merged `development` state.
- **R5** — Synchronize trackers and merge-package status truthfully.
- **R6** — Push `development` only after green validation and stop before any further promotion.

## Child Acts

### M1A — Preflight and branch inventory

- fetch branch topology
- confirm the source branch is still the governed green surface
- confirm `development` is clean before merge

### M1B — Merge and bounded conflict resolution

- merge `codex/m365-authoritative-persona-humanization-expansion-plan` into `development`
- resolve only bounded conflicts inside the governed humanization surface or tracker files
- stop if conflict resolution changes the proven H1-H5 semantics

### M1C — Validation and development push

- rerun the merge-state validation suite
- push `development` only if every required gate is green

### M1D — Governance closeout

- update this package status
- update `Operations/EXECUTION_PLAN.md`
- update `Operations/ACTION_LOG.md`
- update `Operations/PROJECT_FILE_INDEX.md`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-humanization-merge-to-development.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-humanization-merge-to-development-prompt.txt`

## Validation Strategy

- capture source and target branch SHAs before merge
- require an explicit merge commit on `development`
- run:
  - `PYTHONPATH=src python3 scripts/ci/build_persona_registry_v2.py`
  - `python3 scripts/ci/verify_authoritative_digital_employee_records_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_persona_registry_v2.py`
  - `python3 scripts/ci/verify_persona_certification_v1.py`
  - `python3 scripts/ci/verify_department_certification_v1.py`
  - `python3 scripts/ci/verify_enterprise_release_gate_v2.py`
  - `python3 scripts/ci/verify_activated_persona_surface_v1.py`
  - `python3 scripts/ci/verify_workforce_packaging_v1.py`
  - `python3 scripts/ci/verify_*_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_authoritative_digital_employee_records_v1.py tests/test_authoritative_persona_registry_rebase_v1.py tests/test_persona_registry_v2.py tests/test_persona_certification_v1.py tests/test_department_certification_v1.py tests/test_activated_persona_surface_v1.py tests/test_workforce_packaging_v1.py tests/test_*_department_pack_v1.py`
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
- Do not silently rewrite H1-H5 semantics during conflict resolution.
- Stop if `origin/development` drift changes the merge surface materially.
