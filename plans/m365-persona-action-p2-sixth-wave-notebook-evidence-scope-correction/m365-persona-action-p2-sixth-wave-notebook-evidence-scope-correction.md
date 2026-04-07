# Plan: M365 Persona-Action P2 Sixth-Wave Notebook Evidence Scope Correction

**Plan ID:** `m365-persona-action-p2-sixth-wave-notebook-evidence-scope-correction`
**Parent Plan ID:** `m365-persona-action-full-support-remediation`
**Status:** ✅ Complete
**Date:** 2026-04-07
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-p2-sixth-wave-notebook-evidence-scope-correction:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the persona-action remediation truthful and fail-closed by refusing to start the sixth bounded `P2` wave until the non-M365 website slice has explicit notebook-backed evidence accepted by governance.
**Governance evidence:** `notebooks/m365/INV-M365-DA-persona-action-p2-sixth-wave-notebook-evidence-scope-correction-v1.ipynb`, `configs/generated/persona_action_p2_sixth_wave_notebook_evidence_scope_correction_v1_verification.json`

## Objective

Create the bounded child phase that publishes explicit notebook-backed evidence for the sixth bounded `P2` legacy-stub remediation slice so the parent initiative can truthfully reopen the next code-write validation and replace fake website/non-M365 success claims with explicit fail-closed outcomes.

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
  - `P2W`
- Observed bounded sixth-wave `P2` write target:
  - `src/ops_adapter/actions.py`
  - `tests/test_ops_adapter.py`
- Targeted bounded sixth-wave `P2` aliases:
  - `deployment.production`
  - `website.deploy`
  - `cdn.purge`
  - `dns.update`
  - `ssl.renew`
  - `performance.optimize`
  - `backup.restore`
- Derived post-wave-5 legacy-stub backlog:
  - `25` active pairs
  - `31` unique aliases
- Planned `L95` replacement mode:
  - every target alias -> explicit unsupported M365-only failure

## Requirements

- **R0** — Create the bounded `P2X` blocker package.
- **R1** — Freeze the bounded sixth-wave `P2` website/non-M365 slice explicitly.
- **R2** — Produce notebook-backed governance evidence for the bounded sixth-wave `P2` write.
- **R3** — Expand the admissible future evidence surface to include `L95`.
- **R4** — Reopen the bounded sixth-wave `P2` code-write validation under child-plan authority.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Commit and push before resuming `P2`.

## File Allowlist

- `plans/m365-persona-action-p2-sixth-wave-notebook-evidence-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-p2-sixth-wave-notebook-evidence-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-p2-sixth-wave-notebook-evidence-scope-correction-prompt.txt`
- `notebooks/m365/INV-M365-DA-persona-action-p2-sixth-wave-notebook-evidence-scope-correction-v1.ipynb`
- `configs/generated/persona_action_p2_sixth_wave_notebook_evidence_scope_correction_v1_verification.json`
- `docs/ma/lemmas/L95_m365_persona_action_legacy_stub_remediation_v6.md`
- `invariants/lemmas/L95_m365_persona_action_legacy_stub_remediation_v6.yaml`
- `notebooks/m365/INV-M365-DB-persona-action-legacy-stub-remediation-v6.ipynb`
- `notebooks/lemma_proofs/L95_m365_persona_action_legacy_stub_remediation_v6.ipynb`
- `artifacts/scorecards/scorecard_l95.json`
- `configs/generated/persona_action_legacy_stub_remediation_v6_verification.json`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

## Constraints

- Do not begin sixth-wave `P2` code edits inside `P2X` until the bounded write validation is reopened.
- Do not widen into `P3` or `P4` during `P2X`.
- Do not edit runtime code, registries, or tests in `P2X`.
- Commit and push `P2X` before any parent `P2` code work begins.

## Result

- `P2X` is complete.
- Governance notebook `INV-M365-DA` and generated verification are published.
- The future `L95` evidence chain is published and parse-clean.
- MCP `validate_action(file_edit)` is green under child-plan authority for:
  - `src/ops_adapter/actions.py`
  - `tests/test_ops_adapter.py`
- The bounded sixth-wave `P2` repair set is reopened for:
  - `deployment.production`
  - `website.deploy`
  - `cdn.purge`
  - `dns.update`
  - `ssl.renew`
  - `performance.optimize`
  - `backup.restore`
- Control returns to parent `P2`.
