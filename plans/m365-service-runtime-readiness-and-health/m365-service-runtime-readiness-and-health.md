# Plan: M365 Service Runtime Readiness and Health

**Plan ID:** `m365-service-runtime-readiness-and-health`
**Parent Plan ID:** `m365-service-mode-token-acquisition-remediation`
**Status:** 🟠 Draft
**Date:** 2026-03-23
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-service-runtime-readiness-and-health:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the M365 server self-service, truthful, and production-shaped by making its local runtime envelope and health path deterministic.
**Canonical predecessor:** `plans/m365-service-runtime-authority-and-baseline-lock/m365-service-runtime-authority-and-baseline-lock.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) its predecessor phase gate (P0A) is green, (2) the operator presents the approval packet and receives an explicit "go", and (3) no other child phase is concurrently active. It transitions to **Complete** only after its own gate emits GO.

**Ownership boundary (P1A):** This phase owns local runtime, bootstrap, dependency, env-loading, and health truth **only**. It must not diagnose or repair credential-source, auth-mode, or provider-path issues (P2A's scope). If evidence shows the remaining blocker belongs to P2A's domain, this phase must emit NO-GO and stop rather than drift scope.

**Approval and governance gates:** Before execution, the operator must present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before any mutating action and obey the verdict. Stop on first red. Do not auto-advance to the next phase.

## Objective

Repair or confirm the local M365 service bootstrap, dependency envelope, and health contract so the token path runs inside a supported and reachable service runtime.

## Scope

### In scope

- supported Python/runtime envelope
- dependency and env-loading truth
- health endpoint readiness and diagnostics
- focused readiness tests

### Out of scope

- token-provider semantic repair
- UCP-side routing changes
- Microsoft tenant permission changes

### File allowlist

- `plans/m365-service-runtime-readiness-and-health/**`
- `pyproject.toml`
- `src/m365_server/__main__.py`
- `src/ops_adapter/main.py`
- `src/provisioning_api/auth.py`
- `scripts/check_env_credentials.py`
- `scripts/monitor-health.sh`
- `tests/test_api_health.py`
- `tests/test_ops_adapter.py`
- `docs/commercialization/m365-service-runtime-readiness-and-health.md`
- `artifacts/diagnostics/m365_service_runtime_readiness_and_health.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `src/ops_adapter/actions.py`
- `src/smarthaus_graph/client.py`
- `../UCP/**`

## Requirements

- **R1** the M365 service runtime must run inside the supported local envelope
- **R2** health truth must distinguish reachable, misconfigured, and missing-dependency states
- **R3** env/bootstrap loading must be explicit and testable
- **R4** focused readiness validation and diagnostics must exist
- **R5** the phase must stop if token-provider logic, not readiness, is still the blocker

## Execution Sequence

| Task | Description |
| --- | --- |
| `T1` | Capture the exact readiness gap: Python, deps, env, and health state. |
| `T2` | Repair the runtime bootstrap or health contract within the allowlist. |
| `T3` | Add or update focused readiness tests and diagnostics. |
| `T4` | Run the readiness gate and determine whether the token-diagnosis phase may start. |
| `T5` | Update governance surfaces and stop. |

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-service-runtime-readiness-and-health.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-service-runtime-readiness-and-health-prompt.txt`

## Validation Strategy

- targeted health and ops-adapter test coverage
- deterministic readiness artifact
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

- Do not repair token semantics in this phase unless the phase is formally reopened.
- Do not hide missing dependencies behind generic health success.
- Stop if the readiness gate is still red.
