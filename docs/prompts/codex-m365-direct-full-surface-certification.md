# Execution Prompt — Direct Full Surface Certification

Plan Reference: `plan:m365-direct-full-surface-certification`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`

**Mission:** Turn the repo-local M365 runtime from “partially proven” into a truthfully certified direct surface by locking the supported action universe, removing real blockers, and testing the supported actions family by family.

## Governance Lock

Before any write or mutating action:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-direct-full-surface-certification/m365-direct-full-surface-certification.md`
- predecessor evidence:
  - `plans/m365-direct-function-validation/m365-direct-function-validation.md`
  - `docs/commercialization/m365-direct-function-validation.md`
  - `artifacts/diagnostics/m365_direct_function_validation.json`
- certification universe sources:
  - `registry/agents.yaml`
  - `registry/capability_registry.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
  - `registry/executor_routing_v2.yaml`
  - `src/provisioning_api/routers/m365.py`
  - `src/ops_adapter/actions.py`

2. Cite:
- `plan:m365-direct-full-surface-certification:R0` through `R5`
- `F0` through `F4`

3. Stop immediately if:
- the work escapes the allowlist
- UCP-side edits are required
- certification would require undocumented or unsafe tenant changes

## Execution Order

1. `F0` universe lock
2. `F1` enablement
3. `F2` read-path certification
4. `F3` mutation and approval certification
5. `F4` closeout

## Hard rule

Do not report the surface as working unless the tested support matrix says it is certified. If an action cannot be made truthful, fence it out of the certified surface instead of implying support.
