# Plan: M365 Persona-Action G1 Notebook Evidence Scope Correction

**Plan ID:** `m365-persona-action-g1-notebook-evidence-scope-correction`
**Parent Plan ID:** `m365-persona-action-certification`
**Status:** 🟢 Complete
**Date:** 2026-04-07
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-g1-notebook-evidence-scope-correction:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep workforce certification truthful and fail-closed by refusing to advance from observed runtime reachability into published governance truth until `G1` has phase-specific notebook-backed evidence.
**Canonical predecessor:** `plans/m365-persona-action-certification/m365-persona-action-certification.md`
**Governance evidence:** `notebooks/m365/INV-M365-CI-persona-action-g1-notebook-evidence-governance-alignment-v1.ipynb`, `configs/generated/persona_action_g1_notebook_evidence_governance_alignment_v1_verification.json`
**Historical lineage:** successor blocker package after `G1` runtime reachability was proven read-only but tracker synchronization was denied with `map-5-governance-notebook-evidence`.

**Draft vs Active semantics:** This child plan starts in **Draft**. It becomes **Active** only when the parent initiative remains on `G1`, the approval packet is presented and receives explicit `go`, and no sibling phase under the parent initiative is concurrently active. It becomes **Complete** only after `G1` notebook-backed evidence is published, trackers are synchronized, the child package is committed and pushed, and the parent initiative truthfully returns control to `G1`.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook extraction, file edits, commits, pushes, and tracker synchronization. Stop on first red. Do not auto-advance to `G2`.

**Notebook-first discipline:** `G1S` is a notebook-backed governance-unblock phase. The reachability claim, the planned-persona action fence claim, and the governance-closeout admissibility claim must be frozen in notebooks first. No `G1` closeout docs or tracker updates are allowed before the notebook-backed evidence artifacts are green.

## Objective

Create the bounded child phase that produces explicit notebook-backed `G1` persona-reachability evidence so the parent persona-action certification initiative can truthfully publish `G1`, synchronize trackers, and continue to `G2`.

## Current State

- Parent initiative:
  - `plan:m365-persona-action-certification`
- Completed parent phase:
  - `G0`
- Observed but unpublished `G1` runtime truth:
  - `59/59` canonical persona-id resolutions through `/personas/resolve`
  - `59/59` display-name resolutions through `/personas/resolve`
  - `59/59` persona state endpoint reachability through `/personas/{target}/state`
  - `5/5` planned personas fence from action execution with `persona_inactive:<persona_id>` once the bounded header-fallback probe is enabled
- Blocking governance verdict:
  - `validate_action(governance_edit)` for the `G1` tracker closeout returned `allowed:false`
  - violation id: `map-5-governance-notebook-evidence`
- Existing green notebooks:
  - `INV-M365-S-persona-registry-humanized-delegation-integration.ipynb`
  - `INV-M365-AT-humanized-delegation-interface-v1.ipynb`
- Existing green scorecards:
  - `artifacts/scorecards/scorecard_l17.json`
  - `artifacts/scorecards/scorecard_l44.json`
- Gap:
  - those notebooks prove the delegation and registry integration class, but the parent initiative still lacks a phase-specific notebook-backed `G1` reachability artifact and scorecard-ready proof chain for governance closeout

## Decision Rule

`ReachabilityTruthObserved = CanonicalResolve59 AND DisplayResolve59 AND StateReachable59`

`PlannedFenceObserved = PlannedPersonaActionFence5`

`GovernanceCloseoutBlocked = validate_action(governance_edit, G1 closeout) returns map-5-governance-notebook-evidence`

`PhaseSpecificNotebookEvidenceDefined = G1S owns notebook-backed reachability evidence, generated verification output, and tracker synchronization for the parent initiative`

`G1S_GO = ReachabilityTruthObserved AND PlannedFenceObserved AND GovernanceCloseoutBlocked AND PhaseSpecificNotebookEvidenceDefined`

