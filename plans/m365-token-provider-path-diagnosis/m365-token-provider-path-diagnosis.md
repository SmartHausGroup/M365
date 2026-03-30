# Plan: M365 Token Provider Path Diagnosis

**Plan ID:** `m365-token-provider-path-diagnosis`
**Parent Plan ID:** `m365-service-mode-token-acquisition-remediation`
**Status:** 🟠 Draft
**Date:** 2026-03-23
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-token-provider-path-diagnosis:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — preserve truthful, audited M365 execution by replacing ambiguous credential-error stories with exact provider-path evidence.
**Canonical predecessor:** `plans/m365-service-runtime-readiness-and-health/m365-service-runtime-readiness-and-health.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) its predecessor phase gate (P1A) is green, (2) the operator presents the approval packet and receives an explicit "go", and (3) no other child phase is concurrently active. It transitions to **Complete** only after its own gate emits GO.

**Ownership boundary (P2A):** This phase owns credential-source, auth-mode, and provider-path truth **only**. It must not repair runtime bootstrap, dependency, or health issues (P1A's scope). If evidence shows the remaining blocker belongs to P1A's domain, this phase must reopen P1A rather than drift scope.

**Approval and governance gates:** Before execution, the operator must present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before any mutating action and obey the verdict. Stop on first red. Do not auto-advance to the next phase.

## Objective

Determine exactly where the M365 token-acquisition path fails: credential source, auth mode, token provider, library/runtime path, or downstream Microsoft response.

## Scope

### In scope

- credential-source truth
- auth-mode and provider-path truth
- diagnostic surfacing for local and live token behavior
- focused tests and evidence

### Out of scope

- permanent runtime repair beyond bounded observability
- UCP-side changes
- final acceptance

### File allowlist

- `plans/m365-token-provider-path-diagnosis/**`
- `src/ops_adapter/actions.py`
- `src/smarthaus_graph/client.py`
- `src/smarthaus_common/auth_model.py`
- `tests/test_ops_adapter.py`
- `tests/test_auth_model_v2.py`
- `docs/commercialization/m365-token-provider-path-diagnosis.md`
- `artifacts/diagnostics/m365_token_provider_path_diagnosis.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `src/m365_server/__main__.py`
- `../UCP/**`

## Requirements

- **R1** the exact credential source used on the live path must be provable
- **R2** the exact token provider and auth mode must be provable
- **R3** ambiguous `credentials_missing` classification must be eliminated for this path
- **R4** focused tests and diagnostics must distinguish local-runtime from Microsoft-side failures
- **R5** the phase must hand off an explicit repair boundary or explicit GO-to-live-validation

## Execution Sequence

| Task | Description |
| --- | --- |
| `T1` | Inventory the real token-provider path and current outcome classes. |
| `T2` | Add bounded diagnostic surfacing within the allowlist. |
| `T3` | Re-run local and live token-path checks and record exact evidence. |
| `T4` | Decide whether a repair phase is required and what file boundary owns it. |
| `T5` | Update governance surfaces and stop. |

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-token-provider-path-diagnosis.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-token-provider-path-diagnosis-prompt.txt`

## Validation Strategy

- focused auth/token tests
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

- Do not patch broad runtime behavior in this phase unless the diagnosis itself proves it is unavoidable.
- Do not keep generic outcome labels if more specific truth is available.
- Stop when the repair boundary is clear.
