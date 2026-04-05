# MATHS Prompt: M365 Authoritative Persona Certification and Count Rebase

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-certification-and-count-rebase:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-humanization-expansion`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — summarize the H4S result, the staged `59 / 10 / 34 / 25` truth, and the exact count-surface write set.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go".
3. **Call MCP `validate_action` before any mutating action** — obey the verdict and stop on red.
4. **Notebook first** — all count and certification reconciliations occur in notebooks first.
5. **Do not auto-advance to H5** — H5 needs its own approval packet and explicit "go".

## MA Hardline Requirements

1. **Phase 0 — Intent definition first** — restate the staged count-rebase problem, boundaries, guarantees, success criteria, and determinism rules in the approval packet before any notebook work begins.
2. **Phases 1 through 4 — Formal proof chain first** — define the governing formula, calculus, lemmas, and executable invariants for the staged certification and count truth before extraction.
3. **Phase 5 — Notebook development only** — derive every count and certification update in notebooks first with deterministic assertions.
4. **Phase 6 — Scorecard gate** — require scorecard green before changing certification or commercialization count surfaces.
5. **Phase 7 — Extraction parity** — extracted count and certification outputs must mirror the notebook-proven logic exactly.

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after H4S is green and pushed and the operator presents the approval packet and receives "go".

## Execution Rules

- Run checks `H4-COUNT-REBASE-C0` -> `H4-COUNT-REBASE-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:H4-COUNT-REBASE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `H4-COUNT-REBASE`
- Run ID: `m365-authoritative-persona-certification-and-count-rebase`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-certification-and-count-rebase:R1`
  - `plan:m365-authoritative-persona-certification-and-count-rebase:R2`
  - `plan:m365-authoritative-persona-certification-and-count-rebase:R3`
  - `plan:m365-authoritative-persona-certification-and-count-rebase:R4`
  - `plan:m365-authoritative-persona-certification-and-count-rebase:R5`
  - `plan:m365-authoritative-persona-certification-and-count-rebase:R6`

## Context

- Task name: `Rebase certification and count truth to the staged post-H4S state`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-h4-scope-correction/m365-authoritative-persona-h4-scope-correction.md`
  - `registry/persona_registry_v2.yaml`
- Allowlist:
  - `registry/persona_certification_v1.yaml`
  - `registry/department_certification_v1.yaml`
  - `registry/enterprise_release_gate_v2.yaml`
  - `docs/commercialization/m365-persona-certification-v1.md`
  - `docs/commercialization/m365-department-certification-v1.md`
  - `docs/commercialization/m365-persona-registry-v2.md`
  - `docs/commercialization/m365-department-persona-census.md`
  - `scripts/ci/verify_persona_certification_v1.py`
  - `scripts/ci/verify_department_certification_v1.py`
  - `tests/test_persona_certification_v1.py`
  - `tests/test_department_certification_v1.py`
  - `tests/test_persona_registry_v2.py`
  - `notebooks/**`
- Denylist:
  - `registry/activated_persona_surface_v1.yaml`
  - `docs/commercialization/m365-activated-persona-surface-v1.md`
  - `registry/workforce_packaging_v1.yaml`

## M - Model

- Problem: `Certification and commercialization surfaces still enforce the old 39-persona authoritative truth even after H3 rebased the authoritative roster, and H4 may only begin once H4S has corrected the department-pack dependency surface.`
- Goal: `Rebase them to the truthful staged post-H4S state without claiming final activation before H5.`
- Success criteria:
  - `All scoped surfaces agree on 59 total personas and 10 departments`
  - `All scoped surfaces agree on 34 active and 25 planned until H5`
  - `Targeted verifiers and tests are green`
- Out of scope:
  - `final active-surface rebase`
  - `activation`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `all scoped count/certification surfaces are updated`
- Runtime/test evidence:
  - `targeted verifiers and tests pass`
- Governance evidence:
  - `Operations/EXECUTION_PLAN.md updated`
  - `Operations/ACTION_LOG.md updated`
  - `Operations/PROJECT_FILE_INDEX.md updated`
- Determinism evidence:
  - `repeated notebook/build steps reproduce the same count outputs`

## T - Tie

- GO criteria:
  - `59 total / 10 departments / 34 active / 25 planned is consistent everywhere in scope`
  - `No scoped surface over-claims final activation`
- NO-GO criteria:
  - `Any stale 39-persona authoritative claim remains in scope`
  - `Any scoped surface claims more than 34 active before H5`

## H - Harness (ordered checks)

`H4-COUNT-REBASE-C0` Preflight
- Verify H4S is green and pushed and governance docs are current.

`H4-COUNT-REBASE-C1` Baseline inventory
- Capture current count claims across the scoped surfaces.

`H4-COUNT-REBASE-C2` Notebook count reconciliation
- Build the staged truth model in notebooks first.

`H4-COUNT-REBASE-C3` Notebook certification reconciliation
- Derive the certification and documentation updates in notebooks first.

`H4-COUNT-REBASE-C4` Count contract
- Verify 59 total, 10 departments, 34 active, and 25 planned across the scoped surfaces.

`H4-COUNT-REBASE-C5` Anti-overclaim gate
- Fail if any scoped surface claims final activation prematurely.

`H4-COUNT-REBASE-C6` Execute targeted validations
- Run the targeted verifiers and tests.

`H4-COUNT-REBASE-C7` Strict artifact validation
- Fail if any stale count remains in scope.

`H4-COUNT-REBASE-C8` Deterministic replay
- Repeat the build and require identical outputs.

`H4-COUNT-REBASE-C9` Hard gates
1. `git diff --check`
2. `targeted verifiers/tests`
3. `scorecard green`

`H4-COUNT-REBASE-C10` Governance synchronization and final decision
- Update docs, commit, push, and emit GO/NO-GO.

## Output Contract

- Deliverables:
  - `rebased certification/count surfaces`
  - `verification output`
  - `scorecard`
- Validation results:
  - `H4-COUNT-REBASE-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:H4-COUNT-REBASE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`
