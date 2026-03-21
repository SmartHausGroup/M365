# MATHS Prompt: E0A Department and Persona Census

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-ai-workforce-expansion-master-plan:E0A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-WORKFORCE-E0A-C0` -> `M365-WORKFORCE-E0A-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-WORKFORCE-E0A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-WORKFORCE-E0A`
- Run ID: `department-persona-census`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-ai-workforce-expansion-master-plan:R1`
  - `plan:m365-ai-workforce-expansion-master-plan:R2`
  - `plan:m365-ai-workforce-expansion-master-plan:E0A`
- Invariant IDs in scope: `<define or reference during act execution>`
- Lemma IDs in scope: `<define or reference during act execution>`
- Owners: `product`, `engineering`, `MA`

## Context

- Task name: `Department and Persona Census`
- Domain: `docs`
- Dependencies: `E0`
- Allowlist:
  - `registry/ai_team.json`
  - `registry/agents.yaml`
  - `plans/m365-ai-workforce-expansion-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `docs/prompts/codex-m365-ai-workforce-expansion-master-plan*`
  - `docs/commercialization/*`
  - `docs/prompts/*`
  - `plans/*`
- Denylist:
  - `artifacts/certification/m365-v1-candidate-52ca494/* unless explicitly in scope`
  - `UCP/tenants/* unless the act explicitly targets tenant-contract changes`
  - `Any runtime or workload outside Microsoft 365 and UCP integration boundaries`

## M - Model

- Problem: `Universe Definition and Boundary Lock is not yet complete; the workforce cannot honestly claim complete M365 coverage until this act closes its defined gap.`
- Goal: `Lock the authoritative department roster and all digital-employee personas that the workforce must support.`
- Success criteria:
  - `E0A` produces its declared artifacts or runtime changes without scope drift.
  - `E0A` updates plan and tracker state so the next dependency edge is explicit.
  - `E0A` leaves deterministic evidence paths and validation commands for replay.
  - `The authoritative roster resolves to 39 personas across 10 departments and every roster agent ID resolves in registry/agents.yaml.`
- Out of scope:
  - `Declaring complete workforce coverage before the act-specific evidence exists.`
  - `Changing unrelated product boundaries or tenant state outside the act allowlist.`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `Artifacts created or updated for E0A exist with required metadata, status, and dependency fields.`
- Runtime/test evidence:
  - `Act-scoped validation commands for E0A are recorded with expected pass/fail semantics.`
- Governance evidence:
  - `Operations/ACTION_LOG.md, Operations/EXECUTION_PLAN.md, and Operations/PROJECT_FILE_INDEX.md are synchronized if state or artifacts change.`
- Determinism evidence:
  - `A fixed-state replay of the act leaves the same plan status, prompt inventory, and validation signatures for E0A.`

## T - Tie

- Dependency ties:
  - `E0 -> E0A may not claim GO unless predecessors are satisfied.`
  - `E0A -> downstream acts inherit its outputs and must stay blocked if E0A is NO-GO.`
- Known failure modes:
  - `Scope drift outside the act allowlist.`
  - `Prompt or tracker inventory mismatch.`
  - `Validation commands omitted or non-deterministic.`
- GO criteria:
  - `All M365-WORKFORCE-E0A-C0 through M365-WORKFORCE-E0A-C10 checks pass with required evidence.`
- NO-GO criteria:
  - `Any missing required artifact, failed hard gate, unresolved blocker, or replay mismatch.`

## H - Harness (ordered checks)

`M365-WORKFORCE-E0A-C0` Preflight

- Verify governance docs, plan refs, and prerequisite phase status.

`M365-WORKFORCE-E0A-C1` Baseline inventory

- Capture the current baseline for E0A, including artifact presence, phase status, and dependency state.

`M365-WORKFORCE-E0A-C2` Intent and boundary lock

- Confirm the exact objective, success criteria, and out-of-scope boundary for E0A.

`M365-WORKFORCE-E0A-C3` Implementation or specification step 1

- Apply the primary deterministic change required for E0A.

`M365-WORKFORCE-E0A-C4` Implementation or specification step 2

- Apply the secondary deterministic change required for E0A.

`M365-WORKFORCE-E0A-C5` Schema and contract validation

- Hard-fail on missing required keys, statuses, links, or metadata.

`M365-WORKFORCE-E0A-C6` Targeted validations

- Execute the act-scoped validation commands for E0A.

`M365-WORKFORCE-E0A-C7` Strict artifact validation

- Verify required paths exist and reflect the intended state only.

`M365-WORKFORCE-E0A-C8` Deterministic replay

- Repeat the fixed-state validation and require consistent outputs.

`M365-WORKFORCE-E0A-C9` Hard gates (strict order)

1. `Artifact presence and schema checks`
2. `Targeted act validation command(s)`
3. `git diff --check or approved equivalent`

`M365-WORKFORCE-E0A-C10` Governance synchronization and final decision

- Update required docs, synchronize status, and emit final GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `Missing prompt pair, missing tracker sync, or missing dependency state must force NO-GO.`
  - `Capability or scope claims that exceed the act evidence must force NO-GO.`
- Replay checks:
  - `The plan status, prompt inventory, and act-level validation outputs for E0A must remain stable across repeated runs on fixed repo state.`

## Output Contract

- Deliverables:
  - `E0A` artifacts and synchronized tracker state
  - `E0A` validation evidence
- Validation results:
  - `M365-WORKFORCE-E0A-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Residual risks:
  - `state any remaining blockers explicitly or use none`
- Final decision lines:
  - `GATE:M365-WORKFORCE-E0A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Missing required artifact(s), required fields, or required prompt pairs.
- Missing plan ref, governance acknowledgment, or approval gate.
- Scope drift outside the declared allowlist.
- Any failed hard gate or unresolved BLOCKED condition.
- Determinism replay mismatch for fixed repository state.
