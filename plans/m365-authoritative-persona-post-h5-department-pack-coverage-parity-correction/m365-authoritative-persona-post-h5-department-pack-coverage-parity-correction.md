# Plan: M365 Authoritative Persona Post-H5 Department-Pack Coverage Parity Correction

**Plan ID:** `m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction`
**Parent Plan ID:** `m365-authoritative-persona-humanization-merge-to-development`
**Status:** 🟢 Complete
**Date:** 2026-04-06
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the final authoritative workforce truthful and fail-closed by reconciling the department-pack authority surface to the already-governed post-H5 activation truth before any merged `development` push may claim the humanized workforce is integrated.
**Canonical predecessor:** `plans/m365-authoritative-persona-post-h5-certification-parity-scope-correction/m365-authoritative-persona-post-h5-certification-parity-scope-correction.md`
**Canonical blocker target:** `plans/m365-authoritative-persona-humanization-merge-to-development/m365-authoritative-persona-humanization-merge-to-development.md`
**Blocker context:** fresh local `development` merge commit `d194b94` is unpushed and blocked after the department-pack validation slice proved that the source branch still carries staged department-pack coverage contracts for the 20 promoted personas.
**Scope-gap evidence:** `notebooks/m365/INV-M365-CF-authoritative-persona-post-h5-department-pack-coverage-parity-correction-v1.ipynb`, `configs/generated/authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1_verification.json`

**Draft vs Active semantics:** This blocker package starts in **Draft**. It becomes **Active** only after the approval packet is presented and receives explicit `go`, and only while no other merge replay or department-pack correction phase is concurrently active. It becomes **Complete** only after the affected department-pack authority surfaces, commercialization contracts, verifier/test slice, and trackers all reconcile to the final post-H5 truth, the correction branch is committed and pushed, and `M1` is truthfully eligible for a fresh merge replay.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook execution, file edits, tests, commit, and push. Stop on first red. Do not push `development` from this package.

**Notebook-first discipline:** This correction changes department-pack execution claims, so all pack-parity formulas, mismatch inventories, and bounded final-state claims must be re-derived in notebooks first before extraction.

**Status update (2026-04-06 07:42 EDT):** Executed the notebook-first `L84` department-pack coverage-parity correction and closed it `GO`. Published the completed proof chain in `docs/ma/lemmas/L84_m365_authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1.md`, `invariants/lemmas/L84_m365_authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1.yaml`, `notebooks/m365/INV-M365-CF-authoritative-persona-post-h5-department-pack-coverage-parity-correction-v1.ipynb`, `notebooks/lemma_proofs/L84_m365_authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1.ipynb`, `artifacts/scorecards/scorecard_l84.json`, and `configs/generated/authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1_verification.json`; rebased the 7 affected `registry/department_pack_*_v1.yaml` authority surfaces plus their commercialization contracts, verifier scripts, and focused pytest files to the final post-H5 source-branch truth; and preserved the certified `department.status` taxonomy without changing the already-truthful final registry, activation, packaging, or certification surfaces. Validation passed with the 7 targeted department-pack verifier scripts, focused pytest (`28 passed`), `pre-commit run --all-files`, and `git diff --check`. `M1` is now blocked only by a fresh governed replay from the corrected source branch after this package commit/push closes.

## Objective

Rebase the affected department-pack authority surface to the final post-H5 activation truth so every promoted persona that is already `registry-backed` in the authoritative registry is represented consistently in the department-pack contracts, docs, verifiers, and tests before `M1` is replayed again.

## Current State

- corrected source branch: `codex/m365-authoritative-persona-post-h5-parity-correction @ e85be90`
- fresh blocked local merge evidence: `development @ d194b94`, unpushed, preserved on `codex/m1-fresh-replay-blocked-development-d194b94`
- prior blocked local merge evidence: `development @ a895678`, preserved on `codex/m1-replay-blocked-development-a895678`
- live authoritative registry truth already remains final at:
  - `registry/persona_registry_v2.yaml -> 59 total / 54 active / 5 planned`
  - all 20 promoted personas now `coverage_status=registry-backed`
