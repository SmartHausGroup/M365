# Codex Prompt: M365 Persona-Action P2 Third-Wave Notebook Evidence Scope Correction

## Plan Reference

- `plan:m365-persona-action-p2-third-wave-notebook-evidence-scope-correction:R0-R6`

## Objective

Unblock the third bounded `P2` legacy-stub remediation wave by publishing phase-specific notebook-backed evidence and reopening the blocked `file_edit` validation for:

- `src/ops_adapter/actions.py`
- `tests/test_ops_adapter.py`

Target aliases for the bounded third-wave `P2` repair:

- `archive-project`
- `system.health-check`
- `alerts.respond`

## Required Outputs

- the bounded `P2U` plan triplet
- the `P2U` prompt pair
- governance notebook `INV-M365-CU-persona-action-p2-third-wave-notebook-evidence-scope-correction-v1.ipynb`
- generated verification `persona_action_p2_third_wave_notebook_evidence_scope_correction_v1_verification.json`
- the future `L92` evidence chain:
  - `docs/ma/lemmas/L92_m365_persona_action_legacy_stub_remediation_v3.md`
  - `invariants/lemmas/L92_m365_persona_action_legacy_stub_remediation_v3.yaml`
  - `notebooks/m365/INV-M365-CV-persona-action-legacy-stub-remediation-v3.ipynb`
  - `notebooks/lemma_proofs/L92_m365_persona_action_legacy_stub_remediation_v3.ipynb`
  - `artifacts/scorecards/scorecard_l92.json`
  - `configs/generated/persona_action_legacy_stub_remediation_v3_verification.json`

## Guardrails

- do not edit `src/**`, `tests/**`, or `registry/**` in `P2U`
- do not widen into `P3`
- stop on first red gate
- commit and push `P2U` before returning control to `P2`
