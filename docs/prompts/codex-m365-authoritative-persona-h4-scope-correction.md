# MATHS Prompt: M365 Authoritative Persona H4 Scope Correction

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-h4-scope-correction:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-humanization-expansion`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — summarize the H3 result, the H4 `NO-GO` root cause, and the exact department-pack authority write set.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go".
3. **Call MCP `validate_action` before any mutating action** — obey the verdict and stop on red.
4. **Notebook first** — all department-pack count reconciliation and authority updates occur in notebooks first.
5. **Do not auto-advance to H4** — H4 needs its own approval packet and explicit "go" after H4S is green.

## MA Hardline Requirements

1. **Phase 0 — Intent definition first** — restate the department-pack scope-gap problem, the non-goals, required guarantees, success criteria, and determinism rules in the approval packet before any notebook work begins.
2. **Phases 1 through 4 — Formal proof chain first** — define the governing formula, calculus, lemmas, and executable invariants for the staged department-pack rebase before extraction.
3. **Phase 5 — Notebook development only** — model every department-pack count and authority transformation in notebooks first with deterministic assertions.
4. **Phase 6 — Scorecard gate** — require scorecard green before updating any department-pack authority surface.
5. **Phase 7 — Extraction parity** — extracted pack outputs must mirror the notebook-proven logic exactly.

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after H3 is green and the operator presents the approval packet and receives "go".

## Execution Rules

- Run checks `H4S-DEPARTMENT-PACK-REBASE-C0` -> `H4S-DEPARTMENT-PACK-REBASE-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:H4S-DEPARTMENT-PACK-REBASE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `H4S-DEPARTMENT-PACK-REBASE`
- Run ID: `m365-authoritative-persona-h4-scope-correction`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-h4-scope-correction:R1`
  - `plan:m365-authoritative-persona-h4-scope-correction:R2`
  - `plan:m365-authoritative-persona-h4-scope-correction:R3`
  - `plan:m365-authoritative-persona-h4-scope-correction:R4`
  - `plan:m365-authoritative-persona-h4-scope-correction:R5`
  - `plan:m365-authoritative-persona-h4-scope-correction:R6`
  - `plan:m365-authoritative-persona-h4-scope-correction:R7`

## Context

- Task name: `Correct H4 scope by rebasing the department-pack authority surface`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-registry-and-capability-map-rebase/m365-authoritative-persona-registry-and-capability-map-rebase.md`
  - `plans/m365-authoritative-persona-certification-and-count-rebase/m365-authoritative-persona-certification-and-count-rebase.md`
  - `registry/persona_registry_v2.yaml`
  - `registry/department_pack_*_v1.yaml`
- Allowlist:
  - `registry/department_pack_*_v1.yaml`
  - `docs/commercialization/m365-*-department-pack-v1.md`
  - `scripts/ci/verify_*_department_pack_v1.py`
  - `tests/test_*_department_pack_v1.py`
  - `notebooks/**`
  - `artifacts/scorecards/**`
- Denylist:
  - `registry/persona_certification_v1.yaml`
  - `registry/department_certification_v1.yaml`
  - `registry/enterprise_release_gate_v2.yaml`
  - `registry/activated_persona_surface_v1.yaml`
  - `docs/commercialization/m365-activated-persona-surface-v1.md`

## M - Model

- Problem: `H4 cannot truthfully rebase certification and count surfaces while the department-pack authority contracts still encode the old 39-persona distribution.`
- Goal: `Rebase the department-pack authority surface first so H4 can resume on a truthful dependency base.`
- Success criteria:
  - `All 10 department packs agree with the staged post-H3 department counts`
  - `No rebased department pack over-claims active or registry-backed coverage`
  - `Targeted department-pack verifiers and tests are green`
- Out of scope:
  - `certification-contract rebase`
  - `final active-surface rebase`
  - `activation`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `all 10 department-pack authorities are updated`
- Runtime/test evidence:
  - `targeted department-pack verifiers and tests pass`
- Governance evidence:
  - `Operations/EXECUTION_PLAN.md updated`
  - `Operations/ACTION_LOG.md updated`
  - `Operations/PROJECT_FILE_INDEX.md updated`
- Determinism evidence:
  - `repeated notebook/build steps reproduce the same pack counts`

## T - Tie

- GO criteria:
  - `all rebased department packs agree with persona_registry_v2.yaml`
  - `H4 is unblocked but not executed`
- NO-GO criteria:
  - `any department pack still encodes stale 39-persona-era counts`
  - `any rebased pack claims more active or registry-backed personas than the staged truth`

## H - Harness (ordered checks)

`H4S-DEPARTMENT-PACK-REBASE-C0` Preflight
- Verify H3 is green and H4 remains blocked.

`H4S-DEPARTMENT-PACK-REBASE-C1` Baseline mismatch inventory
- Capture current department-pack vs registry count mismatches.

`H4S-DEPARTMENT-PACK-REBASE-C2` Notebook count reconciliation
- Build the staged department-count model in notebooks first.

`H4S-DEPARTMENT-PACK-REBASE-C3` Notebook pack-boundary reconciliation
- Derive the department-pack authority updates in notebooks first.

`H4S-DEPARTMENT-PACK-REBASE-C4` Authority contract
- Verify all 10 pack authorities agree with the staged post-H3 department counts.

`H4S-DEPARTMENT-PACK-REBASE-C5` Anti-overclaim gate
- Fail if any rebased pack over-claims active or registry-backed coverage.

`H4S-DEPARTMENT-PACK-REBASE-C6` Execute targeted validations
- Run the targeted pack verifiers and tests.

`H4S-DEPARTMENT-PACK-REBASE-C7` Strict artifact validation
- Fail if any stale pack count remains in scope.

`H4S-DEPARTMENT-PACK-REBASE-C8` Deterministic replay
- Repeat the build and require identical outputs.

`H4S-DEPARTMENT-PACK-REBASE-C9` Hard gates
1. `git diff --check`
2. `targeted verifiers/tests`
3. `scorecard green`

`H4S-DEPARTMENT-PACK-REBASE-C10` Governance synchronization and final decision
- Update docs, commit, push, and emit GO/NO-GO.

## Output Contract

- Deliverables:
  - `rebased department-pack authorities`
  - `verification output`
  - `scorecard`
- Validation results:
  - `H4S-DEPARTMENT-PACK-REBASE-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:H4S-DEPARTMENT-PACK-REBASE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`
