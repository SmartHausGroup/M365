# Plan: M365 Persona-Action P2 Fourth-Wave Notebook Evidence Scope Correction

**Plan ID:** `m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction`
**Parent Plan ID:** `m365-persona-action-full-support-remediation`
**Status:** ✅ Complete
**Date:** 2026-04-07
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the persona-action remediation truthful and fail-closed by refusing to start the fourth bounded `P2` legacy-stub wave until the phase has explicit notebook-backed evidence accepted by governance.
**Canonical predecessor:** `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
**Governance evidence:** `notebooks/m365/INV-M365-CW-persona-action-p2-fourth-wave-notebook-evidence-scope-correction-v1.ipynb`, `configs/generated/persona_action_p2_fourth_wave_notebook_evidence_scope_correction_v1_verification.json`
**Historical lineage:** successor blocker package after the next bounded `P2` code-write slice was prepared for the project-coordination legacy-stub surface.

**Draft vs Active semantics:** This child plan starts in **Draft** and becomes **Active** once the parent initiative pauses on the fourth bounded `P2` legacy-stub wave, the approval packet receives explicit `go`, and no sibling remediation phase is concurrently active. It becomes **Complete** only after the notebook-backed blocker evidence is published, the blocked fourth-wave `P2` code-write validation is reopened under child-plan authority, trackers are synchronized, and the parent initiative truthfully returns control to `P2`.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook extraction, file edits, commits, pushes, and tracker synchronization. Stop on first red. Do not auto-advance to `P3`.

**Notebook-first discipline:** `P2V` is a notebook-backed governance-unblock phase. The blocked write set, the bounded fourth-wave alias set, and the required future `L93` evidence chain must be frozen in notebooks first. No bounded fourth-wave `P2` code repair is allowed before that notebook-backed evidence exists and the blocked validation is reopened.

## Objective

Create the bounded child phase that publishes explicit notebook-backed evidence for the fourth bounded `P2` legacy-stub remediation slice so the parent initiative can truthfully reopen the next code-write validation and continue legacy-stub repair under governed notebook-first conditions.

## Current State

- Parent initiative:
  - `plan:m365-persona-action-full-support-remediation`
- Completed parent phases:
  - `P0`
  - `P1`
  - `P2S`
  - `P2T`
  - `P2U`
- Completed bounded `P2` waves:
  - `task.create -> planner_create_task`
  - `follow-up.schedule -> calendar_create`
  - `reminder.send -> mail_send`
  - `followup.create -> calendar_create`
  - `client.follow-up -> calendar_create`
  - `satisfaction.survey -> mail_send`
  - `interview.schedule -> calendar_create`
  - `archive-project -> teams_archive`
  - `system.health-check -> health_overview`
  - `alerts.respond -> security_alert_update`
- Observed bounded fourth-wave `P2` write target:
  - `src/ops_adapter/actions.py`
  - `tests/test_ops_adapter.py`
- Targeted bounded fourth-wave `P2` aliases:
  - `task.assign`
  - `deadline.track`
  - `status.update`
  - `report.generate`
- Derived post-wave-3 legacy-stub backlog:
  - `36` active pairs
  - `38` unique aliases
- Existing supporting notebook evidence:
  - `notebooks/m365/INV-M365-CR-persona-action-legacy-stub-remediation-v1.ipynb`
  - `notebooks/m365/INV-M365-CT-persona-action-legacy-stub-remediation-v2.ipynb`
  - `notebooks/m365/INV-M365-CV-persona-action-legacy-stub-remediation-v3.ipynb`
- Existing supporting scorecards:
  - `artifacts/scorecards/scorecard_l90.json`
  - `artifacts/scorecards/scorecard_l91.json`
  - `artifacts/scorecards/scorecard_l92.json`
- Gap:
  - the parent initiative still lacks a phase-specific notebook-backed blocker package that defines the admissible `P2` evidence chain for the bounded project-coordination legacy-stub repair wave

## Decision Rule

`LegacyStubBacklogFrozen = LegacyStubbedUnique38 AND LegacyStubbedPairs36`

`FourthBoundedP2WritePrepared = project_coordination_wave_ready`

`PhaseSpecificEvidenceSurfaceDefined = P2V owns governance notebook evidence, generated verification output, and the required future L93 legacy-stub evidence chain`

`BlockedWriteSetFrozen = actions.py AND tests/test_ops_adapter.py`

`P2V_GO = LegacyStubBacklogFrozen AND FourthBoundedP2WritePrepared AND PhaseSpecificEvidenceSurfaceDefined AND BlockedWriteSetFrozen`

If `P2V_GO` is false, `P2V` must emit `NO-GO`, stop fail-closed, and keep the parent initiative at `P2`.

## Scope

### In scope

- freeze the bounded fourth-wave `P2` project-coordination remediation slice explicitly from remediation truth
- create a phase-specific notebook-backed governance evidence chain for the bounded fourth-wave `P2` code write
- publish generated verification output for that governance evidence
- expand the parent remediation package to acknowledge the `P2V` blocker-fix child phase
- synchronize trackers so the parent initiative truthfully pauses at `P2V`
- reopen the bounded fourth-wave `P2` code-write validation under child-plan authority
- hand control back to the parent initiative with `P2` as the next act only after `P2V` is green, committed, and pushed

### Out of scope

- actual fourth-wave `P2` legacy-stub code remediation
- `P3` permission/alias remediation
- `P4` policy-fence remediation
- runtime code, registry, or test extraction beyond the blocker evidence package
- any UCP-side changes

### File allowlist

- `plans/m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction-prompt.txt`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `notebooks/m365/INV-M365-CW-persona-action-p2-fourth-wave-notebook-evidence-scope-correction-v1.ipynb`
- `configs/generated/persona_action_p2_fourth_wave_notebook_evidence_scope_correction_v1_verification.json`
- `docs/ma/lemmas/L93_m365_persona_action_legacy_stub_remediation_v4.md`
- `invariants/lemmas/L93_m365_persona_action_legacy_stub_remediation_v4.yaml`
- `notebooks/m365/INV-M365-CX-persona-action-legacy-stub-remediation-v4.ipynb`
- `notebooks/lemma_proofs/L93_m365_persona_action_legacy_stub_remediation_v4.ipynb`
- `artifacts/scorecards/scorecard_l93.json`
- `configs/generated/persona_action_legacy_stub_remediation_v4_verification.json`
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

- **R0** — Create the bounded `P2V` blocker package.
- **R1** — Freeze the bounded fourth-wave `P2` project-coordination slice explicitly.
- **R2** — Produce notebook-backed governance evidence for the bounded fourth-wave `P2` write.
- **R3** — Expand the admissible future evidence surface to include `L93`.
- **R4** — Reopen the bounded fourth-wave `P2` code-write validation under child-plan authority.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Commit and push before resuming `P2`.

## Child Acts

### P2VA — Slice freeze

- freeze the post-wave-3 legacy-stub backlog and the exact bounded project-coordination alias set

### P2VB — Governance notebook evidence

- create the phase-specific governance notebook evidence and generated verification output
- define the required future `L93` legacy-stub notebook chain explicitly

### P2VC — Validation reopen and handback

- reopen the bounded fourth-wave `P2` code-write validation under child-plan authority
- synchronize trackers
- validate, commit, push, and return the parent initiative to `P2`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction-prompt.txt`

