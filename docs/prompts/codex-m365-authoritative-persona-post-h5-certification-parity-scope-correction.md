# MATHS Prompt: M365 Authoritative Persona Post-H5 Certification Parity Scope Correction

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-post-h5-certification-parity-scope-correction:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-post-h5-parity-correction`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — summarize the blocked local merge commit `a895678`, the `L82` scope-gap proof, the stale `34 / 25 / 298` certification boundary, and the truthful final `54 / 5 / 430` boundary already present elsewhere.
2. **Wait for explicit `go`** — do not begin correction execution until the operator confirms with `go`.
3. **Call MCP `validate_action` before every mutating action** — this includes notebook execution, file edits, tests, commit, and push.
4. **Notebook first** — all unified certification parity derivation and count fixes must be proven in notebooks first.
5. **Do not push `development`** — this package fixes the source-branch payload only and hands `M1` back a truthful branch for fresh merge replay.

## MA Hardline Requirements

1. **Phase 0 — Intent definition first** — restate the unified certification problem, boundaries, guarantees, success criteria, and determinism rules before notebook work begins.
2. **Phases 1 through 4 — Formula, calculus, lemmas, invariants** — define the final post-H5 persona, department, and release-gate parity formula and machine-enforced obligations before extraction.
3. **Phase 5 — Notebook development only** — prove the final certification and release-gate counts in notebooks first with deterministic assertions.
4. **Phase 6 — Scorecard gate** — require scorecard green before updating certification or release-gate runtime surfaces.
5. **Phase 7 — Extraction parity** — extracted YAML/docs/verifier/test surfaces must mirror the notebook-proven final truth exactly.

## Execution Rules

- Run checks `POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C0` -> `POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION`
- Run ID: `m365-authoritative-persona-post-h5-certification-parity-scope-correction`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-post-h5-certification-parity-scope-correction:R1`
  - `plan:m365-authoritative-persona-post-h5-certification-parity-scope-correction:R2`
  - `plan:m365-authoritative-persona-post-h5-certification-parity-scope-correction:R3`
  - `plan:m365-authoritative-persona-post-h5-certification-parity-scope-correction:R4`
  - `plan:m365-authoritative-persona-post-h5-certification-parity-scope-correction:R5`
  - `plan:m365-authoritative-persona-post-h5-certification-parity-scope-correction:R6`
  - `plan:m365-authoritative-persona-post-h5-certification-parity-scope-correction:R7`
- Invariant IDs in scope: `L83-derived invariants`
- Lemma IDs in scope: `L83`
- Owners: `product`, `engineering`, `MA`

## Context

