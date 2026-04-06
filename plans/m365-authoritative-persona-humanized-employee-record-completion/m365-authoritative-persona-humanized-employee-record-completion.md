# Plan: M365 Authoritative Persona Humanized Employee Record Completion

**Plan ID:** `m365-authoritative-persona-humanized-employee-record-completion`
**Parent Plan ID:** `m365-authoritative-persona-humanization-expansion`
**Status:** 🟢 Complete
**Date:** 2026-04-05
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-humanized-employee-record-completion:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — create truthful named digital-employee records for the `20` promoted personas while preserving bounded metadata, departmental accountability, and fail-closed activation discipline.
**Canonical predecessor:** `plans/m365-authoritative-persona-census-and-department-model-decision/m365-authoritative-persona-census-and-department-model-decision.md`

**Draft vs Active semantics:** This child plan started in **Draft**. It transitioned to **Active** when H1 was green and the operator continued the governed sequence with explicit `go`, and it is now **Complete** because the bounded employee-record artifact, MA evidence chain, verifier, focused test, and tracker updates are green.

**Approval and governance gates:** Before execution, present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before every mutating action and obey the verdict. Stop on first red. Do not auto-advance to H3.

**Notebook-first discipline:** H2 is a notebook-backed authority-definition phase. All record-field iteration, manager/escalation mapping, and artifact construction must occur in notebooks first. No direct runtime or registry extraction is allowed before the H2 notebook evidence and scorecard are green.

## Objective

Create the deterministic named employee-record set for all `20` promoted personas with the exact bounded metadata contract required by the parent initiative, without rebasing the authoritative registries or activating any promoted persona in this phase.

## Decision Rule

`RecordFieldComplete = FOR ALL promoted_persona: {display_name, title, department, manager, escalation_owner, working_style, communication_style, decision_style} are non-empty`

`MetadataBounded = No fields beyond the approved bounded metadata contract are introduced for personality-style data`

`ChainOfCommandBounded = FOR ALL promoted_persona: manager and escalation_owner resolve to an approved department or governance token`

`H2_GO = H1_GO AND RecordFieldComplete AND MetadataBounded AND ChainOfCommandBounded`

If `H2_GO` is false, H2 must emit `NO-GO`, stop, and keep all promoted personas out of the authoritative registries.

## Scope

### In scope

- define the named employee record for each of the `20` promoted personas
- bind each record to the H1-approved department placement
- bind each record to bounded manager and escalation-owner tokens
- create notebook-backed, machine-readable employee-record authority artifacts
- create verification artifacts, scorecards, and tests for the record set

### Out of scope

- editing `registry/ai_team.json`
- editing `registry/persona_registry_v2.yaml`
- editing `registry/persona_capability_map.yaml`
- editing `registry/agents.yaml`
- activating promoted personas
- inventing freeform personality schema
- widening the department model

### File allowlist

- `plans/m365-authoritative-persona-humanized-employee-record-completion/**`
- `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion.md`
- `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion-prompt.txt`
- `registry/authoritative_digital_employee_records_v1.yaml`
- `docs/commercialization/m365-authoritative-digital-employee-records-v1.md`
- `docs/ma/lemmas/L*_m365_authoritative_digital_employee_records_v1.md`
- `invariants/lemmas/L*_m365_authoritative_digital_employee_records_v1.yaml`
- `notebooks/m365/INV-M365-*-authoritative-digital-employee-records-v1.ipynb`
- `notebooks/lemma_proofs/L*_m365_authoritative_digital_employee_records_v1.ipynb`
- `artifacts/scorecards/scorecard_*.json`
- `scripts/ci/verify_authoritative_digital_employee_records_v1.py`
- `configs/generated/authoritative_digital_employee_records_v1_verification.json`
- `tests/test_authoritative_digital_employee_records_v1.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/ai_team.json`
- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`
- `src/**`

## Requirements

- **R1** — Complete all required employee-record fields for the `20` promoted personas.
- **R2** — Keep humanization metadata bounded to `working_style`, `communication_style`, and `decision_style`.
- **R3** — Bind each promoted persona to explicit manager and escalation-owner tokens.
- **R4** — Produce notebook-backed machine-readable and human-readable employee-record artifacts.
- **R5** — Produce deterministic verification, scorecard, and test evidence.
- **R6** — Stop without rebasing registries or activating personas.

## Child Acts

### H2A — Field Contract and Chain-of-Command Lock

- lock the exact field matrix for all `20` promoted personas
- confirm titles, departments, managers, escalation owners, and bounded style fields

### H2B — Notebook-Backed Employee Record Artifact

- create the notebook-backed authority artifact for the `20` employee records
- generate the verification output and scorecard

### H2C — Verification and Governance Closeout

- run targeted verification and tests
- update governance surfaces
- commit and push before advancing to H3

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion-prompt.txt`

## Validation Strategy

- verify all `20` promoted personas exist in the authority artifact
- verify required fields are complete and bounded
- verify manager and escalation-owner tokens are non-empty
- verify scorecard and generated verification artifacts exist
- run `git diff --check`

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] This child plan `status -> complete`

## Execution Outcome

- **Decision:** `GO`
- **Approved by:** `operator explicit go`
- **Completion timestamp:** `2026-04-05 08:08:00 EDT`
- **Employee record artifact:** `registry/authoritative_digital_employee_records_v1.yaml`
- **Verification artifact:** `configs/generated/authoritative_digital_employee_records_v1_verification.json`
- **Validated next act:** `H3`

## Agent Constraints

- Do not edit the authoritative registries in H2.
- Do not add freeform metadata.
- Do not auto-advance to H3.
- Commit and push H2 before any H3 work begins.
