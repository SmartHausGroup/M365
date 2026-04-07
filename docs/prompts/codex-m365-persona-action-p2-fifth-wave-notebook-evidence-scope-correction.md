# Codex Prompt: M365 Persona-Action P2 Fifth-Wave Notebook Evidence Scope Correction

## Plan Reference

- `plan:m365-persona-action-p2-fifth-wave-notebook-evidence-scope-correction:R0-R6`

## Objective

Unblock the fifth bounded `P2` legacy-stub remediation wave by publishing phase-specific notebook-backed evidence and reopening the bounded `file_edit` validation for:

- `src/ops_adapter/actions.py`
- `tests/test_ops_adapter.py`

Target aliases for the bounded fifth-wave `P2` repair:

- `infrastructure.monitor`
- `backup.verify`
- `security.scan`

## Required Outputs

- the bounded `P2W` plan triplet
- the `P2W` prompt pair
- governance notebook `INV-M365-CY-persona-action-p2-fifth-wave-notebook-evidence-scope-correction-v1.ipynb`
- generated verification `persona_action_p2_fifth_wave_notebook_evidence_scope_correction_v1_verification.json`
- the future `L94` evidence chain

## Guardrails

- do not edit `src/**`, `tests/**`, or `registry/**` in `P2W`
- do not widen into `P3`
- stop on first red gate
- commit and push `P2W` before returning control to parent `P2`
