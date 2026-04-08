# Plan: M365 Incident Response War Room Workflow Notebook Evidence Scope Correction

**Plan ID:** `plan:m365-incident-response-war-room-workflow-notebook-evidence-scope-correction`
**Parent Plan ID:** `plan:m365-incident-response-war-room-workflow-enablement`
**Status:** `Complete`
**Date:** `2026-04-08`
**Owner:** `SMARTHAUS`
**Execution plan reference:** `plan:m365-incident-response-war-room-workflow-notebook-evidence-scope-correction:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the incident workflow package truthful and fail-closed by refusing to start runtime code extraction until the blocked workflow code wave has explicit notebook-backed evidence accepted by governance.
**Canonical predecessor:** `plans/m365-incident-response-war-room-workflow-enablement/m365-incident-response-war-room-workflow-enablement.md`
**Governance evidence:** `notebooks/m365/INV-M365-DI-incident-response-war-room-workflow-governance-alignment-v1.ipynb`, `configs/generated/incident_response_war_room_workflow_governance_alignment_v1_verification.json`
**Historical lineage:** successor blocker package after `validate_action(file_edit)` denied the incident workflow runtime write set with `map-2-code-notebook-required`.

**Draft vs Active semantics:** This child plan starts in **Draft** and becomes **Active** only when the parent incident-workflow initiative remains blocked at `R1`, the approval packet receives explicit `go`, and no sibling unblock phase is concurrently active. It becomes **Complete** only after the blocked code-write validation is re-opened under child-plan authority and the parent initiative truthfully returns to `R2`.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action. Stop on first red. Do not start runtime code extraction inside this child package unless the blocked `file_edit` validation turns green under child-plan authority.

**Notebook-first discipline:** This package is a notebook-backed governance-unblock phase. The blocked workflow code-write boundary, the exact MCP denial, and the admissible future `L97` evidence chain must remain explicit before runtime extraction is retried.

## Objective

Create the bounded child phase that publishes explicit notebook-backed blocker evidence for the incident workflow code wave so the parent package can truthfully reopen the first runtime `file_edit` validation and continue at `R2` under governed notebook-first conditions.

## Current State

- Parent initiative:
  - `plan:m365-incident-response-war-room-workflow-enablement`
- Completed parent phase:
  - `R0`
- Parent blocker phase:
  - `R1`
- Blocked workflow code-write set:
  - `src/smarthaus_common/incident_response_war_room.py`
  - `src/provisioning_api/routers/m365.py`
  - `src/smarthaus_graph/client.py`
  - `scripts/ops/provision_incident_response_war_room.py`
  - `tests/test_incident_response_war_room.py`
- Blocking governance verdict:
  - `validate_action(file_edit)` for the intended workflow code wave returned `allowed:false`
  - violation id: `map-2-code-notebook-required`
- Existing supporting notebook evidence:
  - `notebooks/m365/INV-M365-DI-incident-response-war-room-workflow-governance-alignment-v1.ipynb`
  - `notebooks/m365/INV-M365-DJ-incident-response-war-room-workflow-enablement-v1.ipynb`
  - `notebooks/lemma_proofs/L97_m365_incident_response_war_room_workflow_enablement_v1.ipynb`
- Existing supporting verification surface:
  - `configs/generated/incident_response_war_room_workflow_governance_alignment_v1_verification.json`
  - `configs/generated/incident_response_war_room_workflow_enablement_v1_verification.json`
  - `artifacts/scorecards/scorecard_l97.json`
- Gap:
  - the parent initiative still lacks a phase-specific blocker package that reopens the denied workflow code-write validation under child-plan authority

## Decision Rule

`IncidentCodeWaveFrozen = RuntimeModule AND Router AND GraphHelper AND OperatorScript AND FocusedTest`

`FirstR2WriteBlocked = validate_action(file_edit, incident workflow code wave) returns map-2-code-notebook-required`

`PhaseSpecificEvidenceSurfaceDefined = child package owns governance notebook evidence, generated verification output, and the admissible future L97 workflow evidence chain`

`BlockedWriteSetFrozen = incident_response_war_room.py AND m365.py AND client.py AND provision_incident_response_war_room.py AND test_incident_response_war_room.py`

`ChildAuthorityReopensValidation = validate_action(file_edit, incident workflow code wave) under child-plan authority returns allowed:true`

`IWNS_GO = IncidentCodeWaveFrozen AND FirstR2WriteBlocked AND PhaseSpecificEvidenceSurfaceDefined AND BlockedWriteSetFrozen AND ChildAuthorityReopensValidation`

If `IWNS_GO` is false, this child package must emit `NO-GO`, stop fail-closed, and keep the parent initiative blocked before `R2`.

## Scope

### In scope

- restate the incident workflow code-write blocker explicitly from MCP truth
- bind the existing `DI` governance notebook and generated verification to this child package
- bind the existing `L97` workflow evidence chain as the admissible future code-wave surface
- synchronize the parent plan and governance trackers so the incident initiative truthfully pauses at this child package
- reopen the blocked workflow `file_edit` validation under child-plan authority
- hand control back to the parent initiative with `R2` as the next act only if the blocked validation turns green

### Out of scope

- actual incident workflow runtime code edits
- contract-doc or registry synchronization
- focused validation commands
- tenant mutations or live provisioning
- any UCP-side changes

### File allowlist

- `plans/m365-incident-response-war-room-workflow-notebook-evidence-scope-correction/**`
- `docs/prompts/codex-m365-incident-response-war-room-workflow-notebook-evidence-scope-correction.md`
- `docs/prompts/codex-m365-incident-response-war-room-workflow-notebook-evidence-scope-correction-prompt.txt`
- `plans/m365-incident-response-war-room-workflow-enablement/m365-incident-response-war-room-workflow-enablement.md`
- `plans/m365-incident-response-war-room-workflow-enablement/m365-incident-response-war-room-workflow-enablement.yaml`
- `plans/m365-incident-response-war-room-workflow-enablement/m365-incident-response-war-room-workflow-enablement.json`
- `notebooks/m365/INV-M365-DI-incident-response-war-room-workflow-governance-alignment-v1.ipynb`
- `configs/generated/incident_response_war_room_workflow_governance_alignment_v1_verification.json`
- `docs/ma/lemmas/L97_m365_incident_response_war_room_workflow_enablement_v1.md`
- `invariants/lemmas/L97_m365_incident_response_war_room_workflow_enablement_v1.yaml`
- `notebooks/m365/INV-M365-DJ-incident-response-war-room-workflow-enablement-v1.ipynb`
- `notebooks/lemma_proofs/L97_m365_incident_response_war_room_workflow_enablement_v1.ipynb`
- `artifacts/scorecards/scorecard_l97.json`
- `configs/generated/incident_response_war_room_workflow_enablement_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `src/**`
- `tests/**`
- `registry/**`
- `docs/contracts/**`
- `docs/CAIO_M365_CONTRACT.md`
- `../UCP/**`
- any path not listed in the allowlist

## Requirements

- **R0** — Create the bounded incident-workflow blocker package.
- **R1** — Make the incident workflow code-write blocker explicit from MCP truth.
- **R2** — Bind the existing governance notebook evidence to this blocker package.
- **R3** — Bind the admissible future `L97` workflow evidence chain to the child package.
- **R4** — Reopen the blocked workflow `file_edit` validation under child-plan authority.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Hand the parent initiative back to `R2` only if `R4` is green.

## Child Acts

### IWNSA — Blocker restatement

- freeze the exact workflow code-write set and the MCP denial that blocked it

### IWNSB — Governance-evidence binding

- bind the existing `DI` governance notebook evidence and the future `L97` workflow evidence chain to this child package

### IWNSC — Validation reopen and handback

- reopen the blocked workflow `file_edit` validation under child-plan authority
- synchronize trackers
- return the parent initiative to `R2` only if the validation turns green

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-incident-response-war-room-workflow-notebook-evidence-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-incident-response-war-room-workflow-notebook-evidence-scope-correction-prompt.txt`

## Validation Strategy

- require the governance notebook evidence to preserve the observed blocker truth:
  - blocked write set frozen exactly to the workflow code wave
  - MCP violation `map-2-code-notebook-required`
  - existing `DI` and `L97` evidence chain paths remain explicit
- require a retry of the blocked `file_edit` validation under child-plan authority
- require the parent incident plan and governance trackers to point to this child package while the blocker is unresolved
- run `git diff --check` only if the package reaches a state where command execution is explicitly admitted

## Agent Constraints

- Do not begin workflow runtime code edits inside this child package unless the blocked file-edit validation is re-opened successfully.
- Do not widen into contract-doc or registry edits during this child package.
- Do not run validation commands or live tenant mutations inside this child package.

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] child package status synchronized truthfully

## Execution Outcome

- **Decision:** `go`
- **Approved by:** `operator explicit go`
- **Result:** The blocked incident-workflow `validate_action(file_edit)` call reopened green under child-plan authority when the notebook backing metadata was flattened to the live accepted contract. The parent initiative returned to runtime extraction, completed the bounded `R2` and `R3` implementation slices, and then passed the agreed local `R4` validation set. The child package is therefore complete and the parent initiative is now active only for truthful live tenant proof or exact external blocker capture.
