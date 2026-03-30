# Plan: M365 Service Runtime Authority and Baseline Lock

**Plan ID:** `m365-service-runtime-authority-and-baseline-lock`
**Parent Plan ID:** `m365-service-mode-token-acquisition-remediation`
**Status:** 🟠 Draft
**Date:** 2026-03-23
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-service-runtime-authority-and-baseline-lock:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the remaining work in the repo that owns the live M365 runtime and preserve truthful, auditable M365-only execution.
**Canonical predecessor:** `plans/m365-ucp-live-activation-repair/m365-ucp-live-activation-repair.md` (M365-local artifact). The sibling UCP repo is historical implementation lineage only.

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) the operator presents the approval packet and receives an explicit "go", and (2) no other child phase is concurrently active. It transitions to **Complete** only after its own gate emits GO. The parent initiative may be Active while this child is still Draft.

**Approval and governance gates:** Before execution, the operator must present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before any mutating action and obey the verdict. Stop on first red. Do not auto-advance to the next phase.

## Objective

Lock the M365 repo as the active authority for the remaining work and freeze the current service-mode/token-acquisition baseline before any runtime changes begin.

## Scope

### In scope

- publish the M365-native authority boundary for the remaining work
- capture the exact current failure baseline and prerequisite facts
- define the explicit entry gate for the next phase

### Out of scope

- runtime code changes
- edits to the sibling UCP repo
- token-provider repair

### File allowlist

- `plans/m365-service-runtime-authority-and-baseline-lock/**`
- `docs/commercialization/m365-service-runtime-authority-and-baseline-lock.md`
- `artifacts/diagnostics/m365_service_runtime_authority_and_baseline_lock.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `src/**`
- `tests/**`
- `../UCP/**`

## Requirements

- **R1** lock M365 as the governing repo for the remaining service-mode/token work
- **R2** capture the exact current failure boundary and prerequisite truths
- **R3** define the no-advance gate for the readiness phase
- **R4** create a bounded diagnostic artifact or authority doc
- **R5** close governance truthfully without claiming runtime repair

## Execution Sequence

| Task | Description |
| --- | --- |
| `T1` | Define the M365 runtime authority boundary and the relationship to the predecessor UCP slice. |
| `T2` | Capture the current baseline facts that still block live token acquisition. |
| `T3` | Publish the authority/baseline doc and diagnostics artifact. |
| `T4` | Define the exact readiness-phase entry criteria. |
| `T5` | Update governance surfaces and stop. |

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-service-runtime-authority-and-baseline-lock.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-service-runtime-authority-and-baseline-lock-prompt.txt`

## Validation Strategy

- verify the authority doc and diagnostics artifact exist
- verify the next-phase entry criteria are explicit
- run `git diff --check`

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

- Do not modify runtime code in this phase.
- Do not let the active authority drift back to UCP.
- Stop if this phase requires repair work instead of baseline/authority definition.
