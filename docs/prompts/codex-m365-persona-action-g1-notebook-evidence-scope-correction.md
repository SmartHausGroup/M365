# Execution Prompt — Persona-Action G1 Notebook Evidence Scope Correction

Plan Reference: `plan:m365-persona-action-g1-notebook-evidence-scope-correction`
Parent Plan Reference: `plan:m365-persona-action-certification`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`

**Mission:** Unblock `G1` by producing phase-specific notebook-backed persona-reachability evidence, then publish the parent `G1` result truthfully and hand the parent initiative back to `G2`.

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-persona-action-g1-notebook-evidence-scope-correction:R1`
- `PARENT_PLAN_ACK: plan:m365-persona-action-certification`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. Present the approval packet first.
2. Wait for explicit `go`.
3. Call MCP `validate_action` before every mutating action and obey the verdict.
4. Notebook first: no parent `G1` commercialization or tracker closeout before the notebook-backed evidence is green.
5. Do not auto-advance past `G2`.

## Context

- Parent initiative observed but unpublished `G1` runtime truth:
  - `59/59` canonical persona-id resolutions
  - `59/59` display-name resolutions
  - `59/59` persona state endpoint reachability
  - `5/5` planned-persona action fences
- Parent blocker:
  - `map-5-governance-notebook-evidence` on `governance_edit` for the `G1` tracker closeout
- Existing supporting notebook evidence:
  - `notebooks/m365/INV-M365-S-persona-registry-humanized-delegation-integration.ipynb`
  - `notebooks/m365/INV-M365-AT-humanized-delegation-interface-v1.ipynb`
  - `artifacts/scorecards/scorecard_l17.json`
  - `artifacts/scorecards/scorecard_l44.json`

## Execution Order

1. `G1SA` blocker restatement
2. `G1SB` notebook evidence chain
3. `G1SC` parent closeout handback

## Hard Rule

Do not widen into mapping, orphan, or execution-truth claims. `G1S` only proves persona reachability and planned-persona fencing strongly enough for governance closeout.

## Output Contract

- Emit checks exactly:
  - `CHECK:G1S-<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final lines exactly:
  - `GATE:G1S-NOTEBOOK-EVIDENCE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Required Deliverables

- notebook-backed `G1` reachability evidence
- generated verification output
- updated parent commercialization note
- updated parent diagnostics artifact
- synchronized parent plan and trackers
- commit and push of the child package before `G2`
