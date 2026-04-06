# Plan: M365 Authoritative Persona Branch Topology Cleanup

**Plan ID:** `m365-authoritative-persona-branch-topology-cleanup`
**Parent Plan ID:** `m365-authoritative-persona-humanization-merge-replay-to-development`
**Status:** Complete (`R1` through `R5` complete on 2026-04-06)
**Date:** 2026-04-06
**Owner:** SmartHaus
**Execution plan reference:** `plan:m365-authoritative-persona-branch-topology-cleanup:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the repo in an auditable, policy-gated, reviewable state by collapsing redundant local merge-replay residue into one canonical branch and one clean `development` baseline.

## Objective

Clean up the local branch and worktree debt created by repeated blocked `M1` replay attempts without discarding the canonical authoritative-persona source branch or silently preserving redundant local merge state.

## Problem Statement

The current local topology contains:

- one canonical branch with the real authoritative-persona payload:
  - `codex/m365-authoritative-persona-post-h5-parity-correction`
- one local `development` branch pointing at a failed replay merge commit whose committed tree matches the canonical branch
- transient verification side effects left by replay validation
- blocked replay safety branches that no longer need to remain in the local branch list
- older merged predecessor branches that add branch-list noise but no unique canonical value

This state is operationally noisy and obscures which branch should actually be kept.

## Scope

### In scope

- create a formal cleanup initiative and prompt pair
- record the canonical keep-branch set
- discard the transient replay-validation side effects
- realign local `development` to `origin/development`
- delete the redundant local blocked replay branches
- delete the redundant local predecessor and merged feature branches already absorbed into the current canonical history
- delete the stale predecessor remote branch `origin/codex/m365-authoritative-persona-humanization-expansion-plan`
- synchronize `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, and `Operations/PROJECT_FILE_INDEX.md`

### Out of scope

- changing runtime, registry, commercialization, MA, or certification truth
- pushing `development`
- replaying `M1`
- deleting `main`, `staging`, or the canonical corrected source branch
- deleting unrelated remote historical branches outside the scoped predecessor branch

## Requirements

### R1 — Governed cleanup initiative

- Create the cleanup plan triplet and prompt pair.

### R2 — Canonical branch inventory

- Record the keep set, the delete-local set, and the scoped delete-remote set.

### R3 — Worktree and local-branch cleanup

- Discard transient validation side effects.
- Reset local `development` back to `origin/development`.
- Delete the scoped redundant local branches.

### R4 — Scoped remote cleanup

- Delete only the stale predecessor remote branch that is fully superseded by the canonical parity branch.

### R5 — Governance synchronization

- Update execution tracking so this cleanup is recorded and the repo has one clear canonical branch for the authoritative-persona follow-on work.

## Keep Set

- `codex/m365-authoritative-persona-post-h5-parity-correction`
- `development`
- `main`
- `staging`

## Delete Set — Local

- `codex/m1-fresh-replay-blocked-development-d194b94`
- `codex/m1-replay-blocked-development-a895678`
- `codex/m365-authoritative-persona-humanization-expansion-plan`
- `codex/m365-service-mode-runtime-remediation`
- `codex/m365-token-acquisition-validation`
- `feature/m365-universe-batch1-identity-groups`
- `feature/m365_personas`

## Delete Set — Remote

- `origin/codex/m365-authoritative-persona-humanization-expansion-plan`

## Initial Execution Order

1. `R1` Create the cleanup plan and prompt pair.
2. `R2` Record the canonical keep/delete branch inventory.
3. `R3` Discard transient replay-validation residue and realign local `development`.
4. `R4` Delete the scoped redundant local and remote branches.
5. `R5` Synchronize governance tracking and hand control back to the canonical branch.

## Success Criteria

- the transient replay-validation residue is gone
- local `development` equals `origin/development`
- the canonical branch remains clean and checked out
- the scoped redundant local branches are removed
- the stale predecessor remote branch is removed
- tracker files truthfully show the cleanup completion and the next blocker

## Validation

- `git status --short --branch` is clean on `codex/m365-authoritative-persona-post-h5-parity-correction`
- `git rev-parse development` equals `git rev-parse origin/development`
- `git branch -vv` no longer lists the scoped delete-local branches
- `git branch -r` no longer lists `origin/codex/m365-authoritative-persona-humanization-expansion-plan`
- `Operations/ACTION_LOG.md` records the cleanup actions with this plan reference

## Execution Status

- `R1` complete on 2026-04-06: created the cleanup plan triplet, prompt pair, and tracker entries.
- `R2` complete on 2026-04-06: closed the keep/delete inventory and preserved `codex/m365-authoritative-persona-post-h5-parity-correction` as the canonical branch.
- `R3` complete on 2026-04-06: discarded the transient replay-validation side effects, realigned local `development` to `origin/development`, and deleted the scoped redundant local branches.
- `R4` complete on 2026-04-06: deleted the stale predecessor remote branch `origin/codex/m365-authoritative-persona-humanization-expansion-plan`.
- `R5` complete on 2026-04-06: synchronized the plan and governance trackers so branch cleanup is closed and the next blocker is the stale H3 regression expectations surfaced during replay validation.

## Rollback

- the deleted local branches can be recovered from their recorded SHAs if needed
- the deleted remote predecessor branch can be recreated from the canonical branch history if a historical pointer is later required
- cleanup must fail closed if any supposedly redundant branch is found to contain unique required work
