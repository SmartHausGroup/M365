# MATHS Prompt: M365 Live Token Acquisition Classification

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-live-token-acquisition-classification:R1`
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

## Closure Boundary (P4A)

This phase **only** classifies the live token-acquisition outcome and decides advance-to-acceptance or reopen-prior-phase. P4A must **not** issue the final remediation GO/NO-GO — that authority belongs exclusively to P5A.

## Execution Rules

- Run checks `M365-LIVE-TOKEN-C0` -> `M365-LIVE-TOKEN-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-LIVE-TOKEN STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-LIVE-TOKEN`
- Run ID: `m365-live-token-acquisition-classification`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-live-token-acquisition-classification:R1`
  - `plan:m365-live-token-acquisition-classification:R2`
  - `plan:m365-live-token-acquisition-classification:R3`
  - `plan:m365-live-token-acquisition-classification:R4`
  - `plan:m365-live-token-acquisition-classification:R5`

## Context

- Task name: `Classify the repaired live token-acquisition outcome`
- Domain: `runtime`
- Dependencies:
  - `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.md`
  - `tests/test_ops_adapter.py`
  - `tests/test_graph_client.py`
- Allowlist:
  - `plans/m365-live-token-acquisition-classification/**`
  - `tests/test_ops_adapter.py`
  - `tests/test_graph_client.py`
  - `docs/commercialization/m365-live-token-acquisition-classification.md`
  - `artifacts/diagnostics/m365_live_token_acquisition_classification.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `src/**`
  - `../UCP/**`

## M - Model

- Problem: `The repaired path still needs live proof and truthful classification.`
- Goal: `Prove whether live token acquisition now succeeds, fails with invalid credentials, fails with a Microsoft-side permission issue, or still has a local misconfiguration.`
- Success criteria:
  - `Outcome classes are explicit.`
  - `Evidence is retained for the live classification.`
  - `The next boundary is either end-to-end acceptance or an explicit phase reopen.`

## A - Annotate

- Artifact/schema evidence:
  - `live classification doc and diagnostics artifact`
- Runtime/test evidence:
  - `focused live classification coverage`
- Governance evidence:
  - `plan/execution/action-log/file-index sync`
- Determinism evidence:
  - `repeat live classification yields the same outcome class`

## T - Tie

- Dependency ties:
  - `Live classification must follow a green repair phase.`
  - `Acceptance may begin only if the live outcome class is definitive.`
- Known failure modes:
  - `generic error class persists`
  - `local misconfiguration mistaken for Microsoft-side failure`
  - `phase silently fixes code instead of reopening repair`
- GO criteria:
  - `definitive outcome class recorded and next boundary explicit`
- NO-GO criteria:
  - `outcome remains ambiguous or requires hidden code changes`

## H - Harness (ordered checks)

`M365-LIVE-TOKEN-C0` Preflight
- Verify prerequisite repair phase is green.

`M365-LIVE-TOKEN-C1` Outcome-matrix lock
- Define the exact classification matrix.

`M365-LIVE-TOKEN-C2` Coverage update
- Add or update focused classification coverage within the allowlist.

`M365-LIVE-TOKEN-C3` Live classification run
- Execute the repaired live token path and capture exact evidence.

`M365-LIVE-TOKEN-C4` Outcome labeling
- Classify the result as success, invalid credentials, Microsoft-side permission issue, or local misconfiguration.

`M365-LIVE-TOKEN-C5` Reopen-or-advance decision
- Decide whether acceptance may begin.

`M365-LIVE-TOKEN-C6` Execute targeted validations
- Run focused classification validation commands.

`M365-LIVE-TOKEN-C7` Strict artifact validation
- Fail if outcome class or evidence is missing.

`M365-LIVE-TOKEN-C8` Deterministic replay
- Repeat the live classification and require the same class.

`M365-LIVE-TOKEN-C9` Hard gates (strict order)
1. `targeted classification coverage`
2. `artifact readback`
3. `git diff --check`

`M365-LIVE-TOKEN-C10` Governance synchronization and final decision
- Update required docs and emit GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If the phase silently edits runtime code, fail.`
  - `If a Microsoft-side permission issue is not labeled explicitly, fail.`
- Replay checks:
  - `Outcome class must match on repeat execution.`

## Output Contract

- Deliverables:
  - `live token-classification evidence`
  - `classification diagnostics artifact`
  - `explicit advance-or-reopen decision`
- Final decision lines:
  - `GATE:M365-LIVE-TOKEN STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Outcome class remains ambiguous.
- The phase needs hidden runtime repair.
- The M365-versus-Microsoft truth boundary is blurred.
