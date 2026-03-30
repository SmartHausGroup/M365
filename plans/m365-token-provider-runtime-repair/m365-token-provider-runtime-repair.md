# Plan: M365 Token Provider Runtime Repair

**Plan ID:** `m365-token-provider-runtime-repair`
**Parent Plan ID:** `m365-service-mode-token-acquisition-remediation`
**Status:** 🟠 Draft
**Date:** 2026-03-23
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-token-provider-runtime-repair:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — fix the M365-side root cause directly so the platform remains self-service, truthful, and M365-only.
**Canonical predecessor:** `plans/m365-token-provider-path-diagnosis/m365-token-provider-path-diagnosis.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) its predecessor phase gate (P2A) is green, (2) the operator presents the approval packet and receives an explicit "go", and (3) no other child phase is concurrently active. It transitions to **Complete** only after its own gate emits GO.

**Approval and governance gates:** Before execution, the operator must present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before any mutating action and obey the verdict. Stop on first red. Do not auto-advance to the next phase.

## Objective

Apply the minimal M365-side runtime or token-provider repair identified by the diagnosis phase, preserve fail-closed behavior, and keep downstream Microsoft permission errors truthful.

## Scope

### In scope

- token-provider and credential-resolution repair
- bounded runtime/auth fixes in the M365 repo
- focused regression coverage
- repair diagnostics and governance sync

### Out of scope

- UCP-side routing or policy changes
- tenant permission changes
- final end-to-end acceptance

### File allowlist

- `plans/m365-token-provider-runtime-repair/**`
- `pyproject.toml`
- `src/ops_adapter/actions.py`
- `src/smarthaus_graph/client.py`
- `src/smarthaus_common/auth_model.py`
- `src/provisioning_api/auth.py`
- `tests/test_ops_adapter.py`
- `tests/test_graph_client.py`
- `tests/test_env_loading.py`
- `docs/commercialization/m365-token-provider-runtime-repair.md`
- `artifacts/diagnostics/m365_token_provider_runtime_repair.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `../UCP/**`
- `registry/**`

## Requirements

- **R1** the diagnosed token-provider/runtime defect must be fixed in the M365 repo
- **R2** the repaired path must remain fail-closed on missing config or invalid credentials
- **R3** focused regression tests must prove the repaired path
- **R4** downstream Microsoft-side permission errors must stay truthful
- **R5** the phase must stop once live classification is the next dependency boundary

## Execution Sequence

| Task | Description |
| --- | --- |
| `T1` | Restate the exact root cause from the diagnosis phase. |
| `T2` | Implement the bounded runtime/auth repair within the allowlist. |
| `T3` | Add or update focused regression tests and diagnostics. |
| `T4` | Run the repair gate and determine whether live classification may begin. |
| `T5` | Update governance surfaces and stop. |

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-token-provider-runtime-repair.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-token-provider-runtime-repair-prompt.txt`

## Validation Strategy

- targeted auth/graph/env regression suite
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

- Do not broaden the repair beyond the diagnosed root cause.
- Do not relabel downstream Microsoft failures as local fixes.
- Stop if acceptance evidence is needed instead of more code changes.
