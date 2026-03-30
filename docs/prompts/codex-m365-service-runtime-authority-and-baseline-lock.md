# MATHS Prompt: M365 Service Runtime Authority and Baseline Lock

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-service-runtime-authority-and-baseline-lock:R1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — before executing any check, present the plan ref, scope, predecessor status, and intended actions to the operator.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go" in the chat interface.
3. **Call MCP `validate_action` before any mutating action** — before writing, editing, or creating any file, call `validate_action` and obey the verdict. If the verdict is not `allowed`, stop immediately.
4. **Stop on first red** — if any check emits `FAIL` or `BLOCKED`, stop the entire phase. Do not continue to subsequent checks.
5. **Do not auto-advance to the next phase** — even if this phase emits GO, the next phase requires its own approval packet and "go" confirmation.

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after the operator presents the approval packet and receives "go". The parent initiative can be Active while this phase is still Draft.

## Predecessor Authority

The canonical predecessor for this initiative is the M365-local artifact `plans/m365-ucp-live-activation-repair/m365-ucp-live-activation-repair.md`. The sibling UCP repo is historical implementation lineage only.

## Execution Rules

- Run checks `M365-SERVICE-BOUNDARY-C0` -> `M365-SERVICE-BOUNDARY-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-SERVICE-BOUNDARY STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-SERVICE-BOUNDARY`
- Run ID: `m365-service-runtime-authority-and-baseline-lock`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-service-runtime-authority-and-baseline-lock:R1`
  - `plan:m365-service-runtime-authority-and-baseline-lock:R2`
  - `plan:m365-service-runtime-authority-and-baseline-lock:R3`
  - `plan:m365-service-runtime-authority-and-baseline-lock:R4`
  - `plan:m365-service-runtime-authority-and-baseline-lock:R5`
  - `plan:m365-service-runtime-authority-and-baseline-lock:T1`
  - `plan:m365-service-runtime-authority-and-baseline-lock:T2`
  - `plan:m365-service-runtime-authority-and-baseline-lock:T3`
  - `plan:m365-service-runtime-authority-and-baseline-lock:T4`
  - `plan:m365-service-runtime-authority-and-baseline-lock:T5`

## Context

- Task name: `Lock M365 authority and baseline for the remaining service-mode token work`
- Domain: `governance`
- Dependencies:
  - `plans/m365-service-mode-token-acquisition-remediation/m365-service-mode-token-acquisition-remediation.md`
  - `plans/m365-ucp-live-activation-repair/m365-ucp-live-activation-repair.md`
- Allowlist:
  - `plans/m365-service-runtime-authority-and-baseline-lock/**`
  - `docs/commercialization/m365-service-runtime-authority-and-baseline-lock.md`
  - `artifacts/diagnostics/m365_service_runtime_authority_and_baseline_lock.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `../UCP/**`

## M - Model

- Problem: `The remaining service-mode/token-acquisition work is still anchored to the wrong repo authority unless M365 locks it locally.`
- Goal: `Make M365 the active governing repo for the remaining work and capture the exact current baseline before implementation.`
- Success criteria:
  - `The M365 authority boundary is explicit.`
  - `The current baseline facts are retained in one local doc/artifact.`
  - `The exact entry criteria for the readiness phase are explicit.`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `authority/baseline doc exists`
  - `diagnostics artifact exists`
- Governance evidence:
  - `Operations/EXECUTION_PLAN.md updated`
  - `Operations/ACTION_LOG.md updated`
  - `Operations/PROJECT_FILE_INDEX.md updated`
- Determinism evidence:
  - `baseline fact set and next-phase gate are explicit and replayable`

## T - Tie

- Dependency ties:
  - `This phase must complete before runtime readiness work starts.`
  - `The next phase may begin only if the boundary and baseline are explicit.`
- Known failure modes:
  - `M365/UCP authority remains ambiguous`
  - `baseline facts are inferred instead of retained`
- GO criteria:
  - `authority doc, diagnostics artifact, and next-phase gate all exist`
- NO-GO criteria:
  - `authority remains ambiguous or next-phase gate is missing`

## H - Harness (ordered checks)

`M365-SERVICE-BOUNDARY-C0` Preflight
- Read AGENTS, rules, North Star, execution plan, action log, parent plan, child plan, and `docs/governance/MATHS_PROMPT_TEMPLATE.md`.

`M365-SERVICE-BOUNDARY-C1` Baseline inventory
- Capture the exact known remaining failure facts already established.

`M365-SERVICE-BOUNDARY-C2` Authority lock
- Publish the M365-native authority boundary.

`M365-SERVICE-BOUNDARY-C3` Baseline artifact
- Write the bounded local diagnostics artifact.

`M365-SERVICE-BOUNDARY-C4` Next-phase gate
- Define the exact prerequisites for runtime readiness.

`M365-SERVICE-BOUNDARY-C5` Prompt and plan sync
- Re-read plan refs and ensure prompt/plan language agrees.

`M365-SERVICE-BOUNDARY-C6` Execute targeted validations
- Validate file existence and explicit next-phase gate wording.

`M365-SERVICE-BOUNDARY-C7` Strict artifact validation
- Fail if the doc or artifact omits the authority boundary, current baseline, or next-phase gate.

`M365-SERVICE-BOUNDARY-C8` Deterministic replay
- Re-read outputs and require the same boundary and gate language.

`M365-SERVICE-BOUNDARY-C9` Hard gates (strict order)
1. `artifact and plan readback`
2. `file-index/governance readback`
3. `git diff --check`

`M365-SERVICE-BOUNDARY-C10` Governance synchronization and final decision
- Update required docs and emit GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If the phase tries to repair runtime code, fail.`
  - `If the phase leaves UCP as the active authority for remaining work, fail.`
- Replay checks:
  - `The same baseline facts and next-phase gate must appear on reread.`

## Output Contract

- Deliverables:
  - `M365 authority doc`
  - `baseline diagnostics artifact`
  - `explicit readiness-phase entry gate`
- Validation results:
  - `M365-SERVICE-BOUNDARY-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Residual risks:
  - `none or one-line truthful note`
- Final decision lines:
  - `GATE:M365-SERVICE-BOUNDARY STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any repo-authority ambiguity remains.
- Baseline facts are not retained locally.
- The next-phase gate is not explicit.
- Scope drifts into runtime code.
