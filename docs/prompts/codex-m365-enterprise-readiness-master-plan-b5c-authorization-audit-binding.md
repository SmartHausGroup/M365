# MATHS Prompt: B5C Authorization and Audit Binding

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B5C`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B5C-C0` -> `M365-READY-B5C-C8` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-READY-B5C STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B5C`
- Run ID: `b5c-authorization-audit-binding`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R3`
  - `plan:m365-enterprise-readiness-master-plan:R9`
  - `plan:m365-enterprise-readiness-master-plan:B5C`
- Owners: `engineering`, `security`, `operations`

## Context

- Domain: `code`
- Dependencies: `B5B`, `A3`
- Goal: bind Entra-authenticated actor identity to authorization, approval, and audit while preserving explicit service-executor identity.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `src/ops_adapter/main.py`
  - `src/ops_adapter/app.py`
  - `src/ops_adapter/actions.py`
  - `src/ops_adapter/audit.py`
  - `src/ops_adapter/approvals.py`
  - `src/smarthaus_common/permission_enforcer.py`
  - `src/smarthaus_common/tenant_config.py`
  - `docs/commercialization/m365-audit-and-governance-evidence-model.md`
  - `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`
  - `tests/test_ops_adapter.py`
  - `tests/test_policies.py`
- Denylist:
  - live certification execution

## M - Model

- Problem: the runtime still needs a final binding between authenticated human actors, permission tiers, approvals, and audit records.
- Success criteria:
  - authorization is evaluated against actor identity
  - approvals preserve actor identity
  - audit records capture both actor identity and service executor identity

## H - Harness

- `M365-READY-B5C-C0` verify `B5B` closure and active authorization model.
- `M365-READY-B5C-C1` define user or group to tier mapping behavior.
- `M365-READY-B5C-C2` bind actor identity into approval creation and resolution.
- `M365-READY-B5C-C3` bind actor and executor identity into audit records.
- `M365-READY-B5C-C4` add targeted tests for actor-tier enforcement.
- `M365-READY-B5C-C5` add targeted tests for actor/executor audit traceability.
- `M365-READY-B5C-C6` sync certification docs and trackers.
- `M365-READY-B5C-C7` run targeted validation.
- `M365-READY-B5C-C8` emit final gate and next-act state.

## Validation

1. `pytest -q tests/test_ops_adapter.py tests/test_policies.py`
2. `rg -n "approval|audit|actor|executor|permission_tiers|group" src docs tests`
3. `git diff --check`

## No-Go Triggers

- authorization still depends only on service identity
- approvals lose actor identity
- audit cannot distinguish the human actor from the app executor
