# Plan — M365 Persona-Action G2 Validation-Run Scope Correction

- **Plan ID:** `plan:m365-persona-action-g2-validation-run-scope-correction`
- **Parent Plan:** `plan:m365-persona-action-certification`
- **Owner:** `SMARTHAUS`
- **Status:** `active`
- **Date Created:** `2026-04-07`
- **Date Updated:** `2026-04-07`

## Section 1: Intent

- Unblock the governed `G2` closeout for the persona-action certification initiative.
- Create the minimum notebook-backed correction package needed to authorize the mandatory validation run for the completed `G2` write set.
- Do not change the already-computed `G2` mapping totals.

## Section 2: Problem Statement

- `G2` mapping truth is complete locally but cannot be shipped.
- The mandatory closeout validation run for `pre-commit run --all-files` was denied by governance.
- The denial set included:
  - `qual-4-fix-root-cause-mode`
  - `map-7-gating-for-long-running`
  - `qual-5-testing-real-service-warning`
  - `qual-7-metrics-notice`
  - `map-8-notebook-first-for-notebook-error-fix`
- The correction required here is not a runtime or product change. It is a validation-run scope correction for the `G2` ship step.

## Section 3: Boundaries

- In scope:
  - this child correction package
  - notebook-backed governance evidence for the blocked `G2` validation run
  - retry of the blocked `G2` validation gate after the evidence exists
- Out of scope:
  - changing the `G2` classification logic
  - changing runtime behavior
  - changing tenant state
  - widening to `G3`, `G4`, or `G5` before `G2` is committed and pushed

## Section 4: Requirements

- `R1`
  - Freeze the blocked validation-run context for `G2`.
- `R2`
  - Publish notebook-backed governance evidence for the `G2` pre-commit closeout gate.
- `R3`
  - Retry the blocked validation-run authorization using the new evidence.
- `R4`
  - If the gate clears, allow `G2` commit/push and return control to the parent initiative.
- `R5`
  - If the gate remains red, stop fail-closed and report the exact remaining denial.

## Section 5: Artifacts

- `plans/m365-persona-action-g2-validation-run-scope-correction/m365-persona-action-g2-validation-run-scope-correction.md`
- `plans/m365-persona-action-g2-validation-run-scope-correction/m365-persona-action-g2-validation-run-scope-correction.yaml`
- `plans/m365-persona-action-g2-validation-run-scope-correction/m365-persona-action-g2-validation-run-scope-correction.json`
- `docs/prompts/codex-m365-persona-action-g2-validation-run-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-g2-validation-run-scope-correction-prompt.txt`
- `notebooks/m365/INV-M365-CL-persona-action-g2-validation-run-governance-alignment-v1.ipynb`
- `configs/generated/persona_action_g2_validation_run_governance_alignment_v1_verification.json`

## Section 6: Current Result

- `G2` is complete locally but not yet committed.
- The next act for this child package is to use the new notebook-backed evidence to retry the blocked `G2` closeout validation gate.
