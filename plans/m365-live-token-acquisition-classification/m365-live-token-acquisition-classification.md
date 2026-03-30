# Plan: M365 Live Token Acquisition Classification

**Plan ID:** `m365-live-token-acquisition-classification`
**Parent Plan ID:** `m365-service-mode-token-acquisition-remediation`
**Status:** 🟠 Draft
**Date:** 2026-03-23
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-live-token-acquisition-classification:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — preserve honest M365-only operations by classifying the repaired live path truthfully instead of guessing whether failures are local or Microsoft-side.
**Canonical predecessor:** `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) its predecessor phase gate (P3A) is green, (2) the operator presents the approval packet and receives an explicit "go", and (3) no other child phase is concurrently active. It transitions to **Complete** only after its own gate emits GO.

**Closure boundary (P4A):** This phase **only** classifies the live token-acquisition outcome and decides advance-to-acceptance or reopen-prior-phase. P4A must **not** issue the final remediation GO/NO-GO — that authority belongs exclusively to P5A.

**Approval and governance gates:** Before execution, the operator must present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before any mutating action and obey the verdict. Stop on first red. Do not auto-advance to the next phase.

## Objective

Run the repaired live token-acquisition path and classify the result as success, invalid credentials, missing Graph permission, or remaining local misconfiguration.

## Scope

### In scope

- live and targeted token-acquisition proof
- outcome-class definition and evidence capture
- explicit handoff to end-to-end acceptance or phase reopen

### Out of scope

- additional runtime repair unless an earlier phase is reopened
- UCP-side changes

### File allowlist

- `plans/m365-live-token-acquisition-classification/**`
- `tests/test_ops_adapter.py`
- `tests/test_graph_client.py`
- `docs/commercialization/m365-live-token-acquisition-classification.md`
- `artifacts/diagnostics/m365_live_token_acquisition_classification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `src/**`
- `../UCP/**`

## Requirements

- **R1** live token acquisition must be exercised on the repaired path
- **R2** outcomes must be classified as success, invalid credentials, missing Microsoft permission, or local misconfiguration
- **R3** the M365-vs-Microsoft truth boundary must stay explicit
- **R4** focused evidence and diagnostics must exist
- **R5** the phase must either authorize end-to-end acceptance or reopen an earlier phase cleanly

## Execution Sequence

| Task | Description |
| --- | --- |
| `T1` | Define the exact outcome classes and evidence matrix. |
| `T2` | Add or update focused live-classification coverage. |
| `T3` | Run the live and targeted classification path and capture evidence. |
| `T4` | Decide whether acceptance may begin or a prior phase must reopen. |
| `T5` | Update governance surfaces and stop. |

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-live-token-acquisition-classification.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-live-token-acquisition-classification-prompt.txt`

## Validation Strategy

- focused live classification coverage
- deterministic diagnostics artifact
- `git diff --check`

## Governance Closure

- [ ] `Operations/ACTION_LOG.md`
- [ ] `Operations/EXECUTION_PLAN.md`
- [ ] `Operations/PROJECT_FILE_INDEX.md`
- [ ] This plan `status -> complete`

## Execution Outcome

- **Decision:** `pending`
- **Approved by:** `pending`
- **Completion timestamp:** `pending`

## Agent Constraints

- Do not fix code silently in this phase; reopen the prior phase instead.
- Keep Microsoft-side permission truth explicit.
- Stop once the acceptance decision is made.
