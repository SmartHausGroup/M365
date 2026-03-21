# Plan: M365 Repo — MA Scorecard Alignment

**Plan ID:** `m365-ma-scorecard-alignment`
**Status:** Complete (validated 2026-03-17)
**Date:** 2026-03-17
**Owner:** SmartHaus
**Execution plan reference:** `plan:m365-ma-scorecard-alignment:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — governed, auditable, deterministic M365 operations with fail-closed release gates.

## Objective

Align the M365 repo's existing Mathematical Autopsy evidence to the structural artifact layout required by UCP governance, emit a legitimate aggregate `scorecard.json`, and unblock governed `push` without changing runtime behavior.

## Problem Statement

The repo already contains real MA evidence for the CAIO ↔ M365 contract:

- contract intent, mathematics, lemmas, and invariants under `docs/contracts/caio-m365/` and `invariants/`
- proof notebooks under `notebooks/`
- verification artifacts under `configs/generated/`

But UCP currently expects a different repo shape for phase gating and scorecard evaluation. Because those bridge artifacts do not exist, the repo is reported as `phase=0` and `scorecard_status=missing`, which blocks `push`.

## Scope

### In scope

- Create MA bridge documents in the UCP-required locations
- Create projected lemma and invariant artifacts that map cleanly to the existing M365 proofs
- Create required notebook-path artifacts for lemma proofs and module contracts
- Create per-lemma and module scorecards plus the aggregate repo `scorecard.json`
- Validate `phase_status`, `validate_scorecard`, and `validate_action(push)`

### Out of scope

- Runtime code changes
- New algorithm implementation
- Live-tenant commercialization certification
- Replacing existing proof artifacts in `docs/contracts/` or `configs/generated/`

## Requirements

### R1 — Governed initiative and prompts

- Create a formal plan and Codex prompt pair for scorecard alignment.

### R2 — Phase bridge documents

- Add the required MA phase files under `docs/` and `docs/ma/`.

### R3 — Lemma and invariant projections

- Add lemma and invariant projection artifacts that explicitly map to existing M365 proofs and verification JSONs.

### R4 — Notebook path alignment

- Add notebook artifacts in the exact locations UCP phase gating expects.

### R5 — Scorecard projection

- Emit per-lemma and module scorecards plus an aggregate `scorecard.json` rooted in current committed evidence.

### R6 — Governance validation

- Validate that UCP reports phase 9, the scorecard is green, and `push` is allowed.

## Planned Outputs

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

## Success Criteria

- `phase_status` reports completed phase `9`
- `validate_scorecard` returns `green=true`
- `validate_action(push)` returns `allowed=true`
- All new bridge artifacts are traceable to existing repo evidence

## Validation Outcome

- `phase_status` reported completed phase `9` on 2026-03-17.
- `validate_scorecard` reported `green=true` on 2026-03-17.
- `validate_action(push)` reported `allowed=true` on 2026-03-17.

## Validation

- `phase_status(repo)`
- `validate_scorecard(repo)`
- `validate_action(push, repo, ...)`
- `git diff --check`

## Rollback

- Remove the scorecard-alignment bridge docs, notebooks, scorecards, plan, and prompt artifacts in a revert commit if the result cannot be justified or validated honestly.
