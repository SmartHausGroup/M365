# Codex Prompt: M365 Authoritative Persona Branch Topology Cleanup

Plan reference: `plan:m365-authoritative-persona-branch-topology-cleanup:R1`

## Objective

Collapse the local authoritative-persona branch mess into one canonical working branch by discarding transient replay residue, realigning `development` to `origin/development`, and deleting only the explicitly scoped redundant branches.

## Required outputs

- `plans/m365-authoritative-persona-branch-topology-cleanup/m365-authoritative-persona-branch-topology-cleanup.md`
- `plans/m365-authoritative-persona-branch-topology-cleanup/m365-authoritative-persona-branch-topology-cleanup.yaml`
- `plans/m365-authoritative-persona-branch-topology-cleanup/m365-authoritative-persona-branch-topology-cleanup.json`
- `docs/prompts/codex-m365-authoritative-persona-branch-topology-cleanup-prompt.txt`
- synchronized `Operations/EXECUTION_PLAN.md`
- synchronized `Operations/ACTION_LOG.md`
- synchronized `Operations/PROJECT_FILE_INDEX.md`

## Constraints

- keep `codex/m365-authoritative-persona-post-h5-parity-correction`
- keep `development`, `main`, and `staging`
- do not push `development`
- do not replay `M1`
- delete only the scoped redundant branches listed in the plan
- fail closed if any candidate deletion branch is found to contain unique required work

## Required validations

- `git status --short --branch` clean on the canonical branch
- `git rev-parse development` equals `git rev-parse origin/development`
- deleted local branches no longer appear in `git branch -vv`
- deleted remote predecessor branch no longer appears in `git branch -r`

## Notes

- This is repo-topology cleanup, not feature implementation.
- The cleanup must leave one obvious canonical branch for the next governed correction or merge-readiness step.
