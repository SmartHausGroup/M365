# MATHS Prompt: M365 Service-Mode End-to-End Acceptance

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-service-mode-end-to-end-acceptance:R1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — before executing any check, present the plan ref, scope, predecessor status, and intended actions to the operator.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go" in the chat interface.
3. **Call MCP `validate_action` before any mutating action** — before writing, editing, or creating any file, call `validate_action` and obey the verdict. If the verdict is not `allowed`, stop immediately.
4. **Stop on first red** — if any check emits `FAIL` or `BLOCKED`, stop the entire phase. Do not continue to subsequent checks.
5. **Do not auto-advance to the next phase** — even if this phase emits GO, this is the final phase. No further advancement occurs.

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after the operator presents the approval packet and receives "go". The parent initiative can be Active while this phase is still Draft.

## Closure Boundary (P5A)

P5A is the **sole authority** for the final remediation GO/NO-GO. Only P5A may issue that decision, and only after live `sites.root` and `directory.org` acceptance evidence exists. No earlier phase may claim final closure.

## Execution Rules

- Run checks `M365-END-TO-END-C0` -> `M365-END-TO-END-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-END-TO-END STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-END-TO-END`
- Run ID: `m365-service-mode-end-to-end-acceptance`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-service-mode-end-to-end-acceptance:R1`
  - `plan:m365-service-mode-end-to-end-acceptance:R2`
  - `plan:m365-service-mode-end-to-end-acceptance:R3`
  - `plan:m365-service-mode-end-to-end-acceptance:R4`
  - `plan:m365-service-mode-end-to-end-acceptance:R5`

## Context

- Task name: `Run final service-mode end-to-end acceptance`
- Domain: `runtime`
- Dependencies:
  - `plans/m365-live-token-acquisition-classification/m365-live-token-acquisition-classification.md`
  - `tests/test_ops_adapter.py`
  - `tests/test_graph_client.py`
- Allowlist:
  - `plans/m365-service-mode-end-to-end-acceptance/**`
  - `tests/test_ops_adapter.py`
  - `tests/test_graph_client.py`
  - `docs/commercialization/m365-service-mode-end-to-end-acceptance.md`
  - `artifacts/diagnostics/m365_service_mode_end_to_end_acceptance.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `src/**`
  - `../UCP/**`

## M - Model

- Problem: `The remaining M365 work is not closed until live sites.root and directory.org are proven on the repaired service-mode path.`
- Goal: `Emit a truthful final GO or NO-GO for the M365-side remediation.`
- Success criteria:
  - `sites.root is exercised live.`
  - `directory.org is exercised live and classified truthfully.`
  - `Final output is explicit GO or NO-GO.`

## A - Annotate

- Artifact/schema evidence:
  - `acceptance doc and diagnostics artifact`
- Runtime/test evidence:
  - `live acceptance evidence for sites.root and directory.org`
- Governance evidence:
  - `plan/execution/action-log/file-index sync`
- Determinism evidence:
  - `repeat final acceptance on fixed state yields the same final class`

## T - Tie

- Dependency ties:
  - `This phase may start only after live token classification is definitive.`
- Known failure modes:
  - `sites.root still blocked locally`
  - `directory.org result mislabeled`
  - `final output avoids an explicit GO/NO-GO`
- GO criteria:
  - `final live evidence is retained and the final decision is explicit`
- NO-GO criteria:
  - `live evidence is missing, ambiguous, or mislabeled`

## H - Harness (ordered checks)

`M365-END-TO-END-C0` Preflight
- Verify prerequisite live-classification phase is green.

`M365-END-TO-END-C1` Acceptance matrix
- Define final no-go triggers and evidence requirements.

`M365-END-TO-END-C2` Sites.root live run
- Execute and retain the live sites.root path.

`M365-END-TO-END-C3` Directory.org live run
- Execute and retain the live directory.org path.

`M365-END-TO-END-C4` Final classification
- Classify final state as GO or NO-GO and keep Microsoft-side truth explicit.

`M365-END-TO-END-C5` Residual-risk summary
- State remaining local or Microsoft-side limitations truthfully.

`M365-END-TO-END-C6` Execute targeted validations
- Run focused acceptance validation commands.

`M365-END-TO-END-C7` Strict artifact validation
- Fail if sites.root, directory.org, or final decision evidence is missing.

`M365-END-TO-END-C8` Deterministic replay
- Repeat final acceptance and require the same class.

`M365-END-TO-END-C9` Hard gates (strict order)
1. `targeted acceptance coverage`
2. `artifact readback`
3. `git diff --check`

`M365-END-TO-END-C10` Governance synchronization and final decision
- Update required docs and emit GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If a Microsoft-side 403 is hidden or relabeled, fail.`
  - `If the final output avoids GO/NO-GO, fail.`
- Replay checks:
  - `Final outcome class must match on repeat execution.`

## Output Contract

- Deliverables:
  - `final live acceptance evidence`
  - `acceptance diagnostics artifact`
  - `explicit GO or NO-GO closeout`
- Final decision lines:
  - `GATE:M365-END-TO-END STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- sites.root evidence missing.
- directory.org evidence missing or mislabeled.
- final GO/NO-GO decision omitted.
