# MATHS Prompt: B1 Runtime Config Authority Remediation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B1-C0` -> `M365-READY-B1-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-READY-B1 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B1`
- Run ID: `b1-runtime-config-authority-remediation`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R2`
  - `plan:m365-enterprise-readiness-master-plan:B1`
- Owners: `engineering`, `security`, `operations`

## Context

- Domain: `code`
- Dependency: `A2`
- Goal: make tenant-scoped config the real runtime authority, with `.env` limited to bootstrap and local-dev roles.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-canonical-config-contract.md`
  - `docs/commercialization/m365-config-migration-and-auth-policy.md`
  - `docs/ENV.md`
  - `docs/M365_SERVER_APP.md`
  - `src/smarthaus_common/config.py`
  - `src/smarthaus_common/tenant_config.py`
  - `src/provisioning_api/main.py`
  - `src/provisioning_api/agent_command_center.py`
  - `src/provisioning_api/agent_workstation.py`
  - `src/provisioning_api/business_operations.py`
  - `src/provisioning_api/enterprise_dashboard.py`
  - `src/provisioning_api/unified_dashboard.py`
  - `src/m365_server/__main__.py`
  - `tests/test_env_loading.py`
- Denylist:
  - `docs/prompts/**`

## M - Model

- Problem: the documented production contract exists, but runtime still exposes legacy dotenv authority paths.
- Success criteria:
  - one canonical runtime authority path
  - legacy dotenv paths reduced to bootstrap/local-dev only
  - targeted tests prove precedence and tenant selection

## A - Annotate

Required evidence:

- runtime loader implementation path is explicit
- targeted tests cover precedence and tenant selection
- commercialization docs remain consistent with runtime behavior

## H - Harness

- `C0` preflight inventory of current config-loading paths.
- `C1` design the canonical authority path around `UCP_TENANT` and tenant YAML.
- `C2` implement runtime loader changes in the allowlisted files.
- `C3` add or update targeted tests for precedence and tenant selection.
- `C4` sync impacted docs if runtime behavior changes.
- `C5` ensure `.env` remains bootstrap/local only.
- `C6` run targeted validation.
- `C7` run `git diff --check`.
- `C8` sync plan and log.
- `C9` record residual risks.
- `C10` final gate decision.

## Validation

1. `pytest -q tests/test_env_loading.py`
2. `rg -n "load_dotenv|UCP_TENANT|tenant_config" src docs`
3. `git diff --check`

## No-Go Triggers

- production runtime authority remains ambiguous
- direct production `.env` dependence remains in the canonical path
- targeted precedence tests are missing or failing