- `L84` scope-gap evidence proves `M1` still cannot pass because 7 department packs still declare staged contract-only coverage with zero actions for promoted personas:
  - `communication -> 3 mismatches`
  - `engineering -> 1 mismatch`
  - `hr -> 1 mismatch`
  - `marketing -> 1 mismatch`
  - `operations -> 8 mismatches`
  - `project-management -> 2 mismatches`
  - `studio-operations -> 4 mismatches`
- total mismatch count: `20`
- direct failure trigger:
  - `registry/department_pack_communication_v1.yaml -> calendar-management-agent coverage_status=persona-contract-only`
  - `registry/persona_registry_v2.yaml -> calendar-management-agent coverage_status=registry-backed`
  - `src/smarthaus_common/department_pack.py` fails closed on that mismatch before any pack summary may be built

## Decision Rule

`AffectedPackPersonas = {the 20 promoted personas recorded in L84 scope-gap evidence}`

`FinalDepartmentPackCoverageTruth = ForEachPersonaInAffectedPacks(declared.coverage_status = registry.coverage_status)`

`FinalDepartmentPackActionTruth = ForEachPersonaInAffectedPacks((declared.coverage_status = registry-backed -> supported_actions is non-empty and bounded by the persona contract) AND (declared.coverage_status = persona-contract-only -> supported_actions = []))`

`FinalDepartmentPackSummaryTruth = Each affected department-pack summary, KPI block, and commercialization contract reconciles to the final post-H5 persona status boundary without downgrading the 20 promoted personas back to staged contract-only execution`

`PackParityProofGreen = NotebookProofGreen AND GeneratedVerificationGreen`

`PackParityValidationGreen = AffectedDepartmentPackVerifiersGreen AND AffectedDepartmentPackPytestGreen AND PreCommitGreen AND DiffCheckGreen`

`P9_GO = FinalDepartmentPackCoverageTruth AND FinalDepartmentPackActionTruth AND FinalDepartmentPackSummaryTruth AND PackParityProofGreen AND PackParityValidationGreen`

If `P9_GO` is false, this package must emit `NO-GO`, stop fail-closed, and leave `M1` blocked.

## Scope

### In scope

- prove the post-H5 department-pack coverage gap from live repo truth
- rebase the affected department-pack authority YAML files to the final post-H5 coverage and action truth
- update the corresponding commercialization contracts
- update the affected department-pack verifiers and tests
- update `src/smarthaus_common/department_pack.py` only if notebook proof shows a bounded runtime parity fix is required
- publish notebook-backed proof, scorecard, and generated verification output
- update trackers so `M1` is truthfully blocked by this package until green

### Out of scope

- pushing `development`
- staging or main promotion
- release-tag publication
- changing `registry/persona_registry_v2.yaml`
- changing `registry/activated_persona_surface_v1.yaml`
- changing `registry/workforce_packaging_v1.yaml`
- changing `registry/persona_certification_v1.yaml`
- changing `registry/department_certification_v1.yaml`
- changing `registry/enterprise_release_gate_v2.yaml`
- changing `registry/persona_capability_map.yaml`
- changing `registry/agents.yaml`
- changing `registry/ai_team.json`

### File allowlist