## Validation Strategy

- require the governance notebook evidence to preserve the observed blocker truth:
  - `36` legacy-stubbed active pairs
  - `38` legacy-stubbed unique aliases
  - blocked write set frozen exactly
  - bounded alias set frozen exactly
- require generated verification output for the governance-alignment notebook
- require the parent remediation plan and trackers to point to `P2V` while the blocker is unresolved
- require a successful reopen of the bounded fourth-wave `P2` file-edit validation under child-plan authority before handback
- run `git diff --check`

## Agent Constraints

- Do not begin fourth-wave `P2` code edits inside `P2V` until the bounded write validation is reopened.
- Do not widen into `P3` or `P4` during `P2V`.
- Do not edit runtime code, registries, or tests in `P2V`.
- Commit and push `P2V` before any parent `P2` code work begins.

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] this child plan `status -> complete`

## Result

- `P2V` is complete.
- Governance notebook `INV-M365-CW` and generated verification are published.
- The future `L93` evidence chain is published and parse-clean.
- MCP `validate_action(file_edit)` is green under child-plan authority for:
  - `src/ops_adapter/actions.py`
  - `tests/test_ops_adapter.py`
- The bounded fourth-wave `P2` repair set is reopened for:
  - `task.assign`
  - `deadline.track`
  - `status.update`
  - `report.generate`
- Control returns to parent `P2`.
