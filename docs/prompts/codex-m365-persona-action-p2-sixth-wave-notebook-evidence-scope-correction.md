# Codex Prompt: M365 Persona-Action P2 Sixth-Wave Notebook Evidence Scope Correction

## Plan Reference

- `plan:m365-persona-action-p2-sixth-wave-notebook-evidence-scope-correction:R0-R6`

## Objective

Unblock the sixth bounded `P2` legacy-stub remediation wave by publishing phase-specific notebook-backed evidence and reopening the bounded `file_edit` validation for:

- `src/ops_adapter/actions.py`
- `tests/test_ops_adapter.py`

Target aliases for the bounded sixth-wave `P2` repair:

- `deployment.production`
- `website.deploy`
- `cdn.purge`
- `dns.update`
- `ssl.renew`
- `performance.optimize`
- `backup.restore`

## Required Outputs

- the bounded `P2X` plan triplet
- the `P2X` prompt pair
- governance notebook `INV-M365-DA-persona-action-p2-sixth-wave-notebook-evidence-scope-correction-v1.ipynb`
- generated verification `persona_action_p2_sixth_wave_notebook_evidence_scope_correction_v1_verification.json`
- the future `L95` evidence chain

## Guardrails

- do not edit `src/**`, `tests/**`, or `registry/**` in `P2X`
- do not widen into `P3`
- stop on first red gate
- commit and push `P2X` before returning control to parent `P2`
