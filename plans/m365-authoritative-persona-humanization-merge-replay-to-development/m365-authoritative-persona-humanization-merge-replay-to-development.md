# Plan: M365 Authoritative Persona Humanization Merge Replay to Development

**Plan ID:** `m365-authoritative-persona-humanization-merge-replay-to-development`
**Parent Plan ID:** `m365-authoritative-persona-humanization-merge-to-development`
**Status:** 🟡 Draft
**Date:** 2026-04-06
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-humanization-merge-replay-to-development:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — integrate the corrected authoritative persona humanization surface into `development` through one review-approved, auditable, fail-closed replay merge without widening scope beyond the already governed final `59 total / 54 active / 5 planned` truth.
**Canonical predecessor:** `plans/m365-authoritative-persona-humanization-merge-to-development/m365-authoritative-persona-humanization-merge-to-development.md`
**Governance evidence:** `notebooks/m365/INV-M365-CG-authoritative-persona-merge-replay-package-governance-alignment-v1.ipynb`, `configs/generated/authoritative_persona_merge_replay_package_governance_alignment_v1_verification.json`
**Historical lineage:** successor replay package after the original `M1` merge package froze the pre-correction source branch, and after the completed `L83` and `L84` blocker corrections moved the truthful replay boundary to `codex/m365-authoritative-persona-post-h5-parity-correction`.

**Draft vs Active semantics:** This package starts in **Draft**. It becomes **Active** only when the corrected source branch remains clean and pushed, the approval packet is presented and receives explicit `go`, and no other merge or promotion phase is concurrently active. It becomes **Complete** only after `development` is merged from the corrected source branch, validated, pushed, and the trackers are synchronized truthfully.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including `command_exec`, `file_edit`, `commit`, and `push`. Stop on first red. Do not auto-advance to `staging`, `main`, or release-tag work.

**Branch discipline:** Source branch is fixed to `codex/m365-authoritative-persona-post-h5-parity-correction`. Target branch is fixed to `development`. Use an explicit merge commit into `development`. Preserve the blocked local replay evidence on `codex/m1-fresh-replay-blocked-development-d194b94` and `codex/m1-replay-blocked-development-a895678`. Fail closed if `origin/development` drift or merge conflicts require human judgment outside the bounded replay surface.

## Objective

Replay the bounded authoritative persona humanization merge into `development` from the corrected source branch and preserve the exact final governed truth already proven on the corrected source branch.

## Current State

- canonical predecessor package remains fixed to the historical source branch:
  - `codex/m365-authoritative-persona-humanization-expansion-plan @ cca8a90`
- corrected replay source branch:
  - `codex/m365-authoritative-persona-post-h5-parity-correction @ 2a13c5c`
- target branch at replay-package creation:
  - `origin/development @ 4c997ea`
- preserved blocked local merge evidence:
  - `codex/m1-fresh-replay-blocked-development-d194b94 @ d194b94`
  - `codex/m1-replay-blocked-development-a895678 @ a895678`
- corrected source branch status at package creation:
  - clean and pushed
- completed source-branch truth to preserve:
  - `59 total / 54 active / 5 planned / 430 total allowed persona-actions`
- `staging`, `main`, and release tagging remain out of scope for this package

## Decision Rule

`ReplaySourceReady = SourceBranchClean AND SourceBranchPushed AND L83_GO AND L84_GO`

`ReplayTargetReady = LocalDevelopmentClean AND OriginDevelopmentFetched`

`ReplayScoped = MergeSurface ⊆ Diff(4c997ea..2a13c5c) ∪ {replay_package_files, governance_trackers}`

`ReplayValidated = PreCommitGreen AND PersonaBuilderGreen AND TargetedVerifiersGreen AND FocusedPytestGreen AND DiffCheckGreen`

`M1R_GO = ReplaySourceReady AND ReplayTargetReady AND ReplayScoped AND ReplayValidated`

If `M1R_GO` is false, this phase must emit `NO-GO`, stop fail-closed, and leave `development` unpushed.

## Scope

### In scope

- verify corrected source and target branch readiness
- inspect branch drift between the corrected source branch and `development`
- merge the corrected source branch into `development` with an explicit merge commit
- resolve only bounded conflicts inside the already governed H1-H5 plus blocker-correction merge surface and governance trackers
- rerun the final humanization validation slice on merged `development`
- update the replay package and governance trackers truthfully
- push `development` only after green validation

### Out of scope

- promotion to `staging`
- promotion to `main`
- release-tag publication
- new persona, capability, or department-model changes
- edits to `registry/agents.yaml`
- edits to `registry/ai_team.json`

### File allowlist

- `plans/m365-authoritative-persona-humanization-merge-replay-to-development/**`
- `docs/prompts/codex-m365-authoritative-persona-humanization-merge-replay-to-development.md`
- `docs/prompts/codex-m365-authoritative-persona-humanization-merge-replay-to-development-prompt.txt`
- `notebooks/m365/INV-M365-CG-authoritative-persona-merge-replay-package-governance-alignment-v1.ipynb`
- `configs/generated/authoritative_persona_merge_replay_package_governance_alignment_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- any file already changed in the governed humanization surface between `4c997ea` and `2a13c5c`, but only when required for bounded merge conflict resolution that preserves the proven H1-H5 plus L83/L84 semantics

### File denylist

- `registry/agents.yaml`
- `registry/ai_team.json`
- `staging`
- `main`
- release tags
- any file outside the bounded corrected source-branch diff unless separately governed

## Requirements

- **R1** — Verify corrected source and target branch readiness before mutating `development`.
- **R2** — Keep the replay merge bounded to `development` only.
- **R3** — Merge the corrected source branch via an explicit merge commit and bounded conflict resolution.
- **R4** — Re-run the final humanization validation slice on the merged `development` state.
- **R5** — Synchronize trackers and replay-package status truthfully.
- **R6** — Push `development` only after green validation and stop before any further promotion.

## Child Acts

### M1R-A — Preflight and branch inventory

- fetch branch topology
- confirm the corrected source branch is still the governed green replay surface
- confirm `development` is clean before replay merge

### M1R-B — Merge replay and bounded conflict resolution

- merge `codex/m365-authoritative-persona-post-h5-parity-correction` into `development`
- resolve only bounded conflicts inside the governed humanization plus blocker-correction surface or tracker files
- stop if conflict resolution changes the proven semantics

### M1R-C — Validation and development push

- rerun the merge-state validation suite
- push `development` only if every required gate is green

### M1R-D — Governance closeout

- update this package status
- update `Operations/EXECUTION_PLAN.md`
- update `Operations/ACTION_LOG.md`
- update `Operations/PROJECT_FILE_INDEX.md`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-humanization-merge-replay-to-development.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-humanization-merge-replay-to-development-prompt.txt`

## Validation Strategy

- capture corrected source and target branch SHAs before merge
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
- Do not silently rewrite H1-H5, L83, or L84 semantics during conflict resolution.
- Stop if `origin/development` drift changes the replay surface materially.
