# Execution Prompt — Incident Response War Room Workflow Notebook Evidence Scope Correction

Plan Reference: `plan:m365-incident-response-war-room-workflow-notebook-evidence-scope-correction`
Parent Plan Reference: `plan:m365-incident-response-war-room-workflow-enablement`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`

**Mission:** Unblock the incident workflow package by reopening the blocked runtime `file_edit` validation through a phase-specific notebook-backed blocker package, then hand the parent initiative back to `R2` only if that validation is green.

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-incident-response-war-room-workflow-notebook-evidence-scope-correction:R0`
- `PARENT_PLAN_ACK: plan:m365-incident-response-war-room-workflow-enablement`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. Present the approval packet first.
2. Wait for explicit `go`.
3. Call MCP `validate_action` before every mutating action and obey the verdict.
4. Notebook first: do not start runtime extraction until the blocked workflow `file_edit` validation is green under child-plan authority.
5. Do not auto-advance past `R2`.

## Context

- Parent initiative is blocked at `R1` after package activation.
- Blocked workflow code-write set:
  - `src/smarthaus_common/incident_response_war_room.py`
  - `src/provisioning_api/routers/m365.py`
  - `src/smarthaus_graph/client.py`
  - `scripts/ops/provision_incident_response_war_room.py`
  - `tests/test_incident_response_war_room.py`
- Parent blocker:
  - `map-2-code-notebook-required` on `file_edit` for the intended workflow code wave
- Existing supporting evidence:
  - `notebooks/m365/INV-M365-DI-incident-response-war-room-workflow-governance-alignment-v1.ipynb`
  - `configs/generated/incident_response_war_room_workflow_governance_alignment_v1_verification.json`
  - `docs/ma/lemmas/L97_m365_incident_response_war_room_workflow_enablement_v1.md`
  - `invariants/lemmas/L97_m365_incident_response_war_room_workflow_enablement_v1.yaml`
  - `notebooks/m365/INV-M365-DJ-incident-response-war-room-workflow-enablement-v1.ipynb`
  - `notebooks/lemma_proofs/L97_m365_incident_response_war_room_workflow_enablement_v1.ipynb`
  - `artifacts/scorecards/scorecard_l97.json`
  - `configs/generated/incident_response_war_room_workflow_enablement_v1_verification.json`

## Execution Order

1. `IWNSA` blocker restatement
2. `IWNSB` governance-evidence binding
3. `IWNSC` blocked-validation reopen and parent handback

## Hard Rule

Do not begin workflow runtime or test code edits until the blocked file-edit validation is re-opened under child-plan authority.

## Output Contract

- Emit checks exactly:
  - `CHECK:IWNS-<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final lines exactly:
  - `GATE:IWNS-NOTEBOOK-EVIDENCE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Required Deliverables

- child blocker package
- synchronized parent plan state showing the child package as the active blocker phase
- blocked workflow `file_edit` validation retried under child-plan authority
- truthful handback to parent `R2` only if the validation turns green