- `plans/m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction/**`
- `docs/prompts/codex-m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction.md`
- `docs/prompts/codex-m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction-prompt.txt`
- `registry/department_pack_communication_v1.yaml`
- `registry/department_pack_engineering_v1.yaml`
- `registry/department_pack_hr_v1.yaml`
- `registry/department_pack_marketing_v1.yaml`
- `registry/department_pack_operations_v1.yaml`
- `registry/department_pack_project_management_v1.yaml`
- `registry/department_pack_studio_operations_v1.yaml`
- `docs/commercialization/m365-communication-department-pack-v1.md`
- `docs/commercialization/m365-engineering-department-pack-v1.md`
- `docs/commercialization/m365-hr-department-pack-v1.md`
- `docs/commercialization/m365-marketing-department-pack-v1.md`
- `docs/commercialization/m365-operations-department-pack-v1.md`
- `docs/commercialization/m365-project-management-department-pack-v1.md`
- `docs/commercialization/m365-studio-operations-department-pack-v1.md`
- `scripts/ci/verify_communication_department_pack_v1.py`
- `scripts/ci/verify_engineering_department_pack_v1.py`
- `scripts/ci/verify_hr_department_pack_v1.py`
- `scripts/ci/verify_marketing_department_pack_v1.py`
- `scripts/ci/verify_operations_department_pack_v1.py`
- `scripts/ci/verify_project_management_department_pack_v1.py`
- `scripts/ci/verify_studio_operations_department_pack_v1.py`
- `tests/test_communication_department_pack_v1.py`
- `tests/test_engineering_department_pack_v1.py`
- `tests/test_hr_department_pack_v1.py`
- `tests/test_marketing_department_pack_v1.py`
- `tests/test_operations_department_pack_v1.py`
- `tests/test_project_management_department_pack_v1.py`
- `tests/test_studio_operations_department_pack_v1.py`
- `src/smarthaus_common/department_pack.py`
- `configs/generated/communication_department_pack_v1_verification.json`
- `configs/generated/engineering_department_pack_v1_verification.json`
- `configs/generated/hr_department_pack_v1_verification.json`
- `configs/generated/marketing_department_pack_v1_verification.json`
- `configs/generated/operations_department_pack_v1_verification.json`
- `configs/generated/project_management_department_pack_v1_verification.json`
- `configs/generated/studio_operations_department_pack_v1_verification.json`
- `notebooks/m365/INV-M365-*-authoritative-persona-post-h5-department-pack-coverage-parity-correction-v1.ipynb`
- `docs/ma/lemmas/L*_m365_authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1.md`
- `invariants/lemmas/L*_m365_authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1.yaml`
- `notebooks/lemma_proofs/L*_m365_authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1.ipynb`
- `artifacts/scorecards/scorecard_*.json`
- `configs/generated/authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/persona_registry_v2.yaml`
- `registry/activated_persona_surface_v1.yaml`
- `registry/workforce_packaging_v1.yaml`
- `registry/persona_certification_v1.yaml`
- `registry/department_certification_v1.yaml`
- `registry/enterprise_release_gate_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`
- `registry/ai_team.json`
- `development push`
- `staging`
- `main`
- release tags

## Requirements

- **R1** — Make the blocked fresh `M1` department-pack parity gap explicit from live repo truth and `L84` evidence.
- **R2** — Produce MA-backed proof for final post-H5 department-pack coverage and action parity across the affected packs.
- **R3** — Rebase the affected department-pack authority YAML files to the final post-H5 truth.
- **R4** — Rebase the affected commercialization contracts, verifiers, tests, and bounded runtime parity logic if required.
- **R5** — Validate the affected department-pack slice and preserve fail-closed behavior on the remaining planned external personas.
- **R6** — Update trackers so `M1` is truthfully blocked by this package until green, then eligible only for a fresh replay.
- **R7** — Commit and push the correction branch before `M1` resumes.

## Child Acts

### P9A — Blocker Freeze

- freeze the fresh blocked merge evidence and the `L84` mismatch inventory
- define the exact affected department-pack surface

### P9B — Department-Pack Final Parity Rebase

- rebase affected pack YAML/contracts to the final post-H5 coverage and action truth
- keep derivation notebook-first

### P9C — Validation and Handback

- run the affected pack verifier/test slice
- commit and push the correction branch
- mark `M1` blocked only by fresh replay after this package closes green

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction-prompt.txt`

## Validation Strategy

- prove department-pack coverage parity in notebooks before extraction
- run:
  - `PYTHONPATH=src python3 scripts/ci/verify_communication_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_engineering_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_hr_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_marketing_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_operations_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_project_management_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_studio_operations_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_communication_department_pack_v1.py tests/test_engineering_department_pack_v1.py tests/test_hr_department_pack_v1.py tests/test_marketing_department_pack_v1.py tests/test_operations_department_pack_v1.py tests/test_project_management_department_pack_v1.py tests/test_studio_operations_department_pack_v1.py`
  - `pre-commit run --all-files`
  - `git diff --check`
- do not resume `M1` until this package is green, committed, and pushed

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] this package `status -> complete`

## Agent Constraints

- Do not push `development` from this package.
- Do not widen the correction beyond the affected department-pack parity boundary unless notebook proof shows an additional affected pack surface.
- Stop if the correction appears to require changes to the already truthful final registry, activated-surface, packaging, or post-H5 certification surfaces.
