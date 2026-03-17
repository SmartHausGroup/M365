# MATHS Prompt: B2 Fail-Closed Governance and Approval Remediation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B2`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B2-C0` -> `M365-READY-B2-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-READY-B2 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B2`
- Run ID: `b2-fail-closed-governance-approval-remediation`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R3`
  - `plan:m365-enterprise-readiness-master-plan:B2`
- Owners: `engineering`, `security`, `operations`

## Context

- Domain: `code`
- Dependency: `A3`, `B1`
- Goal: make policy, approval, and permission behavior fail closed in the enterprise posture.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`
  - `registry/permission_tiers.yaml`
  - `policies/ops.rego`
  - `src/smarthaus_common/permission_enforcer.py`
  - `src/ops_adapter/policies.py`
  - `src/ops_adapter/app.py`
  - `src/ops_adapter/main.py`
  - `src/ops_adapter/approvals.py`
  - `tests/test_ops_adapter.py`
  - `tests/test_policies.py`
- Denylist:
  - `docs/prompts/**`

## M - Model

- Problem: enterprise claims are blocked while permissive fallbacks and approval ambiguity remain in runtime.
- Success criteria:
  - missing policy/identity/config prerequisites deny rather than allow
  - supported high-risk actions have a deterministic approval posture
  - targeted deny-path and approval tests exist

## H - Harness

- `C0` inventory fail-open and approval gaps.
- `C1` define exact enterprise deny behavior from the commercialization docs.
- `C2` implement fail-closed runtime changes.
- `C3` remediate approval handling for supported mutating actions.
- `C4` add or update targeted policy and approval tests.
- `C5` verify no enterprise path silently falls back to allow.
- `C6` run targeted validation.
- `C7` run `git diff --check`.
- `C8` sync docs if runtime semantics changed.
- `C9` sync plan and log.
- `C10` final gate decision.

## Validation

1. `pytest -q tests/test_ops_adapter.py tests/test_policies.py`
2. `rg -n "fail_open|approval_required|approval" src/ops_adapter src/smarthaus_common policies`
3. `git diff --check`

## No-Go Triggers

- any enterprise path still fails open
- approval behavior for supported high-risk actions remains ambiguous
- targeted deny/approval tests are missing or failing
