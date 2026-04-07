# Codex Prompt — M365 Persona-Action P4 Policy-Fence Scope Correction

You are executing `plan:m365-persona-action-p4-policy-fence-scope-correction`.

## Mission

Freeze the live repo-local OPA drift that now blocks truthful `P4` policy remediation, publish notebook-backed governance evidence for the widened repair surface, and hand control back to the parent `P4` phase without performing the actual policy rewrite.

## Required outcomes

1. Record the exact current repo-local OPA drift totals against the active persona registry.
2. Create the governance notebook and generated verification payload for the `P4S` scope gap.
3. Widen the parent plan and trackers so `P4` may truthfully edit the policy surface next.
4. Validate, commit, and push the child package before returning control to the parent plan.

## Frozen truth to preserve

- `54` active personas
- `53` denied personas
- `419` repo-local `action_not_allowed` persona/action pairs
- `152` denied unique aliases
- stale policy authority currently defined only in:
  - `policies/ops.rego`
  - `policies/agents/m365_administrator.rego`
  - `policies/agents/hr_generalist.rego`
  - `policies/agents/outreach_coordinator.rego`
  - `policies/agents/website_manager.rego`

## Constraints

- Do not execute the actual `P4` policy rewrite here.
- Do not widen into `P5`.
- Stop on first red `validate_action` verdict.
- Keep all edits within the child-package allowlist.

## Validation

- parse/read back the new plan triplet, prompt pair, notebook, and verification payload
- `git diff --check`
- `pre-commit run --all-files`

## Completion

When complete, mark the child package ready for the parent `P4` phase and update:
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`

