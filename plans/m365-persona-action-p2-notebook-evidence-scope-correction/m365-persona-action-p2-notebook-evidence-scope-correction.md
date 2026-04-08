# Plan: M365 Persona-Action P2 Notebook Evidence Scope Correction

**Plan ID:** `m365-persona-action-p2-notebook-evidence-scope-correction`
**Parent Plan ID:** `m365-persona-action-full-support-remediation`
**Status:** 🟢 Complete
**Date:** 2026-04-07
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-p2-notebook-evidence-scope-correction:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the persona-action remediation truthful and fail-closed by refusing to start legacy-stub code repair until the bounded `P2` wave has explicit notebook-backed evidence accepted by governance.
**Canonical predecessor:** `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
**Governance evidence:** `notebooks/m365/INV-M365-CQ-persona-action-p2-notebook-evidence-scope-correction-v1.ipynb`, `configs/generated/persona_action_p2_notebook_evidence_scope_correction_v1_verification.json`
**Historical lineage:** successor blocker package after the first bounded `P2` code write was denied with `map-2-code-notebook-required`.

**Draft vs Active semantics:** This child plan starts in **Draft** and becomes **Active** once the parent initiative is paused on `P2`, the approval packet receives explicit `go`, and no sibling remediation phase is concurrently active. It becomes **Complete** only after the notebook-backed blocker evidence is published, the blocked `P2` code-write validation is reopened under child-plan authority, trackers are synchronized, and the parent initiative truthfully returns control to `P2`.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook extraction, file edits, commits, pushes, and tracker synchronization. Stop on first red. Do not auto-advance to `P3`.

**Notebook-first discipline:** `P2S` is a notebook-backed governance-unblock phase. The blocked write set, the exact MCP denial, and the required future `L90` evidence chain must be frozen in notebooks first. No bounded `P2` code repair is allowed before that notebook-backed evidence exists and the blocked validation is reopened.

## Objective

Create the bounded child phase that publishes explicit notebook-backed evidence for the first bounded `P2` legacy-stub remediation blocker so the parent initiative can truthfully reopen the code-write validation and continue legacy-stub repair under governed notebook-first conditions.

## Current State

- Parent initiative:
  - `plan:m365-persona-action-full-support-remediation`
- Completed parent phases:
  - `P0` read-only backlog lock
  - `P1` dead-route remediation
- Observed bounded `P2` write target:
  - `src/ops_adapter/actions.py`
  - `tests/test_ops_adapter.py`
- Targeted first bounded `P2` aliases:
  - `task.create`
  - `follow-up.schedule`
  - `reminder.send`
- Blocking governance verdict:
  - `validate_action(file_edit)` for the first bounded `P2` code repair returned `allowed:false`
  - violation id: `map-2-code-notebook-required`
- Existing supporting notebook evidence:
  - `notebooks/m365/INV-M365-CK-persona-action-mapping-audit-v1.ipynb`
  - `notebooks/m365/INV-M365-CN-persona-action-route-certification-v1.ipynb`
  - `notebooks/m365/INV-M365-CP-persona-action-dead-route-remediation-v1.ipynb`
- Gap:
  - the parent initiative lacks a phase-specific notebook-backed blocker package that defines the admissible `P2` evidence chain for the first bounded legacy-stub repair wave

## Decision Rule

`LegacyStubBacklogFrozen = LegacyStubbedUnique48 AND LegacyStubbedPairs49`

`FirstBoundedP2WriteBlocked = validate_action(file_edit, first bounded P2 code repair) returns map-2-code-notebook-required`

`PhaseSpecificEvidenceSurfaceDefined = P2S owns governance notebook evidence, generated verification output, and the required future L90 legacy-stub evidence chain`

`BlockedWriteSetFrozen = actions.py AND tests/test_ops_adapter.py`

`P2S_GO = LegacyStubBacklogFrozen AND FirstBoundedP2WriteBlocked AND PhaseSpecificEvidenceSurfaceDefined AND BlockedWriteSetFrozen`

If `P2S_GO` is false, `P2S` must emit `NO-GO`, stop fail-closed, and keep the parent initiative at `P2`.

## Scope

### In scope

- restate the bounded `P2` governance blocker explicitly from certification and MCP truth
- create a phase-specific notebook-backed governance evidence chain for the blocked `P2` code write
- publish generated verification output for that governance evidence
- expand the parent remediation package to acknowledge the `P2S` blocker-fix child phase
- synchronize trackers so the parent initiative truthfully pauses at `P2S`
- reopen the blocked `P2` code-write validation under child-plan authority
- hand control back to the parent initiative with `P2` as the next act only after `P2S` is green, committed, and pushed

### Out of scope

- actual `P2` legacy-stub code remediation
- `P3` permission/alias remediation
- `P4` policy-fence remediation
- runtime code, registry, or test extraction beyond the blocker evidence package
- any UCP-side changes

### File allowlist

- `plans/m365-persona-action-p2-notebook-evidence-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-p2-notebook-evidence-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-p2-notebook-evidence-scope-correction-prompt.txt`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `notebooks/m365/INV-M365-CQ-persona-action-p2-notebook-evidence-scope-correction-v1.ipynb`
- `configs/generated/persona_action_p2_notebook_evidence_scope_correction_v1_verification.json`
- `docs/ma/lemmas/L90_m365_persona_action_legacy_stub_remediation_v1.md`
- `invariants/lemmas/L90_m365_persona_action_legacy_stub_remediation_v1.yaml`
- `notebooks/m365/INV-M365-CR-persona-action-legacy-stub-remediation-v1.ipynb`
- `notebooks/lemma_proofs/L90_m365_persona_action_legacy_stub_remediation_v1.ipynb`
- `artifacts/scorecards/scorecard_l90.json`
- `configs/generated/persona_action_legacy_stub_remediation_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/**`
- `src/**`
- `tests/**`
- `../UCP/**`
- any path not listed in the allowlist

## Requirements

- **R0** — Create the bounded `P2S` blocker package.
- **R1** — Make the bounded `P2` governance blocker explicit from certification and MCP truth.
- **R2** — Produce notebook-backed governance evidence for the blocked `P2` write.
- **R3** — Expand the admissible evidence surface to include the future `L90` legacy-stub notebook chain.
- **R4** — Reopen the blocked `P2` code-write validation under child-plan authority.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Commit and push `P2S` before resuming parent `P2`.

## Child Acts

### P2SA — Blocker restatement

- freeze the certified legacy-stub backlog and the exact MCP denial that blocked the first bounded `P2` write

### P2SB — Governance notebook evidence

- create the phase-specific governance notebook evidence and generated verification output
- define the required future `L90` legacy-stub notebook chain explicitly

### P2SC — Validation reopen and handback

- reopen the blocked `P2` code-write validation under child-plan authority
- synchronize trackers
- validate, commit, push, and return the parent initiative to `P2`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-persona-action-p2-notebook-evidence-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-persona-action-p2-notebook-evidence-scope-correction-prompt.txt`

## Validation Strategy

- require the governance notebook evidence to preserve the observed blocker truth:
  - `49` legacy-stubbed active pairs
  - `48` legacy-stubbed unique aliases
  - blocked write set frozen exactly
  - MCP violation `map-2-code-notebook-required`
- require generated verification output for the governance-alignment notebook
- require the parent remediation plan and trackers to point to `P2S` while the blocker is unresolved
- require a successful reopen of the blocked `P2` file-edit validation under child-plan authority before handback
- run `git diff --check`

## Agent Constraints

- Do not begin `P2` code edits inside `P2S` until the blocked write validation is reopened.
- Do not widen into `P3` or `P4` during `P2S`.
- Do not edit runtime code, registries, or tests in `P2S`.
- Commit and push `P2S` before any parent `P2` code work begins.

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] this child plan `status -> complete`

## Execution Outcome

- **Decision:** `GO`
- **Approved by:** `operator explicit go`
- **Completion timestamp:** `2026-04-07 09:07:00 EDT`
