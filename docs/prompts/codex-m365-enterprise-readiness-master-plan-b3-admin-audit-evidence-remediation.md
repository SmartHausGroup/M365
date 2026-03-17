# MATHS Prompt: B3 Admin Audit and Evidence-Surface Remediation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B3`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B3-C0` -> `M365-READY-B3-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-READY-B3 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B3`
- Run ID: `b3-admin-audit-evidence-remediation`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R4`
  - `plan:m365-enterprise-readiness-master-plan:B3`
- Owners: `engineering`, `security`, `operations`

## Context

- Domain: `code`
- Dependency: `A3`, `B2`
- Goal: close the current admin-audit gap and align enterprise evidence claims with the real runtime surface.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-audit-and-governance-evidence-model.md`
  - `src/ops_adapter/actions.py`
  - `src/ops_adapter/audit.py`
  - `src/provisioning_api/audit.py`
  - `tests/test_ops_adapter.py`
  - `configs/generated/*`
- Denylist:
  - `docs/prompts/**`

## M - Model

- Problem: `snapshot_mode` admin audit blocks enterprise claims.
- Success criteria:
  - admin audit is no longer snapshot-only for the claimed surface
  - audit evidence mapping is explicit and reproducible
  - targeted audit tests or verification artifacts exist

## H - Harness

- `C0` inventory current admin-audit behavior and evidence gaps.
- `C1` define the accepted enterprise audit target state.
- `C2` implement audit-surface remediation.
- `C3` normalize evidence outputs and schema where needed.
- `C4` add targeted audit tests or verification outputs.
- `C5` update commercialization docs if the evidence model changes materially.
- `C6` run targeted validation.
- `C7` run `git diff --check`.
- `C8` sync plan and log.
- `C9` record remaining gaps.
- `C10` final gate decision.

## Validation

1. `pytest -q tests/test_ops_adapter.py`
2. `rg -n "snapshot|audit|admin.audit_log|ops_audit.log" src docs configs/generated`
3. `git diff --check`

## No-Go Triggers

- admin audit remains snapshot-only for the claimed enterprise surface
- evidence mapping is still inconsistent across runtime and docs
- targeted audit verification is missing or failing
