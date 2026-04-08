# Plan: M365 Persona-Action P2 Fifth-Wave Notebook Evidence Scope Correction

**Plan ID:** `m365-persona-action-p2-fifth-wave-notebook-evidence-scope-correction`
**Parent Plan ID:** `m365-persona-action-full-support-remediation`
**Status:** ✅ Complete
**Date:** 2026-04-07
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-p2-fifth-wave-notebook-evidence-scope-correction:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the persona-action remediation truthful and fail-closed by refusing to start the fifth bounded `P2` wave until the `it-operations-manager` slice has explicit notebook-backed evidence accepted by governance.
**Governance evidence:** `notebooks/m365/INV-M365-CY-persona-action-p2-fifth-wave-notebook-evidence-scope-correction-v1.ipynb`, `configs/generated/persona_action_p2_fifth_wave_notebook_evidence_scope_correction_v1_verification.json`

## Objective

Create the bounded child phase that publishes explicit notebook-backed evidence for the fifth bounded `P2` legacy-stub remediation slice so the parent initiative can truthfully reopen the next code-write validation and continue repair under governed notebook-first conditions.

## Current State

- Parent initiative:
  - `plan:m365-persona-action-full-support-remediation`
- Completed parent phases:
  - `P0`
  - `P1`
  - `P2S`
  - `P2T`
  - `P2U`
  - `P2V`
- Observed bounded fifth-wave `P2` write target:
  - `src/ops_adapter/actions.py`
  - `tests/test_ops_adapter.py`
- Targeted bounded fifth-wave `P2` aliases:
  - `infrastructure.monitor`
  - `backup.verify`
  - `security.scan`
- Derived post-wave-4 legacy-stub backlog:
  - `28` active pairs
  - `34` unique aliases
- Planned `L94` replacement modes:
  - `infrastructure.monitor -> health_overview`
  - `security.scan -> security_secure_score`
  - `backup.verify -> explicit unsupported M365-only failure`

## Requirements

- **R0** — Create the bounded `P2W` blocker package.
- **R1** — Freeze the bounded fifth-wave `P2` IT-operations slice explicitly.
- **R2** — Produce notebook-backed governance evidence for the bounded fifth-wave `P2` write.
- **R3** — Expand the admissible future evidence surface to include `L94`.
- **R4** — Reopen the bounded fifth-wave `P2` code-write validation under child-plan authority.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Commit and push before resuming `P2`.

## File Allowlist

- `plans/m365-persona-action-p2-fifth-wave-notebook-evidence-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-p2-fifth-wave-notebook-evidence-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-p2-fifth-wave-notebook-evidence-scope-correction-prompt.txt`
- `notebooks/m365/INV-M365-CY-persona-action-p2-fifth-wave-notebook-evidence-scope-correction-v1.ipynb`
- `configs/generated/persona_action_p2_fifth_wave_notebook_evidence_scope_correction_v1_verification.json`
- `docs/ma/lemmas/L94_m365_persona_action_legacy_stub_remediation_v5.md`
- `invariants/lemmas/L94_m365_persona_action_legacy_stub_remediation_v5.yaml`
- `notebooks/m365/INV-M365-CZ-persona-action-legacy-stub-remediation-v5.ipynb`
- `notebooks/lemma_proofs/L94_m365_persona_action_legacy_stub_remediation_v5.ipynb`
- `artifacts/scorecards/scorecard_l94.json`
- `configs/generated/persona_action_legacy_stub_remediation_v5_verification.json`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

## Constraints

- Do not begin fifth-wave `P2` code edits inside `P2W` until the bounded write validation is reopened.
- Do not widen into `P3` or `P4` during `P2W`.
- Do not edit runtime code, registries, or tests in `P2W`.
- Commit and push `P2W` before any parent `P2` code work begins.

## Result

- `P2W` is complete.
- Governance notebook `INV-M365-CY` and generated verification are published.
- The future `L94` evidence chain is published and parse-clean.
- MCP `validate_action(file_edit)` is green under child-plan authority for:
  - `src/ops_adapter/actions.py`
  - `tests/test_ops_adapter.py`
- The bounded fifth-wave `P2` repair set is reopened for:
  - `infrastructure.monitor`
  - `backup.verify`
  - `security.scan`
- Control returns to parent `P2`.
