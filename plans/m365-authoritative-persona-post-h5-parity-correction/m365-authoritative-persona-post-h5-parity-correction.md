# Plan: M365 Authoritative Persona Post-H5 Parity Correction

**Plan ID:** `m365-authoritative-persona-post-h5-parity-correction`
**Parent Plan ID:** `m365-authoritative-persona-humanization-expansion`
**Status:** 🟡 Draft
**Date:** 2026-04-05
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-post-h5-parity-correction:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep final authoritative workforce claims truthful and fail-closed by correcting stale post-H5 certification and release-gate surfaces before any merged `development` push may claim the humanized workforce is integrated.
**Canonical predecessor:** `plans/m365-authoritative-persona-humanization-merge-to-development/m365-authoritative-persona-humanization-merge-to-development.md`
**Blocker context:** local `development` merge commit `a895678` is unpushed and blocked after `verify_persona_certification_v1.py` exposed stale pre-H5 certification and release-gate truth.

**Draft vs Active semantics:** This blocker package starts in **Draft**. It becomes **Active** only after the approval packet is presented and receives explicit `go`, and only while no other post-H5 correction or merge phase is concurrently active. It becomes **Complete** only after the stale parity gap is corrected, the correction branch is committed and pushed, and `M1` is truthfully unblocked for re-validation.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook execution, file edits, tests, commit, and push. Stop on first red. Do not push `development` from this package.

**Notebook-first discipline:** This correction changes final certification and release-gate count truth, so all count formulas, parity proofs, and acceptance checks must be re-derived in notebooks first before extraction.

## Objective

Correct the stale post-H5 certification and release-gate surfaces so the final authoritative truth is internally consistent at `59 total / 54 active / 5 planned / 430 routed actions`, then hand `M1` back a truthful branch payload for re-validation.

## Current State

- correction branch base: `codex/m365-authoritative-persona-humanization-expansion-plan @ 0f210e9`
- blocked local merge evidence: `development @ a895678`, unpushed
- final authoritative surfaces already at:
  - `registry/persona_registry_v2.yaml -> 59 total / 54 active / 5 planned`
  - `registry/activated_persona_surface_v1.yaml -> 54 active / 5 deferred external`
  - `registry/workforce_packaging_v1.yaml -> 54 active / 5 planned / 430 actions`
- stale downstream surfaces still at staged pre-H5 truth:
  - `registry/persona_certification_v1.yaml -> 34 active / 25 planned / 34 registry-backed`
  - `registry/enterprise_release_gate_v2.yaml -> 34 active certified / 25 planned certified / 298 routed actions`

## Decision Rule

`FinalRegistryTruth = {total_personas=59, active_personas=54, planned_personas=5, registry_backed_personas=54}`

`FinalCertificationTruth = persona_certification.kpis = FinalRegistryTruth AND contract_only_personas = 5`

`FinalReleaseGateTruth = {personas_certified=59, active_personas_certified=54, planned_personas_certified=5, total_routed_actions=430}`

`ParityProofGreen = NotebookProofGreen AND ScorecardGreen AND GeneratedVerificationGreen`

`CorrectionValidationGreen = PersonaCertificationVerifierGreen AND EnterpriseReleaseGateVerifierGreen AND FocusedPytestGreen AND PreCommitGreen AND DiffCheckGreen`

`P5_GO = FinalCertificationTruth AND FinalReleaseGateTruth AND ParityProofGreen AND CorrectionValidationGreen`

If `P5_GO` is false, this package must emit `NO-GO`, stop fail-closed, and leave `M1` blocked.

## Scope

### In scope

- prove the post-H5 parity gap from live repo truth
- rebase `registry/persona_certification_v1.yaml` to the final post-H5 state
- rebase `registry/enterprise_release_gate_v2.yaml` to the final post-H5 state
- update the corresponding commercialization contracts
- update the corresponding verifiers and tests
- publish notebook-backed proof, scorecard, and generated verification output
- update trackers so `M1` is truthfully blocked by this correction until green

