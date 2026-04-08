# Codex Prompt: M365 Persona-Action P2 Second-Wave Notebook Evidence Scope Correction

## Plan Reference

- `plan:m365-persona-action-p2-second-wave-notebook-evidence-scope-correction:R0-R6`

## Objective

Unblock the second bounded `P2` legacy-stub remediation wave by publishing phase-specific notebook-backed evidence and reopening the blocked `file_edit` validation for:

- `src/ops_adapter/actions.py`
- `tests/test_ops_adapter.py`

Target aliases for the bounded second-wave `P2` repair:

- `followup.create`
- `client.follow-up`
- `satisfaction.survey`
- `interview.schedule`

## Required Outputs

- the bounded `P2T` plan triplet
- the `P2T` prompt pair
- governance notebook `INV-M365-CS-persona-action-p2-second-wave-notebook-evidence-scope-correction-v1.ipynb`
- generated verification `persona_action_p2_second_wave_notebook_evidence_scope_correction_v1_verification.json`
- the future `L91` evidence chain:
  - `docs/ma/lemmas/L91_m365_persona_action_legacy_stub_remediation_v2.md`
  - `invariants/lemmas/L91_m365_persona_action_legacy_stub_remediation_v2.yaml`
  - `notebooks/m365/INV-M365-CT-persona-action-legacy-stub-remediation-v2.ipynb`
  - `notebooks/lemma_proofs/L91_m365_persona_action_legacy_stub_remediation_v2.ipynb`
  - `artifacts/scorecards/scorecard_l91.json`
  - `configs/generated/persona_action_legacy_stub_remediation_v2_verification.json`

## Guardrails

- do not edit `src/**`, `tests/**`, or `registry/**` in `P2T`
- do not widen into `P3`
- stop on first red gate
- commit and push `P2T` before returning control to `P2`
