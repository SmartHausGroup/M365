# Execution Prompt — Persona-Action P3 Department-Pack Scope Correction

Plan Reference: `plan:m365-persona-action-p3-department-pack-scope-correction`
Parent Plan Reference: `plan:m365-persona-action-full-support-remediation`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`

**Mission:** Unblock the second bounded `P3` retirement wave by publishing notebook-backed scope evidence, widening `P3` into the affected department-pack authority surfaces, and returning control to the parent initiative so the last non-M365 permission-blocked aliases can be retired truthfully.

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-persona-action-p3-department-pack-scope-correction:R1`
- `PARENT_PLAN_ACK: plan:m365-persona-action-full-support-remediation`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. Present the approval packet first.
2. Wait for explicit `go`.
3. Call MCP `validate_action` before every mutating action and obey the verdict.
4. Notebook first: no widened `P3` repair scope before the governance notebook and verification are green.
5. Do not auto-advance past the parent `P3` act.

## Context

- Parent initiative already completed:
  - `P0`
  - `P1`
  - `P2`
  - first bounded `P3` wave
- Remaining frozen `P3` aliases:
  - `create-project`
  - `deployment.preview`
  - `list-projects`
  - `provision-client-services`
- Companion stale department-pack claims in the same affected packs:
  - `deployment.production`
  - `content.create`
  - `content.update`
  - `analytics.read`
  - `seo.update`
  - `update-project-status`
  - `deprovision-client-services`
  - `get-client-status`
- Affected packs:
  - operations
  - project-management
  - engineering

## Execution Order

1. `P3SA` scope-gap freeze
2. `P3SB` notebook-backed governance evidence
3. `P3SC` parent handback

## Hard Rule

Do not execute the second-wave `P3` retirement edits in this child phase. `P3S` only widens the admissible authority surface and hands control back to the parent initiative.

## Output Contract

- Emit checks exactly:
  - `CHECK:P3S-<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final lines exactly:
  - `GATE:P3S-DEPARTMENT-PACK-SCOPE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Required Deliverables

- bounded `P3S` plan triplet
- `P3S` prompt pair
- governance notebook `INV-M365-DC-persona-action-p3-department-pack-scope-correction-v1.ipynb`
- generated verification `persona_action_p3_department_pack_scope_correction_v1_verification.json`
- widened parent `P3` allowlist and tracker handback
