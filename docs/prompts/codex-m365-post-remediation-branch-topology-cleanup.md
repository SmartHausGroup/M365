# Codex Prompt: M365 Post-Remediation Branch Topology Cleanup

Plan reference: `plan:m365-post-remediation-branch-topology-cleanup:R1`

## Objective

Collapse the post-remediation feature-branch debt into the long-lived `development`, `staging`, and `main` branches only by deleting feature branches that are already fully merged into `development`.

## Required outputs

- `plans/m365-post-remediation-branch-topology-cleanup/m365-post-remediation-branch-topology-cleanup.md`
- `plans/m365-post-remediation-branch-topology-cleanup/m365-post-remediation-branch-topology-cleanup.yaml`
- `plans/m365-post-remediation-branch-topology-cleanup/m365-post-remediation-branch-topology-cleanup.json`
- `docs/prompts/codex-m365-post-remediation-branch-topology-cleanup-prompt.txt`
- synchronized `Operations/EXECUTION_PLAN.md`
- synchronized `Operations/ACTION_LOG.md`
- synchronized `Operations/PROJECT_FILE_INDEX.md`

## Constraints

- keep only `development`, `staging`, and `main`
- delete only the explicitly scoped local and remote feature branches
- fail closed if any candidate deletion branch contains unique commits beyond `development`
- do not change runtime or product files

## Required validations

- `git rev-list --left-right --count development...<branch>` proves zero unique commits on every delete candidate
- deleted local branches no longer appear in `git branch --format='%(refname:short)'`
- deleted remote branches no longer appear in `git branch -r --format='%(refname:short)'`
- `git status --short --branch` is clean on `development`

## Notes

- This is repo-topology cleanup, not feature implementation.
- The cleanup must leave one obvious active branch set: `development`, `staging`, and `main`.
