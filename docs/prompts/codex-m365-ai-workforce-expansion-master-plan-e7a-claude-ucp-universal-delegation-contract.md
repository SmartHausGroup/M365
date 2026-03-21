# MATHS Prompt: E7A Claude to UCP Universal Delegation Contract

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-ai-workforce-expansion-master-plan:E7A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-WORKFORCE-E7A-C0` -> `M365-WORKFORCE-E7A-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-WORKFORCE-E7A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-WORKFORCE-E7A`
- Run ID: `claude-ucp-universal-delegation-contract`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-ai-workforce-expansion-master-plan:R1`
  - `plan:m365-ai-workforce-expansion-master-plan:R11`
  - `plan:m365-ai-workforce-expansion-master-plan:E7A`
- Invariant IDs in scope: `<define or reference during act execution>`
- Lemma IDs in scope: `<define or reference during act execution>`
- Owners: `product`, `engineering`, `MA`

## Context

- Task name: `Claude to UCP Universal Delegation Contract`
- Domain: `integration`
- Dependencies: `E7`
- Allowlist:
  - `plans/m365-ai-workforce-expansion-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `docs/prompts/codex-m365-ai-workforce-expansion-master-plan*`
  - `src/*`
  - `tests/*`
  - `registry/*`
  - `docs/commercialization/*`
  - `notebooks/*`
- Denylist:
  - `artifacts/certification/m365-v1-candidate-52ca494/* unless explicitly in scope`
  - `UCP/tenants/* unless the act explicitly targets tenant-contract changes`
  - `Any runtime or workload outside Microsoft 365 and UCP integration boundaries`

## M - Model

- Problem: `Claude / UCP Workforce Experience is not yet complete; the workforce cannot honestly claim complete M365 coverage until this act closes its defined gap.`
- Goal: `Define the top-level delegation contract between Claude, UCP, and the workforce runtime.`
- Success criteria:
  - `E7A` produces its declared artifacts or runtime changes without scope drift.
  - `E7A` updates plan and tracker state so the next dependency edge is explicit.
  - `E7A` leaves deterministic evidence paths and validation commands for replay.
- Out of scope:
  - `Declaring complete workforce coverage before the act-specific evidence exists.`
  - `Changing unrelated product boundaries or tenant state outside the act allowlist.`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `Artifacts created or updated for E7A exist with required metadata, status, and dependency fields.`
- Runtime/test evidence:
  - `Act-scoped validation commands for E7A are recorded with expected pass/fail semantics.`
- Governance evidence:
  - `Operations/ACTION_LOG.md, Operations/EXECUTION_PLAN.md, and Operations/PROJECT_FILE_INDEX.md are synchronized if state or artifacts change.`
- Determinism evidence:
  - `A fixed-state replay of the act leaves the same plan status, prompt inventory, and validation signatures for E7A.`

## T - Tie

- Dependency ties:
  - `E7 -> E7A may not claim GO unless predecessors are satisfied.`
  - `E7A -> downstream acts inherit its outputs and must stay blocked if E7A is NO-GO.`
- Known failure modes:
  - `Scope drift outside the act allowlist.`
  - `Prompt or tracker inventory mismatch.`
  - `Validation commands omitted or non-deterministic.`
- GO criteria:
  - `All M365-WORKFORCE-E7A-C0 through M365-WORKFORCE-E7A-C10 checks pass with required evidence.`
- NO-GO criteria:
  - `Any missing required artifact, failed hard gate, unresolved blocker, or replay mismatch.`

## H - Harness (ordered checks)

`M365-WORKFORCE-E7A-C0` Preflight

- Verify governance docs, plan refs, and prerequisite phase status.

`M365-WORKFORCE-E7A-C1` Baseline inventory

- Capture the current baseline for E7A, including artifact presence, phase status, and dependency state.

`M365-WORKFORCE-E7A-C2` Intent and boundary lock

- Confirm the exact objective, success criteria, and out-of-scope boundary for E7A.

`M365-WORKFORCE-E7A-C3` Implementation or specification step 1

- Apply the primary deterministic change required for E7A.

`M365-WORKFORCE-E7A-C4` Implementation or specification step 2

- Apply the secondary deterministic change required for E7A.

`M365-WORKFORCE-E7A-C5` Schema and contract validation

- Hard-fail on missing required keys, statuses, links, or metadata.

`M365-WORKFORCE-E7A-C6` Targeted validations

- Execute the act-scoped validation commands for E7A.

`M365-WORKFORCE-E7A-C7` Strict artifact validation

- Verify required paths exist and reflect the intended state only.

`M365-WORKFORCE-E7A-C8` Deterministic replay

- Repeat the fixed-state validation and require consistent outputs.

`M365-WORKFORCE-E7A-C9` Hard gates (strict order)

1. `Artifact presence and schema checks`
2. `Targeted act validation command(s)`
3. `git diff --check or approved equivalent`

`M365-WORKFORCE-E7A-C10` Governance synchronization and final decision

- Update required docs, synchronize status, and emit final GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `Missing prompt pair, missing tracker sync, or missing dependency state must force NO-GO.`
  - `Capability or scope claims that exceed the act evidence must force NO-GO.`
- Replay checks:
  - `The plan status, prompt inventory, and act-level validation outputs for E7A must remain stable across repeated runs on fixed repo state.`

## Output Contract

- Deliverables:
  - `E7A` artifacts and synchronized tracker state
  - `E7A` validation evidence
- Validation results:
  - `M365-WORKFORCE-E7A-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Residual risks:
  - `state any remaining blockers explicitly or use none`
- Final decision lines:
  - `GATE:M365-WORKFORCE-E7A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Missing required artifact(s), required fields, or required prompt pairs.
- Missing plan ref, governance acknowledgment, or approval gate.
- Scope drift outside the declared allowlist.
- Any failed hard gate or unresolved BLOCKED condition.
- Determinism replay mismatch for fixed repository state.
