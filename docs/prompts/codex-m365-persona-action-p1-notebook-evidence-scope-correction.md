# Execution Prompt — Persona-Action P1 Notebook Evidence Scope Correction

Plan Reference: `plan:m365-persona-action-p1-notebook-evidence-scope-correction`
Parent Plan Reference: `plan:m365-persona-action-full-support-remediation`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`

**Mission:** Unblock `P1` by producing phase-specific notebook-backed governance evidence for the first dead-route code write, then reopen the blocked validation truthfully and hand the parent initiative back to `P1`.

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-persona-action-p1-notebook-evidence-scope-correction:R0`
- `PARENT_PLAN_ACK: plan:m365-persona-action-full-support-remediation`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. Present the approval packet first.
2. Wait for explicit `go`.
3. Call MCP `validate_action` before every mutating action and obey the verdict.
4. Notebook first: no `P1` code repair before notebook-backed blocker evidence is green.
5. Do not auto-advance past `P1`.

## Context

- Parent initiative is at `P1` after `P0` read-only backlog lock.
- First blocked write set:
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_common/permission_enforcer.py`
  - `policies/ops.rego`
  - `tests/test_ops_adapter.py`
  - `tests/test_policies.py`
  - `tests/test_executor_routing_v2.py`
- Parent blocker:
  - `map-2-code-notebook-required` on `file_edit` for the first dead-route remediation write
- Existing supporting notebook evidence:
  - `notebooks/m365/INV-M365-CK-persona-action-mapping-audit-v1.ipynb`
  - `notebooks/m365/INV-M365-CN-persona-action-route-certification-v1.ipynb`
  - `artifacts/scorecards/scorecard_l86.json`
  - `artifacts/scorecards/scorecard_l88.json`

## Execution Order

1. `P1SA` blocker restatement
2. `P1SB` governance notebook evidence
3. `P1SC` blocked-validation reopen and parent handback

## Hard Rule

Do not begin `P1` runtime/test code edits until the blocked file-edit validation is re-opened under child-plan authority.

## Output Contract

- Emit checks exactly:
  - `CHECK:P1S-<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final lines exactly:
  - `GATE:P1S-NOTEBOOK-EVIDENCE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Required Deliverables

- notebook-backed blocker evidence
- generated verification output
- updated parent remediation plan/tracker state showing `P1S` as the blocker-fix phase
- reopened `P1` file-edit validation under child-plan authority
- commit and push of the child package before returning to parent `P1`
