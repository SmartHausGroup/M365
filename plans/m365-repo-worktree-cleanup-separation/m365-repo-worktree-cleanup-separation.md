# Plan: M365 Repo — Worktree Cleanup and Separation

**Plan ID:** `m365-repo-worktree-cleanup-separation`
**Status:** Active (`R1`, `R2`, and `R3` complete on 2026-03-17; `R4` next)
**Date:** 2026-03-17
**Owner:** SmartHaus
**Execution plan reference:** `plan:m365-repo-worktree-cleanup-separation:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — production-ready, policy-gated, auditable M365 operations with no credential leakage and no ambiguous repo state.

## Objective

Reduce the current mixed dirty worktree into a safe, reviewable, governed state by removing secret-bearing artifacts, reverting formatter-only noise, and separating the remaining substantive payload into clear keep versus discard buckets.

## Problem Statement

The current worktree mixes:

- legitimate M365 runtime, governance, and packaging work
- repo-wide formatter fallout from a failed `pre-commit run --all-files`
- untracked analysis/demo/dashboard artifacts
- tenant-specific config state
- plaintext secret-bearing documents that should not remain in the repo

This state is unsafe for review and unsafe for future commits unless it is separated deterministically.

## Scope

### In scope

- create a formal cleanup initiative and prompt pair
- remove or sanitize secret-bearing local artifacts that should not remain in the repo worktree
- revert tracked formatter-only noise caused by the failed repo-wide pre-commit run
- classify the remaining substantive payload into:
  - keep in repo
  - split into separate initiative or branch
  - delete as non-canonical/demo/generated residue
- document the outcome in `Operations/ACTION_LOG.md` and `Operations/EXECUTION_PLAN.md`

### Out of scope

- committing the remaining substantive payload
- implementing new runtime features as part of cleanup
- changing commercialization scope or MA scorecard requirements
- deleting substantive feature work without explicit classification

## Requirements

### R1 — Governed cleanup initiative

- Create a formal plan and Codex prompt pair for repo cleanup and worktree separation.

### R2 — Secret scrub

- Remove secret-bearing untracked docs or sanitize them so no plaintext credentials remain in the worktree.
- Identify any credentials that must be rotated due to exposure.

### R3 — Formatter-noise revert

- Revert tracked files whose diffs are formatter-only fallout from the failed repo-wide pre-commit run.
- Do not revert substantive code or documentation changes.

### R4 — Residual payload classification

- Classify the remaining tracked and untracked substantive payload into:
  - canonical M365 pack/runtime work
  - separate demo/dashboard/project-management work
  - generated/cache/junk

### R5 — Governance synchronization

- Update `Operations/EXECUTION_PLAN.md` and `Operations/ACTION_LOG.md` to reflect cleanup actions and remaining decisions.

## Initial Execution Order

1. `R1` Create the cleanup plan and prompt pair.
2. `R2` Remove the known secret-bearing local docs and record the need for credential rotation.
3. `R3` Revert the tracked formatter-only fallout.
4. `R4` Re-assess the reduced worktree and define the next split.
5. `R5` Synchronize governance tracking.

## Execution Status

- `R1` complete on 2026-03-17: created the cleanup plan triplet, prompt pair, and initiative entry in `Operations/EXECUTION_PLAN.md`.
- `R2` complete on 2026-03-17: removed the plaintext secret-bearing local docs `CODEX_CONFIGURATION.md` and `AGENT_SYSTEM_DEEP_DIVE.md` from the worktree. These exposed credentials should be considered compromised and rotated.
- `R3` complete on 2026-03-17: reverted the tracked formatter-only fallout introduced by the failed repo-wide `pre-commit run --all-files`. The formatter-noise bucket is now zero.
- `R4` is in progress on 2026-03-17: by explicit user direction, treat the remaining substantive payload as intended keep-work for commit/push, with only the removed plaintext-secret docs and ignored cache artifacts excluded.

## Success Criteria

- No plaintext credentials remain in untracked repo docs created by local workflow.
- All tracked formatter-only fallout is reverted.
- The remaining worktree is materially smaller and easier to separate.
- Remaining dirty files are classified into explicit keep/split/delete buckets with rationale.

## Validation

- `rg -n "GRAPH_CLIENT_SECRET|MICROSOFT_CLIENT_SECRET|AZURE_CLIENT_SECRET|CAIO_API_KEY" CODEX_CONFIGURATION.md AGENT_SYSTEM_DEEP_DIVE.md` returns no active secret-bearing artifacts because those files are removed or sanitized.
- `git diff --name-only --diff-filter=M` no longer includes the formatter-only bucket identified during triage.
- `git status --short` shows the reduced worktree after `R2` and `R3`.
- `Operations/ACTION_LOG.md` records the cleanup actions with this plan reference.

## Rollback

- If a removed secret-bearing doc must be retained, restore a sanitized version only, never the plaintext secret material.
- If a reverted formatter-noise file is later found to contain real content, re-apply the substantive change in a dedicated follow-up edit rather than restoring the whole noisy diff.
