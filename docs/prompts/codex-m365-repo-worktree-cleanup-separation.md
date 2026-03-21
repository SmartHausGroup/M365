# Codex Prompt: M365 Repo Worktree Cleanup and Separation

Plan reference: `plan:m365-repo-worktree-cleanup-separation:R1`

## Objective

Reduce the repo's mixed dirty worktree into a safe, reviewable state by removing secret-bearing local artifacts, reverting formatter-only fallout, and separating the remaining substantive payload into explicit keep, split, and delete buckets.

## Required outputs

- `plans/m365-repo-worktree-cleanup-separation/m365-repo-worktree-cleanup-separation.md`
- `plans/m365-repo-worktree-cleanup-separation/m365-repo-worktree-cleanup-separation.yaml`
- `plans/m365-repo-worktree-cleanup-separation/m365-repo-worktree-cleanup-separation.json`
- `docs/prompts/codex-m365-repo-worktree-cleanup-separation-prompt.txt`
- synchronized `Operations/EXECUTION_PLAN.md`
- synchronized `Operations/ACTION_LOG.md`

## Constraints

- Do not mass-delete substantive feature work.
- Remove or sanitize plaintext secret-bearing docs immediately.
- Revert only formatter-only tracked diffs during the cleanup revert step.
- Keep commercialization and MA scorecard artifacts intact.
- Fail closed if a file cannot be confidently classified.

## Required validations

- secret-bearing workflow docs no longer exist in plaintext form
- tracked formatter-only noise is reverted
- reduced `git status --short` is captured and reviewed
- `Operations/ACTION_LOG.md` records the cleanup actions

## Notes

- This is a repo hygiene and separation task, not a runtime feature task.
- The main output is a smaller, safer worktree and a clear next split.
