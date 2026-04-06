# Plan: M365 Authoritative Persona H3 Regression Proof Rebinding

**Plan ID:** `m365-authoritative-persona-h3-regression-proof-rebinding`
**Parent Plan ID:** `m365-authoritative-persona-humanization-merge-replay-to-development`
**Status:** Draft
**Date:** 2026-04-06
**Owner:** SmartHaus
**Execution plan reference:** `plan:m365-authoritative-persona-h3-regression-proof-rebinding:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — preserve truthful, auditable workforce state by keeping the live branch on the final post-H5 `59 total / 54 active / 5 planned` authority while binding historical H3 regression checks to frozen H3 proof surfaces instead of stale live-file assumptions.
**Governance evidence:** `notebooks/m365/INV-M365-BZ-authoritative-persona-registry-rebase-v1.ipynb`, `configs/generated/authoritative_persona_registry_rebase_v1_verification.json`

## Objective

Rebind the stale H3 regression surface to the frozen H3 proof artifacts so the historical staged `34 active / 25 planned` assertions remain mechanically enforced without blocking final post-H5 merge replay on the truthful live branch.

## Problem Statement

The remaining `M1` replay blocker is not a live registry defect. It is a stale regression design:

- `tests/test_authoritative_persona_registry_rebase_v1.py` loads the live post-H5 files:
  - `registry/persona_capability_map.yaml`
  - `registry/persona_registry_v2.yaml`
- the test still asserts the H3 staged truth:
  - `34 active / 25 planned`
  - promoted personas remain `persona-contract-only`
- the live branch truth after H5 is correctly:
  - `54 active / 5 planned`
  - promoted personas are `registry-backed`
- the frozen H3 staged proof already exists in:
  - `configs/generated/authoritative_persona_registry_rebase_v1_verification.json`
  - the notebook source `notebooks/m365/INV-M365-BZ-authoritative-persona-registry-rebase-v1.ipynb`

So the correct fix is to rebind the H3 regression to the frozen H3 proof surface, not to mutate the live final registry back toward staged truth.

## Decision Rule

`FrozenH3ProofAvailable = GeneratedH3VerificationExists AND H3NotebookExists`

`RegressionBoundCorrectly = H3RegressionReadsFrozenProof AND H3RegressionDoesNotAssertAgainstLivePostH5RegistryState`

`LiveTruthPreserved = NoEdit(registry/persona_registry_v2.yaml) AND NoEdit(registry/persona_capability_map.yaml) AND NoEdit(registry/activated_persona_surface_v1.yaml) AND NoEdit(registry/workforce_packaging_v1.yaml)`

`PackageValidated = FocusedPytestGreen AND PreCommitGreen AND DiffCheckGreen`

`H3R_GO = FrozenH3ProofAvailable AND RegressionBoundCorrectly AND LiveTruthPreserved AND PackageValidated`

If `H3R_GO` is false, emit `NO-GO`, stop fail-closed, and do not replay `M1`.

## Scope

### In scope

- create a formal correction package and prompt pair
- rebind `tests/test_authoritative_persona_registry_rebase_v1.py` to frozen H3 proof artifacts
- use the existing H3 notebook and generated verification artifact as the historical truth source
- update trackers so `M1` truthfully points at this correction as the next blocker

### Out of scope

- changing the live final post-H5 registry or capability-map truth
- changing activation, packaging, certification, or department-pack live truth
- replaying `M1`
- pushing `development`

### File allowlist

- `plans/m365-authoritative-persona-h3-regression-proof-rebinding/**`
- `docs/prompts/codex-m365-authoritative-persona-h3-regression-proof-rebinding.md`
- `docs/prompts/codex-m365-authoritative-persona-h3-regression-proof-rebinding-prompt.txt`
- `tests/test_authoritative_persona_registry_rebase_v1.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/activated_persona_surface_v1.yaml`
- `registry/workforce_packaging_v1.yaml`
- `development`
- `staging`
- `main`

## Requirements

### R1 — Governed proof-rebinding package

- Create the correction plan triplet and prompt pair.

### R2 — Bind H3 regression to frozen H3 proof

- Update the failing H3 regression so it asserts against the frozen H3 verification surface rather than the live post-H5 authority files.

### R3 — Preserve live final truth

- Do not edit the live post-H5 authoritative registry, capability-map, activation, packaging, or certification surfaces.

### R4 — Validate the bounded correction

- Run the focused H3 regression pytest plus the repo hard gates required for commit.

### R5 — Governance synchronization

- Update trackers so the canonical branch records this correction and hands `M1` back only after green completion.

## Success Criteria

- the H3 regression still proves staged H3 truth mechanically
- the regression no longer assumes the live branch is still in H3
- the live post-H5 authority surfaces remain untouched
- the focused regression validation is green
- `M1` is blocked only by executing this correction package, not by branch clutter

## Validation

- parse checks for the plan JSON/YAML
- focused pytest:
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_authoritative_persona_registry_rebase_v1.py`
- bounded supporting check:
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_persona_registry_v2.py`
- `pre-commit run --all-files`
- `git diff --check`

## Rollback

- restore the pre-correction test binding if the frozen H3 proof is found insufficient
- do not touch live registry truth as part of rollback
