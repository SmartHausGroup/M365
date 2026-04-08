# Codex Prompt: M365 Persona-Action P2 Fourth-Wave Notebook Evidence Scope Correction

## Plan Reference

- `plan:m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction:R0-R6`

## Objective

Unblock the fourth bounded `P2` legacy-stub remediation wave by publishing phase-specific notebook-backed evidence and reopening the bounded `file_edit` validation for:

- `src/ops_adapter/actions.py`
- `tests/test_ops_adapter.py`

Target aliases for the bounded fourth-wave `P2` repair:

- `task.assign`
- `deadline.track`
- `status.update`
- `report.generate`

## Required Outputs

- the bounded `P2V` plan triplet
- the `P2V` prompt pair
- governance notebook `INV-M365-CW-persona-action-p2-fourth-wave-notebook-evidence-scope-correction-v1.ipynb`
- generated verification `persona_action_p2_fourth_wave_notebook_evidence_scope_correction_v1_verification.json`
- the future `L93` evidence chain:
  - `docs/ma/lemmas/L93_m365_persona_action_legacy_stub_remediation_v4.md`
  - `invariants/lemmas/L93_m365_persona_action_legacy_stub_remediation_v4.yaml`
  - `notebooks/m365/INV-M365-CX-persona-action-legacy-stub-remediation-v4.ipynb`
  - `notebooks/lemma_proofs/L93_m365_persona_action_legacy_stub_remediation_v4.ipynb`
  - `artifacts/scorecards/scorecard_l93.json`
  - `configs/generated/persona_action_legacy_stub_remediation_v4_verification.json`

## Guardrails

- do not edit `src/**`, `tests/**`, or `registry/**` in `P2V`
- do not widen into `P3`
- stop on first red gate
- commit and push `P2V` before returning control to `P2`
