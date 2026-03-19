# MATHS Prompt: B5B Runtime Identity Enforcement

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B5B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B5B-C0` -> `M365-READY-B5B-C8` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-READY-B5B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B5B`
- Run ID: `b5b-runtime-identity-enforcement`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R3`
  - `plan:m365-enterprise-readiness-master-plan:R9`
  - `plan:m365-enterprise-readiness-master-plan:B5B`
- Owners: `engineering`, `security`

## Context

- Domain: `code`
- Dependencies: `B5A`, `B2`, `B3`
- Goal: enforce authenticated Entra user identity on governed user-facing execution paths while preserving app-only Graph execution.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `src/ops_adapter/main.py`
  - `src/ops_adapter/app.py`
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_common/permission_enforcer.py`
  - `src/smarthaus_common/tenant_config.py`
  - `tests/test_ops_adapter.py`
  - `tests/test_policies.py`
- Denylist:
  - direct tenant mutations outside the test harness

## M - Model

- Problem: active governed execution paths still need a formally bounded actor-identity enforcement model.
- Success criteria:
  - governed user-facing paths reject missing or invalid actor identity
  - actor identity is propagated through the execution path
  - Graph execution remains app-only and is not replaced by delegated user execution

## H - Harness

- `M365-READY-B5B-C0` verify `B5A` closure and runtime surfaces in scope.
- `M365-READY-B5B-C1` pin current actor-identity ingress and failure modes.
- `M365-READY-B5B-C2` implement explicit actor-identity enforcement.
- `M365-READY-B5B-C3` preserve app-only executor behavior.
- `M365-READY-B5B-C4` add targeted tests for missing or invalid actor identity.
- `M365-READY-B5B-C5` add targeted tests for actor propagation.
- `M365-READY-B5B-C6` sync impacted docs and trackers.
- `M365-READY-B5B-C7` run targeted validation.
- `M365-READY-B5B-C8` emit final gate and next-act state.

## Validation

1. `pytest -q tests/test_ops_adapter.py tests/test_policies.py`
2. `rg -n "Authorization|Bearer|tenant_id|actor|request.state.user|app_only" src tests`
3. `git diff --check`

## No-Go Triggers

- actor identity is optional on governed paths
- delegated user execution silently replaces app-only Graph execution
- targeted deny-path coverage is missing or failing
