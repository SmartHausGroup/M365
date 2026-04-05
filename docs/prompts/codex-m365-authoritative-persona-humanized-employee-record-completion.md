# MATHS Prompt: M365 Authoritative Persona Humanized Employee Record Completion

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-humanized-employee-record-completion:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-humanization-expansion`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — summarize the H1 outcome, the bounded metadata contract, the record artifact surface, and the intended write set.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go".
3. **Call MCP `validate_action` before any mutating action** — obey the verdict and stop on red.
4. **Notebook first** — all H2 iteration occurs in notebooks first; no direct extraction into runtime or authoritative registries.
5. **Do not auto-advance to H3** — H3 needs its own approval packet and explicit "go".

## MA Hardline Requirements

1. **Phase 0 — Intent definition first** — restate what is being built, why, problem boundaries, required guarantees, success criteria, and determinism rules in the approval packet before any notebook work begins.
2. **Phases 1 through 4 — Formal proof chain first** — define the governing formula, calculus, lemmas, and executable invariants before extracting any authority artifact.
3. **Phase 5 — Notebook development only** — implement and iterate in notebooks first, with deterministic assertions immediately after each atomic behavior.
4. **Phase 6 — Scorecard gate** — require scorecard green before any extraction.
5. **Phase 7 — Extraction parity** — any extracted artifact must match the notebook-proven logic exactly.

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after H1 is green and the operator presents the approval packet and receives "go".

## Execution Rules

- Run checks `H2-EMPLOYEE-RECORDS-C0` -> `H2-EMPLOYEE-RECORDS-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:H2-EMPLOYEE-RECORDS STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `H2-EMPLOYEE-RECORDS`
- Run ID: `m365-authoritative-persona-humanized-employee-record-completion`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-humanized-employee-record-completion:R1`
  - `plan:m365-authoritative-persona-humanized-employee-record-completion:R2`
  - `plan:m365-authoritative-persona-humanized-employee-record-completion:R3`
  - `plan:m365-authoritative-persona-humanized-employee-record-completion:R4`
  - `plan:m365-authoritative-persona-humanized-employee-record-completion:R5`
  - `plan:m365-authoritative-persona-humanized-employee-record-completion:R6`

## Context

- Task name: `Create authoritative employee records for the 20 promoted personas`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-census-and-department-model-decision/m365-authoritative-persona-census-and-department-model-decision.md`
  - `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.md`
- Allowlist:
  - `registry/authoritative_digital_employee_records_v1.yaml`
  - `docs/commercialization/m365-authoritative-digital-employee-records-v1.md`
  - `scripts/ci/verify_authoritative_digital_employee_records_v1.py`
  - `tests/test_authoritative_digital_employee_records_v1.py`
  - `notebooks/**`
  - `artifacts/scorecards/**`
  - `configs/generated/**`
- Denylist:
  - `registry/ai_team.json`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
  - `registry/agents.yaml`
  - `src/**`

## M - Model

- Problem: `The 20 promoted personas do not yet have a deterministic authoritative employee-record artifact.`
- Goal: `Create one bounded employee-record authority surface with complete fields and chain-of-command bindings.`
- Success criteria:
  - `All 20 promoted personas have complete required fields.`
  - `Only working_style, communication_style, and decision_style are used for personality-style metadata.`
  - `Manager and escalation_owner are explicit and non-empty for every promoted persona.`
- Out of scope:
  - `Registry rebases`
  - `Activation`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `authoritative_digital_employee_records_v1.yaml exists and contains 20 records`
- Runtime/test evidence:
  - `targeted verifier and tests pass`
- Governance evidence:
  - `Operations/EXECUTION_PLAN.md updated`
  - `Operations/ACTION_LOG.md updated`
  - `Operations/PROJECT_FILE_INDEX.md updated`
- Determinism evidence:
  - `repeated notebook/build steps produce the same employee-record artifact`

## T - Tie

- GO criteria:
  - `All required fields are complete and bounded`
  - `Notebook evidence is green`
  - `Targeted tests pass`
- NO-GO criteria:
  - `Any promoted persona record is incomplete`
  - `Any freeform personality field appears`

## H - Harness (ordered checks)

`H2-EMPLOYEE-RECORDS-C0` Preflight
- Verify H1 is green and governance docs are current.

`H2-EMPLOYEE-RECORDS-C1` Baseline inventory
- Re-read the H1 mapping and required-field contract.

`H2-EMPLOYEE-RECORDS-C2` Notebook field matrix
- Build the 20-persona field matrix in notebooks first.

`H2-EMPLOYEE-RECORDS-C3` Notebook artifact generation
- Generate the employee-record artifact from notebook-backed logic.

`H2-EMPLOYEE-RECORDS-C4` Schema contract
- Verify all required fields and bounded metadata constraints.

`H2-EMPLOYEE-RECORDS-C5` Chain-of-command gate
- Verify manager and escalation-owner bindings are explicit.

`H2-EMPLOYEE-RECORDS-C6` Execute targeted validations
- Run the targeted verifier and tests.

`H2-EMPLOYEE-RECORDS-C7` Strict artifact validation
- Fail if any record is incomplete or any freeform personality field appears.

`H2-EMPLOYEE-RECORDS-C8` Deterministic replay
- Repeat the build and require identical outputs.

`H2-EMPLOYEE-RECORDS-C9` Hard gates
1. `git diff --check`
2. `targeted verifier/tests`
3. `scorecard green`

`H2-EMPLOYEE-RECORDS-C10` Governance synchronization and final decision
- Update docs, commit, push, and emit GO/NO-GO.

## Output Contract

- Deliverables:
  - `employee record artifact`
  - `verification output`
  - `scorecard`
- Validation results:
  - `H2-EMPLOYEE-RECORDS-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:H2-EMPLOYEE-RECORDS STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`
