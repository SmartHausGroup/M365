# Codex Prompt: M365 MA Scorecard Alignment

Plan reference: `plan:m365-ma-scorecard-alignment:R1`

## Objective

Create the minimum legitimate MA bridge required for UCP governance to recognize the M365 repo as phase-complete and scorecard-green, using the repo's existing contract, invariant, notebook, and verification evidence.

## Required outputs

- `docs/NORTH_STAR.md`
- `docs/ma/phase1_formula.md`
- `docs/ma/phase2_calculus.md`
- `docs/ma/lemmas/L1_*.md` through `L5_*.md`
- `invariants/lemmas/L1_*.yaml` through `L5_*.yaml`
- `notebooks/lemma_proofs/L1_*.ipynb` through `L5_*.ipynb`
- `notebooks/m365_contracts.ipynb`
- `artifacts/scorecards/scorecard_l1.json` through `scorecard_l5.json`
- `artifacts/scorecards/scorecard_m365_contracts.json`
- `scorecard.json`

## Constraints

- Do not change runtime code.
- Do not invent new product capabilities.
- Keep every new artifact traceable to existing evidence under:
  - `docs/contracts/caio-m365/`
  - `invariants/`
  - `notebooks/`
  - `configs/generated/`
- Fail closed if any required green assertion cannot be justified from committed repo evidence.

## Required validations

- `phase_status(repo)` reports phase `9`
- `validate_scorecard(repo)` returns `green=true`
- `validate_action(push, ...)` returns `allowed=true`
- `git diff --check` is clean on the changed files

## Notes

- This is a governance-structure and scorecard projection task.
- It does not replace the commercialization plan's later live-tenant evidence phases.
