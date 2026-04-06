# Execution Prompt — Direct Function Validation

Plan Reference: `plan:m365-direct-function-validation`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`
MATHS Template: `docs/governance/MATHS_PROMPT_TEMPLATE.md`

**Mission:** Execute direct repo-local M365 function tests one by one, classify outcomes truthfully, and repair any remaining repo-local defects without widening into UCP or tenant-admin work.

## Governance Lock (Mandatory)

Before any write, test, or command:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-direct-function-validation/m365-direct-function-validation.md`
- `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
- `docs/commercialization/m365-direct-runtime-readiness-remediation.md`
- `artifacts/diagnostics/m365_direct_runtime_readiness_remediation.json`
- `src/provisioning_api/main.py`
- `src/provisioning_api/routers/m365.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/actions.py`
- `src/smarthaus_common/tenant_config.py`
- `src/smarthaus_common/executor_routing.py`
- `src/smarthaus_common/power_apps_client.py`
- `src/smarthaus_common/power_automate_client.py`
- `src/smarthaus_graph/client.py`
- `registry/executor_routing_v2.yaml`
- `tests/test_endpoints.py`
- `tests/test_ops_adapter.py`
- `tests/test_executor_routing_v2.py`
- `tests/test_power_apps_expansion_v2.py`
- `tests/test_power_automate_expansion_v2.py`
- `tests/test_auth_model_v2.py`

2. Verify alignment + plan linkage:
- cite `plan:m365-direct-function-validation:R0` through `R4`
- cite `plan:m365-direct-function-validation:T1` through `T5`
- stop immediately if the work escapes the allowlist or drifts into UCP-side or tenant-admin work

3. Enforce approval protocol:
- this package is approved for execution
- call `validate_action` before any mutating action
- stop on first red

## Context

- Task name: `Direct repo-local function validation for the repaired M365 runtime`
- Domain: `infrastructure`
- Success rule:
  - `A function is green if it succeeds directly or if its failure is proven to be an external prerequisite rather than a repo-local defect.`
- Out of scope:
  - `UCP runtime changes`
  - `tenant-admin remediation`
  - `permission bypasses`

## M - Model

- Problem:
  - `The repo runtime is repaired enough for a live matrix, but there is not yet a governed per-function truth record.`
- Goal:
  - `Make it possible to ask for direct testing of specific functions and get truthful results from this repo version.`
- Required matrix:
  - `admin/governance`
  - `Teams`
  - `SharePoint`
  - `email`
  - `calendar`
  - `Power Apps`
  - `Power Automate`
  - `service health`

## A - Annotate

Required evidence:

- Human-readable closeout:
  - `docs/commercialization/m365-direct-function-validation.md`
- Machine-readable closeout:
  - `artifacts/diagnostics/m365_direct_function_validation.json`
- Runtime/test evidence:
  - direct instruction-surface results
  - governed action-surface results
  - focused pytest if any code change is required
- Governance evidence:
  - `Operations/ACTION_LOG.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/PROJECT_FILE_INDEX.md`

## T - Tie

- Dependency ties:
  - `The repaired direct-runtime harness from the prior package is the predecessor boundary for this package.`
  - `If a live function fails for a repo-local reason, the defect must be repaired before closeout.`
  - `If a live function fails for a tenant or local-module prerequisite, classify it and continue.`
- GO criteria:
  - `The direct function matrix is complete and every result is classified truthfully.`
- NO-GO criteria:
  - `Known repo-local defects remain in the direct function path.`
  - `Green would require bypassing actor identity, approvals, or permissions.`

## H - Harness (ordered checks)

`M365-DIRECT-FUNCTION-C0` Package and baseline lock
- Confirm the package artifacts and predecessor remediation evidence exist.

`M365-DIRECT-FUNCTION-C1` Harness baseline
- Reconfirm the documented local direct instruction and governed action harnesses.

`M365-DIRECT-FUNCTION-C2` Core direct matrix
- Execute admin/governance, Teams, and SharePoint direct tests.

`M365-DIRECT-FUNCTION-C3` Remaining direct matrix
- Execute email, calendar, Power Apps, Power Automate, and service-health direct tests.

`M365-DIRECT-FUNCTION-C4` Targeted remediation
- If C2 or C3 exposes a repo-local defect, repair it and rerun the affected tests plus focused regression coverage.

`M365-DIRECT-FUNCTION-C5` Hard gates
1. direct matrix rerun complete
2. focused pytest for any changed surfaces
3. `pre-commit run --all-files`
4. `git diff --check`

`M365-DIRECT-FUNCTION-C6` Diagnostics and closeout
- Publish the direct-function diagnostics and close the governance trackers.

## S - Stress-test

- `If a direct function still fails because of repo-local import, routing, or harness drift, fail the phase.`
- `If a function fails because of Graph permission, missing local modules, or a Microsoft service-side error, classify it as external truth rather than masking it.`
- `Repeat the usable direct harness and require the same classification on replay.`

