# Codex Prompt — M365 Persona-Action P5 Recertification Scope Correction

You are executing `plan:m365-persona-action-p5-recertification-scope-correction`.

## Mission

Freeze the live post-remediation workforce totals that now make the old certification artifact stale, publish notebook-backed governance evidence for the widened `P5` recertification surface, and hand control back to the parent `P5` phase without publishing the final recertified matrix yet.

## Required outcomes

1. Record the exact live post-`P4` workforce totals.
2. Create the governance notebook and generated verification payload for the `P5S` scope gap.
3. Widen the parent plan and trackers so `P5` may truthfully publish the final recertification next.
4. Validate, commit, and push the child package before returning control to the parent plan.

## Frozen truth to preserve

- stale published certification still says `184` unique aliases and `430` active pairs
- live post-`P4` workforce truth is `172` unique aliases and `445` active pairs
- repo-local OPA now allows `410` active pairs
- explicit unsupported perimeter is `35` active pairs across `32` unique aliases

## Constraints

- Do not publish the final `P5` certification artifact here.
- Do not reopen `P1` through `P4`.
- Stop on first red `validate_action` verdict.
- Keep all edits within the child-package allowlist.

## Validation

- parse/read back the new plan triplet, prompt pair, notebook, and verification payload
- `git diff --check`
- `pre-commit run --all-files`

## Completion

When complete, mark the child package ready for the parent `P5` phase and update:
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
