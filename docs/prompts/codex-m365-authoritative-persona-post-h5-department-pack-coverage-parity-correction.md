# MATHS Prompt: M365 Authoritative Persona Post-H5 Department-Pack Coverage Parity Correction

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-humanization-merge-to-development`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — summarize the fresh blocked merge commit `d194b94`, the `L84` scope-gap proof, the `20` coverage mismatches across `7` department packs, and the already-truthful final post-H5 registry boundary.
2. **Wait for explicit `go`** — do not begin correction execution until the operator confirms with `go`.
3. **Call MCP `validate_action` before every mutating action** — this includes notebook execution, file edits, tests, commit, and push.
4. **Notebook first** — all department-pack coverage and action parity derivation must be proven in notebooks first.
5. **Do not push `development`** — this package repairs the source-branch payload only and hands `M1` back a truthful branch for fresh merge replay.

## MA Hardline Requirements

1. **Phase 0 — Intent definition first** — restate the department-pack parity problem, boundaries, guarantees, success criteria, and determinism rules before notebook work begins.
2. **Phases 1 through 4 — Formula, calculus, lemmas, invariants** — define the final department-pack coverage/action parity formula and machine-enforced obligations before extraction.
3. **Phase 5 — Notebook development only** — prove the affected-pack final state in notebooks first with deterministic assertions.
4. **Phase 6 — Scorecard gate** — require scorecard green before updating pack authority or runtime surfaces.
5. **Phase 7 — Extraction parity** — extracted YAML/docs/verifier/test surfaces must mirror the notebook-proven final truth exactly.

## Execution Rules

- Run checks `POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C0` -> `POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION`
- Run ID: `m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R1`
  - `plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R2`
  - `plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R3`
  - `plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R4`
  - `plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R5`
  - `plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R6`
  - `plan:m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction:R7`
- Invariant IDs in scope: `L84-derived invariants`
- Lemma IDs in scope: `L84`
- Owners: `product`, `engineering`, `MA`

## Context

- Task name: `Correct the post-H5 department-pack authority surface so fresh M1 replay can pass`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-humanization-merge-to-development/m365-authoritative-persona-humanization-merge-to-development.md`
  - `plans/m365-authoritative-persona-post-h5-certification-parity-scope-correction/m365-authoritative-persona-post-h5-certification-parity-scope-correction.md`
  - `notebooks/m365/INV-M365-CF-authoritative-persona-post-h5-department-pack-coverage-parity-correction-v1.ipynb`
  - `configs/generated/authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1_verification.json`
  - local blocked merge evidence `development @ d194b94`
- Allowlist:
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
  - `configs/generated/*_department_pack_v1_verification.json`
  - `notebooks/**`
  - `docs/ma/lemmas/**`
  - `invariants/lemmas/**`
  - `artifacts/scorecards/**`
  - `configs/generated/authoritative_persona_post_h5_department_pack_coverage_parity_correction_v1_verification.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
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
  - `staging/main/tag work`

## M - Model

- Problem: `The final active workforce truth already marks the 20 promoted personas as registry-backed, but 7 department-pack contracts still declare them persona-contract-only with zero actions, so the fresh M1 replay fails before the pack summary slice can build.`
- Goal: `Rebase the affected department-pack contracts to the final post-H5 coverage/action truth without changing already truthful registry, activation, packaging, or certification surfaces.`
- Success criteria:
  - `all 20 promoted personas in affected department packs reconcile to registry-backed coverage where the authoritative registry already says registry-backed`
  - `supported_actions for affected registry-backed pack personas are no longer empty`
  - `affected department-pack docs, verifiers, and tests match the final post-H5 pack truth`
  - `affected department-pack verifier/test slice plus pre-commit are green`
  - `M1 is unblocked for a fresh merge replay`
- Out of scope:
  - `push development`
  - `change registry/persona_registry_v2.yaml`
  - `change activated, packaging, or post-H5 certification/release-gate surfaces`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `affected department-pack authority YAML files no longer lag the final registry coverage truth`
- Runtime/test evidence:
  - `affected department-pack verifiers and tests pass`
- Governance evidence:
  - `M1 remains blocked until this correction is green`
  - `validate_action is used before every mutating step`
- Determinism evidence:
  - `repeated notebook replay yields the same mismatch inventory and final parity counts`

## T - Tie

- Dependency ties:
  - `H5 final truth remains authoritative`
  - `L83 post-H5 certification parity remains authoritative`
  - `L84 scope-gap proof must remain true before widening this package`
  - `this correction must close before M1 may be retried`
  - `notebooks must pass before extraction`
  - `validation must pass before commit and push`
- Known failure modes:
  - `additional department-pack surfaces beyond the 7 affected packs are stale`
  - `the correction tries to mutate already truthful registry or certification surfaces`
  - `pack tests/verifiers still encode staged contract-only coverage after extraction`
- GO criteria:
  - `final affected department-pack surfaces match the authoritative registry coverage truth`
  - `targeted validation is green`
- NO-GO criteria:
  - `any affected pack still mismatches the registry`
  - `any out-of-scope surface must change`
  - `development push is attempted from this package`

## H - Harness (ordered checks)

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C0` Preflight

- Read governance docs and confirm this blocker package is the active next act.

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C1` Blocker inventory

- Capture the `L84` scope-gap proof, the fresh blocked merge evidence, and the exact affected-pack mismatch matrix.

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C2` Governance gate

- Run `validate_action` before every mutating action and stop on red.

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C3` MA intent and formula

- Define the final pack coverage/action parity formula for the affected department packs.

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C4` Lemmas and invariants

- Publish `L84`-derived invariants for the final affected-pack parity boundary.

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C5` Notebook proof replay

- Derive the affected-pack correction in notebooks and require deterministic replay.

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C6` Extraction

- Update only the affected department-pack authority, docs, verifiers, tests, and bounded runtime parity logic if required.

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C7` Targeted validation

- Run:
  - `PYTHONPATH=src python3 scripts/ci/verify_communication_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_engineering_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_hr_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_marketing_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_operations_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_project_management_department_pack_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_studio_operations_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_communication_department_pack_v1.py tests/test_engineering_department_pack_v1.py tests/test_hr_department_pack_v1.py tests/test_marketing_department_pack_v1.py tests/test_operations_department_pack_v1.py tests/test_project_management_department_pack_v1.py tests/test_studio_operations_department_pack_v1.py`

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C8` Hard gates

- Run:
  - `pre-commit run --all-files`
  - `git diff --check`

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C9` Governance synchronization

- Update trackers to show that M1 is blocked by this package until green, then becomes eligible for fresh merge replay only after package closeout.

`POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C10` Commit, push, and final decision

- Commit and push the correction branch only if all gates are green, then emit GO or NO-GO and stop.

## Output Contract

- Deliverables:
  - `corrected affected department-pack artifacts`
  - `L84 proof chain`
  - `verification output`
- Validation results:
  - `POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:POST-H5-DEPARTMENT-PACK-COVERAGE-PARITY-CORRECTION STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Missing approval packet or explicit `go`.
- Any governance rejection for notebook execution, tests, commit, or push.
- Any requirement to modify already truthful final registry, activated-surface, packaging, or post-H5 certification surfaces.
- Any failed verifier, pytest, pre-commit, or `git diff --check` gate.
- Any attempt to push `development` from this package.