If `G1S_GO` is false, `G1S` must emit `NO-GO`, stop fail-closed, and keep the parent initiative at `G1`.

## Scope

### In scope

- restate the `G1` blocker explicitly from live runtime and governance truth
- create a phase-specific notebook-backed reachability evidence chain for the parent initiative
- publish generated verification output for the `G1` reachability claim
- update the parent commercialization note and diagnostics artifact with the notebook-backed `G1` result
- synchronize the parent plan and governance trackers only after the `G1` notebook evidence is admissible
- hand control back to the parent initiative with `G2` as the next act only after `G1S` is green, committed, and pushed

### Out of scope

- `G2` mapping, orphan, or stub classification
- any runtime code, registry, routing, or auth-model changes
- any UCP-side changes
- any widening of the workforce graph beyond the frozen `G0` baseline

### File allowlist

- `plans/m365-persona-action-g1-notebook-evidence-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-g1-notebook-evidence-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-g1-notebook-evidence-scope-correction-prompt.txt`
- `plans/m365-persona-action-certification/m365-persona-action-certification.md`
- `docs/commercialization/m365-persona-action-certification.md`
- `artifacts/diagnostics/m365_persona_action_certification.json`
- `docs/ma/lemmas/L*_m365_persona_action_reachability_certification_v1.md`
- `invariants/lemmas/L*_m365_persona_action_reachability_certification_v1.yaml`
- `notebooks/m365/INV-M365-*-persona-action-reachability-certification-v1.ipynb`
- `notebooks/lemma_proofs/L*_m365_persona_action_reachability_certification_v1.ipynb`
- `notebooks/m365/INV-M365-CI-persona-action-g1-notebook-evidence-governance-alignment-v1.ipynb`
- `artifacts/scorecards/scorecard_*.json`
- `configs/generated/persona_action_reachability_certification_v1_verification.json`
- `configs/generated/persona_action_g1_notebook_evidence_governance_alignment_v1_verification.json`
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

- **R1** — Make the `G1` governance blocker explicit from live runtime and MCP truth.
- **R2** — Produce phase-specific notebook-backed `G1` persona reachability evidence.
- **R3** — Produce generated verification output for the `G1` reachability evidence chain.
- **R4** — Publish the notebook-backed `G1` result into the parent commercialization and diagnostics artifacts.
- **R5** — Synchronize the parent plan and governance trackers truthfully after the notebook evidence is green.
- **R6** — Commit and push `G1S` before resuming the parent initiative at `G2`.

## Child Acts

### G1SA — Blocker restatement

- freeze the live runtime reachability counts and the exact governance denial that blocked `G1`

### G1SB — Notebook evidence chain

- create the phase-specific notebook-backed reachability evidence, verification output, and any required lemma/invariant bindings

### G1SC — Parent closeout handback

- publish the `G1` result into the parent artifacts
- synchronize trackers
- validate, commit, push, and return the parent initiative to `G2`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-persona-action-g1-notebook-evidence-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-persona-action-g1-notebook-evidence-scope-correction-prompt.txt`

## Validation Strategy

- require the `G1` notebook evidence to preserve the observed runtime totals:
  - `59/59` canonical resolutions
  - `59/59` display-name resolutions
  - `59/59` state reachability
  - `5/5` planned-persona fences
- require generated verification output for the governance-alignment and `G1` evidence chain
- require the parent commercialization note and diagnostics artifact to match the notebook-backed totals exactly
- require tracker truth to point to `G2` only after the child package is green
- run `git diff --check`

## Agent Constraints

- Do not begin `G2` inside `G1S`.
- Do not edit runtime code, registries, or tests in `G1S`.
- Do not claim execution truth or orphan truth in `G1S`; this phase is reachability-evidence only.
- Commit and push `G1S` before any `G2` work begins.

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] this child plan `status -> complete`

## Execution Outcome

- **Decision:** `GO`
- **Approved by:** `operator explicit go`
- **Completion timestamp:** `2026-04-07 06:33:24 EDT`
