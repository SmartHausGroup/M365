# Plan: M365 Persona-Action P5 Recertification Scope Correction

**Plan ID:** `m365-persona-action-p5-recertification-scope-correction`
**Parent Plan ID:** `m365-persona-action-full-support-remediation`
**Status:** 🟡 Draft
**Date:** 2026-04-08
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-p5-recertification-scope-correction:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the workforce support matrix truthful and fail-closed by refusing to publish the old `G5` certification totals after `P1` through `P4` materially changed the active persona/action graph.
**Canonical predecessor:** `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
**Governance evidence:** `notebooks/m365/INV-M365-DE-persona-action-p5-recertification-scope-correction-v1.ipynb`, `configs/generated/persona_action_p5_recertification_scope_correction_v1_verification.json`
**Historical lineage:** successor blocker package after `P4` collapsed repo-local OPA drift, leaving the parent initiative ready for final recertification but without an admitted notebook-backed evidence surface for the new live workforce totals.

**Draft vs Active semantics:** This child plan starts in **Draft**. It becomes **Active** only when the parent initiative remains on `P5`, the approval packet receives explicit `go`, and no sibling child phase is concurrently active. It becomes **Complete** only after the new live workforce universe is notebook-backed, the parent plan/tracker handoff is synchronized, the child package is committed and pushed, and control is truthfully returned to parent `P5`.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook extraction, file edits, tests, commit, and push. Stop on first red. Do not publish the final `P5` certification artifact from this child phase.

**Notebook-first discipline:** `P5S` is a notebook-backed governance-unblock phase. The new live workforce totals, repaired support perimeter, and exact recertification evidence set must be frozen in notebooks first. No final `P5` commercialization or diagnostic recertification write is allowed before this scope evidence is green.

## Objective

Create the bounded child phase that widens `P5` into the notebook-backed recertification evidence surface required to republish the workforce matrix after the remediation program changed the live persona/action universe.

## Current State

- Parent initiative:
  - `plan:m365-persona-action-full-support-remediation`
- Completed parent phases:
  - `P0`
  - `P1`
  - `P2`
  - `P3`
  - `P4`
- Stale predecessor certification still published:
  - `184` unique aliases
  - `430` active persona/action pairs
- Live post-`P4` workforce truth now observed read-only:
  - `172` unique active aliases
  - `445` active persona/action pairs
  - `410` active pairs admitted by repo-local OPA
  - `35` active pairs explicitly denied as unsupported
  - `32` unsupported unique aliases
- Governance blocker if `P5` begins without a child package:
  - the parent allowlist includes the old certification doc/artifact and trackers, but not the notebook, lemma, invariant, scorecard, or generated verification surfaces required to republish final recertification truth under MA/governance rules

## Decision Rule

`StaleCertificationExists = (published_unique_aliases = 184) AND (published_active_pairs = 430)`

`LiveUniverseShifted = (live_unique_aliases = 172) AND (live_active_pairs = 445)`

`UnsupportedPerimeterFrozen = (unsupported_unique_aliases = 32) AND (unsupported_active_pairs = 35)`

`NotebookBackedScopeDefined = P5S owns a phase-specific governance notebook and generated verification output proving the widened recertification evidence set`

`P5S_GO = StaleCertificationExists AND LiveUniverseShifted AND UnsupportedPerimeterFrozen AND NotebookBackedScopeDefined`

If `P5S_GO` is false, `P5S` must emit `NO-GO`, stop fail-closed, and keep the parent initiative at `P5`.

## Scope

### In scope

- restate the exact live post-`P4` workforce totals that make the current certification artifact stale
- publish notebook-backed governance evidence and generated verification output for the widened `P5` recertification boundary
- admit the required lemma, invariant, notebook, scorecard, generated verification, commercialization, and diagnostics surfaces into the bounded `P5` repair set
- synchronize the parent plan and governance trackers truthfully
- hand control back to the parent initiative only after the child package is committed and pushed

### Out of scope

- publishing the final recertified `P5` workforce matrix itself
- new runtime remediations beyond the already-complete `P1` through `P4` program
- UCP runtime changes
- tenant-side permission or environment changes

### File allowlist

- `plans/m365-persona-action-p5-recertification-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-p5-recertification-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-p5-recertification-scope-correction-prompt.txt`
- `notebooks/m365/INV-M365-DE-persona-action-p5-recertification-scope-correction-v1.ipynb`
- `configs/generated/persona_action_p5_recertification_scope_correction_v1_verification.json`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `docs/commercialization/m365-persona-action-certification.md`
- `artifacts/diagnostics/m365_persona_action_certification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `../UCP/**`
- any path not listed in the allowlist

## Requirements

- **R1** — Make the post-`P4` live-universe shift explicit from current runtime truth.
- **R2** — Produce notebook-backed governance evidence for the widened `P5` recertification set.
- **R3** — Admit the required `P5` lemma, invariant, notebook, scorecard, generated verification, doc, and diagnostic artifact surfaces into the bounded parent closeout.
- **R4** — Reopen the future bounded `P5` final-closeout write under child-plan authority.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Commit and push `P5S` before resuming the parent initiative.

## Child Acts

### P5SA — Universe-shift freeze

- freeze the live post-`P4` pair and alias totals plus the explicit unsupported perimeter

### P5SB — Governance notebook evidence

- publish the phase-specific notebook-backed scope evidence and generated verification output

### P5SC — Parent handback

- widen the parent `P5` recertification evidence surface truthfully
- synchronize trackers
- validate, commit, push, and return the initiative to `P5`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-persona-action-p5-recertification-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-persona-action-p5-recertification-scope-correction-prompt.txt`

## Validation Strategy

- require the governance notebook and generated verification to preserve:
  - `172` live unique active aliases
  - `445` live active persona/action pairs
  - `410` repo-local OPA-allowed active pairs
  - `35` explicit unsupported active pairs
  - `32` explicit unsupported unique aliases
- require the parent plan allowlist to widen only to the notebook-backed recertification evidence surfaces required for `P5`
- require tracker truth to point to `P5S` while the child package is active
- run `git diff --check`

## Agent Constraints

- Do not publish the final `P5` recertification artifact inside `P5S`.
- Do not widen beyond the notebook-backed recertification evidence surfaces.
- Do not reopen `P1` through `P4`.
- Commit and push `P5S` before any `P5` final-closeout edits begin.

## Governance Closure

- [ ] `Operations/ACTION_LOG.md`
- [ ] `Operations/EXECUTION_PLAN.md`
- [ ] `Operations/PROJECT_FILE_INDEX.md`
- [ ] this child plan `status -> complete`