### Out of scope

- pushing `development`
- staging or main promotion
- release-tag publication
- changing `registry/persona_registry_v2.yaml`
- changing `registry/activated_persona_surface_v1.yaml`
- changing `registry/workforce_packaging_v1.yaml`
- changing `registry/agents.yaml`
- changing `registry/ai_team.json`

### File allowlist

- `plans/m365-authoritative-persona-post-h5-parity-correction/**`
- `docs/prompts/codex-m365-authoritative-persona-post-h5-parity-correction.md`
- `docs/prompts/codex-m365-authoritative-persona-post-h5-parity-correction-prompt.txt`
- `registry/persona_certification_v1.yaml`
- `registry/enterprise_release_gate_v2.yaml`
- `docs/commercialization/m365-persona-certification-v1.md`
- `docs/commercialization/m365-enterprise-release-gate-v2.md`
- `scripts/ci/verify_persona_certification_v1.py`
- `scripts/ci/verify_enterprise_release_gate_v2.py`
- `tests/test_persona_certification_v1.py`
- `tests/test_enterprise_release_gate_v2.py`
- `docs/ma/lemmas/L*_m365_authoritative_persona_post_h5_parity_correction_v1.md`
- `invariants/lemmas/L*_m365_authoritative_persona_post_h5_parity_correction_v1.yaml`
- `notebooks/m365/INV-M365-*-authoritative-persona-post-h5-parity-correction-v1.ipynb`
- `notebooks/lemma_proofs/L*_m365_authoritative_persona_post_h5_parity_correction_v1.ipynb`
- `artifacts/scorecards/scorecard_*.json`
- `configs/generated/authoritative_persona_post_h5_parity_correction_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/persona_registry_v2.yaml`
- `registry/activated_persona_surface_v1.yaml`
- `registry/workforce_packaging_v1.yaml`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`
- `registry/ai_team.json`
- `staging`
- `main`
- release tags

## Requirements

- **R1** — Make the blocked `M1` parity gap explicit from live repo truth.
- **R2** — Produce MA-backed proof for final post-H5 certification and release-gate parity.
- **R3** — Rebase persona certification to the final `59 / 54 / 5` truth.
- **R4** — Rebase the enterprise release gate to the final `59 / 54 / 5 / 430` truth.
- **R5** — Update commercialization contracts, verifiers, and tests to the final parity state.
- **R6** — Validate the correction branch and restore `M1` to a truthfully unblockable state.
- **R7** — Commit and push the correction branch before `M1` resumes.

## Child Acts

### P5A — Blocker Freeze

- capture the exact stale/final surface mismatch
- freeze the local blocked merge evidence without pushing `development`

### P5B — Final Parity Rebase

- rebase persona certification and enterprise release-gate truth to final post-H5 state
- keep all derivation notebook-first

### P5C — Validation and Handback

- run targeted verifiers and tests
- commit and push the correction branch
- mark `M1` blocked only by re-validation on a fresh merge replay

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-post-h5-parity-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-post-h5-parity-correction-prompt.txt`

## Validation Strategy

- prove parity in notebooks before extraction
- run:
  - `python3 scripts/ci/verify_persona_certification_v1.py`
  - `python3 scripts/ci/verify_enterprise_release_gate_v2.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_persona_certification_v1.py tests/test_enterprise_release_gate_v2.py`
  - `pre-commit run --all-files`
  - `git diff --check`
- do not resume `M1` until this package is green, committed, and pushed

## Governance Closure

- [ ] `Operations/ACTION_LOG.md`
- [ ] `Operations/EXECUTION_PLAN.md`
- [ ] `Operations/PROJECT_FILE_INDEX.md`
- [ ] this package `status -> complete`

## Agent Constraints

- Do not push `development` from this package.
- Do not widen the correction beyond the stale certification and release-gate parity boundary.
- Stop if the correction appears to require changes to the already truthful final registry, activated-surface, or packaging surfaces.
