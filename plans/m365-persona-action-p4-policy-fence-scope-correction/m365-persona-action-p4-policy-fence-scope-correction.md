# Plan: M365 Persona-Action P4 Policy-Fence Scope Correction

**Plan ID:** `m365-persona-action-p4-policy-fence-scope-correction`
**Parent Plan ID:** `m365-persona-action-full-support-remediation`
**Status:** 🟢 Complete
**Date:** 2026-04-07
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-p4-policy-fence-scope-correction:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep persona policy truth fail-closed by refusing to widen the policy surface until the repo-local OPA drift against the active persona registry is frozen, notebook-backed, and bounded.
**Canonical predecessor:** `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
**Governance evidence:** `notebooks/m365/INV-M365-DD-persona-action-p4-policy-fence-scope-correction-v1.ipynb`, `configs/generated/persona_action_p4_policy_fence_scope_correction_v1_verification.json`
**Historical lineage:** successor blocker package after `P3` closed the dead-route, legacy-stub, and permission/alias backlog far enough to expose the next real repo-local blocker: OPA policy drift is now denying the overwhelming majority of the active persona/action graph.
**Completion status (2026-04-07 13:14 EDT):** `GO` — widened the parent `P4` repair surface to the notebook-backed policy-governance evidence boundary, then handed the parent initiative back to `P4` for the actual repo-local policy rewrite.

**Draft vs Active semantics:** This child plan starts in **Draft**. It becomes **Active** only when the parent initiative remains on `P4`, the approval packet receives explicit `go`, and no sibling child phase is concurrently active. It becomes **Complete** only after the policy-drift scope is notebook-backed, the parent plan and trackers are synchronized, the child package is committed and pushed, and control is truthfully returned to the parent `P4` remediation wave.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook extraction, file edits, tests, commit, and push. Stop on first red. Do not auto-advance to `P5`.

**Notebook-first discipline:** `P4S` is a notebook-backed governance-unblock phase. The repo-local OPA drift, affected policy surfaces, and admissible future repair set must be frozen in notebooks first. No widened `P4` policy, approval-risk, or test edits are allowed before the scope evidence is green.

## Objective

Create the bounded child phase that widens `P4` into the required policy-governance evidence surface so the parent initiative can truthfully repair repo-local OPA drift instead of leaving the active persona graph fenced by stale policy state.

## Current State

- Parent initiative:
  - `plan:m365-persona-action-full-support-remediation`
- Completed parent phases:
  - `P0`
  - `P1`
  - `P2`
  - `P3`
- Live repo-local policy drift now observed against the active registry:
  - `54` active personas
  - `53` active personas with at least one OPA `action_not_allowed` denial
  - `419` active persona/action pairs denied by repo-local OPA
  - `152` unique persona-facing aliases denied by repo-local OPA
- Current repo-local policy authority only covers a stale micro-surface:
  - `policies/ops.rego`
  - `policies/agents/m365_administrator.rego`
  - `policies/agents/hr_generalist.rego`
  - `policies/agents/outreach_coordinator.rego`
  - `policies/agents/website_manager.rego`
- Drift examples from current live repo truth:
  - `website-manager` now owns SharePoint/files actions in the authoritative registry, but `policies/ops.rego` still only allows retired website-deployment aliases
  - `m365-administrator` now owns broad bounded SharePoint/files/directory/app reads, but repo-local OPA still denies most of them
  - most active personas have no matching repo-local OPA allow surface at all
- Governance blocker if `P4` begins without a child package:
  - the parent allowlist includes policy files and tests, but not the notebook-backed scope evidence required to justify a large policy-surface rewrite

## Decision Rule

`ActivePersonaSurface = 54`

`DeniedPersonaSurface = 53`

`ActionNotAllowedPairTotal = 419`

`ActionNotAllowedUniqueAliasTotal = 152`

`PolicyAuthorityDriftEstablished = repo-local OPA allows only a stale subset of personas and aliases while the authoritative registry now exposes a much broader active M365 surface`

`NotebookBackedScopeDefined = P4S owns a phase-specific governance notebook and generated verification output proving the widened policy-repair set`

`P4S_GO = (DeniedPersonaSurface > 0) AND (ActionNotAllowedPairTotal > 0) AND PolicyAuthorityDriftEstablished AND NotebookBackedScopeDefined`

If `P4S_GO` is false, `P4S` must emit `NO-GO`, stop fail-closed, and keep the parent initiative at `P4`.

## Scope

### In scope

- restate the exact repo-local OPA drift from the live persona registry
- publish notebook-backed governance evidence and generated verification output for the widened `P4` boundary
- admit the required policy, approval-risk, and focused validation surfaces into the bounded `P4` repair set
- synchronize the parent plan and governance trackers truthfully
- hand control back to the parent initiative only after the child package is committed and pushed

### Out of scope

- executing the actual `P4` policy rewrites
- `P5` re-certification closeout
- UCP runtime changes
- tenant-side permission or environment enablement outside the repo

### File allowlist

- `plans/m365-persona-action-p4-policy-fence-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-p4-policy-fence-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-p4-policy-fence-scope-correction-prompt.txt`
- `notebooks/m365/INV-M365-DD-persona-action-p4-policy-fence-scope-correction-v1.ipynb`
- `configs/generated/persona_action_p4_policy_fence_scope_correction_v1_verification.json`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `policies/ops.rego`
- `policies/agents/*.rego`
- `registry/agents.yaml`
- `registry/persona_registry_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `src/smarthaus_common/approval_risk.py`
- `tests/test_policies.py`
- `tests/test_ops_adapter.py`
- `tests/test_approval_risk_v2.py`
- `docs/commercialization/m365-persona-action-certification.md`
- `artifacts/diagnostics/m365_persona_action_certification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `../UCP/**`
- any path not listed in the allowlist

## Requirements

- **R1** — Make the repo-local `P4` policy-drift scope explicit from live registry truth.
- **R2** — Produce notebook-backed governance evidence for the widened `P4` repair set.
- **R3** — Admit the required policy, approval-risk, and focused validation surfaces into the bounded `P4` repair set.
- **R4** — Reopen the future bounded `P4` file-edit validation under child-plan authority for policy remediation.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Commit and push `P4S` before resuming the parent initiative.

## Child Acts

### P4SA — Policy-drift freeze

- freeze the live OPA `action_not_allowed` totals, affected personas, and affected policy surfaces

### P4SB — Governance notebook evidence

- publish the phase-specific notebook-backed scope evidence and generated verification output

### P4SC — Parent handback

- widen the parent `P4` repair surface truthfully
- synchronize trackers
- validate, commit, push, and return the initiative to `P4`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-persona-action-p4-policy-fence-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-persona-action-p4-policy-fence-scope-correction-prompt.txt`

## Validation Strategy

- require the governance notebook and generated verification to preserve:
  - `54` active personas
  - `53` denied personas
  - `419` repo-local `action_not_allowed` persona/action pairs
  - `152` denied unique aliases
  - the exact repo-local policy files that currently define the stale allow surface
- require the parent plan allowlist to widen only to the policy, approval-risk, and focused validation surfaces required for `P4`
- require tracker truth to point to `P4S` while the child package is active
- run `git diff --check`

## Agent Constraints

- Do not execute the actual `P4` policy rewrite inside `P4S`.
- Do not widen beyond repo-local policy, approval-risk, and focused validation surfaces.
- Do not widen into `P5`.
- Commit and push `P4S` before any `P4` file edits begin.

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] this child plan `status -> complete`

## Execution Outcome

- **Decision:** `GO`
- **Approved by:** `operator explicit go`
- **Completion timestamp:** `2026-04-07 13:14:26 EDT`
