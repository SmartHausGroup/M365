# Lemma L84 — M365 Authoritative Persona Post-H5 Department-Pack Coverage Parity Correction v1

## Statement

If the final post-H5 authoritative registry already marks the 20 promoted personas as
`registry-backed`, the shared department-pack runtime already fails closed on any declared
coverage or action mismatch, and the fresh `M1` replay is blocked only because 7
department-pack contracts still encode staged contract-only coverage, then the only truthful
bounded correction is to rebase those 7 department-pack contracts, docs, verifiers, and tests
to the same final registry-backed action surface while preserving the existing
`department.status` taxonomy required by downstream certification surfaces.

## Inputs

- `registry/persona_registry_v2.yaml`
- `registry/department_pack_communication_v1.yaml`
- `registry/department_pack_engineering_v1.yaml`
- `registry/department_pack_hr_v1.yaml`
- `registry/department_pack_marketing_v1.yaml`
- `registry/department_pack_operations_v1.yaml`
- `registry/department_pack_project_management_v1.yaml`
- `registry/department_pack_studio_operations_v1.yaml`
- `src/smarthaus_common/department_pack.py`
- `configs/generated/authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1_verification.json`

## Governing Formula

`P9_GO = BlockerProven AND FinalPackCoverageParity AND FinalPackActionParity AND FinalPackStateTruth AND PreservedDepartmentStatusTaxonomy AND DeterministicReplay`

where:

- `BlockerProven := fresh_M1_blocked_merge_commit = d194b94 AND mismatch_total = 20 AND affected_department_count = 7`
- `FinalPackCoverageParity := FOR ALL persona in affected packs, declared.coverage_status = registry.coverage_status`
- `FinalPackActionParity := FOR ALL persona in affected packs, declared.supported_actions = registry.allowed_actions`
- `FinalPackStateTruth := communication, engineering, hr, operations, project-management, and studio-operations default to ready without queue pressure; marketing remains blocked because 5 external personas are still planned`
- `PreservedDepartmentStatusTaxonomy := FOR ALL affected departments, department.status remains equal to the currently certified H4S taxonomy`
- `DeterministicReplay := repeated proof replay emits the same verification hash and the same target summaries`

## Proof Sketch

1. The final post-H5 authoritative registry already reports the 20 promoted personas as active,
   `registry-backed`, and action-bearing.
2. The shared department-pack runtime already enforces exact equality between each declared
   coverage/action surface and the authoritative registry, so no runtime change is required to
   expose the blocker.
3. The fresh blocked `M1` replay and the initial `L84` mismatch inventory prove that the only
   remaining inconsistency is the staged department-pack contract layer across 7 departments.
4. Reclassifying the 20 promoted personas to `registry-backed` and copying their action lists from
   the authoritative registry yields truthful pack summaries of:
   - communication `4 / 4 / 4 / 49 / ready`
   - engineering `8 / 8 / 8 / 65 / ready`
   - hr `2 / 2 / 2 / 10 / ready`
   - marketing `8 / 3 / 3 / 24 / blocked`
   - operations `10 / 10 / 10 / 85 / ready`
   - project-management `5 / 5 / 5 / 40 / ready`
   - studio-operations `9 / 9 / 9 / 61 / ready`
5. Marketing remains fail-closed because the 5 deferred external-platform personas still remain
   `planned` and `persona-contract-only`, which is the intended post-H5 exception.
6. The already-certified `department.status` taxonomy is preserved, so this correction does not
   reopen the downstream certification boundary that is already green.
7. Therefore `M1` can resume only after the affected department-pack authority, docs, verifiers,
   and tests all reconcile to this same final parity state.

## Machine Bindings

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
- `configs/generated/authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1_verification.json`
