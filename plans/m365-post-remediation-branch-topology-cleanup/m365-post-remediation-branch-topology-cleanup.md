# Plan: M365 Post-Remediation Branch Topology Cleanup

**Plan ID:** `plan:m365-post-remediation-branch-topology-cleanup`
**Parent Plan ID:** `plan:m365-persona-action-full-support-merge-to-development`
**Status:** `complete`
**Date:** `2026-04-08`
**Owner:** `SmartHaus`
**Execution plan reference:** `plan:m365-post-remediation-branch-topology-cleanup:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the repo in an auditable, policy-gated, reviewable state by collapsing merged feature-branch debt into the long-lived `development`, `staging`, and `main` branches only.

## Objective

Clean up the local and remote feature-branch debt left after the persona-action remediation and merge-to-`development` initiatives are complete, without discarding any unique work.

## Problem Statement

The current branch topology contains only long-lived environment branches plus several merged feature branches that are already fully reachable from `development`:

- local feature branches:
  - `codex/m365-direct-function-validation`
  - `codex/m365-direct-runtime-readiness-remediation`
  - `codex/m365-persona-action-certification-plan`
  - `codex/m365-persona-action-full-support-remediation`
- remote feature branches:
  - `origin/codex/m365-direct-function-validation`
  - `origin/codex/m365-direct-runtime-readiness-remediation`
  - `origin/codex/m365-persona-action-certification-plan`
  - `origin/codex/m365-persona-action-full-support-remediation`
  - `origin/codex/m365-token-acquisition-validation`
  - `origin/feature/m365_personas`

This state is operationally noisy and increases the chance of stale-branch mistakes even though the work is already merged into `development`.

## Scope

### In scope

- create a formal cleanup initiative and prompt pair
- record the keep set and the explicitly approved delete sets
- verify that each delete-candidate branch has `0` unique commits beyond `development`
- delete the four local `codex/*` feature branches
- delete the six stale remote feature branches
- synchronize `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, and `Operations/PROJECT_FILE_INDEX.md`

### Out of scope

- deleting `development`, `staging`, or `main`
- changing runtime, registry, commercialization, MA, or certification truth
- new merge or promotion work
- deleting any branch found to contain unique, unmerged work

## Requirements

### R1 — Governed cleanup initiative

- Create the cleanup plan triplet and prompt pair.

### R2 — Canonical branch inventory

- Record the keep set, the delete-local set, and the delete-remote set.

### R3 — Unique-work verification

- Prove every delete-candidate branch has `0` commits not reachable from `development`.

### R4 — Local branch cleanup

- Delete the four scoped local `codex/*` feature branches.

### R5 — Remote branch cleanup

- Delete the six scoped stale remote feature branches.

### R6 — Governance synchronization

- Update execution tracking so cleanup is recorded and the repo is left with only `development`, `staging`, and `main` as the active branch set.

## Keep Set

- `development`
- `staging`
- `main`

## Delete Set — Local

- `codex/m365-direct-function-validation`
- `codex/m365-direct-runtime-readiness-remediation`
- `codex/m365-persona-action-certification-plan`
- `codex/m365-persona-action-full-support-remediation`

## Delete Set — Remote

- `origin/codex/m365-direct-function-validation`
- `origin/codex/m365-direct-runtime-readiness-remediation`
- `origin/codex/m365-persona-action-certification-plan`
- `origin/codex/m365-persona-action-full-support-remediation`
- `origin/codex/m365-token-acquisition-validation`
- `origin/feature/m365_personas`

## Initial Execution Order

1. `R1` Create the cleanup plan and prompt pair.
2. `R2` Record the canonical keep/delete branch inventory.
3. `R3` Prove every delete candidate is fully merged into `development`.
4. `R4` Delete the scoped local feature branches.
5. `R5` Delete the scoped remote feature branches.
6. `R6` Synchronize governance tracking and leave only the long-lived environment branches.

## Success Criteria

- local branch list contains only `development`, `staging`, and `main`
- remote branch list contains only `origin/development`, `origin/staging`, and `origin/main`
- every deleted branch was proven to have `0` unique commits beyond `development`
- tracker files truthfully show the cleanup completion

## Validation

- `git status --short --branch` is clean on `development`
- `git rev-list --left-right --count development...<branch>` returns `<n> 0` for every delete candidate before deletion
- `git branch --format='%(refname:short)'` no longer lists the scoped local feature branches
- `git branch -r --format='%(refname:short)'` no longer lists the scoped remote feature branches
- `Operations/ACTION_LOG.md` records the cleanup actions with this plan reference

## Execution Status

- `R1` complete on 2026-04-08: created the cleanup plan triplet, prompt pair, and tracker activation on `development`.
- `R2` complete on 2026-04-08: froze the keep set at `development`, `staging`, and `main`, and the approved local/remote delete sets exactly as governed.
- `R3` complete on 2026-04-08: proved each delete-candidate branch had `0` unique commits beyond `development` before deletion (`38/0`, `44/0`, `31/0`, and `3/0` for the four local `codex/*` branches).
- `R4` complete on 2026-04-08: deleted the scoped local branches `codex/m365-direct-function-validation`, `codex/m365-direct-runtime-readiness-remediation`, `codex/m365-persona-action-certification-plan`, and `codex/m365-persona-action-full-support-remediation`.
- `R5` complete on 2026-04-08: deleted the scoped remote branches `origin/codex/m365-direct-function-validation`, `origin/codex/m365-direct-runtime-readiness-remediation`, `origin/codex/m365-persona-action-certification-plan`, `origin/codex/m365-persona-action-full-support-remediation`, `origin/codex/m365-token-acquisition-validation`, and `origin/feature/m365_personas`.
- `R6` complete on 2026-04-08: synchronized the plan and governance trackers so the repo now exposes only `development`, `staging`, and `main` locally and on origin.

## Rollback

- deleted local branches can be recreated from `development` history if a historical pointer is later needed
- deleted remote branches can be recreated from the merged commit history if an external pointer is later required
- cleanup must fail closed if any supposedly redundant branch is found to contain unique required work
