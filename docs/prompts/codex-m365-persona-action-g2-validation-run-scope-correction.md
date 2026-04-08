# Execution Prompt — Persona-Action G2 Validation-Run Scope Correction

Plan Reference: `plan:m365-persona-action-g2-validation-run-scope-correction`
Parent Reference: `plan:m365-persona-action-certification`
North Star Reference: `Operations/NORTHSTAR.md`

## Mission

Unblock the blocked `G2` closeout validation run without changing the already-computed `G2` mapping truth.

## Required Order

1. Load the blocked `G2` state and denial reasons.
2. Use the `INV-M365-CL` notebook-backed governance evidence.
3. Retry the blocked validation-run authorization.
4. If the gate clears, return to the parent initiative and ship `G2`.
5. If the gate remains denied, stop fail-closed and report the exact remaining blocker.

## Hard Rule

Do not widen this child phase into `G3`, `G4`, or `G5`.
