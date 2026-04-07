# Codex Prompt: M365 Persona-Action P2 Notebook Evidence Scope Correction

## Plan Reference

- `plan:m365-persona-action-p2-notebook-evidence-scope-correction:R0-R6`

## Objective

Unblock the first bounded `P2` legacy-stub remediation wave by publishing phase-specific notebook-backed evidence and reopening the blocked `file_edit` validation for:

- `src/ops_adapter/actions.py`
- `tests/test_ops_adapter.py`

Target aliases for the first bounded `P2` wave:

- `task.create`
- `follow-up.schedule`
- `reminder.send`

## Required Outputs

- the bounded `P2S` plan triplet
- the `P2S` prompt pair
- governance notebook `INV-M365-CQ-persona-action-p2-notebook-evidence-scope-correction-v1.ipynb`
- generated verification `persona_action_p2_notebook_evidence_scope_correction_v1_verification.json`
- the future `L90` evidence chain:
  - `docs/ma/lemmas/L90_m365_persona_action_legacy_stub_remediation_v1.md`
  - `invariants/lemmas/L90_m365_persona_action_legacy_stub_remediation_v1.yaml`
  - `notebooks/m365/INV-M365-CR-persona-action-legacy-stub-remediation-v1.ipynb`
  - `notebooks/lemma_proofs/L90_m365_persona_action_legacy_stub_remediation_v1.ipynb`
  - `artifacts/scorecards/scorecard_l90.json`
  - `configs/generated/persona_action_legacy_stub_remediation_v1_verification.json`

## Guardrails

- do not edit `src/**`, `tests/**`, or `registry/**` in `P2S`
- do not widen into `P3`
- stop on first red gate
- commit and push `P2S` before returning control to `P2`
