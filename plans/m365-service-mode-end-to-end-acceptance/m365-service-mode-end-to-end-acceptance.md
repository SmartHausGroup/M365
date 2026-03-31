# Plan: M365 Service-Mode End-to-End Acceptance

**Plan ID:** `m365-service-mode-end-to-end-acceptance`
**Parent Plan ID:** `m365-service-mode-token-acquisition-remediation`
**Status:** 🟠 Draft
**Date:** 2026-03-23
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-service-mode-end-to-end-acceptance:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — close the remaining M365 work with a truthful live decision based on real M365 execution, not inference or cross-repo guesswork.
**Canonical predecessor:** `plans/m365-live-token-acquisition-classification/m365-live-token-acquisition-classification.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) its predecessor phase gate (P4A) is green, (2) the operator presents the approval packet and receives an explicit "go", and (3) no other child phase is concurrently active. It transitions to **Complete** only after its own gate emits GO.

**Closure boundary (P5A):** P5A is the **sole authority** for the final remediation GO/NO-GO. Only P5A may issue that decision, and only after live `sites.root` and `directory.org` acceptance evidence exists. No earlier phase may claim final closure.

**Approval and governance gates:** Before execution, the operator must present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before any mutating action and obey the verdict. Stop on first red. Do not auto-advance to the next phase.

## Objective

Run the final live acceptance for service-mode `sites.root` and `directory.org`, classify the final state truthfully, and close the remediation with an explicit GO or NO-GO.

## Scope

### In scope

- final live acceptance matrix
- live `sites.root` and `directory.org` execution evidence
- explicit GO or NO-GO closeout
- operator handoff and governance sync

### Out of scope

- new runtime repair without formally reopening a prior phase
- UCP-side code changes

### File allowlist

- `plans/m365-service-mode-end-to-end-acceptance/**`
- `tests/test_ops_adapter.py`
- `tests/test_graph_client.py`
- `docs/commercialization/m365-service-mode-end-to-end-acceptance.md`
- `artifacts/diagnostics/m365_service_mode_end_to_end_acceptance.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `src/**`
- `../UCP/**`

## Requirements

- **R1** final acceptance must use the repaired service-mode path only
- **R2** `sites.root` and `directory.org` must be exercised live and classified truthfully
- **R3** the final decision must be explicit GO or NO-GO
- **R4** residual Microsoft-side permission issues must remain clearly labeled as downstream
- **R5** governance closeout and operator handoff must be synchronized

## Execution Sequence

| Task | Description |
| --- | --- |
| `T1` | Define the final acceptance matrix and no-go triggers. |
| `T2` | Run the live `sites.root` acceptance path. |
| `T3` | Run the live `directory.org` acceptance path and classify any downstream Microsoft result. |
| `T4` | Decide final GO or NO-GO. |
| `T5` | Update governance surfaces and close the initiative. |

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-service-mode-end-to-end-acceptance.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-service-mode-end-to-end-acceptance-prompt.txt`

## Validation Strategy

- live acceptance evidence
- deterministic acceptance artifact
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

- Do not blur a Microsoft-side 403 into a local M365 failure.
- Do not reopen code paths silently in this phase.
- Final output must be explicit GO or NO-GO.
