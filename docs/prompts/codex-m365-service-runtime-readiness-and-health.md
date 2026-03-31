# MATHS Prompt: M365 Service Runtime Readiness and Health

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-service-runtime-readiness-and-health:R1`
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

## Ownership Boundary (P1A)

This phase owns local runtime, bootstrap, dependency, env-loading, and health truth **only**. It must not diagnose or repair credential-source, auth-mode, or provider-path issues (P2A's scope). If evidence shows the remaining blocker belongs to P2A's domain, this phase must emit NO-GO and stop.

## Execution Rules

- Run checks `M365-SERVICE-READINESS-C0` -> `M365-SERVICE-READINESS-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-SERVICE-READINESS STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-SERVICE-READINESS`
- Run ID: `m365-service-runtime-readiness-and-health`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-service-runtime-readiness-and-health:R1`
  - `plan:m365-service-runtime-readiness-and-health:R2`
  - `plan:m365-service-runtime-readiness-and-health:R3`
  - `plan:m365-service-runtime-readiness-and-health:R4`
  - `plan:m365-service-runtime-readiness-and-health:R5`

## Context

- Task name: `Repair or confirm local M365 runtime readiness and health truth`
- Domain: `runtime`
- Dependencies:
  - `plans/m365-service-runtime-authority-and-baseline-lock/m365-service-runtime-authority-and-baseline-lock.md`
  - `pyproject.toml`
  - `src/m365_server/__main__.py`
  - `src/ops_adapter/main.py`
  - `tests/test_api_health.py`
  - `tests/test_ops_adapter.py`
- Allowlist:
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
- Denylist:
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_graph/client.py`
  - `../UCP/**`

## M - Model

- Problem: `The M365 service must be running in a supported, reachable runtime before token-path work means anything.`
- Goal: `Make readiness, dependencies, env loading, and health status deterministic and testable.`
- Success criteria:
  - `Supported runtime envelope is explicit.`
  - `Health truth distinguishes healthy versus misconfigured versus missing dependencies.`
  - `Focused readiness tests are green.`

## A - Annotate

- Artifact/schema evidence:
  - `readiness doc and diagnostics artifact`
- Runtime/test evidence:
  - `targeted health and ops-adapter tests`
- Governance evidence:
  - `plan/execution/action-log/file-index sync`
- Determinism evidence:
  - `repeat health/readiness checks classify the state the same way`

## T - Tie

- Dependency ties:
  - `Readiness must be green before token diagnosis starts.`
- Known failure modes:
  - `unsupported Python`
  - `missing dependencies`
  - `health endpoint lies or is unreachable`
- GO criteria:
  - `runtime envelope and health truth are explicit and green enough for diagnosis`
- NO-GO criteria:
  - `readiness gate still red or ambiguous`

## H - Harness (ordered checks)

`M365-SERVICE-READINESS-C0` Preflight
- Verify prerequisite phase is complete.

`M365-SERVICE-READINESS-C1` Baseline inventory
- Capture current Python, dependency, env, and health posture.

`M365-SERVICE-READINESS-C2` Bootstrap and health repair
- Repair only the readiness surfaces in the allowlist.

`M365-SERVICE-READINESS-C3` Test updates
- Add or update focused readiness tests.

`M365-SERVICE-READINESS-C4` Diagnostics artifact
- Write the readiness diagnostics artifact.

`M365-SERVICE-READINESS-C5` Health truth validation
- Ensure the service reports truthful health classes.

`M365-SERVICE-READINESS-C6` Execute targeted validations
- Run targeted health/readiness commands.

`M365-SERVICE-READINESS-C7` Strict artifact validation
- Fail if runtime envelope, health class, or dependency findings are missing.

`M365-SERVICE-READINESS-C8` Deterministic replay
- Repeat the readiness check and require the same classification.

`M365-SERVICE-READINESS-C9` Hard gates (strict order)
1. `targeted readiness tests`
2. `artifact readback`
3. `git diff --check`

`M365-SERVICE-READINESS-C10` Governance synchronization and final decision
- Update required docs and emit GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If health reports green while required deps are missing, fail.`
  - `If the phase drifts into token-provider repair, fail.`
- Replay checks:
  - `Repeat readiness classification must match.`

## Output Contract

- Deliverables:
  - `readiness fix or confirmed-ready runtime posture`
  - `readiness diagnostics artifact`
  - `focused readiness validation evidence`
- Final decision lines:
  - `GATE:M365-SERVICE-READINESS STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Unsupported runtime envelope remains.
- Health truth is still ambiguous.
- Scope drifts into token-provider semantics.
