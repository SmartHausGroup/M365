# MATHS Prompt: M365 Authoritative Persona Activation Gate Closeout

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-activation-gate-closeout:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-humanization-expansion`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — summarize the H4 result, the final `59 total / 54 active / 5 planned` target, and the activation-gate prerequisites for all `20` promoted personas.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go".
3. **Call MCP `validate_action` before any mutating action** — obey the verdict and stop on red.
4. **Notebook first** — all activation-gate checks and final count truth occur in notebooks first.
5. **Final phase discipline** — this is the last child phase; close it truthfully or stop fail-closed.

## MA Hardline Requirements

1. **Phase 0 — Intent definition first** — restate the final activation-gate problem, boundaries, guarantees, success criteria, and determinism rules in the approval packet before any notebook work begins.
2. **Phases 1 through 4 — Formal proof chain first** — define the governing formula, calculus, lemmas, and executable invariants for final activation before extraction.
3. **Phase 5 — Notebook development only** — verify prerequisites and derive final-state transforms in notebooks first with deterministic assertions.
4. **Phase 6 — Scorecard gate** — require scorecard green before activating promoted personas or publishing final count truth.
5. **Phase 7 — Extraction parity** — extracted final registry and active-surface outputs must mirror the notebook-proven logic exactly.

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after H4 is green and the operator presents the approval packet and receives "go".

## Execution Rules

- Run checks `H5-ACTIVATION-CLOSEOUT-C0` -> `H5-ACTIVATION-CLOSEOUT-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:H5-ACTIVATION-CLOSEOUT STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `H5-ACTIVATION-CLOSEOUT`
- Run ID: `m365-authoritative-persona-activation-gate-closeout`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-activation-gate-closeout:R1`
  - `plan:m365-authoritative-persona-activation-gate-closeout:R2`
  - `plan:m365-authoritative-persona-activation-gate-closeout:R3`
  - `plan:m365-authoritative-persona-activation-gate-closeout:R4`
  - `plan:m365-authoritative-persona-activation-gate-closeout:R5`
  - `plan:m365-authoritative-persona-activation-gate-closeout:R6`

## Context

- Task name: `Close the fail-closed activation gate and publish the final active surface`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-certification-and-count-rebase/m365-authoritative-persona-certification-and-count-rebase.md`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
- Allowlist:
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
  - `registry/activated_persona_surface_v1.yaml`
  - `registry/workforce_packaging_v1.yaml`
  - `docs/commercialization/m365-activated-persona-surface-v1.md`
  - `docs/commercialization/m365-workforce-packaging-v1.md`
  - `scripts/ci/build_persona_registry_v2.py`
  - `scripts/ci/verify_persona_registry_v2.py`
  - `scripts/ci/verify_activated_persona_surface_v1.py`
  - `scripts/ci/verify_workforce_packaging_v1.py`
  - `tests/test_persona_registry_v2.py`
  - `tests/test_activated_persona_surface_v1.py`
  - `tests/test_workforce_packaging_v1.py`
  - `notebooks/**`
- Denylist:
  - `registry/agents.yaml`
  - `registry/ai_team.json`

## M - Model

- Problem: `The 20 promoted personas remain staged and non-active until the final activation gate closes.`
- Goal: `Activate all 20 only after every fail-closed prerequisite is green and publish the truthful final active-surface state.`
- Success criteria:
  - `All 20 promoted personas satisfy the activation prerequisites`
  - `persona_registry_v2.yaml ends at 59 total / 54 active / 5 planned`
  - `activated_persona_surface_v1.yaml ends at 54 active / 5 deferred external`
- Out of scope:
  - `changing registry/agents.yaml`
  - `adding new personas beyond the governed 20`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `final registry and active-surface artifacts are updated`
- Runtime/test evidence:
  - `targeted builder/verifier/tests pass`
- Governance evidence:
  - `Operations/EXECUTION_PLAN.md updated`
  - `Operations/ACTION_LOG.md updated`
  - `Operations/PROJECT_FILE_INDEX.md updated`
- Determinism evidence:
  - `repeated notebook/build steps reproduce the same final counts`

## T - Tie

- GO criteria:
  - `All 20 promoted personas meet the gate prerequisites`
  - `59 total / 54 active / 5 planned is consistent across the final scoped surfaces`
  - `54 active / 5 deferred external is consistent in the active-surface contract`
- NO-GO criteria:
  - `Any promoted persona fails the gate prerequisites`
  - `Any partial activation occurs`

## H - Harness (ordered checks)

`H5-ACTIVATION-CLOSEOUT-C0` Preflight
- Verify H4 is green and governance docs are current.

`H5-ACTIVATION-CLOSEOUT-C1` Baseline inventory
- Capture current staged activation state.

`H5-ACTIVATION-CLOSEOUT-C2` Notebook activation-gate verification
- Prove every promoted persona satisfies the fail-closed prerequisites in notebooks first.

`H5-ACTIVATION-CLOSEOUT-C3` Notebook final-state transform
- Derive the final registry and active-surface outputs in notebooks first.

`H5-ACTIVATION-CLOSEOUT-C4` Final registry contract
- Verify `59 total / 54 active / 5 planned`.

`H5-ACTIVATION-CLOSEOUT-C5` Final active-surface contract
- Verify `54 active / 5 deferred external`.

`H5-ACTIVATION-CLOSEOUT-C6` Execute targeted validations
- Run the targeted builder, verifiers, and tests.

`H5-ACTIVATION-CLOSEOUT-C7` Strict artifact validation
- Fail if any promoted persona remains partially activated or if counts diverge.

`H5-ACTIVATION-CLOSEOUT-C8` Deterministic replay
- Repeat the build and require identical outputs.

`H5-ACTIVATION-CLOSEOUT-C9` Hard gates
1. `git diff --check`
2. `targeted builder/verifier/tests`
3. `scorecard green`

`H5-ACTIVATION-CLOSEOUT-C10` Governance synchronization and final decision
- Update docs, commit, push, and emit GO/NO-GO.

## Output Contract

- Deliverables:
  - `final registry and active-surface artifacts`
  - `verification output`
  - `scorecard`
- Validation results:
  - `H5-ACTIVATION-CLOSEOUT-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:H5-ACTIVATION-CLOSEOUT STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`