- Task name: `Correct the post-H5 parity package scope so M1 can be truthfully unblocked`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-post-h5-parity-correction/m365-authoritative-persona-post-h5-parity-correction.md`
  - `plans/m365-authoritative-persona-humanization-merge-to-development/m365-authoritative-persona-humanization-merge-to-development.md`
  - `notebooks/m365/INV-M365-CD-authoritative-persona-post-h5-parity-correction-v1.ipynb`
  - `configs/generated/authoritative_persona_post_h5_parity_correction_v1_verification.json`
  - local blocked merge evidence `development @ a895678`
- Allowlist:
  - `registry/persona_certification_v1.yaml`
  - `registry/department_certification_v1.yaml`
  - `registry/enterprise_release_gate_v2.yaml`
  - `docs/commercialization/m365-persona-certification-v1.md`
  - `docs/commercialization/m365-department-certification-v1.md`
  - `docs/commercialization/m365-enterprise-release-gate-v2.md`
  - `scripts/ci/verify_persona_certification_v1.py`
  - `scripts/ci/verify_department_certification_v1.py`
  - `scripts/ci/verify_enterprise_release_gate_v2.py`
  - `tests/test_persona_certification_v1.py`
  - `tests/test_department_certification_v1.py`
  - `tests/test_enterprise_release_gate_v2.py`
  - `notebooks/**`
  - `docs/ma/lemmas/**`
  - `invariants/lemmas/**`
  - `artifacts/scorecards/**`
  - `configs/generated/authoritative_persona_post_h5_certification_parity_scope_correction_v1_verification.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `registry/persona_registry_v2.yaml`
  - `registry/activated_persona_surface_v1.yaml`
  - `registry/workforce_packaging_v1.yaml`
  - `registry/persona_capability_map.yaml`
  - `registry/agents.yaml`
  - `registry/ai_team.json`
  - `development push`
  - `staging/main/tag work`

## M - Model

- Problem: `The final active workforce truth is already at 59 / 54 / 5 and 430 actions, but persona certification, department certification, and the enterprise release gate still claim the staged pre-H5 34 / 25 and 298-action state.`
- Goal: `Rebase the stale certification boundary to the final post-H5 truth without changing the already truthful final registry, activated-surface, or packaging surfaces.`
- Success criteria:
  - `persona_certification_v1.yaml reflects 59 total / 54 active / 5 planned / 54 registry-backed / 5 contract-only`
  - `department_certification_v1.yaml reflects 10 departments / 59 total / 54 active / 5 planned / 54 registry-backed / 5 contract-only`
  - `enterprise_release_gate_v2.yaml reflects 59 certified / 54 active certified / 5 planned certified / 430 routed actions`
  - `targeted verifiers/tests plus pre-commit are green`
  - `M1 is unblocked for fresh merge replay`
- Out of scope:
  - `push development`
  - `change registry/persona_registry_v2.yaml`
  - `change activated or packaging final-state surfaces`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `stale persona, department, and release-gate contracts are updated to final post-H5 parity`
- Runtime/test evidence:
  - `persona certification, department certification, and enterprise release-gate verifiers/tests pass`
- Governance evidence:
  - `M1 remains blocked until this correction is green`
  - `validate_action` is used before every mutating step`
- Determinism evidence:
  - `repeated notebook replays yield the same final parity counts`

## T - Tie

- Dependency ties:
  - `H5 final truth remains authoritative`
  - `L82 scope-gap proof must remain true before widening this package`
  - `this correction must close before M1 may be retried`
  - `notebooks must pass before extraction`
  - `validation must pass before commit and push`
- Known failure modes:
  - `the stale boundary extends beyond persona certification, department certification, and enterprise release gate`
  - `the correction tries to mutate already truthful final registry or packaging surfaces`
  - `verifiers/tests still encode staged pre-H5 counts after extraction`
- GO criteria:
  - `final certification surfaces match the already truthful 59 / 54 / 5 / 430 state`
  - `targeted validation is green`
- NO-GO criteria:
  - `any parity drift remains`
  - `any out-of-scope surface must change`
  - `development push is attempted from this package`

## H - Harness (ordered checks)

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C0` Preflight

- Read governance docs and confirm this scope-correction package is the active next act.

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C1` Blocker inventory

- Capture the `L82` scope-gap proof, the stale-vs-final certification matrix, and the blocked local merge evidence.

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C2` Governance gate

- Run `validate_action` before every mutating action and stop on red.

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C3` MA intent and formula

- Define the final unified certification formula for persona, department, and release-gate surfaces.

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C4` Lemmas and invariants

- Publish `L83` and the executable invariant metadata for the final unified certification boundary.

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C5` Notebook proof replay

- Derive the unified certification correction in notebooks and require deterministic replay.

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C6` Extraction

- Update only the stale certification/release-gate surfaces, docs, verifiers, and tests.

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C7` Targeted validation

- Run:
  - `python3 scripts/ci/verify_persona_certification_v1.py`
  - `python3 scripts/ci/verify_department_certification_v1.py`
  - `python3 scripts/ci/verify_enterprise_release_gate_v2.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_persona_certification_v1.py tests/test_department_certification_v1.py tests/test_enterprise_release_gate_v2.py`

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C8` Hard gates

- Run:
  - `pre-commit run --all-files`
  - `git diff --check`

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C9` Governance synchronization

- Update trackers to show that M1 is blocked by this package until green, then becomes eligible for fresh merge replay only after package closeout.

`POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C10` Commit, push, and final decision

- Commit and push the correction branch only if all gates are green, then emit GO or NO-GO and stop.

## Output Contract

- Deliverables:
  - `corrected persona, department, and release-gate certification artifacts`
  - `L83 proof chain`
  - `verification output`
- Validation results:
  - `POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:POST-H5-CERTIFICATION-PARITY-SCOPE-CORRECTION STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Missing approval packet or explicit `go`.
- Any governance rejection for notebook execution, tests, commit, or push.
- Any requirement to modify already truthful final registry, activated-surface, or packaging surfaces.
- Any failed verifier, pytest, pre-commit, or `git diff --check` gate.
- Any attempt to push `development` from this package.
